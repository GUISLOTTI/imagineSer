"""Gera a página de avaliação às cegas do T2 a partir de saida/t2-chave.csv.

A página recebe só o código, o tema e o tamanho de cada imagem; a configuração (a chave) nunca sai deste PC.

  bancada/.venv/Scripts/python bancada/pagina_avaliacao.py [--simular]

Saída: bancada/saida/avaliacao/bancada-t2.html e o mapa de arquivos (arquivos.json) para publicar como artifact.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from PIL import Image

AQUI = Path(__file__).resolve().parent
NOMES = {"polvo": "Polvo", "figado": "Fígado", "saturno": "Saturno", "tartaruga": "Tartaruga"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args()
    saida = AQUI / "saida" / ("simulado" if args.simular else "")
    chave = list(csv.DictReader((saida / "t2-chave.csv").open(encoding="utf-8")))
    prompts = json.loads((AQUI / "prompts.json").read_text("utf-8"))
    temas = {t["id"]: {"nome": NOMES.get(t["id"], t["id"]), "conferir": t["notas_anatomia"]} for t in prompts["t2"]}

    imagens, arquivos = [], {}
    for linha in sorted(chave, key=lambda l: int(l["codigo"])):
        origem = next((saida / "t2-cegas").glob(f"img-{linha['codigo']}.*"))
        with Image.open(origem) as im:
            w, h = im.size
        publicado = f"img/{origem.name}"
        imagens.append({"codigo": linha["codigo"], "tema": Path(linha["arquivo"]).stem.rsplit("-", 1)[0],
                        "arquivo": publicado, "w": w, "h": h})
        arquivos[publicado] = origem.relative_to(AQUI.parent).as_posix()

    html = (AQUI / "avaliacao_modelo.html").read_text("utf-8")
    html = html.replace("__IMAGENS__", json.dumps(imagens, ensure_ascii=False))
    html = html.replace("__TEMAS__", json.dumps(temas, ensure_ascii=False))
    destino = saida / "avaliacao"
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "bancada-t2.html").write_text(html, "utf-8")
    (destino / "arquivos.json").write_text(json.dumps(arquivos, indent=1), "utf-8")
    print(f"{len(imagens)} imagens -> {(destino / 'bancada-t2.html').relative_to(AQUI).as_posix()}")


if __name__ == "__main__":
    main()
