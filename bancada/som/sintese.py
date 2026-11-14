"""Efeitos sonoros sintetizados por código (ADR-0018). Nada de material de terceiros: cada som nasce de osciladores,
ruído e filtros aqui, com semente fixa, então a proveniência é este arquivo + a semente.

Cada função devolve um array float32 em 48 kHz, mono (N,) ou estéreo (N, 2), com pico perto de 1.
`tom` multiplica as frequências (1 = original); `semente` muda os detalhes aleatórios.
"""
from __future__ import annotations

import numpy as np
from scipy import signal

SR = 48_000


# ---------------- utilidades ----------------
def _t(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def _fase(freq: np.ndarray) -> np.ndarray:
    """Integra uma frequência que varia no tempo (Hz por amostra) em fase."""
    return 2 * np.pi * np.cumsum(freq) / SR


def _decai(t: np.ndarray, tau: float, ataque: float = 0.002) -> np.ndarray:
    return np.minimum(1, t / max(ataque, 1e-4)) * np.exp(-t / tau)


def _ruido(n: int, rng: np.random.Generator, cor: str = "branco") -> np.ndarray:
    x = rng.standard_normal(n)
    if cor == "branco":
        return x
    espectro = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    f[0] = f[1]
    espectro /= np.sqrt(f) if cor == "rosa" else f  # rosa: 1/f de potência; marrom: 1/f²
    y = np.fft.irfft(espectro, n)
    return y / (np.abs(y).max() + 1e-9)


def _banda(x: np.ndarray, baixo: float, alto: float, ordem: int = 4) -> np.ndarray:
    sos = signal.butter(ordem, [baixo, min(alto, SR / 2 - 100)], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def _passa_baixa(x: np.ndarray, corte: float, ordem: int = 4) -> np.ndarray:
    return signal.sosfilt(signal.butter(ordem, corte, fs=SR, output="sos"), x)


def _banda_movel(x: np.ndarray, centro: np.ndarray, largura_oitavas: float = 0.8) -> np.ndarray:
    """Filtro passa-banda cujo centro (Hz) varia no tempo, via STFT (sem cliques)."""
    nper = 1024
    f, tt, Z = signal.stft(x, SR, nperseg=nper)
    idx = np.clip((tt * SR).astype(int), 0, len(centro) - 1)
    c = centro[idx][None, :]
    oit = np.log2(np.maximum(f[:, None], 1) / c)
    Z *= np.exp(-0.5 * (oit / (largura_oitavas / 2)) ** 2)
    _, y = signal.istft(Z, SR, nperseg=nper)
    y = y[: len(x)]
    return np.pad(y, (0, len(x) - len(y)))


def _normal(x: np.ndarray, pico: float = 0.95) -> np.ndarray:
    m = np.abs(x).max()
    return (x * (pico / m) if m > 0 else x).astype(np.float32)


def _estereo(x: np.ndarray, pan_ini: float, pan_fim: float) -> np.ndarray:
    pan = np.linspace(pan_ini, pan_fim, len(x))
    ang = (pan + 1) * np.pi / 4
    return np.stack([x * np.cos(ang), x * np.sin(ang)], axis=1)


# ---------------- sons ----------------
def bolha(tom: float = 1, semente: int = 0, f0: float | None = None) -> np.ndarray:
    """Uma bolha: senoide que sobe de tom e some rápido (modelo de ressonância de bolha)."""
    rng = np.random.default_rng(semente)
    f0 = (f0 or rng.uniform(500, 1400)) * tom
    t = _t(0.09)
    freq = f0 * (1 + 9 * t)
    x = np.sin(_fase(freq)) * _decai(t, 0.022, 0.001)
    return _normal(x)


def bolhas(tom: float = 1, semente: int = 0, n: int = 9, dur: float = 0.7) -> np.ndarray:
    rng = np.random.default_rng(semente)
    saida = np.zeros(int((dur + 0.1) * SR))
    for i in range(n):
        b = bolha(tom, semente * 100 + i) * rng.uniform(0.35, 1.0)
        ini = int(rng.uniform(0, dur) * SR)
        saida[ini:ini + len(b)] += b
    return _normal(saida, 0.9)


def ventosa(tom: float = 1, semente: int = 0, gruda: bool = False) -> np.ndarray:
    """Som-chave da ventosa. Solta: "plop" que sobe. Gruda: "tchup" que desce, mais molhado."""
    rng = np.random.default_rng(semente)
    t = _t(0.16)
    var = rng.uniform(0.92, 1.08) * tom
    if gruda:
        freq = var * (650 * np.exp(-t / 0.018) + 210)
        corpo = np.sin(_fase(freq)) * _decai(t, 0.03, 0.0015)
        molhado = _passa_baixa(_ruido(len(t), rng), 2600) * _decai(t, 0.022, 0.001) * 0.55
    else:
        freq = var * (260 + 700 * (1 - np.exp(-t / 0.014)))
        corpo = np.sin(_fase(freq)) * _decai(t, 0.028, 0.0012)
        molhado = _banda(_ruido(len(t), rng), 900, 4200) * _decai(t, 0.006, 0.0005) * 0.5
    grave = np.sin(_fase(np.full(len(t), 115 * var))) * _decai(t, 0.022, 0.001) * 0.45
    return _normal(corpo + molhado + grave)


def pop(tom: float = 1, semente: int = 0) -> np.ndarray:
    """Pop curto e brilhante (etiqueta aparecendo)."""
    rng = np.random.default_rng(semente)
    t = _t(0.14)
    freq = tom * (480 + 950 * (1 - np.exp(-t / 0.012)))
    x = np.sin(_fase(freq)) * _decai(t, 0.045, 0.001)
    x += 0.25 * np.sin(2 * _fase(freq)) * _decai(t, 0.025, 0.001)
    x += _banda(_ruido(len(t), rng), 2000, 9000) * _decai(t, 0.002, 0.0003) * 0.35
    return _normal(x)


def pop_grande(tom: float = 1, semente: int = 0) -> np.ndarray:
    """"Boing" curto e redondo (personagem aparecendo / pulando)."""
    t = _t(0.42)
    freq = tom * (170 + 380 * (1 - np.exp(-t / 0.05))) * (1 + 0.025 * np.sin(2 * np.pi * 11 * t))
    x = np.sin(_fase(freq)) * _decai(t, 0.16, 0.004)
    x += 0.35 * np.sin(_fase(freq * 0.5)) * _decai(t, 0.09, 0.004)
    return _normal(x)


_ESCALA = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16]  # maior, a partir de Dó5


def tique(tom: float = 1, semente: int = 0, nota: int = 0) -> np.ndarray:
    """Nota de marimba (contagem sobe na escala: 1, 2, 3...)."""
    rng = np.random.default_rng(semente)
    f = 523.25 * 2 ** (_ESCALA[nota % len(_ESCALA)] / 12) * tom
    t = _t(0.55)
    x = np.sin(2 * np.pi * f * t) * _decai(t, 0.22, 0.001)
    x += 0.35 * np.sin(2 * np.pi * f * 3.93 * t) * _decai(t, 0.045, 0.001)
    x += 0.12 * np.sin(2 * np.pi * f * 9.2 * t) * _decai(t, 0.012, 0.0005)
    x += _banda(_ruido(len(t), rng), 1500, 7000) * _decai(t, 0.0015, 0.0002) * 0.25
    return _normal(x)


def plim(tom: float = 1, semente: int = 0) -> np.ndarray:
    """Duas notas rápidas subindo (etiqueta importante)."""
    a, b = tique(tom, semente, 4), tique(tom, semente + 1, 7)
    saida = np.zeros(int(0.08 * SR) + len(b))
    saida[: len(a)] += a * 0.8
    saida[int(0.08 * SR):] += b
    return _normal(saida)


def whoosh(tom: float = 1, semente: int = 0, dur: float = 0.7, pan_ini: float = 0, pan_fim: float = 0,
           grave: bool = False) -> np.ndarray:
    """Passagem de ar: ruído rosa com banda que sobe e desce; o pan acompanha o movimento."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    k = np.linspace(0, 1, n)
    lo, hi = (140, 900) if grave else (300, 2600)
    centro = tom * lo * (hi / lo) ** np.sin(np.pi * np.clip(k * 1.1, 0, 1)) ** 1.5
    x = _banda_movel(_ruido(n, rng, "rosa"), centro, 1.1)
    env = np.sin(np.pi * np.clip(k, 0, 1)) ** 2 * np.minimum(1, (1 - k) * 8)
    return _estereo(_normal(x * env), pan_ini, pan_fim).astype(np.float32)


def esticar(tom: float = 1, semente: int = 0) -> np.ndarray:
    """"Fuíp" elástico (braço desenrolando)."""
    rng = np.random.default_rng(semente)
    t = _t(0.32)
    k = t / t[-1]
    freq = tom * rng.uniform(0.95, 1.05) * (210 + 520 * k ** 0.7) * (1 + 0.035 * np.sin(2 * np.pi * 19 * t))
    env = np.sin(np.pi * k) ** 1.3
    x = np.sin(_fase(freq)) * env + 0.18 * np.sin(2 * _fase(freq)) * env
    x += _banda_movel(_ruido(len(t), rng), freq * 2.2, 0.6) * env * 0.25
    return _normal(x)


def piscar(tom: float = 1, semente: int = 0) -> np.ndarray:
    """Dois cliques de madeira bem curtos (olhos piscando)."""
    t = _t(0.05)
    um = np.sin(2 * np.pi * 1750 * tom * t) * _decai(t, 0.007, 0.0004)
    um += 0.4 * np.sin(2 * np.pi * 3900 * tom * t) * _decai(t, 0.003, 0.0003)
    saida = np.zeros(int(0.2 * SR))
    saida[: len(um)] += um
    saida[int(0.075 * SR): int(0.075 * SR) + len(um)] += um * 0.85
    return _normal(saida)


def camuflagem(tom: float = 1, semente: int = 0, dur: float = 1.9) -> np.ndarray:
    """Transformação: brilho granulado agudo + "uóm" grave tremendo."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    saida = np.zeros(n)
    for _ in range(46):
        f = rng.uniform(2200, 6800) * tom
        ini = int(rng.uniform(0, dur * 0.85) * SR)
        g = _t(0.18)
        grao = np.sin(2 * np.pi * f * g) * _decai(g, 0.05, 0.002) * rng.uniform(0.2, 0.6)
        fim = min(n, ini + len(g))
        saida[ini:fim] += grao[: fim - ini]
    freq = tom * (380 * np.exp(-k * 1.4) + 120)
    saida += 0.6 * np.sin(_fase(freq)) * (0.6 + 0.4 * np.sin(2 * np.pi * 7.5 * t))
    env = np.minimum(1, k * 6) * np.minimum(1, (1 - k) * 3)
    return _estereo(_normal(saida * env), -0.25, 0.25).astype(np.float32)


def nadar(tom: float = 1, semente: int = 0, dur: float = 0.6, pan_ini: float = 0.6, pan_fim: float = 0) -> np.ndarray:
    """Peixe nadando: chiado de água com a batida da cauda."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    t = np.arange(n) / SR
    k = t / dur
    x = _banda(_ruido(n, rng, "rosa"), 700 * tom, 4500 * tom)
    batida = 0.55 + 0.45 * np.sin(2 * np.pi * 15 * t) ** 2
    env = np.sin(np.pi * k) ** 1.5
    return _estereo(_normal(x * batida * env), pan_ini, pan_fim).astype(np.float32)


def pergunta(tom: float = 1, semente: int = 0) -> np.ndarray:
    """"Hã?" de apito de êmbolo: sobe de tom com vibrato e um pouco de sopro."""
    rng = np.random.default_rng(semente)
    t = _t(0.5)
    k = t / t[-1]
    freq = tom * (480 + 420 * k ** 1.8) * (1 + 0.02 * np.sin(2 * np.pi * 6 * t))
    env = np.minimum(1, t / 0.04) * np.minimum(1, (1 - k) * 5)
    x = np.sin(_fase(freq)) * env
    x += _banda_movel(_ruido(len(t), rng), freq, 0.35) * env * 0.3
    return _normal(x)


def impacto(tom: float = 1, semente: int = 0) -> np.ndarray:
    """Baque macio na areia."""
    rng = np.random.default_rng(semente)
    t = _t(0.35)
    freq = tom * (95 * np.exp(-t / 0.08) + 45)
    x = np.sin(_fase(freq)) * _decai(t, 0.11, 0.002)
    x += _passa_baixa(_ruido(len(t), rng), 900) * _decai(t, 0.03, 0.001) * 0.6
    return _normal(x)


def ambiente(tom: float = 1, semente: int = 0, dur: float = 20.0) -> np.ndarray:
    """Fundo do mar: grave abafado que respira devagar + bolhas distantes. Não é música."""
    rng = np.random.default_rng(semente)
    n = int(dur * SR)
    t = np.arange(n) / SR
    canais = []
    for c in range(2):
        # faixa 110–600 Hz: é o que alto-falante de celular reproduz (abaixo disso some no telefone)
        r = _banda(_ruido(n, rng, "rosa"), 110 * tom, 600 * tom, 2)
        r += 0.5 * _banda(_ruido(n, rng, "marrom"), 50, 140, 2)
        r *= 0.75 + 0.25 * np.sin(2 * np.pi * (0.09 + 0.02 * c) * t + c)
        canais.append(r)
    x = np.stack(canais, axis=1)
    x /= np.abs(x).max()
    for i in range(int(dur * 1.2)):
        b = bolha(0.8 * tom, semente * 1000 + i) * rng.uniform(0.05, 0.14)
        ini = int(rng.uniform(0, max(0.1, dur - 0.2)) * SR)
        lado = rng.uniform(-1, 1)
        fim = min(n, ini + len(b))
        x[ini:fim, 0] += b[: fim - ini] * (1 - lado) / 2
        x[ini:fim, 1] += b[: fim - ini] * (1 + lado) / 2
    borda = int(0.5 * SR)
    rampa = np.linspace(0, 1, borda)
    x[:borda] *= rampa[:, None]
    x[-borda:] *= rampa[::-1, None]
    return (x / np.abs(x).max() * 0.95).astype(np.float32)


CATALOGO = {
    "bolha": bolha, "bolhas": bolhas, "ventosa": ventosa, "pop": pop, "pop_grande": pop_grande, "tique": tique,
    "plim": plim, "whoosh": whoosh, "esticar": esticar, "piscar": piscar, "camuflagem": camuflagem, "nadar": nadar,
    "pergunta": pergunta, "impacto": impacto, "ambiente": ambiente,
}

# Volume padrão de cada som na mixagem (dB); o evento pode somar um ajuste.
GANHO_DB = {
    "ambiente": -27, "whoosh": -12, "bolha": -14, "bolhas": -12, "ventosa": -7, "pop": -11, "pop_grande": -8,
    "tique": -10, "plim": -10, "esticar": -15, "piscar": -11, "camuflagem": -11, "nadar": -13, "pergunta": -9,
    "impacto": -8,
}


def gerar(nome: str, **params) -> np.ndarray:
    if nome not in CATALOGO:
        raise ValueError(f"som desconhecido: {nome}")
    x = CATALOGO[nome](**params).copy()
    # rampa final de 15 ms: som que termina "cortado" vira clique audível
    borda = min(len(x), int(0.015 * SR))
    rampa = np.linspace(1, 0, borda)
    x[-borda:] *= rampa[:, None] if x.ndim == 2 else rampa
    return x
