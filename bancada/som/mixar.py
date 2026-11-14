"""Mixa a trilha de efeitos de uma cena: lista de eventos {t, som, vol?, pan?, ...params} → WAV estéreo 48 kHz.

Uso como módulo: mixar(eventos, duracao, destino).  O renderizar.py chama isto e junta o áudio ao vídeo.
Uso direto:  python bancada/som/mixar.py catalogo   → bancada/saida/som/catalogo.mp4 (cada som com o nome na tela,
             para o Gabriel ouvir e apontar "o som X ficou ruim").
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sintese  # noqa: E402

SR = sintese.SR
RAIZ = Path(__file__).resolve().parents[2]
CHAVES_DO_EVENTO = {"t", "som", "vol", "pan"}


def _posicionar(x: np.ndarray, pan: float) -> np.ndarray:
    if x.ndim == 2:
        return x
    ang = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)], axis=1)


# ---------------- a voz manda (ADR-0018) ----------------
# Quando a narração fala, os efeitos abaixam (ducking) e abrem um "buraco" na faixa de presença da fala (~1–4 kHz),
# onde mora a inteligibilidade. Ambiente abaixa mais que os efeitos. Tudo com 40 ms de antecipação: como a mixagem
# é feita depois, dá para baixar os efeitos um instante ANTES de a palavra começar.
DUCK_EFEITOS_DB = 6.0
DUCK_AMBIENTE_DB = 9.0
BURACO_FALA_DB = 5.0
VOZ_RMS = 0.1          # fala normalizada a −20 dBFS RMS (antes do loudnorm final)
HOP = 256


def _atividade_voz(voz: np.ndarray) -> np.ndarray:
    """0 = silêncio, 1 = falando, por bloco de HOP amostras; sobe rápido, desce em ~300 ms, antecipa 40 ms."""
    n = len(voz) // HOP
    rms = np.sqrt(np.mean(voz[: n * HOP].reshape(n, HOP) ** 2, axis=1) + 1e-12)
    db = 20 * np.log10(rms / (rms.max() + 1e-12))
    alvo = np.clip((db + 40) / 15, 0, 1)
    sobe, desce = 1 - np.exp(-1 / 2), 1 - np.exp(-1 / (0.3 * SR / HOP))
    saida, v = np.zeros_like(alvo), 0.0
    for i, x in enumerate(alvo):
        v += (x - v) * (sobe if x > v else desce)
        saida[i] = v
    k = int(0.04 * SR / HOP)
    return np.concatenate([saida[k:], np.full(k, saida[-1])])


def _abrir_espaco(bus: np.ndarray, atividade: np.ndarray, duck_db: float, buraco_db: float) -> np.ndarray:
    saida = np.zeros_like(bus)
    for c in range(bus.shape[1]):
        f, tt, Z = signal.stft(bus[:, c], SR, nperseg=1024, noverlap=1024 - HOP)
        presenca = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / 2000) / 0.7) ** 2)[:, None]
        a = atividade[np.clip(np.round(tt * SR / HOP).astype(int), 0, len(atividade) - 1)][None, :]
        Z *= 10 ** ((-duck_db * a - buraco_db * a * presenca) / 20)
        _, y = signal.istft(Z, SR, nperseg=1024, noverlap=1024 - HOP)
        saida[: min(len(y), len(bus)), c] = y[: len(bus)]
    return saida


def _rms_db(x: np.ndarray, mascara: np.ndarray) -> float:
    return float(10 * np.log10(np.mean(x[mascara] ** 2) + 1e-12))


def mixar(eventos: list[dict], duracao: float, destino: Path, voz: np.ndarray | None = None,
          ajustar: bool = True) -> dict:
    n = int((duracao + 1.0) * SR)
    efeitos = np.zeros((n, 2), dtype=np.float64)
    ambiente = np.zeros((n, 2), dtype=np.float64)
    cache: dict[str, np.ndarray] = {}
    for e in eventos:
        params = {k: v for k, v in e.items() if k not in CHAVES_DO_EVENTO}
        chave = json.dumps([e["som"], params], sort_keys=True)
        if chave not in cache:
            cache[chave] = sintese.gerar(e["som"], **params)
        x = _posicionar(cache[chave], e.get("pan", 0.0))
        ganho = 10 ** ((sintese.GANHO_DB[e["som"]] + e.get("vol", 0.0)) / 20)
        ini = int(e["t"] * SR)
        if ini >= n:
            continue
        fim = min(n, ini + len(x))
        (ambiente if e["som"] == "ambiente" else efeitos)[ini:fim] += x[: fim - ini] * ganho
    m = int(duracao * SR)
    efeitos, ambiente = efeitos[:m], ambiente[:m]
    info: dict = {"eventos": len(eventos), "sons_distintos": len(cache)}

    if voz is not None:
        voz = np.pad(voz, (0, max(0, m - len(voz))))[:m].astype(np.float64)
        voz = signal.sosfilt(signal.butter(2, 80, btype="high", fs=SR, output="sos"), voz)
        atividade = _atividade_voz(voz)
        falando = np.repeat(atividade > 0.5, HOP)[:m]
        falando = np.pad(falando, (0, m - len(falando)))
        voz *= VOZ_RMS / np.sqrt(np.mean(voz[falando] ** 2) + 1e-12)
        if ajustar:
            efeitos = _abrir_espaco(efeitos, atividade, DUCK_EFEITOS_DB, BURACO_FALA_DB)
            ambiente = _abrir_espaco(ambiente, atividade, DUCK_AMBIENTE_DB, BURACO_FALA_DB)
        fundo = efeitos + ambiente
        # métrica: quanto a voz fica acima de tudo o resto enquanto fala (e só na faixa de presença)
        presenca = lambda x: signal.sosfilt(signal.butter(4, [1000, 4000], btype="band", fs=SR, output="sos"), x, axis=0)
        info["voz_acima_do_fundo_db"] = round(_rms_db(voz, falando) - _rms_db(fundo.mean(axis=1), falando), 1)
        info["voz_acima_do_fundo_1a4khz_db"] = round(
            _rms_db(presenca(voz), falando) - _rms_db(presenca(fundo.mean(axis=1)), falando), 1)
        info["ajuste_voz"] = ajustar
        mix = fundo + voz[:, None]
    else:
        mix = efeitos + ambiente
    # corta o subgrave (< 40 Hz): ninguém ouve no celular e ele rouba volume da mixagem
    mix = signal.sosfilt(signal.butter(2, 40, btype="high", fs=SR, output="sos"), mix, axis=0)
    info["pico_antes_do_limitador"] = round(float(np.abs(mix).max()), 3)
    # limitador suave: só age perto do teto, sem cortar picos secos
    mix = np.where(np.abs(mix) > 0.7, np.sign(mix) * (0.7 + 0.25 * np.tanh((np.abs(mix) - 0.7) / 0.25)), mix)
    destino.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(destino, SR, (mix * 32767).astype(np.int16))
    return info


def catalogo() -> Path:
    """Vídeo com cada som e o nome na tela (para o Gabriel avaliar som por som)."""
    from PIL import Image, ImageDraw, ImageFont
    import imageio_ffmpeg

    itens = [
        ("bolhas", {}), ("ventosa (solta)", {"som": "ventosa"}), ("ventosa (gruda)", {"som": "ventosa", "gruda": True}),
        ("pop", {}), ("pop_grande", {}), ("tique 1-8 (contagem)", {"som": "tique", "seq": 8}), ("plim", {}),
        ("whoosh", {"pan_ini": -0.8, "pan_fim": 0.8}), ("whoosh grave", {"som": "whoosh", "grave": True, "dur": 1.6}),
        ("esticar", {}), ("piscar", {}), ("camuflagem", {}), ("nadar", {}), ("pergunta", {}), ("impacto", {}),
        ("ambiente (fundo do mar)", {"som": "ambiente", "dur": 4.0}),
    ]
    eventos, marcas, t = [], [], 0.6
    for nome, p in itens:
        p = dict(p)
        som = p.pop("som", nome.split(" ")[0])
        seq = p.pop("seq", 0)
        marcas.append((t, nome))
        if seq:
            for i in range(seq):
                eventos.append({"t": t + i * 0.27, "som": som, "nota": i})
            t += seq * 0.27 + 0.9
        else:
            eventos.append({"t": t, "som": som, **p})
            t += len(sintese.gerar(som, **p)) / SR + 0.8
    duracao = t + 0.4
    pasta = RAIZ / "bancada" / "saida" / "som"
    wav = pasta / "catalogo.wav"
    mixar(eventos, duracao, wav)

    fonte = ImageFont.truetype(str(RAIZ / "assets-marca" / "fontes" / "LilitaOne-Regular.ttf"), 64)
    menor = ImageFont.truetype(str(RAIZ / "assets-marca" / "fontes" / "LilitaOne-Regular.ttf"), 34)
    fps, w, h = 10, 720, 1280
    destino = pasta / "catalogo.mp4"
    ff = subprocess.Popen(
        [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(destino)],
        stdin=subprocess.PIPE,
    )
    for i in range(int(duracao * fps)):
        tq = i / fps
        atual = [(k, nome) for k, (ti, nome) in enumerate(marcas) if ti <= tq + 0.05]
        img = Image.new("RGB", (w, h), (14, 52, 82))
        d = ImageDraw.Draw(img)
        d.text((w / 2, 140), "Catálogo de sons", font=menor, fill=(255, 214, 0), anchor="mm")
        if atual:
            k, nome = atual[-1]
            d.text((w / 2, h / 2 - 40), f"{k + 1}", font=fonte, fill=(255, 214, 0), anchor="mm")
            d.text((w / 2, h / 2 + 50), nome, font=fonte, fill="white", anchor="mm", stroke_width=4, stroke_fill=(22, 22, 42))
        ff.stdin.write(img.tobytes())
    ff.stdin.close()
    ff.wait()
    return destino


if __name__ == "__main__":
    if sys.argv[1:] == ["catalogo"]:
        print(catalogo())
    else:
        print(__doc__)
