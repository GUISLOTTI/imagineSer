"""Bancada visual do Imagine Ser (Fase 0). Protocolo: docs/05-bancada-visual.md. Regras: .claude/rules/bancada.md.

Rode na raiz do repositório com o Python do ambiente virtual:
  bancada/.venv/Scripts/python bancada/bancada.py <comando> [opções]

Comandos:
  testar                  1 imagem do schnell (A) + 1 do klein (C) + teste da API de consumo. Rode primeiro.
  t1 --config X [--n 10]  T1, método 1: lote de N imagens de uma configuração. Depois de ~10 min, rode `neurons`.
  t1-limite --config X --estimativa N
                          T1, método 2: gera até o erro 3036 (rodar logo depois de 00:00 UTC = 21:00 em Brasília).
  neurons                 Mede pela API o consumo dos lotes pendentes (lotes com mais de 10 min).
  t2 [--configs A,B,C,F]  T2: 4 temas x 3 prompts por configuração. Retoma de onde parou.
  embaralhar --teste t2   Copia as imagens com nomes aleatórios para a avaliação às cegas.
  resumo                  Tabela por configuração para colar em docs/08.

Opção global --simular: não chama a API (imagens de mentira, CSVs em saida/simulado/), para testar o fluxo.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import shutil
import sys
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw

import cf

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
CONFIGS = {k: {**v, "id": k} for k, v in json.loads((AQUI / "configs.json").read_text("utf-8")).items()
           if not k.startswith("_")}
PROMPTS = json.loads((AQUI / "prompts.json").read_text("utf-8"))
ESTILO = json.loads((RAIZ / "config" / "estilo.json").read_text("utf-8"))
TERMOS = "https://bfl.ai/legal/terms-of-service"
EXTENSOES = {".png", ".jpg", ".webp"}
FRANQUIA_DIA = 10_000

COLUNAS_RESULTADOS = ["data_utc", "lote", "teste", "config", "modelo", "passos", "tamanho_pedido",
                      "tamanho_recebido", "referencias", "seed", "tema", "prompt_id", "segundos_imagem",
                      "tentativas", "bytes", "arquivo", "erro"]
COLUNAS_LOTES = ["lote", "teste", "config", "inicio_utc", "fim_utc", "imagens_ok", "chamadas_analytics",
                 "neurons_total", "neurons_imagem_analytics", "neurons_imagem_limite", "observacao"]


class Ambiente:
    """Caminhos de saída; no modo simulado, tudo vai para saida/simulado/ (fora do Git)."""

    def __init__(self, simular: bool):
        self.simular = simular
        base = AQUI / "saida"
        self.saida = base / "simulado" if simular else base
        dados = self.saida if simular else AQUI
        self.resultados = dados / "resultados.csv"
        self.lotes = dados / "lotes.csv"
        self.cred = None if simular else cf.carregar_credenciais()


# ---------- utilidades ----------

def agora() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def de_iso(texto: str) -> datetime:
    return datetime.strptime(texto, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def ler_csv(caminho: Path) -> list[dict]:
    if not caminho.exists():
        return []
    with caminho.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def anexar_csv(caminho: Path, colunas: list[str], linha: dict) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    novo = not caminho.exists()
    with caminho.open("a", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        if novo:
            escritor.writeheader()
        escritor.writerow({c: linha.get(c, "") for c in colunas})


def reescrever_csv(caminho: Path, colunas: list[str], linhas: list[dict]) -> None:
    with caminho.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=colunas)
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow({c: linha.get(c, "") for c in colunas})


def extensao(dados: bytes) -> str:
    if dados[:8] == b"\x89PNG\r\n\x1a\n":
        return ".png"
    if dados[:3] == b"\xff\xd8\xff":
        return ".jpg"
    if dados[:4] == b"RIFF" and dados[8:12] == b"WEBP":
        return ".webp"
    return ".bin"


def ja_existe(destino_sem_ext: Path) -> bool:
    return any(destino_sem_ext.with_suffix(e).exists() for e in EXTENSOES)


def montar_prompt(sujeito: str, cfg: dict) -> str:
    partes = [ESTILO["prefixo"], sujeito, cfg.get("sufixo_prompt", ""), ESTILO["restricoes"]]
    return ". ".join(p.strip().rstrip(".") for p in partes if p.strip()) + "."


def tamanho_pedido(cfg: dict) -> str:
    return f"{cfg['largura']}x{cfg['altura']}" if cfg.get("largura") else "padrão do modelo"


def referencias(amb: Ambiente, n: int) -> list[bytes]:
    """As n primeiras imagens do T1 da configuração C, reduzidas para menos de 512x512 (exigência do klein)."""
    if n == 0:
        return []
    pasta = amb.saida / "t1" / "C"
    imagens = sorted(p for p in pasta.glob("*") if p.suffix in EXTENSOES) if pasta.exists() else []
    if len(imagens) < n:
        raise SystemExit(f"Esta configuração precisa de {n} imagem(ns) de referência: rode antes `t1 --config C`.")
    refs = []
    for caminho in imagens[:n]:
        with Image.open(caminho) as im:
            im = im.convert("RGB")
            im.thumbnail((496, 496))
            buf = BytesIO()
            im.save(buf, "PNG")
            refs.append(buf.getvalue())
    return refs


def gerar_simulado(cfg: dict, prompt: str, seed: int | None) -> cf.Resultado:
    rnd = random.Random(f"{cfg['id']}|{prompt}|{seed}")
    w, h = cfg.get("largura", 1024), cfg.get("altura", 1024)
    img = Image.new("RGB", (w, h), tuple(rnd.randrange(40, 200) for _ in range(3)))
    ImageDraw.Draw(img).text((24, 24), f"SIMULADO config {cfg['id']}", fill=(255, 255, 255))
    buf = BytesIO()
    img.save(buf, "JPEG", quality=90)
    return cf.Resultado(buf.getvalue(), round(rnd.uniform(0.5, 3.0), 2), 1)


def gerar_e_registrar(amb: Ambiente, cfg: dict, teste: str, lote: str, sujeito: str, destino: Path,
                      seed: int | None = None, refs: list[bytes] | None = None,
                      tema: str = "", prompt_id: str = "") -> Path:
    """Gera uma imagem, grava o arquivo + proveniência e anexa a linha em resultados.csv. Propaga erros da API."""
    refs = refs or []
    seed = seed if cfg["formato"] == "multipart" else None  # o schnell não aceita seed
    prompt = montar_prompt(sujeito, cfg)
    linha = {"data_utc": iso(agora()), "lote": lote, "teste": teste, "config": cfg["id"], "modelo": cfg["modelo"],
             "passos": cfg.get("passos", 4), "tamanho_pedido": tamanho_pedido(cfg), "referencias": len(refs),
             "seed": "" if seed is None else seed, "tema": tema, "prompt_id": prompt_id}
    pedido = cf.Pedido(modelo=cfg["modelo"], formato=cfg["formato"], prompt=prompt, passos=cfg.get("passos"),
                       largura=cfg.get("largura"), altura=cfg.get("altura"), seed=seed,
                       guidance=cfg.get("guidance"), referencias=refs)
    try:
        res = gerar_simulado(cfg, prompt, seed) if amb.simular else cf.gerar(amb.cred, pedido)
    except cf.ErroWorkersAI as exc:
        linha["erro"] = str(exc)
        anexar_csv(amb.resultados, COLUNAS_RESULTADOS, linha)
        raise

    arquivo = destino.with_suffix(extensao(res.imagem))
    arquivo.parent.mkdir(parents=True, exist_ok=True)
    arquivo.write_bytes(res.imagem)
    with Image.open(BytesIO(res.imagem)) as im:
        recebido = f"{im.width}x{im.height}"
    proveniencia = {
        "ferramenta": "Cloudflare Workers AI (REST)", "modelo": cfg["modelo"], "config": cfg["id"],
        "data_utc": linha["data_utc"], "prompt": prompt, "seed": seed, "passos": cfg.get("passos", 4),
        "tamanho_pedido": linha["tamanho_pedido"], "tamanho_recebido": recebido,
        "referencias_sha256": [hashlib.sha256(r).hexdigest() for r in refs],
        "sha256": hashlib.sha256(res.imagem).hexdigest(), "termos": TERMOS,
        "licenca": "Apache 2.0 (a confirmar antes do ADR-0005)", "simulado": amb.simular,
    }
    arquivo.with_suffix(".json").write_text(json.dumps(proveniencia, ensure_ascii=False, indent=2), "utf-8")
    linha.update({"tamanho_recebido": recebido, "segundos_imagem": res.segundos, "tentativas": res.tentativas,
                  "bytes": len(res.imagem), "arquivo": arquivo.relative_to(AQUI).as_posix()})
    anexar_csv(amb.resultados, COLUNAS_RESULTADOS, linha)
    return arquivo


def registrar_lote(amb: Ambiente, lote: str, teste: str, config: str, inicio: datetime, fim: datetime,
                   ok: int, observacao: str = "", **extra) -> None:
    anexar_csv(amb.lotes, COLUNAS_LOTES, {"lote": lote, "teste": teste, "config": config,
                                          "inicio_utc": iso(inicio), "fim_utc": iso(fim), "imagens_ok": ok,
                                          "observacao": observacao, **extra})


def exigir_intervalo(amb: Ambiente) -> None:
    """Lotes precisam de 2 min de folga entre si para a janela de analytics não misturar configurações."""
    lotes = ler_csv(amb.lotes)
    if lotes and not amb.simular:
        espera = de_iso(lotes[-1]["fim_utc"]) + timedelta(minutes=2) - agora()
        if espera.total_seconds() > 0:
            raise SystemExit(f"Aguarde {int(espera.total_seconds()) + 1} s: o lote anterior terminou há pouco.")


def config(cid: str) -> dict:
    if cid not in CONFIGS:
        raise SystemExit(f"Configuração desconhecida: {cid}. Opções: {', '.join(CONFIGS)}")
    return CONFIGS[cid]


def sujeito_t1(cfg: dict) -> str:
    return PROMPTS["t1"]["sujeito_com_referencia" if cfg.get("referencias") else "sujeito"]


# ---------- comandos ----------

def cmd_testar(amb: Ambiente, args) -> None:
    lote = f"conexao-{agora():%Y%m%dT%H%M%S}"
    inicio = agora()
    ok = 0
    for cid in ("A", "C"):
        cfg = CONFIGS[cid]
        try:
            arq = gerar_e_registrar(amb, cfg, "conexao", lote, PROMPTS["t1"]["sujeito"],
                                    amb.saida / "conexao" / f"{lote}-{cid}", seed=1)
            ok += 1
            with Image.open(arq) as im:
                print(f"[{cid}] ok: {im.width}x{im.height} -> {arq.relative_to(AQUI).as_posix()}")
        except cf.ExigePlanoPago as exc:
            print(f"[{cid}] exige Workers Paid ({exc}). Configuração fora da bancada; nunca assinar.")
        except cf.ErroWorkersAI as exc:
            print(f"[{cid}] erro: {exc}")
    registrar_lote(amb, lote, "conexao", "A+C", inicio, agora(), ok)
    if amb.simular:
        print("[analytics] não testado no modo simulado.")
        return
    try:
        uso = cf.neurons(amb.cred, agora() - timedelta(hours=2), agora() + timedelta(minutes=1))
        print(f"[analytics] ok. Últimas 2 h (pode atrasar alguns minutos): {uso or 'nenhum uso registrado ainda'}")
    except cf.ErroWorkersAI as exc:
        print(f"[analytics] {exc}. Sem a permissão 'Account Analytics: Read' no token, o T1 usa só o método do limite.")


def cmd_t1(amb: Ambiente, args) -> None:
    cfg = config(args.config)
    exigir_intervalo(amb)
    refs = referencias(amb, cfg.get("referencias", 0))
    lote = f"t1-{cfg['id']}-{agora():%Y%m%dT%H%M%S}"
    inicio, ok, obs = agora(), 0, ""
    try:
        for i in range(1, args.n + 1):
            gerar_e_registrar(amb, cfg, "t1", lote, sujeito_t1(cfg), amb.saida / "t1" / cfg["id"] / f"{lote}-{i:02d}",
                              seed=1000 + i, refs=refs)
            ok += 1
            print(f"[t1 {cfg['id']}] {i}/{args.n}")
    except cf.LimiteDiarioAtingido:
        obs = "parou no 3036"
        print("Franquia do dia esgotada (3036). Recomeça às 00:00 UTC (21:00 em Brasília).")
    except cf.ErroWorkersAI as exc:
        obs = f"erro: {exc}"
        print(f"Lote interrompido: {exc}")
    registrar_lote(amb, lote, "t1", cfg["id"], inicio, agora(), ok, obs)
    print(f"Lote {lote}: {ok} imagem(ns). Daqui a ~10 min, rode `neurons` para medir o consumo.")


def cmd_t1_limite(amb: Ambiente, args) -> None:
    """Método 2: neurons/imagem = (franquia - uso anterior do dia) / imagens geradas até o 3036."""
    cfg = config(args.config)
    exigir_intervalo(amb)
    refs = referencias(amb, cfg.get("referencias", 0))
    # Trava: sem 3036 até ~1,3x a franquia, a conta pode não estar no Workers Free. Para antes de gastar.
    teto = int(1.3 * FRANQUIA_DIA / args.estimativa) + 1
    usado_antes = 0.0
    if not amb.simular:
        meia_noite = agora().replace(hour=0, minute=0, second=0)
        try:
            usado_antes = sum(n for _, n in cf.neurons(amb.cred, meia_noite, agora()).values())
        except cf.ErroWorkersAI as exc:
            print(f"Uso anterior do dia desconhecido ({exc}); assumindo 0. Rode logo após 00:00 UTC.")
    lote = f"t1lim-{cfg['id']}-{agora():%Y%m%dT%H%M%S}"
    inicio, ok, obs, extra = agora(), 0, "", {}
    try:
        for i in range(1, teto + 1):
            if amb.simular and ok * args.estimativa >= FRANQUIA_DIA:
                raise cf.LimiteDiarioAtingido("3036 simulado", 3036, 429)
            gerar_e_registrar(amb, cfg, "t1-limite", lote, sujeito_t1(cfg),
                              amb.saida / "t1-limite" / cfg["id"] / f"{lote}-{i:03d}", seed=5000 + i, refs=refs)
            ok += 1
            if ok % 10 == 0:
                print(f"[t1-limite {cfg['id']}] {ok} imagens")
        obs = "ALERTA: teto atingido sem 3036; conferir se a conta está no Workers Free"
        print(obs)
    except cf.LimiteDiarioAtingido:
        obs = f"3036 após {ok} imagens; uso anterior do dia: {round(usado_antes, 1)} neurons"
        if ok:
            extra["neurons_imagem_limite"] = round((FRANQUIA_DIA - usado_antes) / ok, 2)
        print(obs, f"-> {extra.get('neurons_imagem_limite', '?')} neurons/imagem")
    except cf.ErroWorkersAI as exc:
        obs = f"erro: {exc}"
        print(f"Interrompido: {exc}")
    registrar_lote(amb, lote, "t1-limite", cfg["id"], inicio, agora(), ok, obs, **extra)


def cmd_neurons(amb: Ambiente, args) -> None:
    if amb.simular:
        print("Medição de consumo não existe no modo simulado.")
        return
    lotes = ler_csv(amb.lotes)
    mudou = False
    for lote in lotes:
        # Só o T1 tem lotes isolados no tempo (uma configuração por janela); os demais se sobrepõem.
        if lote["teste"] != "t1" or lote["neurons_total"] or not int(lote["imagens_ok"] or 0):
            continue
        fim = de_iso(lote["fim_utc"])
        if agora() - fim < timedelta(minutes=10):
            print(f"{lote['lote']}: aguarde mais {int((fim + timedelta(minutes=10) - agora()).total_seconds() // 60) + 1} min.")
            continue
        try:
            uso = cf.neurons(amb.cred, de_iso(lote["inicio_utc"]) - timedelta(seconds=10), fim + timedelta(seconds=60))
        except cf.ErroWorkersAI as exc:
            print(f"{exc}. Sem analytics, use o método do limite (t1-limite).")
            return
        chamadas = sum(c for c, _ in uso.values())
        total = sum(n for _, n in uso.values())
        ok = int(lote["imagens_ok"])
        lote.update({"chamadas_analytics": chamadas, "neurons_total": round(total, 2),
                     "neurons_imagem_analytics": round(total / ok, 2)})
        mudou = True
        aviso = "" if chamadas == ok else f" (atenção: {chamadas} chamadas no analytics vs {ok} imagens)"
        print(f"{lote['lote']}: {round(total, 1)} neurons / {ok} imagens = {round(total / ok, 2)} por imagem{aviso}")
    if mudou:
        reescrever_csv(amb.lotes, COLUNAS_LOTES, lotes)


def cmd_t2(amb: Ambiente, args) -> None:
    for cid in args.configs.split(","):
        cfg = config(cid.strip())
        if cfg.get("referencias"):
            print(f"[{cfg['id']}] usa referência: pertence ao T3, não ao T2. Pulando.")
            continue
        lote = f"t2-{cfg['id']}-{agora():%Y%m%dT%H%M%S}"
        inicio, ok, obs, parar = agora(), 0, "", False
        try:
            for tema in PROMPTS["t2"]:
                for j, sujeito in enumerate(tema["prompts"], 1):
                    destino = amb.saida / "t2" / cfg["id"] / f"{tema['id']}-{j}"
                    if ja_existe(destino):
                        continue
                    gerar_e_registrar(amb, cfg, "t2", lote, sujeito, destino, seed=2000 + j,
                                      tema=tema["id"], prompt_id=f"{tema['id']}-{j}")
                    ok += 1
                    print(f"[t2 {cfg['id']}] {tema['id']}-{j}")
        except cf.LimiteDiarioAtingido:
            obs, parar = "parou no 3036", True
            print("Franquia do dia esgotada (3036). Rode de novo depois das 00:00 UTC: continua de onde parou.")
        except cf.ErroWorkersAI as exc:
            obs = f"erro: {exc}"
            print(f"[{cfg['id']}] interrompida: {exc}")
        if ok or obs:
            registrar_lote(amb, lote, "t2", cfg["id"], inicio, agora(), ok, obs)
        if parar:
            break


def cmd_embaralhar(amb: Ambiente, args) -> None:
    origem = amb.saida / args.teste
    imagens = sorted(p for p in origem.rglob("*") if p.suffix in EXTENSOES) if origem.exists() else []
    if not imagens:
        raise SystemExit(f"Nenhuma imagem em {origem}.")
    # Incremental: imagens já embaralhadas mantêm o código (as notas dadas continuam valendo); só as novas ganham código.
    destino = amb.saida / f"{args.teste}-cegas"
    destino.mkdir(parents=True, exist_ok=True)
    caminho_chave = amb.saida / f"{args.teste}-chave.csv"
    chave = ler_csv(caminho_chave)
    ja = {linha["arquivo"] for linha in chave}
    usados = {int(linha["codigo"]) for linha in chave}
    novas = [c for c in imagens if c.relative_to(amb.saida).as_posix() not in ja]
    livres = [n for n in range(1000, 10000) if n not in usados]
    codigos = random.SystemRandom().sample(livres, len(novas))
    for codigo, caminho in sorted(zip(codigos, novas)):
        shutil.copy2(caminho, destino / f"img-{codigo}{caminho.suffix}")
        prov = json.loads(caminho.with_suffix(".json").read_text("utf-8"))
        chave.append({"codigo": codigo, "arquivo": caminho.relative_to(amb.saida).as_posix(),
                      "config": prov["config"], "tamanho_recebido": prov["tamanho_recebido"]})
    reescrever_csv(caminho_chave, ["codigo", "arquivo", "config", "tamanho_recebido"], chave)
    print(f"{len(novas)} imagem(ns) nova(s), {len(chave)} no total em {destino.relative_to(AQUI).as_posix()}; "
          f"chave em {caminho_chave.name} (não abrir antes das notas).")


def media(valores: list[float]) -> str:
    return f"{sum(valores) / len(valores):.1f}" if valores else "—"


def cmd_resumo(amb: Ambiente, args) -> None:
    linhas, lotes = ler_csv(amb.resultados), ler_csv(amb.lotes)
    print("| Config | Imagens ok | Erros | s/imagem (média) | Tamanho recebido | Neurons/imagem (analytics) | Neurons/imagem (limite) |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for cid in CONFIGS:
        da_config = [l for l in linhas if l["config"] == cid]
        if not da_config:
            continue
        oks = [l for l in da_config if not l["erro"]]
        segs = [float(l["segundos_imagem"]) for l in oks if l["segundos_imagem"]]
        tamanhos = sorted({l["tamanho_recebido"] for l in oks})
        an = [float(l["neurons_imagem_analytics"]) for l in lotes if l["config"] == cid and l["neurons_imagem_analytics"]]
        li = [float(l["neurons_imagem_limite"]) for l in lotes if l["config"] == cid and l["neurons_imagem_limite"]]
        print(f"| {cid} | {len(oks)} | {len(da_config) - len(oks)} | {media(segs)} | {', '.join(tamanhos) or '—'} "
              f"| {media(an)} | {media(li)} |")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Bancada visual do Imagine Ser (Fase 0).")
    p.add_argument("--simular", action="store_true", help="não chama a API; imagens de mentira")
    sub = p.add_subparsers(dest="comando", required=True)
    sub.add_parser("testar")
    t1 = sub.add_parser("t1")
    t1.add_argument("--config", required=True)
    t1.add_argument("--n", type=int, default=10)
    lim = sub.add_parser("t1-limite")
    lim.add_argument("--config", required=True)
    lim.add_argument("--estimativa", type=float, required=True, help="neurons/imagem medidos no método 1")
    sub.add_parser("neurons")
    t2 = sub.add_parser("t2")
    t2.add_argument("--configs", default="A,B,C,F")
    emb = sub.add_parser("embaralhar")
    emb.add_argument("--teste", default="t2")
    sub.add_parser("resumo")
    args = p.parse_args()

    amb = Ambiente(args.simular)
    {"testar": cmd_testar, "t1": cmd_t1, "t1-limite": cmd_t1_limite, "neurons": cmd_neurons, "t2": cmd_t2,
     "embaralhar": cmd_embaralhar, "resumo": cmd_resumo}[args.comando](amb, args)


if __name__ == "__main__":
    main()
