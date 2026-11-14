"""Narração PROVISÓRIA com a voz do Windows ("Microsoft Maria Desktop", pt-BR, System.Speech), só para testar a
mixagem voz × efeitos antes de termos o Chirp 3 HD. Robótica de propósito: não é candidata a voz do canal.

sintetizar(segmentos, duracao) → array mono float32 em 48 kHz com cada trecho começando no seu `ini`.
Se um trecho não cabe na janela [ini, fim], ele é refeito mais rápido (Rate do System.Speech, até +4).
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from scipy.io import wavfile

SR = 48_000
VOZ = "Microsoft Maria Desktop"

_PS = r"""
Add-Type -AssemblyName System.Speech
$itens = Get-Content -Raw -Encoding UTF8 $args[0] | ConvertFrom-Json
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
$s.SelectVoice('%s')
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo(48000, [System.Speech.AudioFormat.AudioBitsPerSample]::Sixteen, [System.Speech.AudioFormat.AudioChannel]::Mono)
foreach ($i in $itens) {
  $s.Rate = [int]$i.rate
  $s.SetOutputToWaveFile($i.wav, $fmt)
  $s.Speak([string]$i.texto)
}
$s.SetOutputToNull()
""" % VOZ


def _falar(itens: list[dict], pasta: Path) -> list[np.ndarray]:
    lista = pasta / "itens.json"
    lista.write_text(json.dumps(itens, ensure_ascii=False), encoding="utf-8")
    script = pasta / "falar.ps1"
    script.write_text(_PS, encoding="utf-8-sig")
    subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), str(lista)],
                   check=True, capture_output=True)
    saida = []
    for i in itens:
        _, x = wavfile.read(i["wav"])
        x = x.astype(np.float32) / 32768
        nz = np.flatnonzero(np.abs(x) > 0.01)  # apara silêncio das pontas
        saida.append(x[nz[0]: nz[-1] + 1] if len(nz) else x)
    return saida


def sintetizar(segmentos: list[dict], duracao: float) -> tuple[np.ndarray, list[dict]]:
    with tempfile.TemporaryDirectory() as tmp:
        pasta = Path(tmp)
        rates = [1] * len(segmentos)
        for _ in range(4):
            itens = [{"texto": s["texto"], "rate": r, "wav": str(pasta / f"seg{k}.wav")}
                     for k, (s, r) in enumerate(zip(segmentos, rates))]
            falas = _falar(itens, pasta)
            longos = [k for k, (s, f) in enumerate(zip(segmentos, falas))
                      if len(f) / SR > (s["fim"] - s["ini"]) and rates[k] < 4]
            if not longos:
                break
            for k in longos:
                rates[k] += 1
    voz = np.zeros(int(duracao * SR) + SR, dtype=np.float32)
    relatorio = []
    for s, f, r in zip(segmentos, falas, rates):
        ini = int(s["ini"] * SR)
        fim = min(len(voz), ini + len(f))
        voz[ini:fim] += f[: fim - ini]
        relatorio.append({"texto": s["texto"], "ini": s["ini"], "dur_fala": round(len(f) / SR, 2),
                          "janela": round(s["fim"] - s["ini"], 2), "rate": r})
    return voz[: int(duracao * SR)], relatorio
