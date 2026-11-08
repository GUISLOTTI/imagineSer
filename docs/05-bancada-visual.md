# Bancada visual (Fase 0) — protocolo

Objetivo: decidir, com dados, o modelo e a técnica de imagem do MVP. Custo: US$ 0 (Cloudflare Workers AI no plano
Workers Free). Duração estimada: 5 dias úteis. Resultado: ADR-0005 passa de "Proposta" para "Aceita".

## Antes de começar

- Conta Cloudflare no plano **Workers Free** (nunca assinar Workers Paid).
- Token de API da Cloudflare só com permissão de Workers AI, guardado fora do Git (variável de ambiente local).
- Scripts em `bancada/`; saídas em `bancada/saida/` (ignorada pelo Git); resultados em `bancada/resultados.csv`.

## Por que medir

A documentação do FLUX.1 schnell informa US$ 0,0000528 por *tile* de 512×512 (4,80 neurons) e US$ 0,0001056 por
passo (9,60 neurons), passos de 4 (padrão) a 8, mas **não documenta largura, altura nem resolução de saída**, nem se o
passo é cobrado por imagem ou por *tile*. Faixa estimada: 57,6 a 326,4 neurons por imagem (30 a 173 imagens/dia).
O FLUX.2 klein 4B custa 26,05 neurons por *tile* de saída e aceita imagens de referência; pode exigir Workers Paid
(erro 5035) — o teste confirma.

**Confirmado na documentação oficial em 07/11/2026** (esquemas `schema-input.json` dos modelos, changelog do klein de
15/01/2026, páginas de preços e de erros):

- **schnell:** aceita só `prompt` e `steps` (máx. 8); o esquema proíbe outros campos. **Sem seed e sem tamanho.**
- **klein 4B:** formulário multipart com `prompt`, `width` e `height` (256–1920; padrão 1024×768), `seed`, `guidance` e
  até 4 imagens `input_image_0..3`, cada uma menor que 512×512. Passos fixos em 4. Entrada: 5,37 neurons por *tile*.
- **Erros:** 3036 (HTTP 429) = franquia do dia esgotada; 5035 (HTTP 403) = exige Workers Paid; 3040 (HTTP 429) =
  falta de capacidade momentânea (pode repetir).
- **Consumo por API (hipótese, não documentada):** dataset GraphQL `aiInferenceAdaptiveGroups`, campo
  `sum.totalNeurons`, com a permissão "Account Analytics: Read" no token. Se funcionar, substitui a leitura manual do
  painel no T1; o comando `testar` confirma.

## Configurações

| Id | Modelo | Parâmetros |
| --- | --- | --- |
| A | FLUX.1 schnell | 4 passos |
| B | FLUX.1 schnell | 8 passos |
| C | FLUX.2 klein 4B | só texto, 768×1344 |
| D | FLUX.2 klein 4B | 1 imagem de referência, 768×1344 |
| E | FLUX.2 klein 4B | 3 imagens de referência, 768×1344 |
| F | FLUX.2 klein 4B | só texto, vertical nativo 1080×1920 (para o T5) |

Definição exata em `bancada/configs.json`; prompts em `bancada/prompts.json`; prefixo de estilo em `config/estilo.json`.

## Testes

### T1 — Consumo real
1. Para cada configuração, um lote de 10 imagens (`t1 --config X`), com pelo menos 2 min entre lotes, para a janela
   de consumo não misturar configurações. Depois de ~10 min, `neurons` mede o consumo do lote pela API de analytics.
2. Em outro dia, para as 2 configurações finalistas, `t1-limite`: gerar até o erro 3036, logo depois das 00:00 UTC
   (21:00 em Brasília): neurons/imagem ≈ (10.000 − uso anterior do dia) ÷ imagens geradas. Trava: sem 3036 até ~1,3×
   a franquia estimada, o script para e alerta (a conta poderia não estar no Workers Free).
3. Por imagem, `bancada/resultados.csv`: config, modelo, passos, tamanho pedido e recebido, referências, seed, tempo,
   tentativas, erro. Por lote, `bancada/lotes.csv`: janela, imagens, neurons pelo analytics e pelo limite.
- **Passa:** os dois métodos diferem no máximo 10%.

### T2 — Qualidade
- Temas: polvo, fígado, Saturno, tartaruga. 3 prompts por tema, mesmo prefixo de estilo (`config/estilo.json`).
- Configurações só de texto: A, B, C e F (D e E dependem de referência e entram no T3). `t2` retoma de onde parou se
  a franquia do dia acabar; `embaralhar` prepara as cópias às cegas.
- Avaliação às cegas (arquivos renomeados aleatoriamente), nota 1–5 em: estilo 3D estilizado, anatomia ou
  correção técnica, nitidez no celular, ausência de artefatos.
- **Passa:** média ≥ 3,5 e nenhuma imagem escolhida com anatomia ≤ 2.

### T3 — Consistência de personagem
- Uma imagem canônica do polvo e 6 cenas diferentes, por três métodos:
  (a) descrição fixa + mesma seed (só no klein: o schnell não aceita seed); (b) imagem de referência (D/E);
  (c) personagem recortado (rembg) e reaproveitado como camada sobre fundos gerados sem ele.
- **Passa:** o Gabriel reconhece o mesmo personagem em ≥ 5 de 6 cenas.

### T4 — Movimento
- Clipe de 20 s com 5 imagens usando: movimento de câmera com *easing*, paralaxe em 2–3 camadas, "respiração"
  (escala 1–2% em onda), troca de pose por corte, partículas por script, legenda palavra a palavra.
- Renderizar num runner do GitHub (ubuntu-latest) e medir o tempo.
- **Passa:** "parece animação 3D estilizada leve" em ≥ 4 de 5 planos, avaliado no celular; render < 10 min.

### T5 — Formato vertical
- Comparar recorte do quadrado + ampliação local vs. saída vertical nativa (se o klein aceitar tamanho).
- **Passa:** sem perda de nitidez perceptível no celular a 1080×1920.

## Como rodar

Na raiz, com o ambiente virtual (`python -m venv bancada/.venv` e `pip install -r bancada/requirements.txt`):
`bancada/.venv/Scripts/python bancada/bancada.py <comando>`. Ordem: `testar` → `t1` para cada configuração (C antes
de D e E, que usam imagens do C como referência) → `neurons` → `t2` → `embaralhar` → `resumo` (tabela para o
`docs/08`). `--simular` roda tudo sem chamar a API. T3–T5 ganham scripts depois dos resultados do T1 e do T2.

## Regra de decisão

Escolher a configuração **mais barata** que passe em T2, T3 e T4. Se nenhuma passar em T3, adotar o método (c):
consistência por construção, com o personagem gerado uma vez e reaproveitado. Registrar o resultado em
`docs/03-decisoes.md` (ADR-0005) com o número medido de neurons por episódio e a margem diária.

## Licenças a registrar

FLUX.1 schnell e FLUX.2 klein 4B: confirmar nos termos ligados nas páginas dos modelos da Cloudflare e da Black
Forest Labs. rembg e o modelo de recorte usado: confirmar licença antes de adotar. Fonte das legendas: licença OFL.
