"""Cliente mínimo do Cloudflare Workers AI e da API GraphQL de analytics, para a bancada.

Segredos: lidos do arquivo de ambiente da raiz (CF_ACCOUNT_ID, CF_AI_TOKEN). Nunca são impressos nem gravados;
as mensagens de erro carregam só o código e a mensagem devolvidos pela Cloudflare.

Erros (https://developers.cloudflare.com/workers-ai/platform/errors/, conferido em 07/11/2026):
- 3036 (HTTP 429): franquia gratuita do dia esgotada. Nunca repetir; renova às 00:00 UTC.
- 5035 (HTTP 403): modelo exige Workers Paid. Nunca assinar: a configuração sai da bancada.
- 3040 (HTTP 429), outros 429 e 5xx, timeout: transitórios; até 3 tentativas com espera crescente.
"""
from __future__ import annotations

import base64
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
API = "https://api.cloudflare.com/client/v4"
TIMEOUT_S = 120
TENTATIVAS = 3


class ErroWorkersAI(Exception):
    def __init__(self, mensagem: str, codigo: int | None = None, http: int | None = None):
        super().__init__(mensagem)
        self.codigo = codigo
        self.http = http


class LimiteDiarioAtingido(ErroWorkersAI):
    """Erro 3036: a franquia de 10.000 neurons do dia acabou."""


class ExigePlanoPago(ErroWorkersAI):
    """Erro 5035: o modelo só roda no Workers Paid."""


@dataclass(frozen=True)
class Credenciais:
    conta: str
    token: str

    def __repr__(self) -> str:  # nunca expor o token em log ou traceback
        return "Credenciais(<ocultas>)"


def carregar_credenciais() -> Credenciais:
    load_dotenv(RAIZ / ".env")
    conta = os.environ.get("CF_ACCOUNT_ID", "").strip()
    token = os.environ.get("CF_AI_TOKEN", "").strip()
    faltando = [nome for nome, valor in (("CF_ACCOUNT_ID", conta), ("CF_AI_TOKEN", token)) if not valor]
    if faltando:
        raise SystemExit(f"Faltam variáveis no arquivo de ambiente da raiz: {', '.join(faltando)}")
    return Credenciais(conta, token)


@dataclass
class Pedido:
    modelo: str
    formato: str  # "json" (schnell) ou "multipart" (klein)
    prompt: str
    passos: int | None = None
    largura: int | None = None
    altura: int | None = None
    seed: int | None = None
    guidance: float | None = None
    referencias: list[bytes] = field(default_factory=list)


@dataclass
class Resultado:
    imagem: bytes
    segundos: float
    tentativas: int


def _erro(resp: requests.Response) -> tuple[int | None, str]:
    try:
        erros = resp.json().get("errors") or []
        if erros:
            codigo = erros[0].get("code")
            return codigo, f"HTTP {resp.status_code}, código {codigo}: {erros[0].get('message')}"
    except ValueError:
        pass
    return None, f"HTTP {resp.status_code}: {resp.text[:200]}"


def _enviar(cred: Credenciais, pedido: Pedido) -> requests.Response:
    url = f"{API}/accounts/{cred.conta}/ai/run/{pedido.modelo}"
    cabecalho = {"Authorization": f"Bearer {cred.token}"}
    if pedido.formato == "json":
        corpo: dict = {"prompt": pedido.prompt}
        if pedido.passos is not None:
            corpo["steps"] = pedido.passos
        return requests.post(url, headers=cabecalho, json=corpo, timeout=TIMEOUT_S)

    partes: dict = {"prompt": (None, pedido.prompt)}
    for nome, valor in (("width", pedido.largura), ("height", pedido.altura),
                        ("seed", pedido.seed), ("guidance", pedido.guidance)):
        if valor is not None:
            partes[nome] = (None, str(valor))
    for i, ref in enumerate(pedido.referencias):
        partes[f"input_image_{i}"] = (f"ref{i}.png", ref, "image/png")
    return requests.post(url, headers=cabecalho, files=partes, timeout=TIMEOUT_S)


def gerar(cred: Credenciais, pedido: Pedido) -> Resultado:
    for tentativa in range(1, TENTATIVAS + 1):
        inicio = time.perf_counter()
        try:
            resp = _enviar(cred, pedido)
        except (requests.Timeout, requests.ConnectionError) as exc:
            if tentativa == TENTATIVAS:
                raise ErroWorkersAI(f"falha de rede após {TENTATIVAS} tentativas ({type(exc).__name__})") from None
            time.sleep(5 * tentativa)
            continue
        segundos = round(time.perf_counter() - inicio, 2)

        if resp.ok:
            if resp.headers.get("content-type", "").startswith("image/"):
                return Resultado(resp.content, segundos, tentativa)
            imagem = (resp.json().get("result") or {}).get("image")
            if not imagem:
                raise ErroWorkersAI("resposta sem o campo image", http=resp.status_code)
            return Resultado(base64.b64decode(imagem), segundos, tentativa)

        codigo, mensagem = _erro(resp)
        if codigo == 3036:
            raise LimiteDiarioAtingido(mensagem, codigo, resp.status_code)
        if codigo == 5035:
            raise ExigePlanoPago(mensagem, codigo, resp.status_code)
        transitorio = resp.status_code == 429 or resp.status_code >= 500
        if not transitorio or tentativa == TENTATIVAS:
            raise ErroWorkersAI(mensagem, codigo, resp.status_code)
        time.sleep(5 * 2 ** (tentativa - 1))
    raise AssertionError("inalcançável")


# Consumo pela API GraphQL de analytics. Não há página oficial para este dataset: o nome e o campo
# (aiInferenceAdaptiveGroups, sum.totalNeurons) vêm de projetos de terceiros e são testados no comando `testar`.
# O token precisa da permissão "Account Analytics: Read". Os dados podem atrasar alguns minutos.
_CONSULTA = """
query Neurons($conta: string!, $inicio: Time!, $fim: Time!) {
  viewer {
    accounts(filter: {accountTag: $conta}) {
      aiInferenceAdaptiveGroups(limit: 1000, filter: {datetime_geq: $inicio, datetime_lt: $fim}) {
        count
        sum { totalNeurons }
        %s
      }
    }
  }
}
"""


def neurons(cred: Credenciais, inicio: datetime, fim: datetime) -> dict[str, tuple[int, float]]:
    """Devolve {modelo: (chamadas, neurons)} na janela; usa a chave "total" se o dataset não separar por modelo."""
    variaveis = {"conta": cred.conta,
                 "inicio": inicio.strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "fim": fim.strftime("%Y-%m-%dT%H:%M:%SZ")}
    ultimo_erro = ""
    for dimensoes in ("dimensions { modelId }", ""):
        resp = requests.post(f"{API}/graphql", timeout=60,
                             headers={"Authorization": f"Bearer {cred.token}"},
                             json={"query": _CONSULTA % dimensoes, "variables": variaveis})
        dados = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
        if resp.ok and not dados.get("errors"):
            contas = (dados.get("data") or {}).get("viewer", {}).get("accounts") or []
            grupos = contas[0].get("aiInferenceAdaptiveGroups", []) if contas else []
            saida: dict[str, tuple[int, float]] = {}
            for g in grupos:
                chave = (g.get("dimensions") or {}).get("modelId", "total")
                chamadas, total = saida.get(chave, (0, 0.0))
                saida[chave] = (chamadas + int(g.get("count") or 0),
                                total + float((g.get("sum") or {}).get("totalNeurons") or 0))
            return saida
        erros = dados.get("errors") or [{"message": resp.text[:200]}]
        ultimo_erro = f"HTTP {resp.status_code}: {erros[0].get('message')}"
    raise ErroWorkersAI(f"analytics indisponível ({ultimo_erro})")
