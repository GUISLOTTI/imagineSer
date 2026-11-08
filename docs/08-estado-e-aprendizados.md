# Estado e aprendizados

Atualizado ao fim de cada tarefa. Três partes: estado das contas, medições (números reais, com método) e lições.
Quando passar de ~200 linhas, mover medições e lições antigas para `docs/arquivo/`.

## Estado das contas — 07/11/2026

| Item | Estado | Próxima ação |
| --- | --- | --- |
| Claude | Créditos de uso extra desligados ✔ | — |
| GitHub | Repositório privado `GUISLOTTI/imagineSer` ✔ | Confirmar que não há forma de pagamento; ajustes de Actions na Fase 1 |
| Cloudflare | Plano **Free** confirmado pelo Gabriel (07/11; o painel avisa quando os 10 mil do dia acabam) ✔; token com Workers AI + Account Analytics: Read ✔ | — |
| Buffer | Instagram e TikTok conectados ✔ | Confirmar tipo de conta e modo de publicação (Fase 3, pela API) |
| YouTube | Conta criada; canal ainda sem @ | Conectar ao Buffer quando o @ liberar (previsto para 08/11) |
| Google Cloud | Pendente | Na vez das vozes (exige cartão) |
| TikTok | Manter como **conta pessoal**: o Creator Rewards exige "personal account" (ADR-0012) | — |
| Instagram | Deve ser conta profissional (Criador) para publicar sem notificação | Confirmar na Fase 3 |

## Agenda sugerida pelo Buffer

Gerada pelo Buffer com a meta de 7 posts/semana. Ponto de partida, não decisão (ADR-0015). Em 3/semana, o publicador
usa os horários de terça, quinta e sábado de cada rede. Fuso da conta do Buffer: conferir pela API na Fase 3.
YouTube: sem horários até o canal ser conectado.

| Dia | Instagram | TikTok |
| --- | --- | --- |
| Segunda | 20:00–21:00 | 09:00–10:00 |
| Terça | 19:00–20:00 | 07:00–08:00 |
| Quarta | 18:00–19:00 | 06:00–07:00 |
| Quinta | 10:00–11:00 | 22:00–23:00 |
| Sexta | 07:00–08:00 | 22:00–23:00 |
| Sábado | 22:00–23:00 | 08:00–09:00 |
| Domingo | 22:00–23:00 | 09:00–10:00 |

## Medições

Formato: data · o que · método · resultado · arquivo de dados. Dados brutos da bancada: `bancada/resultados.csv`
(por imagem) e `bancada/lotes.csv` (por lote). O modo `--simular` não gera medição.

### 07/11/2026, sábado, 23:01–23:21 (Brasília) — T1, consumo real por imagem

Método: lotes de 10 imagens por configuração, isolados no tempo; consumo lido pela API de analytics
(`aiInferenceAdaptiveGroups`, `sum.totalNeurons`, separado por modelo). 61 imagens, 0 erros.

| Config | Neurons/imagem | Imagens/dia (10.000) | s/imagem | Recebido | Bate com a tabela de preços |
| --- | --- | --- | --- | --- | --- |
| A — schnell, 4 passos | 172,8 | 57 | 2,3 | 1024×1024 | 4 *tiles* × (4,80 + 4 × 9,60) |
| B — schnell, 8 passos | 326,4 | 30 | 2,1 | 1024×1024 | 4 *tiles* × (4,80 + 8 × 9,60) |
| C — klein, 768×1344 | 104,2 | 95 | 9,6 | 768×1344 | 4 *tiles* × 26,05 |
| D — klein + 1 referência | 107,1 | 93 | 4,9 | 768×1344 | C + 0,54 *tile* de entrada × 5,37 |
| E — klein + 3 referências | 112,8 | 88 | 5,3 | 768×1344 | C + 3 × 0,54 × 5,37 |
| F — klein, pedido 1080×1920 | 206,1 | 48 | 9,6 | **1072×1920** | 7,91 *tiles* (área pedida) × 26,05 |

Conclusões medidas:
- O analytics coincide com a fórmula oficial de preço até a casa decimal: as duas fontes concordam, então o T1 passa
  sem o método do limite (que se mostrou impreciso, ver abaixo).
- O schnell cobra os passos **por *tile***: o pior caso das estimativas do plano.
- O klein cobra a saída pela área pedida (fracionada), com mínimo aparente de 4 *tiles* (C: 3,94 → 4), e as
  referências pela área fracionada de entrada. Ele arredonda a largura para múltiplo de 16 (1080 → 1072).
- **O corte da franquia não é exato:** o dia fechou em 10.570,6 neurons sem nenhum erro 3036. O nosso contador
  (8.000/dia na produção) é o teto real; o 3036 é só a rede de segurança.
- Custo por episódio, supondo ~30 imagens (cenas, ficha do personagem, fundos e regerações): C ≈ 3.100 neurons
  (0,3 dia de franquia); F ≈ 6.200 (0,6); A ≈ 5.200 (0,5); B ≈ 9.800 (1,0). Qualidade ainda não avaliada (T2).
- Observação qualitativa (1 amostra, sem decisão): o D manteve o mesmo personagem da referência e trocou só o
  cenário, mas copiou também a pose. O T3 mede isso.

### 07/11/2026, sábado, noite (Brasília) — T4 v1 (movimento), sem gastar franquia

Método: `bancada/t4_movimento.py`, 5 planos de 4 s com as imagens do T1 (C-01 e D-01/04/07/10), recorte com rembg
(`isnet-general-use`), paralaxe em 2 camadas, respiração, pulso, foco, bolhas, vinheta, legenda palavra a palavra
(Lilita One, OFL) e pan rápido. Render neste PC: **155 s para 20 s em 1080×1920 a 30 fps** (23 s de preparo).
Episódio de 60–75 s ≈ 8–10 min neste PC; falta medir no runner do GitHub (critério: < 10 min para o clipe de 20 s).

Resultado: o pipeline funciona, mas **não vai para avaliação**:
- Preencher o buraco do personagem com desfoque gera mancha visível em fundo detalhado (recife), e aumentar a máscara
  só alarga a mancha. Próxima versão: cenário gerado sem o personagem + recorte por cima (método c do T3).
- As 4 imagens D vistas têm **a mesma pose** da referência: a troca de pose depende do T3.
- Legenda a 62% da altura cobria o personagem; a 72% fica legível e livre do rosto.

## Lições

| Data | Lição | Origem | Virou regra em |
| --- | --- | --- | --- |
| 07/11/2026 | No Windows, o Git converte LF em CRLF e quebra scripts bash; `*.sh` fica fixo em LF | Primeiro commit | `.gitattributes` |
| 07/11/2026 | Neste PC o Claude Code tem Bash e PowerShell; hooks e bloqueios precisam cobrir os dois | Teste do hook | `.claude/settings.json` |
| 07/11/2026 | Guias de terceiros sobre monetização divergem entre si; só decidir com página oficial ou medição | Pesquisa de monetização | ADR-0015 |
| 07/11/2026 | Exemplo de código da doc pode contradizer o esquema (o curl do schnell manda `seed`, que o esquema proíbe); vale o `schema-input.json` | Scripts da bancada | `docs/05` |
| 07/11/2026 | No Windows, stdout e stderr do Python não são UTF-8 por padrão; scripts reconfiguram os dois | Teste do `bancada.py` | `bancada/bancada.py` |
| 07/11/2026 | A trava de intervalo entre lotes pulou o lote A logo após o `testar`; o loop seguiu sem avisar no fim | T1 | Rodar o pulado no final; checar `lotes.csv` ao fim de cada rodada |
| 07/11/2026 | A franquia gratuita não corta exatamente em 10.000 (passou para 10.570 sem 3036); não usar o 3036 como medida | T1 | `docs/05` (T1) |
| 07/11/2026 | Paralaxe não funciona "inventando" o fundo atrás do personagem; precisa de cenário gerado sem ele | T4 v1 | `docs/05` (T3c e T4) |
| 07/11/2026 | Conferir uma folha de quadros antes de mandar vídeo ao Gabriel pegou dois defeitos; vira passo fixo | T4 v1 | `.claude/rules/bancada.md` |
| 07/11/2026 | Falei "hoje às 21:05" pensando em UTC; para o Gabriel era sábado 23:54 e o certo era "domingo às 21:05". Horário sempre em Brasília, com dia da semana, conferido com `date` | Conversa | `CLAUDE.md` (Horários) |
