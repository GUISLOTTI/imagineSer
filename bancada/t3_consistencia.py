"""T3 da bancada: o mesmo personagem em 6 cenas, por 4 métodos (docs/05-bancada-visual.md).

  (a)  descrição fixa do personagem + mesma seed (config C, klein só texto)
  (b1) 1 imagem de referência (o polvo canônico), pedindo pose e ação diferentes em cada cena (config D)
  (b2) 3 referências: o canônico + 2 cenas do b1 (config E) — roda depois do b1
  (c)  personagem canônico recortado (rembg) sobre 6 cenários gerados SEM o personagem (config C). Os cenários
       também servem de fundo para a paralaxe do T4 v2.

Canônico: a primeira imagem do T1 da config C. Retoma de onde parou (pula cenas que já existem).
Custo estimado: ~2.600 neurons (6 x 104 + 6 x 107 + 6 x 113 + 6 x 104).

  bancada/.venv/Scripts/python bancada/t3_consistencia.py [--simular] [--metodos a,b1,b2,c]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageFilter

import bancada as b
import cf

PERSONAGEM = ("a friendly cartoon common octopus with reddish-brown textured skin, a rounded head, big round glossy "
              "eyes with dark pupils, a small smile and eight curling arms with pale suckers")
CENAS = [
    ("swimming above a colorful coral reef, arms trailing behind its body", "an empty colorful coral reef in clear blue water, no animals"),
    ("hiding inside a large spiral seashell on the sand, only its eyes and two arms peeking out", "a large empty spiral seashell lying on the sandy sea floor, no animals"),
    ("stretching one arm toward a tiny crab on the sand, curious expression", "a tiny crab on a sandy sea floor with soft light rays, no octopus"),
    ("turning gray and bumpy to blend in with the rocks around it", "a pile of gray bumpy rocks on the sea floor, no animals"),
    ("squeezing its soft body through a narrow gap between two big rocks", "a narrow gap between two big rocks on the sea floor, no animals"),
    ("resting next to an old wooden treasure chest in deep blue water", "an old wooden treasure chest on the deep blue sea floor, no animals"),
]


def png_ref(caminho: Path) -> bytes:
    with Image.open(caminho) as im:
        im = im.convert("RGB")
        im.thumbnail((496, 496))
        buf = BytesIO()
        im.save(buf, "PNG")
        return buf.getvalue()


def canonico(amb: b.Ambiente) -> Path:
    destino = amb.saida / "t3" / "canonico.jpg"
    if not destino.exists():
        origem = sorted((amb.saida / "t1" / "C").glob("*-01.jpg"))
        if not origem:
            raise SystemExit("Falta o canônico: rode `bancada.py t1 --config C` antes.")
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origem[0], destino)
        shutil.copy2(origem[0].with_suffix(".json"), destino.with_suffix(".json"))
    return destino


def gerar_metodo(amb: b.Ambiente, metodo: str, cfg_id: str, sujeitos: list[str], seed: int | None,
                 refs: list[bytes]) -> bool:
    """Gera as cenas que faltam. Devolve False se a franquia acabou."""
    cfg = b.CONFIGS[cfg_id]
    lote = f"t3-{metodo}-{b.agora():%Y%m%dT%H%M%S}"
    inicio, ok, obs, seguir = b.agora(), 0, "", True
    try:
        for i, sujeito in enumerate(sujeitos, 1):
            destino = amb.saida / "t3" / metodo / f"cena-{i}"
            if b.ja_existe(destino):
                continue
            b.gerar_e_registrar(amb, cfg, "t3", lote, sujeito, destino,
                                seed=seed if seed is not None else 3000 + i, refs=refs, prompt_id=f"cena-{i}")
            ok += 1
            print(f"[t3 {metodo}] cena {i}")
    except cf.LimiteDiarioAtingido:
        obs, seguir = "parou no 3036", False
        print("Franquia do dia esgotada. Rode de novo depois das 21:00 (Brasília): continua de onde parou.")
    except cf.ErroWorkersAI as exc:
        obs = f"erro: {exc}"
        print(f"[t3 {metodo}] interrompido: {exc}")
    if ok or obs:
        b.registrar_lote(amb, lote, "t3", cfg_id, inicio, b.agora(), ok, obs)
    return seguir


def compor_c(amb: b.Ambiente) -> None:
    """Cola o recorte do canônico sobre cada cenário vazio, com sombra suave. Não gasta franquia."""
    from rembg import new_session, remove

    pasta = amb.saida / "t3" / "c"
    fundos = sorted(pasta.glob("fundo-*.jpg"))
    if not fundos:
        return
    recorte_path = amb.saida / "t3" / "canonico-recorte.png"
    if not recorte_path.exists():
        with Image.open(canonico(amb)) as im:
            remove(im.convert("RGB"), session=new_session("isnet-general-use")).save(recorte_path)
    perso = Image.open(recorte_path)
    perso = perso.crop(perso.getbbox())
    for fundo_path in fundos:
        destino = pasta / fundo_path.name.replace("fundo-", "cena-")
        if destino.exists():
            continue
        fundo = Image.open(fundo_path).convert("RGBA")
        escala = fundo.height * 0.42 / perso.height
        p = perso.resize((int(perso.width * escala), int(perso.height * escala)), Image.LANCZOS)
        x = (fundo.width - p.width) // 2
        y = int(fundo.height * 0.80) - p.height
        sombra = Image.new("RGBA", fundo.size)
        mascara = p.getchannel("A").point(lambda a: int(a * 0.45))
        sombra.paste((0, 0, 0, 255), (x + 10, y + 18), mascara)
        fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(14)))
        fundo.alpha_composite(p, (x, y))
        fundo.convert("RGB").save(destino, quality=92)
        prov = json.loads(fundo_path.with_suffix(".json").read_text("utf-8"))
        prov.update({"composicao": "recorte do canônico (rembg isnet-general-use) sobre este fundo",
                     "canonico": "t3/canonico.jpg",
                     "sha256": hashlib.sha256(destino.read_bytes()).hexdigest()})
        destino.with_suffix(".json").write_text(json.dumps(prov, ensure_ascii=False, indent=2), "utf-8")
        print(f"[t3 c] {destino.name} composta")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--simular", action="store_true")
    ap.add_argument("--metodos", default="a,b1,b2,c")
    args = ap.parse_args()
    amb = b.Ambiente(args.simular)
    metodos = args.metodos.split(",")
    can = canonico(amb)
    ref_can = png_ref(can)

    if "a" in metodos:
        if not gerar_metodo(amb, "a", "C", [f"{PERSONAGEM}, {cena}" for cena, _ in CENAS], 1001, []):
            return
    if "b1" in metodos:
        sujeitos = [f"The octopus character from image 0, with exactly the same colors, face and proportions, but in a "
                    f"new pose: {cena}" for cena, _ in CENAS]
        if not gerar_metodo(amb, "b1", "D", sujeitos, None, [ref_can]):
            return
    if "b2" in metodos:
        b1 = [amb.saida / "t3" / "b1" / f"cena-{i}.jpg" for i in (1, 3)]
        if all(p.exists() for p in b1):
            sujeitos = [f"The same octopus character shown in images 0, 1 and 2, with the same colors, face and "
                        f"proportions: {cena}" for cena, _ in CENAS]
            if not gerar_metodo(amb, "b2", "E", sujeitos, None, [ref_can] + [png_ref(p) for p in b1]):
                return
        else:
            print("[t3 b2] precisa das cenas 1 e 3 do b1; pulando.")
    if "c" in metodos:
        cfg = b.CONFIGS["C"]
        lote = f"t3-c-{b.agora():%Y%m%dT%H%M%S}"
        inicio, ok, obs = b.agora(), 0, ""
        try:
            for i, (_, fundo) in enumerate(CENAS, 1):
                destino = amb.saida / "t3" / "c" / f"fundo-{i}"
                if b.ja_existe(destino):
                    continue
                b.gerar_e_registrar(amb, cfg, "t3", lote, fundo, destino, seed=4000 + i, prompt_id=f"fundo-{i}")
                ok += 1
                print(f"[t3 c] fundo {i}")
        except cf.LimiteDiarioAtingido:
            obs = "parou no 3036"
            print("Franquia do dia esgotada. Rode de novo depois das 21:00 (Brasília).")
        except cf.ErroWorkersAI as exc:
            obs = f"erro: {exc}"
            print(f"[t3 c] interrompido: {exc}")
        if ok or obs:
            b.registrar_lote(amb, lote, "t3", "C", inicio, b.agora(), ok, obs)
        compor_c(amb)


if __name__ == "__main__":
    main()
