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

## Configurações

| Id | Modelo | Parâmetros |
| --- | --- | --- |
| A | FLUX.1 schnell | 4 passos |
| B | FLUX.1 schnell | 8 passos |
| C | FLUX.2 klein 4B | só texto, 768×1344 (se aceitar tamanho) |
| D | FLUX.2 klein 4B | 1 imagem de referência |
| E | FLUX.2 klein 4B | 3 imagens de referência |

## Testes

### T1 — Consumo real
1. Para cada configuração, gerar 10 imagens numa hora fixa do dia e anotar o consumo por modelo no painel do
   Workers AI. Uma configuração por janela de horário, para não misturar.
2. Em outro dia, para as 2 configurações finalistas, gerar até receber o erro 3036 e contar:
   neurons/imagem ≈ 10.000 ÷ imagens geradas (descontando o que o painel mostrar de outros usos).
3. Gravar em `resultados.csv`: `config, modelo, passos, tamanho_pedido, tamanho_recebido (ffprobe), referencias,
   neurons_imagem_painel, neurons_imagem_limite, segundos_imagem, erro`.
- **Passa:** os dois métodos diferem no máximo 10%.

### T2 — Qualidade
- Temas: polvo, fígado, Saturno, tartaruga. 3 prompts por tema, mesmo prefixo de estilo (`config/estilo.json`).
- Avaliação às cegas (arquivos renomeados aleatoriamente), nota 1–5 em: estilo 3D estilizado, anatomia ou
  correção técnica, nitidez no celular, ausência de artefatos.
- **Passa:** média ≥ 3,5 e nenhuma imagem escolhida com anatomia ≤ 2.

### T3 — Consistência de personagem
- Uma imagem canônica do polvo e 6 cenas diferentes, por três métodos:
  (a) descrição fixa + mesma seed; (b) imagem de referência (D/E); (c) personagem recortado (rembg) e reaproveitado
  como camada sobre fundos gerados sem ele.
- **Passa:** o Gabriel reconhece o mesmo personagem em ≥ 5 de 6 cenas.

### T4 — Movimento
- Clipe de 20 s com 5 imagens usando: movimento de câmera com *easing*, paralaxe em 2–3 camadas, "respiração"
  (escala 1–2% em onda), troca de pose por corte, partículas por script, legenda palavra a palavra.
- Renderizar num runner do GitHub (ubuntu-latest) e medir o tempo.
- **Passa:** "parece animação 3D estilizada leve" em ≥ 4 de 5 planos, avaliado no celular; render < 10 min.

### T5 — Formato vertical
- Comparar recorte do quadrado + ampliação local vs. saída vertical nativa (se o klein aceitar tamanho).
- **Passa:** sem perda de nitidez perceptível no celular a 1080×1920.

## Regra de decisão

Escolher a configuração **mais barata** que passe em T2, T3 e T4. Se nenhuma passar em T3, adotar o método (c):
consistência por construção, com o personagem gerado uma vez e reaproveitado. Registrar o resultado em
`docs/03-decisoes.md` (ADR-0005) com o número medido de neurons por episódio e a margem diária.

## Licenças a registrar

FLUX.1 schnell e FLUX.2 klein 4B: confirmar nos termos ligados nas páginas dos modelos da Cloudflare e da Black
Forest Labs. rembg e o modelo de recorte usado: confirmar licença antes de adotar. Fonte das legendas: licença OFL.
