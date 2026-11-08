# Plano MVP v2 — Imagine Ser (US$ 20/mês)

Nov 4, 2026 · @Gabriel Guislotti

> **Atualização de 07/11/2026:** os ADRs 0010–0014 (`docs/03-decisoes.md`) prevalecem sobre este plano onde
> divergirem. Seções afetadas: §3 (duração padrão acima de 1 min), §4 (cota dimensionada; corte de faturamento na
> Fase 2), §6.1 item 6 (`reconciliar` também lê o Buffer), §7 (sem anotações manuais), §9 (aprovação por estoque,
> sem prazos; sem PR de pauta; sem cron no `produzir`), §10 (6 workflows; Python auxiliar; rascunhos das skills já
> na Fase 0), §11 (pendências resolvidas).

## Resumo da v2

**O MVP roda inteiro com US$ 0 além do Claude Pro.** O Pro é o motor de pesquisa e roteiro (via GitHub Action). Todo o resto usa franquias gratuitas com teto rígido ou corte automático. A publicação nas três redes passa pelo Buffer Free, que envia o sinal de conteúdo gerado por IA para YouTube, Instagram e TikTok. O contexto vai para o terminal como arquivos versionados no repositório.

**Decisões travadas nesta versão:**

| Tema | Decisão | Muda em relação à v1? |
| --- | --- | --- |
| Orçamento | Teto de US$ 20/mês = Claude Pro já pago. Nenhuma API paga (Claude, Gemini, geração de vídeo) no MVP | Sim: cenários pagos viram referência futura |
| Franquias gratuitas | Permitidas só com limite rígido: corte por plano, cota ou contador próprio | Novo |
| Imagem | Cloudflare Workers AI, plano Workers Free; modelo escolhido na bancada de testes (FLUX.1 schnell ou FLUX.2 klein 4B) | Sim: sem número fixo de imagens/dia |
| Voz | Google Chirp 3 HD pt-BR, projeto isolado com contador e corte de faturamento | Detalhado |
| Publicação | Buffer Free (3 canais) para YouTube, Instagram e TikTok, com `isAiGenerated` nos três | Sim: Buffer também para YouTube e Instagram no MVP |
| Plataformas | YouTube, Instagram e TikTok, perfil @imagineser.oficial. Bilibili fora do escopo | Sim |
| Duração | Padrão de 30–90 s (alvo 45–70 s); teto de 120 s | Sim |
| Cadência | 3 por semana até os critérios da seção de validação passarem | Detalhado |
| Contexto para o terminal | `CLAUDE.md` curto + `docs/` + ADRs + skills, entregues como kit | Novo |

A aba "Análise v1" continua válida para a arquitetura-alvo (servidor próprio, cenários pagos). Onde divergir, vale esta aba.

## 1. Transplante para o Claude Code no terminal

**O "cérebro" vai como arquivos dentro do repositório: um `CLAUDE.md` curto, que o Claude Code carrega sozinho em toda sessão, mais documentos em `docs/` lidos sob demanda.** É o único formato que sobrevive entre sessões, fica versionado no Git e é lido também pelos workflows do GitHub Actions. Esta conversa não fica acessível ao terminal.

| Opção | Como funciona | Problema | Veredito |
| --- | --- | --- | --- |
| Colar um resumo no novo chat | Texto na primeira mensagem | Some quando a sessão acaba; perde detalhes e fontes | Não |
| Contar com a memória do claude.ai | Notas automáticas da conta | Não há garantia de que o Claude Code no terminal as leia; não é versionado nem revisável | Não depender |
| Exportar este documento inteiro para o `CLAUDE.md` | Tudo carregado sempre | A documentação recomenda menos de 200 linhas por `CLAUDE.md`; arquivo longo gasta contexto e reduz a aderência às regras ([memória do Claude Code](https://code.claude.com/docs/en/memory)) | Não |
| **`CLAUDE.md` curto + `docs/` + regras por pasta + skills + hooks** | O `CLAUDE.md` tem só o que vale sempre e aponta para os docs; `.claude/rules/` carrega regras só ao mexer em certas pastas; skills guardam procedimentos | Precisa ser mantido atualizado (regra no próprio `CLAUDE.md`) | **Recomendado** |

**Por que também hooks:** o `CLAUDE.md` é contexto, não trava. A documentação indica um hook `PreToolUse` para bloquear uma ação de forma garantida. Use-o para três regras inegociáveis: não ler `.env` e segredos, não editar `.github/workflows/` sem você pedir, não rodar o comando `publicar` localmente.

**Conteúdo do kit** (entregue em .zip junto com esta revisão):

```text
CLAUDE.md                       ← regras permanentes + mapa dos docs (< 150 linhas)
PRIMEIRA-SESSAO.md              ← prompt para colar na 1ª sessão do terminal
.gitignore
.claude/settings.json           ← permissões (deny para segredos) e hook
.claude/hooks/bloquear.sh       ← o hook PreToolUse
.claude/rules/dotnet.md         ← carrega ao mexer em src/ e tests/
.claude/rules/workflows.md      ← carrega ao mexer em .github/
.claude/rules/episodios.md      ← carrega ao mexer em episodes/
docs/00-briefing-original.md
docs/01-plano-mvp-v2.md         ← esta aba exportada
docs/02-analise-v1-referencia.md
docs/03-decisoes.md             ← registro de decisões (ADRs)
docs/04-guia-editorial.md
docs/05-bancada-visual.md       ← protocolo do teste de imagem
docs/06-seguranca.md
docs/07-fontes.md
```

**Como fazer o transplante:**

1. Crie um repositório privado no GitHub (sugestão: `imaginaser-fabrica`) e clone no seu PC.
2. Descompacte o kit na raiz e faça o primeiro commit (`chore: contexto inicial`).
3. Abra o terminal na raiz e rode `claude`. Confirme com `/context` que o `CLAUDE.md` aparece em *Memory files*.
4. Cole o conteúdo de `PRIMEIRA-SESSAO.md`. Ele pede ao Claude que leia os docs, devolva um resumo com dúvidas e proponha o plano da Fase 0, **sem escrever código**.
5. Daqui em diante: decisão nova vira um ADR em `docs/03-decisoes.md`; regra permanente vira uma linha no `CLAUDE.md`. Este documento no claude.ai fica como histórico.

## 2. Geração visual: neurons revisados e bancada de testes

**A conta da v1 ("\~58 neurons, \~170 imagens/dia") assumia duas coisas que a documentação não confirma: a resolução de saída e como o passo é cobrado.** Refeita com o que está documentado, a faixa vai de cerca de 30 a 170 imagens por dia — uma incerteza de 6 vezes. Por isso o número real tem de ser medido.

**O que a documentação diz (consultado em 04/11/2026):**

- **Preço do FLUX.1 schnell:** US$ 0,0000528 por *tile* de 512×512 + US$ 0,0001056 por passo. Na taxa de US$ 0,011 por 1.000 neurons, isso dá 4,80 neurons por *tile* e 9,60 por passo ([preços](https://developers.cloudflare.com/workers-ai/platform/pricing/)).
- **Parâmetros do schnell:** `prompt` e `steps` (padrão 4, máximo 8). A página do modelo **não tem largura nem altura** e não informa a resolução de saída ([modelo](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/)). Na prática, imagem quadrada: um vídeo 9:16 exige recorte e ampliação.
- **FLUX.2 klein 4B:** 26,05 neurons por *tile* de saída. Licença Apache 2.0, a única do FLUX.2 com uso comercial livre ([Vercel](https://vercel.com/ai-gateway/models/flux-2-klein-4b.md)). Aceita imagens de referência, mas a página da Cloudflare não detalha os parâmetros.
- **FLUX.2 dev e klein 9B:** licença não comercial ([VentureBeat](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in)). **Fora do projeto.**
- **Limite rígido:** no plano Workers Free, ao passar de 10.000 neurons/dia a chamada falha com erro 3036 (HTTP 429) e não há cobrança. A cobrança de US$ 0,011 por 1.000 neurons só existe no Workers Paid. O limite renova às 00:00 UTC ([erros](https://developers.cloudflare.com/workers-ai/platform/errors)). Alguns modelos exigem Workers Paid (erro 5035) — a bancada confirma se o klein é um deles.

**Faixa de consumo do schnell (supondo saída de 1024×1024 = 4 *tiles*):**

| Como o passo é cobrado | 4 passos | 8 passos |
| --- | --- | --- |
| Por imagem: 4 × 4,80 + passos × 9,60 | 57,6 neurons → \~173 imagens/dia | 96,0 neurons → \~104 imagens/dia |
| Por *tile*: 4 × (4,80 + passos × 9,60) | 172,8 neurons → \~57 imagens/dia | 326,4 neurons → \~30 imagens/dia |

**Consequência de projeto:** orçar por episódio, não por dia. Um job diário de fila gera imagens até 8.000 neurons/dia (20% de margem) e continua no dia seguinte se faltar. Com 3 episódios por semana, cada um tem pelo menos 2 dias de franquia: até \~16.000 neurons.

**Bancada de testes (Fase 0, cerca de 5 dias, custo US$ 0):**

| Teste | Como | Métrica | Critério para passar |
| --- | --- | --- | --- |
| T1 — Consumo real | Para cada configuração, gerar 10 imagens numa hora fixa e ler o consumo por modelo no painel do Workers AI. Confirmar num segundo dia rodando até o erro 3036: neurons por imagem = 10.000 ÷ imagens geradas | Neurons/imagem, segundos/imagem, resolução recebida (ffprobe), erros | Número medido, com no máximo 10% de diferença entre os dois métodos |
| T2 — Qualidade | 4 temas (polvo, fígado, Saturno, tartaruga) × 3 prompts × cada configuração; nomes embaralhados para você avaliar às cegas | Nota de 1 a 5 em estilo 3D estilizado, anatomia, nitidez no celular e artefatos | Média ≥ 3,5 e nenhuma imagem escolhida com anatomia ≤ 2 |
| T3 — Consistência | Uma imagem canônica do polvo e 6 cenas: (a) descrição fixa + mesma seed; (b) imagem de referência (klein); (c) recorte do personagem reaproveitado sobre fundos diferentes | Em quantas cenas você reconhece o mesmo personagem | ≥ 5 de 6 |
| T4 — Movimento | Clipe de 20 s com 5 imagens usando as técnicas da seção 3, renderizado num runner do GitHub | Tempo de render; avaliação no celular: "parece animação 3D estilizada leve?" | Sim em ≥ 4 de 5 planos; render < 10 min |
| T5 — Formato vertical | Recorte do quadrado + ampliação local vs. saída vertical nativa (se o klein aceitar tamanho) | Nitidez a 1080×1920; tempo | Sem perda perceptível no celular |

Configurações testadas: A) schnell 4 passos; B) schnell 8 passos; C) klein 4B só texto; D) klein 4B com 1 referência; E) klein 4B com 3 referências. **Regra de decisão:** a configuração mais barata que passe em T2, T3 e T4. Se nenhuma passar em T3, a consistência vem por construção: o personagem é gerado uma vez, recortado e reaproveitado como camada (opção c). O resultado vira um ADR.

## 3. Produção: duração e técnica visual

**Recomendo alvo de 45–70 s, dentro da faixa padrão de 30–90 s, com teto rígido de 120 s validado por código.** É o bastante para uma mini-narrativa em três atos e mantém o episódio em 8–10 imagens únicas, o que cabe na franquia de imagens. A faixa ideal é hipótese: após 4 semanas, compare a retenção por faixa de duração.

| Formato narrativo | Duração-alvo | Palavras (estimativa, a calibrar na Fase 0) |
| --- | --- | --- |
| Pergunta intrigante ou fato único | 30–45 s | 70–110 |
| Padrão: "como funciona", comparação, segunda pessoa | 45–70 s | 110–170 |
| Ciclo de vida, história cronológica | 70–90 s | 170–220 |
| Exceção aprovada no PR de roteiro | até 120 s | até 290 |

Os limites das redes não apertam: Shorts aceitam até 3 min, Reels por API de 3 s a 15 min e TikTok pelo Buffer de 3 s a 10 min.

**Como parecer animação 3D estilizada sem vídeo generativo.** A regra: um plano a cada 3–5 s (14–18 planos em 60 s), mas cada imagem gerada rende 2 planos com enquadramento e movimento diferentes. Tudo é feito localmente no FFmpeg, sem custo.

| Técnica | Como | Onde usar |
| --- | --- | --- |
| Movimento de câmera | Aproximação, afastamento, pan e tilt com *easing* sobre a imagem | Todos os planos |
| Paralaxe em camadas | Personagem recortado automaticamente (rembg) + fundo gerado sem o personagem + partículas; cada camada se move numa velocidade | Planos de destaque |
| Micro-animação | "Respiração" (escala de 1–2% em onda), leve oscilação, pequeno salto nas batidas da narração | Personagem em cena |
| Troca de pose | 2–3 variações do personagem alternadas por corte no ritmo da fala | Ações ("abre os braços", "vira") |
| Luz e atmosfera | Raios de luz, bolhas, poeira gerados por script; vinheta; gradiente animado | Ambientação |
| Foco | Desfoque do fundo que muda durante o plano | Revelações |
| Infografia | Setas, números e escalas desenhados por código | Fatos numéricos |
| Transições | Pan rápido com desfoque de movimento; corte por forma parecida | Ritmo |
| Legendas | Palavra a palavra, grandes, fonte com licença livre (OFL) | Sempre |
| Som | Narração + efeitos sintetizados por script (whoosh, pop), sem material de terceiros; sem música no MVP | Sempre |

**Consistência visual entre episódios:**

- **Bíblia visual** em `docs/` e `config/estilo.json`: prefixo de prompt fixo, paleta, iluminação, "lente", fundo e restrições ("sem texto na imagem").
- **Ficha do personagem por episódio:** gerar 6–8 candidatas, escolher uma canônica e derivar as poses dela. A ficha entra no PR de vídeo para sua revisão.
- **Mesmas regras de enquadramento** em todo episódio: personagem no terço central, legendas na faixa do meio, longe das áreas cobertas pelos botões das redes.

**Especificação do master:** 1080×1920, 30 fps, H.264, áudio AAC 48 kHz a 128 kbps (dentro da [especificação do Instagram](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media)). Loudness normalizado por código. Um único master serve as três redes.

## 4. Narração: Google Chirp 3 HD

**Confirmado: pt-BR suportado, 1 milhão de caracteres grátis por mês e uso do áudio compatível com os termos.** O risco está no faturamento: o Google exige conta de faturamento com cartão, e o orçamento do Google Cloud **avisa, mas não bloqueia** gastos. Por isso o controle é em camadas.

**Fatos (consultados em 04/11/2026):**

- **Franquia:** 0 a 1 milhão de caracteres/mês grátis no Chirp 3 HD; acima disso, US$ 30 por milhão. Contam espaços, quebras de linha e tags SSML, exceto `<mark>` ([preços](https://cloud.google.com/text-to-speech/pricing)).
- **Uso estimado:** \~4.000 caracteres por episódio, já com regerações → \~52 mil/mês em 3/semana (5% da franquia); \~120 mil em 7/semana (12%).
- **Recursos em pt-BR:** velocidade de 0,25 a 2,0; pausas por marcação; pronúncia personalizada em IPA ou X-SAMPA; SSML com `<phoneme>` e `<sub>` em requisições síncronas. O SSML e os controles de voz estão em *Preview*, sob os termos de pré-lançamento ([Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd)).
- **Licença:** pelos termos de serviço, o Google não reivindica propriedade sobre o conteúdo gerado. A restrição relevante é não usar a saída para criar ou treinar modelo concorrente. Não encontrei exigência de atribuição ([termos](https://cloud.google.com/terms/service-terms)).
- **Rótulo nas redes:** a Meta cita "Reel narrado com voz de IA realista" como caso que pede rótulo. Todo post sai com `isAiGenerated = true`.

**Controles contra cobrança (cinco camadas):**

1. **Projeto isolado** no Google Cloud, só com a API Text-to-Speech ativada.
2. **Contador próprio, que é o teto real:** a `Factory.Cli` soma os caracteres enviados (com SSML) num arquivo de uso mensal versionado. Recusa acima de 800 mil/mês e de 12 mil por episódio.
3. **Cota da API reduzida** no console (requisições por minuto). Limita a velocidade de um eventual loop, não o total.
4. **Orçamento de US$ 1** com alertas em 50%, 90% e 100%, ligado a uma função que desativa o faturamento do projeto ([procedimento oficial](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications)). O Google avisa que as notificações têm atraso e que recursos podem ser apagados — aceitável num projeto que só tem TTS.
5. **Sem chave de serviço:** o GitHub Actions autentica por federação de identidade (OIDC) numa conta de serviço com papel mínimo. Não existe arquivo de chave para vazar.

**Pior caso realista:** um bug que passe pelo contador e gere 200 mil caracteres extras antes do corte custaria US$ 6 (200 mil × US$ 30 por milhão). Por isso a camada 2 bloqueia antes de chamar a API, e não depois.

**Plano B:** não há alternativa gratuita equivalente com uso comercial. O plano gratuito da ElevenLabs proíbe uso comercial. O Azure F0 é citado por terceiros como restrito a uso não comercial nas vozes prontas (não verifiquei na fonte oficial). Se o Google falhar, a narração para e o episódio espera.

## 5. Plataformas: YouTube, Instagram e TikTok

**No MVP, as três redes publicam automaticamente pelo Buffer Free, que tem exatamente 3 canais e envia o sinal de conteúdo gerado por IA nas três.** Buffer é parceiro oficial das plataformas, então não há automação de navegador nem atalho fora das regras. As APIs diretas do YouTube e do Instagram ficam como plano B (fase 4); no TikTok, a API direta não é viável para ferramenta própria.

|  | YouTube (Shorts) | Instagram (Reels) | TikTok |
| --- | --- | --- | --- |
| **Integração oficial direta** | [Data API v3](https://developers.google.com/youtube/v3/docs/videos/insert): viável. Desde 02/11/2026 projetos não verificados não ficam presos ao modo privado; publique o app OAuth "em produção", senão o token expira em 7 dias ([Google](https://support.google.com/cloud/answer/10311615)) | [Instagram API com login do Instagram](https://developers.facebook.com/docs/instagram-platform/content-publishing): viável; 100 posts/24 h; vídeo por URL pública; sem agendamento nativo | [Content Posting API](https://developers.tiktok.com/doc/content-sharing-guidelines): **inviável**. Sem auditoria, só posta em privado; as diretrizes vetam ferramenta para as próprias contas |
| **Publicação automática no MVP** | Buffer: título, privacidade, categoria, "feito para crianças", `isAiGenerated`, notificar inscritos ([campos](https://developers.buffer.com/types/YoutubePostMetadataInput.html)) | Buffer: tipo `reel`, compartilhar no feed, primeiro comentário, `isAiGenerated` ([campos](https://developers.buffer.com/types/InstagramPostMetadataInput.html)) | Buffer: `isAiGenerated` para vídeo ([campos](https://developers.buffer.com/types/TikTokPostMetadataInput.html)) |
| **Publicação assistida ("Notify Me": aviso no celular e você finaliza no app)** | Disponível; só como contingência | Obrigatória para música, stickers, texto, links, tags de produto ou proporção fora do aceito ([Buffer](https://buffer.helpscoutdocs.com/article/657-scheduling-instagram-posts-and-reels)) | Obrigatória para sons do TikTok, efeitos, enquetes e stickers ([Buffer](https://support.buffer.com/article/559-using-tiktok-with-buffer)) |
| **Requisitos de conta** | Canal @imagineser.oficial conectado ao Buffer | Conta **profissional** (Business ou Creator); conta pessoal cai sempre em Notify Me | O Buffer se contradiz (uma página antiga diz só conta Business; as atuais aceitam pessoal). Confirmar ao conectar |
| **Limites que importam** | Vídeo vertical de até 3 min vira Short | Reel de 3 s a 15 min, até 300 MB | 3 s a 10 min, até 1 GB, 23–60 fps, 2.200 caracteres, até 5 hashtags, 25 posts/24 h |
| **Métricas** | YouTube Studio (manual semanal); API de Analytics na fase 4 | Insights do app (manual) | App do TikTok (manual): o Buffer não traz analytics do TikTok |

**Buffer em detalhe:**

- **Plano gratuito:** 3 canais, 10 posts agendados por canal, 1 usuário, sem fluxo de aprovação (não faz falta: as aprovações ficam no GitHub) ([preços](https://buffer.com/pricing)).
- **API:** GraphQL em `api.buffer.com`, chave pessoal, em beta público. No plano grátis: 1 chave, 150 chamadas a cada 15 min, 600 por 24 h e 1.000 por canal a cada 30 dias ([limites](https://developers.buffer.com/guides/api-limits.html)). Em 3/semana são \~39 posts/mês.
- **Mídia:** não há upload. O post recebe uma URL pública, e o **Buffer baixa o vídeo na hora de publicar**, não ao criar o post ([hospedagem de mídia](https://developers.buffer.com/guides/hosting-media)). A URL tem de valer até lá.
- **Estratégia:** o publicador cria o post logo após a aprovação do vídeo, já com o horário de publicação, e uma URL pré-assinada do R2 válida por 72 h (cobre o horário e eventuais novas tentativas). Grava o ID do post. Depois do horário, consulta o status (`sent` ou `error`).
- **Riscos:** API em beta pode mudar; o roadmap do Buffer cita um bug de detecção de duplicado que bloqueia posts recriados ([roadmap](https://developers.buffer.com/roadmap)); o Buffer é ponto único de falha. Por isso a fase 4 adiciona a API direta do YouTube como plano B, e o runbook de publicação manual existe desde o início.

## 6. Segurança

**A garantia de "nada publica sem as duas aprovações" fica no código do publicador, que consulta a API do GitHub. Não depende de configuração do repositório.** No GitHub Free, branches protegidos só existem em repositório público ([GitHub](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)). Então o publicador não confia no conteúdo do branch principal: confia só em revisões feitas pelo seu usuário.

### 6.1 As duas aprovações

Antes de cada post, `Factory.Cli publicar` exige, nesta ordem:

1. **PR de roteiro** do episódio mesclado, com revisão `APPROVED` cujo autor é o seu login (variável `OWNER_LOGIN` do repositório) e feita no último commit do PR.
2. **PR de vídeo** do episódio mesclado, com a mesma regra.
3. **Encadeamento:** o `video.json` do commit aprovado (lido pela API, não do disco) aponta para o hash do roteiro aprovado no passo 1.
4. **Hash do arquivo:** o master é baixado do R2 e o SHA-256 recalculado tem de bater com o aprovado. A chave no R2 contém o hash (`masters/ep0007/<sha256>.mp4`) e nunca é sobrescrita.
5. **Interruptor geral:** variável de repositório `PUBLICACAO_ATIVA=true`, que só você altera em Settings.
6. **Isolamento:** só o job `publicar` recebe a chave do Buffer.

Os PRs são abertos pelo `github-actions[bot]`, então você pode aprová-los. Para isso é preciso ligar "Allow GitHub Actions to create and approve pull requests" — o que também deixaria um workflow aprovar PRs. Por isso o passo 1 exige o **seu** login: aprovação de bot não conta.

**Testes negativos obrigatórios antes de ligar a publicação:** master trocado após aprovação; PR mesclado sem revisão; aprovação feita num commit antigo; aprovação por outro usuário ou bot; `PUBLICACAO_ATIVA=false`. Todos têm de bloquear.

### 6.2 Duplicidade

- Cada episódio tem `publicacoes.json` com um estado por rede: `AGENDADA → ENVIANDO → CRIADA_NO_BUFFER → PUBLICADA` ou `FALHOU`. Chave de idempotência: episódio + rede + hash do master.
- O publicador grava `ENVIANDO` e faz *push* **antes** de chamar o Buffer; grava o ID do post logo depois.
- Se cair entre as duas gravações: na nova tentativa, lista os posts do canal no Buffer e procura o marcador `#ep0007` no texto. Achou: adota o ID. Não achou: cria.
- O workflow `publicar` usa `concurrency` (um por vez, sem cancelar o que está rodando). A detecção de duplicado do próprio Buffer é a última rede de proteção.

### 6.3 Recuperação de jobs interrompidos

- **Etapas idempotentes por conteúdo:** a saída de cada etapa tem chave = hash das entradas (ex.: `img/cena-04/<hash do prompt>.jpg`). Se já existe no R2, a etapa pula.
- **Checkpoint no Git:** cada etapa concluída atualiza o `episode.json` no branch do episódio.
- **Concessão com prazo:** etapa em andamento grava `rodando_ate`. O workflow `reconciliar`, três vezes por dia, reenfileira etapas com prazo vencido. Depois de 3 tentativas, o episódio fica `BLOQUEADO` e abre uma *issue* de alerta.
- **Fila de imagens:** cenas pendentes ficam listadas; o job diário continua de onde parou. Erro 3036 (franquia do dia acabou) não gera retry: espera até 00:05 UTC.
- **Tetos:** `timeout-minutes` em todo job e `--max-turns` no Claude Code.

### 6.4 Segredos

| Segredo | Onde fica | Quem usa | Escopo |
| --- | --- | --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | GitHub Secret | Jobs de pauta, roteiro e ajuste | Sua assinatura; gerar com `claude setup-token`; renovar a cada 90 dias |
| `CF_AI_TOKEN` | GitHub Secret | Job `produzir` | Token da Cloudflare só com permissão de Workers AI |
| Chaves do R2 | GitHub Secret | `produzir` (escrita), `publicar` (leitura) | Uma chave por bucket e por papel |
| Google Cloud | Nada guardado | `produzir` | Federação OIDC numa conta de serviço com papel mínimo |
| `BUFFER_API_KEY` | GitHub Secret | Só `publicar` | A chave não tem escopos (o Buffer ainda não oferece): por isso o isolamento |

**Regras:** segredo só no `env` do passo que o usa; `permissions:` mínimas por job; ações de terceiros fixadas por SHA do commit. Os jobs do Claude Code usam o `GITHUB_TOKEN` padrão, que **não tem permissão para alterar** `.github/workflows/` ([GitHub](https://github.com/orgs/community/discussions/35410)) — assim, uma página maliciosa lida na pesquisa não consegue induzir o Claude a mudar os workflows. As ferramentas do Claude ficam restritas a busca, leitura web, leitura e escrita de arquivos e o comando `validar`, sem shell livre. No seu PC: `.env` fora do Git, `gitleaks` antes de cada commit e o hook do Claude Code bloqueando a leitura de segredos.

## 7. Validação: quando subir de 3 para 5 e para 7 por semana

**Suba de cadência só depois de 4 semanas seguidas cumprindo todos os critérios obrigatórios do nível atual.** Se algum falhar por 2 semanas seguidas, volte ao nível anterior. As métricas de audiência não bloqueiam: decidem formato, não capacidade.

| Critério (obrigatório) | Como medir | Para ir de 3 → 5 | Para ir de 5 → 7 |
| --- | --- | --- | --- |
| Pontualidade | Horários publicados ou cobertos pela reserva ÷ horários previstos | 100% | 100% |
| Segurança | Publicações sem dupla aprovação; posts duplicados | 0 e 0 | 0 e 0 |
| Qualidade do roteiro | Roteiros aprovados com no máximo 1 ajuste | ≥ 75% | ≥ 85% |
| Qualidade do vídeo | Vídeos aprovados na 1ª versão | ≥ 75% | ≥ 85% |
| Fatos | Erros factuais confirmados após publicar | 0 | 0 |
| Limite do Pro | % do limite semanal do plano usado pelo pipeline (em claude.ai/settings/usage, anotado toda segunda) | ≤ 50% (projeta ≤ 85% em 5/semana) | ≤ 60% (projeta ≤ 85% em 7/semana) |
| Franquia de imagens | Neurons por episódio ÷ 10.000 | ≤ 1,2 dia de franquia | ≤ 0,8 dia de franquia |
| GitHub Actions | Minutos do mês ÷ \~2.000 inclusos | ≤ 40% | ≤ 55% |
| Voz | Caracteres do mês ÷ 1 milhão | ≤ 30% | ≤ 30% |
| Seu tempo | Minutos por episódio (ler roteiro + assistir vídeo + ajustes), anotados no PR | ≤ 25 min | ≤ 20 min |
| Reserva | Episódios aprovados em estoque | ≥ 2 | ≥ 3 |

**Sinais de audiência (não bloqueiam):** retenção média e % que assistiu até o fim por faixa de duração e por formato narrativo; seguidores ganhos por episódio; nenhum aviso de política nas três redes. Desde a primeira publicação, anote toda semana num `metricas/AAAA-SS.csv` (10 minutos copiando dos painéis) e analise com o Claude no fim de semana. Correlação não é causa: só mude o formato depois de ver o padrão em pelo menos 6 episódios.

## 8. Custos revisados

**Custo adicional previsto: US$ 0. O único gasto é o Claude Pro, já pago (US$ 20, cerca de R$ 106 com IOF).** Dois serviços exigem cartão cadastrado (Cloudflare R2 e Google Cloud) e não têm teto nativo de gasto; neles, o teto é o nosso código. A exposição máxima num cenário de falha é de cerca de US$ 6–7 no mês.

| Item | Categoria | Franquia gratuita | Uso estimado em 3/semana | Limite rígido | Cobrança possível |
| --- | --- | --- | --- | --- | --- |
| Claude Pro (pesquisa, roteiro, checagem, storyboard) | **Coberto pela assinatura** | Janela de 5 h + limite semanal, não publicados em tokens | A medir na Fase 0 | O plano para ao bater o limite | Só se você ligar os créditos de uso extra em claude.ai/settings/usage. **Manter desligado** |
| GitHub Free (Actions, repositório privado) | Grátis | US$ 12 de computação/mês (\~2.000 min Linux) e 500 MB de artefatos ([GitHub](https://docs.github.com/en/billing/concepts/product-billing/github-actions)) | \~670 min (34%): \~40 min por episódio + \~150 min de jobs fixos | Sem forma de pagamento, o uso é bloqueado ao esgotar | Nenhuma, se você **não** cadastrar pagamento no GitHub |
| Cloudflare Workers AI (imagens) | Grátis | 10.000 neurons/dia | A medir (T1); a regra limita a 8.000/dia | Plano Workers Free: erro 3036 ao esgotar | Nenhuma, desde que você **não** assine o Workers Paid |
| Cloudflare R2 (vídeos e imagens) | Grátis, com cartão cadastrado | 10 GB-mês, 1 milhão de operações classe A, 10 milhões classe B, saída grátis | \~2–4 GB | Sem teto nativo. Regra de ciclo de vida (intermediários apagados em 14 dias, masters em 90) + `Factory.Cli` recusa upload se o bucket passar de 8 GB | US$ 0,015/GB-mês acima de 10 GB: centavos |
| Google Cloud TTS, Chirp 3 HD (voz) | Grátis, com cartão cadastrado | 1 milhão de caracteres/mês | \~52 mil (5%) | Contador da `Factory.Cli` (800 mil/mês) + corte de faturamento (seção 4) | US$ 30 por milhão acima da franquia; pior caso \~US$ 6 |
| Buffer Free (publicação) | Grátis, sem cartão | 3 canais; 10 posts agendados por canal; API com 600 chamadas/24 h | \~39 posts/mês | Limites do plano | Nenhuma |
| APIs do YouTube e do Instagram (plano B, fase 4) | Grátis | Cotas diárias | — | A própria cota | Nenhuma |
| Telegram (aviso opcional) | Grátis | — | — | — | Nenhuma |
| Música, domínio, servidor, APIs de IA pagas | **Fora do MVP** | — | — | — | — |

**Detalhe que mudou o desenho:** o GitHub cobra cada job arredondando para cima por minuto. Um workflow rodando de hora em hora consumiria \~720 min/mês sozinho. Por isso a publicação é disparada pela aprovação (o Buffer agenda o horário) e o único job periódico é o `reconciliar`, três vezes por dia. Em 7/semana, a estimativa sobe para \~1.350 min (68%) — o critério da seção 7 acompanha isso.

**Premissas:** US$ 1 = R$ 5,30 efetivo (cotação perto de R$ 5,01 em 07/10/2026 + IOF de cartão e spread). Preços e franquias consultados em 03–04/11/2026.

## 9. Arquitetura final: cronograma da solução inicial

**Cada episódio leva cerca de dois dias do roteiro ao post, e você só atua em dois momentos: aprovar o roteiro (até 12h de D-2) e aprovar o vídeo (até 22h de D-1).** Todo o resto roda no GitHub Actions; nada depende do seu PC ligado.

```text
Cronograma de um episódio (diagrama no documento original):
D-2 05:30  Claude Code (Action, Pro): pesquisa, roteiro, checagem, storyboard → Factory.Cli validar → PR 1
D-2 até 12h  Você: revisa e aprova o PR 1 (merge)
D-2 → D-1  Factory.Cli produzir: ficha do personagem, imagens FLUX (fila diária, Cloudflare), narração (Google TTS),
           legendas, render, QA → master no R2 → PR 2   (se a franquia de imagens acabar, continua às 00:05 UTC)
D-1 até 22h  Você: assiste e aprova o PR 2 (merge) → Factory.Cli publicar confere 2 aprovações + hash → cria os
           posts no Buffer para o horário
D (horário)  Buffer publica em YouTube, Instagram e TikTok com isAiGenerated; reconciliar confere 3× ao dia
```

Se a franquia diária de imagens acabar no meio, o `produzir` continua às 21:05 (00:05 UTC) e o PR de vídeo sai no dia seguinte, ainda antes do prazo.

**Agenda semanal em 3 episódios (horário de Brasília; o cron do GitHub usa UTC, então 05:30 = `30 8 * * *`):**

| Dia | Automático | Você |
| --- | --- | --- |
| Domingo | 05:30 roteiro do episódio de terça | Aprovar a pauta da semana; aprovar o roteiro de terça |
| Segunda | Produção do episódio de terça; PR de vídeo | Assistir e aprovar o vídeo de terça; anotar as métricas da semana (10 min) |
| Terça | Buffer publica o episódio 1; 05:30 roteiro do episódio de quinta | Aprovar o roteiro de quinta |
| Quarta | Produção do episódio de quinta | Aprovar o vídeo de quinta |
| Quinta | Publica o episódio 2; 05:30 roteiro do episódio de sábado | Aprovar o roteiro de sábado |
| Sexta | Produção do episódio de sábado | Aprovar o vídeo de sábado |
| Sábado | Publica o episódio 3; 09:00 proposta de pauta da semana seguinte (PR) | — |

O `reconciliar` roda às 07h, 15h e 23h todos os dias. O horário de publicação alterna entre 12h e 19h nas primeiras 4 semanas, para comparar.

**Workflows e gatilhos:**

| Workflow | Gatilho | O que faz | Segredos |
| --- | --- | --- | --- |
| `pauta-semanal` | Sábado 09:00 | Claude propõe 3 temas + 2 reservas, sem repetir publicados → PR | Claude |
| `roteiro` | Cron 05:30 nos dias de roteiro, ou manual | Claude pesquisa, escreve, checa, faz storyboard → `validar` → PR 1 | Claude |
| `ajuste` | Comentário `@claude ajuste:` num PR | Claude revisa no mesmo PR → `validar` | Claude |
| `produzir` | Merge do PR 1, e cron 00:05 UTC para continuar a fila de imagens | Ficha, imagens, voz, legendas, render, QA → R2 → PR 2 | Cloudflare, R2 (escrita), Google via OIDC |
| `publicar` | Merge do PR 2 | Confere as duas aprovações e o hash → cria os 3 posts no Buffer para o horário | Buffer, R2 (leitura) |
| `reconciliar` | 07h, 15h e 23h | Retoma etapas vencidas, confere status no Buffer, abre *issue* se algo falhou | Buffer, R2 (leitura) |
| `ci` | Todo push e PR | Build e testes da `Factory.Cli` | Nenhum |

## 10. Plano de implementação

**Um repositório, uma solução .NET 10 com quatro projetos, sete skills, sete workflows.** Os agentes são skills do Claude Code; todo efeito no mundo externo (APIs, R2, Buffer) passa pela `Factory.Cli`, que tem testes.

**Estrutura do repositório:**

```text
imaginaser-fabrica/
├─ CLAUDE.md  ·  PRIMEIRA-SESSAO.md  ·  README.md  ·  .gitignore
├─ .claude/
│  ├─ settings.json            permissões + hook
│  ├─ hooks/bloquear.sh
│  ├─ rules/                   dotnet.md · workflows.md · episodios.md
│  └─ skills/
│     ├─ pauta-semanal/SKILL.md
│     ├─ pesquisar/SKILL.md     + fontes-confiaveis.md
│     ├─ roteirizar/SKILL.md    + formulas-narrativas.md
│     ├─ checar-fatos/SKILL.md
│     ├─ storyboard/SKILL.md    + biblia-visual.md
│     ├─ metadados/SKILL.md
│     └─ aplicar-ajuste/SKILL.md
├─ .github/
│  ├─ workflows/  pauta-semanal · roteiro · ajuste · produzir · publicar · reconciliar · ci
│  └─ PULL_REQUEST_TEMPLATE/  roteiro.md · video.md (checklists)
├─ docs/  00–07 (do kit) · runbooks/ (publicar-manual, recuperar-episodio, rotacionar-segredos)
├─ config/  calendario.json · limites.json · estilo.json · pronuncia.json · plataformas.json
├─ schemas/  episode · dossie · afirmacoes · roteiro · storyboard · metadados · publicacoes (.schema.json)
├─ pautas/   banco-de-temas.json · publicados.json
├─ episodes/2026-11-10-ep0001-polvo/
│  episode.json · dossie.md · afirmacoes.json · roteiro.md · storyboard.json
│  metadados.json · video.json · publicacoes.json
├─ uso/      2026-11.json   (caracteres de TTS e neurons por dia)
├─ metricas/ 2026-46.csv
├─ src/
│  ├─ Factory.Domain/          estados, regras de transição, limites (sem I/O)
│  ├─ Factory.Infrastructure/  WorkersAi, GoogleTts, R2, Buffer, GitHubApprovals
│  ├─ Factory.Media/           FFmpeg, legendas ASS, recorte, QA técnico
│  └─ Factory.Cli/             comandos: validar · produzir · publicar · reconciliar · uso
├─ tests/Factory.Tests/         xUnit: transições, portão de aprovação, idempotência, limites
└─ bancada/                     scripts e resultados dos testes T1–T5
```

**Agentes (skills) e o que cada um pode fazer:**

| Skill | Entrada | Saída (validada por schema) | Ferramentas permitidas |
| --- | --- | --- | --- |
| `pauta-semanal` | `calendario.json`, `banco-de-temas.json`, `publicados.json` | Proposta de 3 temas + 2 reservas | Leitura de arquivos |
| `pesquisar` | Tema e ângulo | `dossie.md`: fontes com URL, autor/instituição, datas e trecho literal | Busca e leitura web, escrita só na pasta do episódio |
| `roteirizar` | Dossiê, guia editorial | `roteiro.md` com cada frase factual ligada a uma afirmação | Leitura e escrita de arquivos, **sem web** |
| `checar-fatos` | Roteiro, dossiê | `afirmacoes.json` (verde, amarelo, vermelho; tipo de afirmação) | Leitura web para reler a fonte |
| `storyboard` | Roteiro, bíblia visual | `storyboard.json`: planos, prompts, movimento, poses | Leitura e escrita de arquivos |
| `metadados` | Roteiro | `metadados.json` por rede (título, descrição, hashtags, marcador `#epNNNN`) | Leitura e escrita de arquivos |
| `aplicar-ajuste` | Comentário do PR | Nova versão do arquivo indicado | As da skill afetada |

No workflow, o `checar-fatos` roda numa invocação separada do `roteirizar`, para não "corrigir a própria prova". A parte determinística da checagem (URL responde, trecho literal existe na página, DOI resolve) fica no `validar`.

**Ordem de desenvolvimento:**

1. **Semana 0 — Transplante.** Repositório, kit, primeira sessão no terminal. Conectar as três contas @imagineser.oficial ao Buffer e confirmar tipo de conta (Instagram profissional; TikTok aceito para publicação automática).
2. **Fase 0 — Bancada (1–2 semanas).** Testes T1–T5 de imagem; 5 vozes Chirp 3 HD; post de teste pelo Buffer com `isAiGenerated` em cada rede; um episódio feito à mão com as skills rodando localmente. ADRs: modelo de imagem, voz, duração.
3. **Fase 1 — Roteiro (2 semanas).** `Factory.Domain` + schemas + `validar` + skills de pesquisa, roteiro e checagem + workflows `roteiro` e `ajuste`. Portão: 6 PRs de roteiro que você aprovaria.
4. **Fase 2 — Produção (2–3 semanas).** `Factory.Media` + clientes de Workers AI, Google e R2 + workflow `produzir` + limites e contadores. Portão: 4 vídeos aprovados; render < 10 min; limites testados.
5. **Fase 3 — Publicação (1–2 semanas).** Cliente do Buffer + portão de aprovação + `publicar` + `reconciliar` + testes negativos + runbook manual. Portão: todos os testes negativos bloqueando.
6. **Fase 4 — Operação em 3/semana (4+ semanas).** Métricas semanais; API direta do YouTube como plano B. Depois, os critérios da seção 7 decidem a subida para 5 e 7.

## 11. Pendências que dependem de você

Para cada uma, a premissa adotada até você decidir.

- [x] **Marca:** "Imagine Ser" / @imagineser.oficial (contas já existem).
- [x] **Repositório:** privado (ADR-0002), nome `imagineser-fabrica`.
- [ ] **Cartão no R2 e no Google Cloud:** *premissa: sim.* Google na vez da voz (Fase 0); R2 só na Fase 2.
- [ ] **Conferir agora:** créditos de uso extra do Claude desligados; nenhuma forma de pagamento no GitHub; Cloudflare no plano Workers Free.
- [ ] **Tipo de conta:** Instagram profissional (Business ou Creator)? TikTok pessoal ou Business? Confirmar ao conectar no Buffer.
- [x] **Público infantil:** público geral (13+); "feito para crianças" = não por padrão, visível no PR de roteiro para o Gabriel ver ao aprovar.
- [x] **Prazos de aprovação:** não há prazos (ADR-0011).
- [x] **Música:** sem trilha no MVP (ADR-0008).

## Fontes desta revisão

Consultadas em 04/11/2026. As fontes da v1 estão na outra aba.

**Claude Code**

- [Memória e CLAUDE.md](https://code.claude.com/docs/en/memory) · [Skills](https://code.claude.com/docs/en/skills) · [Settings e permissões](https://code.claude.com/docs/en/settings) · [GitHub Actions](https://code.claude.com/docs/en/github-actions)

**Imagem (Cloudflare e Black Forest Labs)**

- [Workers AI — preços e franquia](https://developers.cloudflare.com/workers-ai/platform/pricing/) · [Erros (3036, 5035)](https://developers.cloudflare.com/workers-ai/platform/errors)
- [FLUX.1 schnell](https://developers.cloudflare.com/workers-ai/models/flux-1-schnell/) · [FLUX.2 klein 4B](https://developers.cloudflare.com/workers-ai/models/flux-2-klein-4b/) · [FLUX.2 dev](https://developers.cloudflare.com/workers-ai/models/flux-2-dev/)
- [Licença do klein 4B (Vercel)](https://vercel.com/ai-gateway/models/flux-2-klein-4b.md) · [Licenças do FLUX.2 (VentureBeat)](https://venturebeat.com/technology/black-forest-labs-launches-open-source-flux-2-klein-to-generate-ai-images-in)

**Voz (Google Cloud)**

- [Chirp 3 HD](https://docs.cloud.google.com/text-to-speech/docs/chirp3-hd) · [Preços do TTS](https://cloud.google.com/text-to-speech/pricing) · [Termos de serviço](https://cloud.google.com/terms/service-terms) · [Desativar faturamento por notificação](https://docs.cloud.google.com/billing/docs/how-to/disable-billing-with-notifications) · [Status de publicação do OAuth](https://support.google.com/cloud/answer/10311615)

**Buffer**

- [Preços](https://buffer.com/pricing) · [Limites da API](https://developers.buffer.com/guides/api-limits.html) · [Hospedagem de mídia](https://developers.buffer.com/guides/hosting-media) · [Roadmap da API](https://developers.buffer.com/roadmap)
- Campos: [TikTok](https://developers.buffer.com/types/TikTokPostMetadataInput.html) · [YouTube](https://developers.buffer.com/types/YoutubePostMetadataInput.html) · [Instagram](https://developers.buffer.com/types/InstagramPostMetadataInput.html)
- [TikTok no Buffer](https://support.buffer.com/article/559-using-tiktok-with-buffer) · [Instagram no Buffer](https://buffer.helpscoutdocs.com/article/657-scheduling-instagram-posts-and-reels)

**GitHub**

- [Branches protegidos](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches) · [Cobrança do Actions](https://docs.github.com/en/billing/concepts/product-billing/github-actions) · [`GITHUB_TOKEN` e workflows](https://github.com/orgs/community/discussions/35410)
