"""T4 da bancada: clipe de 20 s com 5 planos a partir de imagens paradas (docs/05-bancada-visual.md).

Técnicas: movimento de câmera com easing, paralaxe em 2 camadas (personagem recortado com rembg sobre o fundo
preenchido), "respiração" do personagem, oscilação, pulso na batida, mudança de foco, partículas (bolhas) por script,
vinheta, legenda palavra a palavra e transição de pan rápido. Sem áudio (o T4 avalia só a imagem). Não gasta
franquia: usa as imagens do T1.

  bancada/.venv/Scripts/python bancada/t4_movimento.py [--rascunho]

--rascunho renderiza em 540x960 e 15 fps, para iterar rápido. Saída em bancada/saida/t4/.
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from rembg import new_session, remove
from scipy.ndimage import gaussian_filter

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
SAIDA = AQUI / "saida" / "t4"
FONTE = RAIZ / "assets-marca" / "fontes" / "LilitaOne-Regular.ttf"
MODELO_RECORTE = "isnet-general-use"
DUR_PLANO = 4.0
TEXTO = "Imagine ser um polvo. Oito braços, olhos curiosos e o fundo do mar inteiro para explorar."

# (imagem do T1, movimento). As imagens D usam a primeira do C como referência: mesmo personagem.
PLANOS = [
    ("t1/C/*-01.jpg", "aproximar"),
    ("t1/D/*-01.jpg", "subir"),
    ("t1/D/*-04.jpg", "afastar_foco"),
    ("t1/D/*-07.jpg", "lateral"),
    ("t1/D/*-10.jpg", "pulso"),
]


def suave(x: float) -> float:
    """Easing in-out (seno): começa e termina devagar."""
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


@dataclass
class Camada:
    fundo: Image.Image        # RGB, buraco do personagem preenchido
    personagem: Image.Image   # RGBA recortado, mesmo tamanho do fundo
    ancora: tuple[float, float]  # base do personagem (x, y) em pixels da imagem


def preparar(caminho: Path, sessao) -> Camada:
    img = Image.open(caminho).convert("RGB")
    recorte = remove(img, session=sessao)  # RGBA
    alfa = np.asarray(recorte.getchannel("A"), dtype=np.float32) / 255.0
    # Preenche o buraco do fundo com desfoque normalizado (média ponderada só do que é fundo).
    # A máscara é dilatada (MaxFilter) para o preenchimento cobrir também a borda semitransparente do recorte.
    peso = 1.0 - np.asarray(recorte.getchannel("A").point(lambda a: 255 if a > 8 else 0)
                            .filter(ImageFilter.MaxFilter(31)), dtype=np.float32) / 255.0
    rgb = np.asarray(img, dtype=np.float32)
    num = np.stack([gaussian_filter(rgb[..., c] * peso, 40) for c in range(3)], axis=-1)
    den = gaussian_filter(peso, 40)[..., None] + 1e-6
    preenchido = rgb * peso[..., None] + (num / den) * (1.0 - peso[..., None])
    fundo = Image.fromarray(np.clip(preenchido, 0, 255).astype(np.uint8))
    ys, xs = np.nonzero(alfa > 0.5)
    ancora = (float(xs.mean()), float(ys.max())) if len(xs) else (img.width / 2, img.height * 0.75)
    return Camada(fundo, recorte, ancora)


def janela(img_w: int, img_h: int, w: int, h: int, zoom: float, cx: float, cy: float) -> tuple[float, ...]:
    """Caixa de recorte (em pixels da imagem) que cobre a tela w x h com o zoom e o centro dados."""
    escala = max(w / img_w, h / img_h) * zoom
    bw, bh = w / escala, h / escala
    cx = min(max(cx, bw / 2), img_w - bw / 2)
    cy = min(max(cy, bh / 2), img_h - bh / 2)
    return (cx - bw / 2, cy - bh / 2, cx + bw / 2, cy + bh / 2)


def camera(movimento: str, t: float, img_w: int, img_h: int) -> dict:
    """Parâmetros do plano no instante t (0..DUR_PLANO): zoom e centro do fundo e do personagem, desfoque."""
    p = suave(t / DUR_PLANO)
    cx, cy = img_w / 2, img_h / 2
    respirar = 1.0 + 0.012 * math.sin(2 * math.pi * t / 2.2)
    c = {"z_fundo": 1.0, "z_perso": 1.0, "cx": cx, "cy": cy, "dx_perso": 0.0, "dy_perso": 0.0,
         "respirar": respirar, "desfoque": 0.0}
    if movimento == "aproximar":
        c.update(z_fundo=1.0 + 0.06 * p, z_perso=1.0 + 0.16 * p)
    elif movimento == "subir":
        c.update(z_fundo=1.12, z_perso=1.16, cy=img_h * (0.62 - 0.14 * p))
    elif movimento == "afastar_foco":
        c.update(z_fundo=1.14 - 0.10 * p, z_perso=1.20 - 0.18 * p, desfoque=6.0 * p)
    elif movimento == "lateral":
        c.update(z_fundo=1.12, z_perso=1.15, cx=img_w * (0.44 + 0.12 * p), dx_perso=-img_w * 0.05 * p,
                 dy_perso=img_h * 0.008 * math.sin(2 * math.pi * t / 1.6))
    elif movimento == "pulso":
        batida = math.exp(-((t - 1.2) / 0.12) ** 2) * 0.05  # "pop" curto em t = 1,2 s
        c.update(z_fundo=1.0 + 0.05 * p, z_perso=1.02 + 0.10 * p + batida)
    return c


def renderizar_plano(cam: Camada, movimento: str, t: float, w: int, h: int) -> Image.Image:
    iw, ih = cam.fundo.size
    c = camera(movimento, t, iw, ih)
    fundo = cam.fundo.resize((w, h), Image.BICUBIC, box=janela(iw, ih, w, h, c["z_fundo"], c["cx"], c["cy"]))
    if c["desfoque"] > 0.1:
        fundo = fundo.filter(ImageFilter.GaussianBlur(c["desfoque"] * w / 1080))
    # Personagem: zoom próprio (paralaxe) + respiração ancorada na base do corpo.
    z = c["z_perso"] * c["respirar"]
    ax, ay = cam.ancora
    cx = ax + (c["cx"] - ax) / c["respirar"] - c["dx_perso"]
    cy = ay + (c["cy"] - ay) / c["respirar"] - c["dy_perso"]
    perso = cam.personagem.resize((w, h), Image.BICUBIC, box=janela(iw, ih, w, h, z, cx, cy))
    quadro = fundo.convert("RGBA")
    quadro.alpha_composite(perso)
    return quadro.convert("RGB")


def bolhas(quadro: Image.Image, t: float, semente: int = 7) -> None:
    w, h = quadro.size
    rnd = np.random.default_rng(semente)
    camada = Image.new("RGBA", (w, h))
    d = ImageDraw.Draw(camada)
    for _ in range(36):
        x0, vel, raio, fase = rnd.uniform(0, w), rnd.uniform(0.05, 0.16) * h, rnd.uniform(4, 14) * w / 1080, rnd.uniform(0, 10)
        y = h + 40 - ((t + fase) * vel) % (h + 80)
        x = x0 + 12 * w / 1080 * math.sin(t * 2 + fase)
        d.ellipse((x - raio, y - raio, x + raio, y + raio), outline=(255, 255, 255, 150), width=max(1, int(raio / 4)))
        d.ellipse((x - raio * 0.45, y - raio * 0.55, x - raio * 0.1, y - raio * 0.2), fill=(255, 255, 255, 170))
    quadro.paste(camada, (0, 0), camada)


def vinheta(w: int, h: int) -> np.ndarray:
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    return np.clip(1.0 - 0.35 * np.clip(r - 0.55, 0, None) ** 1.5, 0.55, 1.0)[..., None].astype(np.float32)


def legenda(quadro: Image.Image, t: float, total: float, fonte: ImageFont.FreeTypeFont) -> None:
    """Palavra a palavra, em grupos de até 3, a palavra falada em amarelo. Tempo uniforme (sem narração no T4)."""
    palavras = TEXTO.split()
    i = min(int(t / total * len(palavras)), len(palavras) - 1)
    inicio = (i // 3) * 3
    grupo = palavras[inicio:inicio + 3]
    w, h = quadro.size
    d = ImageDraw.Draw(quadro)
    larguras = [d.textlength(p + " ", font=fonte) for p in grupo]
    x = (w - sum(larguras)) / 2
    y = h * 0.72  # abaixo do corpo do personagem e acima da faixa coberta pelos botões das redes
    contorno = max(2, int(fonte.size / 12))
    for k, (p, lw) in enumerate(zip(grupo, larguras)):
        cor = (255, 214, 0) if inicio + k == i else (255, 255, 255)
        d.text((x, y), p, font=fonte, fill=cor, stroke_width=contorno, stroke_fill=(0, 0, 0))
        x += lw


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--rascunho", action="store_true")
    args = ap.parse_args()
    w, h, fps = (540, 960, 15) if args.rascunho else (1080, 1920, 30)

    inicio = time.perf_counter()
    sessao = new_session(MODELO_RECORTE)
    origem = AQUI / "saida"
    caminhos = []
    for padrao, _ in PLANOS:
        achados = sorted(origem.glob(padrao))
        if not achados:
            raise SystemExit(f"Imagem não encontrada: {padrao} (rode o T1 antes).")
        caminhos.append(achados[0])
    camadas = [preparar(c, sessao) for c in caminhos]
    t_preparo = time.perf_counter() - inicio

    SAIDA.mkdir(parents=True, exist_ok=True)
    for i, cam in enumerate(camadas, 1):  # recortes para inspeção
        cam.personagem.save(SAIDA / f"recorte-{i}.png")
    nome = "t4-rascunho" if args.rascunho else "t4"
    destino = SAIDA / f"{nome}.mp4"
    cmd = [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destino)]
    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    fonte = ImageFont.truetype(str(FONTE), int(92 * w / 1080))
    vin = vinheta(w, h)
    total = DUR_PLANO * len(PLANOS)
    transicao = 0.25  # pan rápido com desfoque de movimento entre o 3º e o 4º plano
    n_quadros = int(total * fps)
    for q in range(n_quadros):
        t = q / fps
        k = min(int(t // DUR_PLANO), len(PLANOS) - 1)
        tp = t - k * DUR_PLANO
        quadro = renderizar_plano(camadas[k], PLANOS[k][1], tp, w, h)
        perto = (k == 2 and tp > DUR_PLANO - transicao) or (k == 3 and tp < transicao)
        if perto:
            dist = (DUR_PLANO - tp) if k == 2 else tp
            forca = 1.0 - dist / transicao
            deslocamento = int(forca * w * 0.25) * (-1 if k == 2 else 1)
            quadro = Image.fromarray(np.roll(np.asarray(quadro), deslocamento, axis=1))
            quadro = quadro.filter(ImageFilter.BoxBlur(max(1, int(forca * 30 * w / 1080))))
        bolhas(quadro, t)
        arr = (np.asarray(quadro, dtype=np.float32) * vin).astype(np.uint8)
        quadro = Image.fromarray(arr)
        legenda(quadro, t, total, fonte)
        ffmpeg.stdin.write(quadro.tobytes())
    ffmpeg.stdin.close()
    if ffmpeg.wait() != 0:
        raise SystemExit("FFmpeg falhou.")
    t_total = time.perf_counter() - inicio

    info = {"arquivo": destino.name, "tamanho": f"{w}x{h}", "fps": fps, "duracao_s": total,
            "imagens": [c.relative_to(origem).as_posix() for c in caminhos], "modelo_recorte": MODELO_RECORTE,
            "segundos_preparo": round(t_preparo, 1), "segundos_total": round(t_total, 1),
            "fonte_legenda": "Lilita One (SIL OFL 1.1)", "movimentos": [m for _, m in PLANOS]}
    destino.with_suffix(".json").write_text(json.dumps(info, ensure_ascii=False, indent=2), "utf-8")
    print(f"{destino.relative_to(AQUI).as_posix()}: {n_quadros} quadros em {t_total:.1f} s "
          f"(preparo {t_preparo:.1f} s, inclui baixar o modelo de recorte na 1ª vez)")


if __name__ == "__main__":
    main()
