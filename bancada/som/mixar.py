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


def mixar(eventos: list[dict], duracao: float, destino: Path) -> dict:
    n = int((duracao + 1.0) * SR)
    mix = np.zeros((n, 2), dtype=np.float64)
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
        mix[ini:fim] += x[: fim - ini] * ganho
    mix = mix[: int(duracao * SR)]
    # corta o subgrave (< 40 Hz): ninguém ouve no celular e ele rouba volume da mixagem
    mix = signal.sosfilt(signal.butter(2, 40, btype="high", fs=SR, output="sos"), mix, axis=0)
    pico = float(np.abs(mix).max())
    # limitador suave: só age perto do teto, sem cortar picos secos
    mix = np.where(np.abs(mix) > 0.7, np.sign(mix) * (0.7 + 0.25 * np.tanh((np.abs(mix) - 0.7) / 0.25)), mix)
    destino.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(destino, SR, (mix * 32767).astype(np.int16))
    return {"eventos": len(eventos), "sons_distintos": len(cache), "pico_antes_do_limitador": round(pico, 3)}


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
