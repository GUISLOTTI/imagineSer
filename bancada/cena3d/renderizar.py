"""Renderiza uma cena 3D (bancada T6) quadro a quadro: Chrome sem janela → imagens → FFmpeg → MP4.

A cena é uma página local (cena.html + cenas/<nome>.js, Three.js). Para cada quadro, o script chama
`window.cena.quadro(t)` e recebe a imagem pronta (3D + legenda + etiquetas). Nada depende do relógio,
então o resultado não depende da velocidade da máquina.

Uso:
  python bancada/cena3d/renderizar.py --cena polvo                      # vídeo 1080x1920, 30 fps
  python bancada/cena3d/renderizar.py --cena polvo --rascunho           # 540x960, 15 fps
  python bancada/cena3d/renderizar.py --cena polvo --gl swiftshader     # sem GPU (como no runner do GitHub)
  python bancada/cena3d/renderizar.py --cena polvo --quadros 0,2.4,7.8  # só alguns quadros, numa folha PNG

Saídas em bancada/saida/t6/ (fora do Git): <cena>[-sufixo].mp4 + .json (medição e proveniência) + folha de quadros.
O servidor local só entrega bancada/cena3d/ e assets-marca/fontes/ (nunca a raiz do repositório).
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import platform
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import imageio_ffmpeg
from PIL import Image
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parents[2]
CENA3D = RAIZ / "bancada" / "cena3d"
FONTES = RAIZ / "assets-marca" / "fontes"
SAIDA = RAIZ / "bancada" / "saida" / "t6"
PERMITIDOS = {"/cena3d/": CENA3D, "/fontes/": FONTES}


class Servidor(SimpleHTTPRequestHandler):
    """Entrega só os diretórios permitidos; qualquer outro caminho é 404."""

    def translate_path(self, path: str) -> str:
        caminho = path.split("?", 1)[0].split("#", 1)[0]
        for prefixo, pasta in PERMITIDOS.items():
            if caminho.startswith(prefixo):
                alvo = (pasta / caminho[len(prefixo):]).resolve()
                if alvo.is_relative_to(pasta):
                    return str(alvo)
        return str(CENA3D / "__inexistente__")

    def log_message(self, *args) -> None:  # silencioso
        pass


Servidor.extensions_map = {**SimpleHTTPRequestHandler.extensions_map, ".js": "text/javascript", ".ttf": "font/ttf"}


def argumentos_gl(modo: str) -> list[str]:
    if modo == "swiftshader":
        return ["--use-angle=swiftshader", "--enable-unsafe-swiftshader"]
    return ["--enable-gpu", "--ignore-gpu-blocklist"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cena", default="polvo")
    ap.add_argument("--largura", type=int, default=1080)
    ap.add_argument("--altura", type=int, default=1920)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--rascunho", action="store_true", help="540x960 a 15 fps")
    ap.add_argument("--gl", choices=["gpu", "swiftshader"], default="gpu")
    ap.add_argument("--quadros", help="instantes em segundos separados por vírgula; gera só uma folha PNG")
    ap.add_argument("--ate", type=float, help="renderiza só até este instante (s)")
    ap.add_argument("--sufixo", default="")
    a = ap.parse_args()
    if a.rascunho:
        a.largura, a.altura, a.fps = 540, 960, 15

    SAIDA.mkdir(parents=True, exist_ok=True)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), partial(Servidor))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{httpd.server_port}/cena3d/cena.html?cena={a.cena}&w={a.largura}&h={a.altura}"

    erros: list[str] = []
    with sync_playwright() as pw:
        navegador = pw.chromium.launch(channel="chrome", headless=True, args=argumentos_gl(a.gl))
        pagina = navegador.new_page(viewport={"width": 400, "height": 400})
        pagina.on("console", lambda m: erros.append(f"{m.type}: {m.text}") if m.type in ("error", "warning") else None)
        pagina.on("pageerror", lambda e: erros.append(f"pageerror: {e}"))
        t_ini = time.perf_counter()
        pagina.goto(url)
        try:
            pagina.wait_for_function("window.cenaPronta === true", timeout=60_000)
        except Exception:
            print("\n".join(erros) or "a cena não ficou pronta", file=sys.stderr)
            raise SystemExit(1)
        preparo = time.perf_counter() - t_ini
        info = pagina.evaluate("window.cena.info()")
        duracao = pagina.evaluate("window.cena.duracao")
        print(f"cena {a.cena}: {duracao:.1f} s · {a.largura}x{a.altura} · WebGL: {info['renderer']}")

        def quadro(t: float, formato: str = "jpeg") -> bytes:
            dado = pagina.evaluate("([t, f]) => window.cena.quadro(t, f)", [t, formato])
            return base64.b64decode(dado.split(",", 1)[1])

        nome = f"{a.cena}{a.sufixo}"
        if a.quadros:
            instantes = [float(x) for x in a.quadros.split(",")]
            imgs = [Image.open(io.BytesIO(quadro(t, "png"))).convert("RGB") for t in instantes]
            w = 360
            mini = [im.resize((w, round(im.height * w / im.width))) for im in imgs]
            folha = Image.new("RGB", (w * min(4, len(mini)), mini[0].height * ((len(mini) + 3) // 4)), "black")
            for i, im in enumerate(mini):
                folha.paste(im, ((i % 4) * w, (i // 4) * im.height))
            destino = SAIDA / f"{nome}-quadros.png"
            folha.save(destino)
            print(f"folha: {destino}")
            if erros:
                print("avisos do navegador:\n  " + "\n  ".join(dict.fromkeys(erros)), file=sys.stderr)
            navegador.close()
            return

        fim = min(duracao, a.ate) if a.ate else duracao
        total = int(round(fim * a.fps))
        destino = SAIDA / f"{nome}.mp4"
        ff = subprocess.Popen(
            [imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps),
             "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
             "-movflags", "+faststart", str(destino)],
            stdin=subprocess.PIPE,
        )
        t_render = time.perf_counter()
        for i in range(total):
            ff.stdin.write(quadro(i / a.fps))
            if i % (a.fps * 2) == 0:
                passado = time.perf_counter() - t_render
                print(f"\r  quadro {i}/{total} · {passado / max(1, i) * 1000:.0f} ms/quadro", end="", flush=True)
        ff.stdin.close()
        ff.wait()
        render = time.perf_counter() - t_render
        navegador.close()
    httpd.shutdown()

    medicao = {
        "cena": a.cena, "data_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "resolucao": f"{a.largura}x{a.altura}", "fps": a.fps, "quadros": total, "duracao_video_s": round(total / a.fps, 2),
        "gl": a.gl, "webgl_renderer": info["renderer"], "three": info["three"],
        "preparo_s": round(preparo, 1), "render_s": round(render, 1), "ms_por_quadro": round(render / max(1, total) * 1000, 1),
        "maquina": platform.platform(), "arquivo": destino.name,
        "proveniencia": "cena procedural (código em bancada/cena3d), sem modelo generativo; Three.js MIT; fonte Lilita One OFL",
        "avisos_navegador": list(dict.fromkeys(erros))[:20],
    }
    destino.with_suffix(".json").write_text(json.dumps(medicao, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{destino.name}: {render:.1f} s de render para {total / a.fps:.1f} s de vídeo "
          f"({medicao['ms_por_quadro']} ms/quadro, preparo {preparo:.1f} s)")
    if erros:
        print("avisos do navegador:\n  " + "\n  ".join(medicao["avisos_navegador"]), file=sys.stderr)


if __name__ == "__main__":
    main()
