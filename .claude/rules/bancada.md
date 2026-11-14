---
paths:
  - "bancada/**"
---

# Regras para a bancada (Fase 0)

- Python 3 num ambiente virtual em `bancada/.venv` (fora do Git); dependências com versão fixada em
  `bancada/requirements.txt`.
- Segredos só do `.env` da raiz, lidos pelo script (python-dotenv); nunca imprimir, registrar em log nem gravar em
  arquivo. O Claude não abre o `.env`.
- Workers AI: o plano Free corta sozinho em 10.000 neurons/dia (erro 3036). No primeiro 3036 o script para e não tenta
  de novo; nunca há retry automático para esse erro. Google TTS: no máximo 12 mil caracteres por rodada.
- Saídas (imagens, áudio, vídeo) em `bancada/saida/` (fora do Git); resultados tabulados em `bancada/resultados.csv`
  (no Git).
- Cada chamada registra: data e hora UTC, configuração, parâmetros, seed, tempo, consumo, erro e arquivo gerado. O
  resumo de cada rodada vai para `docs/08` (Medições).
- Cada arquivo gerado tem um `.json` ao lado com a proveniência: modelo, data, prompt, seed e link dos termos.
- Avaliação às cegas: o script embaralha e renomeia os arquivos antes de o Gabriel dar nota; a chave de
  correspondência fica num arquivo separado, que só é aberto depois das notas.
- Nada vai para o Gabriel sem ter rodado de verdade pelo menos uma vez.
- Vídeo: antes de mandar, extrair uma folha de quadros (início, meio, fim de cada plano e transições) e conferir
  recorte, legenda e artefatos. Defeito conhecido não vai para avaliação.
- Formato visual novo: antes de montar o teste, analisar as referências do Gabriel quadro a quadro (duração, cortes,
  folha de quadros) e registrar em `docs/08`.
- Cenas 3D (T6): tudo em função do tempo `t` (nada de relógio nem `Math.random` sem semente); conferir uma folha de
  quadros (`--quadros`) antes de renderizar o vídeo inteiro.
