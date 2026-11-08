# Fábrica de conteúdo com IA — Análise de arquitetura

Nov 3, 2026 · @Gabriel Guislotti

> **Substituída em parte pelo Plano MVP v2 (04/11/2026).** Onde as duas abas divergirem, vale a v2: orçamento máximo de US$ 20/mês, nenhuma API paga no MVP e Bilibili fora do escopo. Esta aba fica como referência para quando o orçamento crescer (arquitetura-alvo, cenários pagos).

## 1. Resumo executivo

**Recomendação, ajustada ao teto de US$ 20/mês: começar com uma operação que roda no GitHub Actions usando o seu Claude Pro (pela GitHub Action oficial do Claude Code, autenticada com o token da assinatura) e serviços em faixa gratuita.** O estado e as aprovações ficam no próprio repositório, como pull requests. Quando o orçamento crescer, o núcleo migra para a aplicação .NET própria descrita neste documento (caminho D).

**Verifiquei sua hipótese sobre o Pro:**

- **Permitido:** a documentação da [GitHub Action](https://code.claude.com/docs/en/github-actions) aceita o `CLAUDE_CODE_OAUTH_TOKEN` do Pro e diz que, com ele, as execuções usam a assinatura em vez de cobrança de API. O mesmo vale para `claude -p` e Agent SDK logados no plano ([artigo de suporte](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)).
- **Proibido:** pegar o token da assinatura e chamar a API direto do seu próprio app. Tem que ser o binário oficial do Claude Code ([termos](https://code.claude.com/docs/en/legal-and-compliance)).
- **Quanto rende:** a Anthropic não publica o limite do Pro em tokens. Há uma janela de 5 h e um limite semanal, compartilhados com o seu uso de desenvolvimento. É plausível que renda mais que US$ 20 de API, mas não há número oficial nem garantia: o piloto vai medir.
- **O Pro não inclui créditos de API** (só Max, Ultra e Team). E ele consome o orçamento inteiro, então todo o resto precisa ser gratuito.

**O que cabe nos US$ 20:** GitHub Free com repositório privado (US$ 12 de computação inclusos, cerca de 2.000 minutos); imagens no Cloudflare Workers AI (10.000 *neurons*/dia grátis); voz Google Chirp 3 HD (1 milhão de caracteres/mês grátis); Cloudflare R2 (10 GB grátis); APIs do YouTube e do Instagram (gratuitas); TikTok via Buffer Free; Bilibili manual.

**O que você abre mão no começo:** imagens de qualidade menor (FLUX gratuito em vez de Gemini), nenhum clipe animado (só movimento de câmera), o app do GitHub fazendo papel de painel, risco de bater o limite do Pro em 7 episódios/semana e agendamento com possível atraso de minutos.

Por que a arquitetura-alvo (quando o orçamento crescer) é um backend próprio:

- **Os requisitos críticos são de backend, não de agente.** Estado persistente, aprovação presa a uma versão específica do arquivo, idempotência, teto de custo e publicação sem duplicidade pedem banco de dados, máquina de estados e jobs com retry. Nenhuma ferramenta pronta entrega isso tudo sem gambiarra.
- **As Scheduled Tasks do Claude Code não servem de runtime crítico.** Estão em *research preview*, consomem o limite da sua assinatura, rodam em modo automático sem portão de aprovação e têm intervalo mínimo de 1 hora. Os termos dizem que os limites de Pro/Max pressupõem "uso individual comum". Servem bem para manutenção do código, não para a fábrica.
- **A sua stack já resolve.** ASP.NET Core + Hangfire + SQL Server cobrem painel, fila durável e agendamento com fuso horário. Existe SDK oficial da Anthropic para C#. Não há ganho real em trocar de linguagem.
- **A IA fica onde agrega:** pesquisa com fontes, roteiro, checagem, storyboard e metadados (Claude API); imagens (Gemini); animação pontual (Kling via fal); voz (Google Chirp 3 HD ou ElevenLabs). A montagem é determinística (FFmpeg).

O que você precisa saber antes de investir:

- **Automação completa nas quatro redes não é possível hoje por vias oficiais.** YouTube e Instagram: sim, via API direta na sua própria conta. TikTok: a API proíbe expressamente "ferramenta para subir conteúdo nas contas que você ou sua equipe gerenciam" — o caminho oficial é um parceiro aprovado (Buffer) ou rascunho que você finaliza no app. Bilibili: a plataforma aberta exige empresa com licença comercial chinesa → publicação manual assistida.
- **Monetização depende de valor editorial humano.** O YouTube remove a monetização do canal inteiro quando identifica conteúdo "inautêntico" (em massa, por template). Sua revisão e a variedade narrativa são requisito de negócio, não só de qualidade.
- **Custo mensal estimado** (premissas na seção 10): no modo orçamento, US$ 20 (cerca de R$ 106, só o Claude Pro). Com backend próprio e serviços pagos, de cerca de R$ 560 (3/semana, econômico) a R$ 1.490 (7/semana, intermediário); o avançado chega a R$ 3.150/mês.
- **Seu tempo:** cerca de 10–15 min por roteiro e 5–10 min por vídeo, mais 1 h no planejamento semanal. Em 7/semana, algo como 3–4 h por semana.

## 2. Comparação de caminhos

Com o teto de US$ 20, comece pelo caminho E (descrito abaixo da tabela) e tenha o D como destino. O D vence no longo prazo porque é o único que dá garantia técnica de "nada publica sem aprovação" e ainda usa serviços prontos onde a API oficial fecha a porta. O A falha em confiabilidade e termos de uso; o C falha em manutenção quando a lógica de versões e custos cresce.

| Caminho | Autonomia | Confiabilidade | Custo mensal típico | Manutenção | Limite decisivo | Veredito |
| --- | --- | --- | --- | --- | --- | --- |
| **A.** Só Claude Code + Markdown + Scheduled Tasks | Média: roda na nuvem, mas o "estado" são arquivos num repositório | Baixa: *research preview*; status "Succeeded" só diz que a sessão terminou, não que o trabalho foi feito; para se o GitHub desconectar | LLM coberto pela assinatura até o limite semanal; mídia paga à parte | Baixa no início, alta depois (prompts frágeis, sem testes) | Sessão roda em modo automático, sem portão de aprovação; termos pressupõem uso individual comum; mínimo de 1 h entre execuções | Só para prototipar prompts editoriais |
| **B.** Claude Code para desenvolver + backend próprio | Alta | Alta: estado em banco, retries, idempotência sob seu controle | \~R$ 270 de infraestrutura + APIs por uso | Média: código seu, mas modular | Tempo de construção (estimo 6–10 semanas em noites e fins de semana) | Bom, mas reinventa o que um parceiro já resolve no TikTok |
| **C.** Low-code (n8n, Make, Zapier) + serviços de IA | Alta para fluxos lineares; n8n tem nó de espera por webhook | Média: aprovação por versão, invalidação e teto de custo viram emaranhado de nós | n8n auto-hospedado: só servidor; Make/Zapier: cresce por operação | Média-alta após alguns meses; versionar e testar fluxo visual é ruim | Regras de negócio ficam espalhadas e sem testes automatizados | Bom para protótipo de integração, ruim como núcleo |
| **D.** Híbrido (recomendado) | Alta | Alta no núcleo; dependências externas isoladas atrás de interfaces | R$ 320–480 fixos + APIs por uso (seção 10) | Média, com boa parte do código escrita com o Claude Code | Ainda depende de parceiro (Buffer) para TikTok e de operação manual no Bilibili | **Construir** |

**E. Modo orçamento (≤ US$ 20/mês) — o ponto de partida.** É uma versão disciplinada do caminho A: o Claude Code roda dentro do GitHub Actions com o token do Pro, e o repositório vira banco de estado e fila de aprovação. Difere do A em três pontos que resolvem as objeções da tabela:

- **Estado e aprovação com garantia:** cada episódio é uma pasta versionada no Git; aprovar é aprovar um pull request, o que fica registrado com autor, data/hora e commit. A publicação só roda a partir do branch principal, protegido por regra de branch.
- **IA só nas etapas de texto:** o Claude Code faz pesquisa, roteiro, checagem e storyboard. Montagem, QA e publicação são uma ferramenta .NET de linha de comando, determinística, chamada pelos mesmos workflows.
- **Rede e segredos sem amarras:** os runners do GitHub acessam qualquer API, e as chaves ficam em GitHub Secrets. As Scheduled Tasks da nuvem da Anthropic têm rede restrita por lista de domínios e seguem em *research preview*.

Limites honestos do modo E: o limite do Pro pode não aguentar 7 episódios por semana somados ao seu uso de desenvolvimento; o agendamento do GitHub pode atrasar alguns minutos; e o "painel" é o app do GitHub. Por isso a migração para o caminho D está prevista no plano (seção 11).

No caminho D, cada peça tem um papel só:

- **Backend próprio (.NET):** estado, fila, aprovações, custos, publicação em YouTube e Instagram, métricas.
- **Claude API (chave da Console, Termos Comerciais):** os agentes de pesquisa, roteiro, checagem e storyboard.
- **Serviços de mídia por API:** imagem, vídeo, voz, música.
- **Buffer API:** publicação no TikTok por um parceiro oficial.
- **Claude Code (sua assinatura):** escrever e manter o software; opcionalmente uma Scheduled Task semanal que abre PR com atualização de dependências. Nunca no caminho crítico de produção.

## 3. Arquitetura recomendada

São duas arquiteturas em sequência: a de partida, que cabe em US$ 20/mês e roda inteira no GitHub, e a arquitetura-alvo, com servidor próprio, para quando o orçamento crescer. Nas duas, nada crítico depende do seu computador ligado.

### 3a. Partida: modo orçamento (GitHub Actions + Claude Pro)

> (Diagrama ou gráfico no documento original: arquitetura de partida · modo orçamento.)

O Claude Code só escreve arquivos e abre PRs; quem chama APIs pagas ou publica é a `Factory.Cli`, e só depois de um PR aprovado por você.

**Componentes:**

- **Repositório privado** com uma pasta por episódio (`episodes/2026-11-10-polvo/`): `episode.json` (status, versões, hashes, custos), `dossie.md`, `afirmacoes.json`, `roteiro.md`, `storyboard.json`, `metadados.json`, `publicacoes.json`. O histórico do Git é a trilha de auditoria.
- **Skills do Claude Code** versionadas em `.claude/skills/` (pesquisar, roteirizar, checar, storyboard): são os "agentes" da seção 4.
- **Ferramenta .NET de linha de comando** (`Factory.Cli`) com os comandos `produzir`, `qa`, `publicar`, `metricas` e `validar`. Toda a parte determinística mora aqui e é reaproveitada na arquitetura-alvo.
- **Workflows do GitHub Actions:** `pauta-semanal`, `roteiro-diario`, `produzir`, `publicar` (de hora em hora) e `metricas` (diário). Cada um com `concurrency`, `timeout-minutes` e `--max-turns` para o Claude Code.
- **Serviços gratuitos:** Workers AI (imagens), Google TTS (voz), R2 (vídeos e imagens; o Git guarda só texto e hashes), APIs do YouTube e do Instagram, Buffer Free (TikTok).

**Um dia no modo orçamento:**

1. 08:30 UTC (05:30 em Brasília), `roteiro-diario` pega o próximo episódio planejado e roda o Claude Code com o token do Pro. Ele pesquisa, escreve, checa e abre um pull request "Roteiro: Polvo" com o pacote completo.
2. O app do GitHub notifica seu celular. Você lê o PR (roteiro, tabela de afirmações com fontes, storyboard) e escolhe: aprovar e fazer merge, ou comentar `@claude ajuste: …` para o Claude revisar no mesmo PR.
3. O merge dispara `produzir`: imagens, voz, legendas, render, QA. O master vai para o R2 e um segundo PR "Vídeo: Polvo" traz o link do player, o SHA-256 e o checklist.
4. Você assiste, marca o checklist e aprova esse PR. O merge define o horário de publicação.
5. `publicar` roda de hora em hora. Antes de cada upload, `Factory.Cli` consulta a API do GitHub e exige: PR mesclado, revisão **APPROVED feita pelo seu usuário** no último commit, e hash do arquivo igual ao aprovado. YouTube e Instagram via API; TikTok entra na fila do Buffer; para o Bilibili abre uma *issue* com link de download e metadados prontos.

**Detalhe que importa:** no GitHub Free, proteção de branch e *rulesets* não estão disponíveis em repositório privado (a confirmar na sua conta). Por isso a verificação de aprovação fica no código do publicador, não só na configuração do repositório. Os PRs são abertos pelo app do Claude, então você consegue aprová-los (o GitHub não deixa o autor aprovar o próprio PR).

### 3b. Arquitetura-alvo (quando o orçamento crescer)

Tudo que é crítico passa a rodar num único servidor na nuvem (monólito modular em Docker Compose), com painel próprio. Os componentes conversam pelo banco de dados e pela fila do Hangfire — sem broker de mensagens, sem microserviços. A `Factory.Cli` vira a camada de domínio do worker.

**Na nuvem (servidor único, Docker Compose):**

- **Painel web** (ASP.NET Core, Razor Pages ou Blazor Server): calendário, fila, roteiro com fontes, player, botões de aprovação, custos, erros e métricas. Login com ASP.NET Identity + segundo fator (passkey ou TOTP), atrás de proxy com TLS.
- **Endpoints de webhook** no mesmo app: botões do Telegram, links assinados de e-mail.
- **Worker** (servidor Hangfire, processo separado, mesmo código): executa cada etapa como job curto e idempotente; jobs recorrentes com fuso `America/Sao_Paulo`.
- **SQL Server Express** (container): estado dos episódios, versões, aprovações, custos, fontes, publicações, métricas e o storage do próprio Hangfire.
- **Cloudflare R2** (S3-compatível): imagens, áudio, clipes, masters e versões. Os uploads para Instagram e Buffer usam URL pré-assinada com validade curta.
- **Observabilidade:** logs estruturados (Serilog) com `episodeId` e `jobId`, health check e monitor externo que alerta no Telegram.

**Serviços externos (todos atrás de interfaces, trocáveis):** Claude API com busca e leitura web; Gemini API (imagens); fal (Kling para animação); Google Cloud TTS ou ElevenLabs (voz); ElevenLabs Music; YouTube Data API; Instagram Graph API; Buffer API (TikTok); Telegram Bot API; bases científicas abertas (Crossref, PubMed, GBIF).

**No seu computador:** Visual Studio + Claude Code para desenvolver; navegador ou celular para o painel; upload manual no Bilibili. Nada do pipeline depende dele ligado.

**Exemplo de um dia, ponta a ponta:**

1. 05:30 — job recorrente pega o próximo episódio `PLANEJADO` e enfileira Pesquisa → Checagem → Roteiro → Storyboard. Cada job grava o resultado e enfileira o próximo.
2. \~06:30 — o pacote fica `ROTEIRO_PENDENTE`; o sistema manda o resumo no Telegram e no e-mail, com link para o painel.
3. 06:50 — job de SLA confere: se o pacote não ficou pronto, alerta e oferece um episódio da reserva.
4. Você aprova (versão 3 do roteiro, hash gravado). A transação grava a aprovação e um evento na tabela *outbox*; o despachante enfileira a Produção.
5. Produção: imagens → clipes → voz → música → legendas → render → QA automático. Ao final, `VIDEO_PENDENTE` e novo aviso.
6. Você assiste e aprova o master (hash SHA-256 do arquivo). O planejador cria uma linha de publicação por plataforma com o horário escolhido.
7. No horário, cada job de publicação confere de novo se a aprovação casa com o hash do arquivo que vai subir, publica, grava ID e URL. Depois, jobs de métricas em 1 h, 24 h, 7 dias e 28 dias.

## 4. Papel de cada agente

Só sete papéis precisam de IA; todo o resto é código determinístico. Regra de ouro: **nenhum agente de IA tem credencial de publicação nem altera estado** — cada um devolve um JSON validado por schema, e só o orquestrador (código) grava e avança o episódio.

**No modo orçamento**, cada agente é uma *skill* do Claude Code executada pela GitHub Action com o token do Pro, e o "schema validado" é um arquivo JSON que `Factory.Cli validar` confere antes de o PR ser aberto. Na arquitetura-alvo, as mesmas instruções viram chamadas à Messages API. Para poupar o limite do Pro: Sonnet nas etapas de texto, Haiku nos metadados, `--max-turns` baixo e dossiê enxuto (só os trechos citados, não páginas inteiras).

**Agentes de IA (chamadas à Messages API com ferramentas; o Agent SDK não é necessário):**

| Agente | Modelo sugerido | Entrada | Saída | Ferramentas | Limites e permissões |
| --- | --- | --- | --- | --- | --- |
| Planejador de pauta (semanal) | Sonnet 5.5 | Pilares, banco de temas, publicados, resumo de métricas | 7 temas + 3 reservas, cada um com ângulo e motivo | Consulta ao banco (somente leitura) | Grava só propostas; você confirma |
| Pesquisador | Sonnet 5.5 | Tema, ângulo, perguntas | Dossiê: fontes (URL, título, autor/instituição, datas) + afirmações candidatas com trecho literal da fonte | Busca e leitura web; Crossref, PubMed, GBIF | Até 20 buscas e teto de tokens por episódio |
| Roteirista | Sonnet 5.5 (Opus 5.5 no cenário avançado) | Dossiê, guia de estilo, fórmulas narrativas variadas | Roteiro com cada frase factual marcada com o ID da afirmação; gancho; título; duração estimada | Nenhuma: **sem web**, só o dossiê | Não pode introduzir fato que não esteja no dossiê |
| Checador | Sonnet 5.5, prompt e contexto separados | Roteiro + dossiê | Tabela de afirmações: verde/amarelo/vermelho, tipo (fato, hipótese, estimativa, dramatização) | Leitura web (relê a fonte), Crossref | Vermelho bloqueia o pacote |
| Diretor de storyboard | Sonnet 5.5 | Roteiro aprovado, bíblia visual, ficha do personagem | Cenas em JSON: tempo, fala, prompt de imagem, movimento de câmera, anima ou não, notas anatômicas | Nenhuma | Teto de cenas e de segundos animados |
| Redator de metadados | Haiku 5.5 | Roteiro aprovado | Título, descrição, hashtags e texto de capa por plataforma | Nenhuma | Limites de caracteres validados por código |
| QA visual assistivo | Sonnet 5.5 (visão) | Quadros-chave + notas anatômicas | Lista de suspeitas ("polvo com 6 braços na cena 4") | Nenhuma | Só sinaliza; nunca aprova |

O **analista semanal** (Sonnet 5.5) é opcional: recebe métricas já agregadas por SQL e escreve hipóteses, sem mudar nada.

**Por que o checador não é "outra IA dizendo que parece certo":** a parte que dá prova é determinística. O código confere se a URL responde, se o trecho citado existe literalmente na página baixada, se o DOI resolve no Crossref e se números têm duas fontes independentes (domínios diferentes). O modelo só julga se a frase do roteiro diz o mesmo que o trecho — e em caso de dúvida marca amarelo para você decidir.

**Componentes determinísticos (código, sem IA):**

- **Orquestrador:** máquina de estados, transições, outbox, chaves de idempotência.
- **Clientes de mídia:** imagem, animação, voz e música; cada chamada registra custo, modelo, prompt e termos vigentes.
- **Alinhador de legendas:** usa os timestamps por caractere da ElevenLabs; com Google TTS, alinhamento forçado com faster-whisper num container Python pequeno.
- **Renderizador (FFmpeg):** movimento de câmera sobre imagens, transições, legendas ASS, mixagem e normalização de loudness.
- **QA técnico:** ffprobe (resolução, fps, codec, duração), loudness, quadros pretos ou congelados, silêncio longo, legenda fora da área segura.
- **Publicadores:** um por plataforma, com verificação de aprovação e hash antes do upload.
- **Coletor de métricas** e **controlador de custos** (livro-razão + disjuntor).

## 5. Fluxo de aprovações

O painel web é a fonte da verdade; o Telegram avisa e permite aprovar o roteiro com um toque; o e-mail é cópia de arquivo. Nenhum agente espera resposta: cada aprovação vira uma linha no banco, e essa gravação dispara o próximo job.

**No modo orçamento**, o mesmo fluxo usa pull requests no lugar do painel: o PR de roteiro é a Aprovação 1, o PR de vídeo é a Aprovação 2, e o app do GitHub no celular é o canal de aviso e de decisão. A aprovação fica gravada pelo próprio GitHub (revisor, data/hora, commit). Pedir ajuste é comentar `@claude ajuste: …`; trocar tema é fechar o PR com o rótulo `trocar-tema`. As seis camadas de garantia abaixo valem igual, com a checagem de "revisão APPROVED do seu usuário + hash" no lugar da tabela `Approval`.

> (Diagrama ou gráfico no documento original: fluxo de aprovações · 2 portões humanos.)

Os dois laços de ajuste geram uma versão nova, e a aprovação antiga deixa de valer; o publicador confere o hash de novo no momento do upload.

**Canais comparados:**

| Canal | Uso | Privacidade | Custo | Facilidade |
| --- | --- | --- | --- | --- |
| Painel web (login + 2º fator) | Leitura completa, fontes, player, aprovação do vídeo | Alta: seu servidor, seu login | Incluído na hospedagem | Boa no celular se o layout for responsivo |
| Telegram (bot privado) | Aviso das 07h e do vídeo pronto; aprovar ou pedir ajuste no roteiro | Média: conversas com bot não têm criptografia de ponta a ponta | Gratuito | Excelente: botões na própria notificação |
| E-mail | Cópia do pacote para arquivo e plano B se o Telegram falhar | Média | Desprezível nesse volume | Boa para ler, ruim para agir |

Regra de segurança do e-mail: o link **nunca aprova sozinho**. Filtros antivírus abrem links automaticamente; por isso o link leva a uma página do painel que exige sessão e um clique (POST).

**Aprovação 1 — roteiro (até 07h):**

1. O pacote chega no Telegram como resumo: tema, título, gancho, duração e contagem de afirmações verdes, amarelas e vermelhas. Botões: Aprovar, Pedir ajuste, Trocar tema, Abrir no painel.
2. Cada botão carrega um token assinado (HMAC) com episódio, versão do roteiro, ação e validade. O bot só aceita o seu `chat_id`.
3. "Pedir ajuste" abre campo de texto; o comentário volta ao Roteirista e gera a versão seguinte. A aprovação vale só para a versão exibida.
4. Aprovar grava `Approval` + evento na outbox na mesma transação; o despachante enfileira a Produção em segundos.

**Aprovação 2 — vídeo final (só no painel):**

1. O aviso traz o link do player. O botão Aprovar só habilita depois que o player registra pelo menos 95% assistidos.
2. O checklist do briefing (sincronia, anatomia, pronúncia, áudio, legendas, licenças, aviso de IA) é marcado e salvo junto.
3. A aprovação guarda usuário, data/hora, ID da versão e o SHA-256 do arquivo master.

**Como garantir que nada seja publicado sem autorização (seis camadas):**

1. **Transição:** jobs de publicação só são criados na entrada em `VIDEO_APROVADO`.
2. **Rechecagem no momento do upload:** o publicador baixa o arquivo do R2, calcula o SHA-256 e exige uma aprovação válida com o mesmo hash. Divergiu: aborta, `FALHA_PERMANENTE`, alerta.
3. **Invalidação automática:** gravar nova versão de roteiro ou master marca as aprovações anteriores como `INVALIDADA` na mesma transação.
4. **Restrição no banco:** `Publication.ApprovalId` é obrigatório e aponta para a aprovação daquela versão.
5. **Credenciais isoladas:** só o módulo publicador lê os tokens das plataformas; agentes de IA não têm acesso.
6. **Interruptor geral:** "Publicação pausada" no painel, conferido por todo publicador antes de cada upload.

**Prazo vencido:** se o roteiro não for aprovado até um horário limite (sugestão: 12h), o episódio continua `ROTEIRO_PENDENTE` e o horário do dia usa um episódio da reserva já em `VIDEO_APROVADO`. Sem reserva, o dia fica sem post. Nunca há publicação automática de algo não aprovado.

## 6. Stack sugerida

.NET 10 + Hangfire + SQL Server Express + Cloudflare R2 + FFmpeg, num servidor Hetzner de 4 vCPU/8 GB. A escolha pesa sua experiência, mas cada item também se justifica tecnicamente; onde outra opção é melhor em algum eixo, está dito.

**No modo orçamento** a stack encolhe sem jogar código fora: servidor → GitHub Actions; SQL Server → arquivos JSON versionados no Git; Hangfire → workflows com `cron`, `concurrency` e retry; painel → app do GitHub; Claude API → Claude Code Action com o token do Pro. Ficam iguais: .NET 10 (`Factory.Cli`), FFmpeg, R2, e as interfaces para cada serviço externo. A tabela abaixo descreve a arquitetura-alvo.

| Camada | Escolha | Por quê | Alternativa e quando usar |
| --- | --- | --- | --- |
| Linguagem e web | .NET 10 (ASP.NET Core), Razor Pages + htmx | Você domina; um só código para painel, webhooks e worker; [SDK oficial da Anthropic para C#](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/csharp) com suporte a `IChatClient` | Python: ecossistema de mídia mais rico; usar só num container auxiliar (alinhamento de legenda) se preciso |
| Fila e agendamento | [Hangfire](https://www.hangfire.io/pricing/) (versão Open, gratuita inclusive para uso comercial) | Jobs persistentes, retry automático, painel, jobs recorrentes com fuso horário; storage SQL Server é o oficialmente suportado | [Temporal Cloud](https://temporal.io/pricing): fluxos duráveis com sinais de aprovação nativos, sem mensalidade base; vale se os fluxos ficarem complexos, mas tem curva de aprendizado alta |
| Banco | SQL Server Express em container Linux | Gratuito, você já usa; limite de 10 GB por banco é suficiente porque a mídia fica no R2 | PostgreSQL: gasta muito menos RAM e permite um servidor menor (economia de \~R$ 100/mês); o Hangfire para PostgreSQL é pacote da comunidade |
| Arquivos | [Cloudflare R2](https://developers.cloudflare.com/r2/pricing/) | US$ 0,015/GB-mês, saída gratuita, 10 GB grátis; S3-compatível | Backblaze B2 ou Azure Blob, com a mesma interface S3 |
| Hospedagem | [Hetzner Cloud CPX32](https://www.hetzner.com/cloud/regular-performance) (4 vCPU, 8 GB, 160 GB, € 35,99/mês) na Alemanha ou Finlândia | Custo baixo e previsível; latência ao Brasil não importa para trabalho em lote | Azure (App Service + Azure SQL) se quiser serviços gerenciados e pagar mais |
| Montagem de vídeo | FFmpeg + ffprobe + legendas ASS (libass) | Determinístico, gratuito, roda no mesmo servidor | Remotion (React): legendas animadas mais ricas, mas outra stack e licença a verificar |
| Modelos de linguagem | Claude API: Sonnet 5.5, Haiku 5.5, Opus 5.5 | Bom em pesquisa com citação e escrita em português; busca e leitura web nativas | Gemini API atrás da mesma interface `IChatClient`, como plano B |
| Segredos | Variáveis de ambiente vindas de arquivo fora do Git + Docker secrets; mascaramento nos logs | Simples e suficiente para um servidor | Infisical ou Azure Key Vault ao crescer |
| Notificações | Telegram Bot API + e-mail transacional | Gratuito ou quase; botões de ação | WhatsApp Business API: pago e mais burocrático |
| Observabilidade | Serilog + Seq, painel do Hangfire (atrás do login), monitor externo de uptime | Rastrear cada job por episódio | Grafana + Loki |
| Entrega | GitHub Actions: build, testes, imagem Docker, deploy por SSH | Reprodutível; o Claude Code ajuda a manter | — |
| Backup | Backup diário do banco para bucket R2 separado e versionado + backup do servidor Hetzner | Recuperação em menos de 1 h | — |

Minha avaliação honesta sobre SQL Server vs PostgreSQL: tecnicamente o PostgreSQL é a escolha mais natural em Linux e mais barata em memória. Recomendo SQL Server porque reduz o que você precisa aprender de uma vez e o Hangfire o suporta oficialmente. Com EF Core, migrar depois é viável.

## 7. Ferramentas de conteúdo

**Abordagem visual recomendada: híbrida.** De 12 a 16 imagens 3D estilizadas por episódio, com movimento de câmera feito no FFmpeg, mais 2 a 6 clipes animados de 5 s só nos momentos de maior valor narrativo. Gerar os 60–90 s inteiros em vídeo generativo custaria de US$ 13 a 80 por episódio (US$ 0,07–0,30/s com 2–3 tentativas) e pioraria a consistência entre clipes.

**Consistência de personagem:** para cada episódio, gerar primeiro uma *ficha do personagem* com 3–4 imagens de referência aprovadas pelo QA. Todas as cenas usam essa ficha como imagem de referência (edição multi-imagem). Os clipes animados partem dessas imagens (image-to-video), nunca de texto puro. Um *prompt de estilo* fixo da marca (paleta, iluminação, lente) entra em toda geração.

| Etapa | Ferramenta recomendada | API | Uso comercial | Preço (consultado em 03/11/2026) | Custo por episódio | Limitações | Plano B |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pesquisa | [Claude API: busca e leitura web](https://platform.claude.com/docs/en/about-claude/pricing) + Crossref, PubMed, GBIF | Sim | Sim (Termos Comerciais) | Busca: US$ 10 por 1.000; leitura: só tokens | \~US$ 0,15 de buscas + tokens (seção 10) | Qualidade depende da allowlist de domínios | Gemini com busca do Google |
| Imagem | [Gemini Nano Banana 2.1](https://ai.google.dev/gemini-api/docs/pricing) | Sim | Google não reivindica a propriedade; no plano pago, prompts não treinam modelos ([termos](https://ai.google.dev/gemini-api/terms)) | US$ 0,0336 (1K), US$ 0,0504 (2K); lote pela metade | US$ 0,90–2,30 (18–46 imagens 2K com regerações) | Erros anatômicos ocasionais; texto na imagem instável | FLUX.2 ([BFL](https://bfl.ai/pricing), a partir de US$ 0,048/imagem; ler os termos da API) |
| Animação | [Kling 2.5 Turbo Pro / v3 Pro via fal](https://fal.ai/pricing) | Sim, assíncrona | Licença definida por modelo: conferir na página do modelo antes de ativar | US$ 0,07/s (2.5 Turbo Pro); US$ 0,14/s (v3 Pro) | US$ 1,40–10,50 | Clipes de 5–10 s; fila de minutos; deformações em movimento rápido | [Veo 3.1 ou Seedance 2.0 no fal](https://fal.ai/learn/tools/best-image-to-video-apis-2026) (US$ 0,20–0,30/s) |
| Voz (econômico) | [Google Cloud TTS Chirp 3 HD](https://cloud.google.com/text-to-speech/pricing), pt-BR | Sim | Sim | US$ 30 por 1 milhão de caracteres; 1 milhão grátis por mês | \~US$ 0 (≈ 4 mil caracteres/episódio cabem na faixa grátis) | Menos expressiva; legenda exige alinhamento forçado | Azure Speech: 0,5 milhão de caracteres grátis/mês e SSML de fonemas |
| Voz (qualidade) | [ElevenLabs](https://elevenlabs.io/pricing/api) | Sim, com timestamps por caractere | Só em planos pagos ([regra](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform)); plano grátis não permite uso comercial | Starter US$ 6 (75 mil caracteres); Creator US$ 22 (275 mil) | Coberto pelo plano | Use só vozes da biblioteca; nunca clone voz de pessoa real | Google Chirp 3 HD |
| Música | [ElevenLabs Music](https://elevenlabs.io/pricing/api) | Sim | A partir do Starter | US$ 0,15/min; minutos inclusos no plano | \~US$ 0 com biblioteca reutilizada | Faixas de até 5 min | Biblioteca licenciada (Epidemic Sound, Artlist) — confirmar que a licença cobre as quatro redes |
| Legendas | Texto do roteiro + timestamps do TTS → ASS (queimada) e SRT/VTT | Local | — | Gratuito | US$ 0 | Exige alinhamento forçado com Google TTS | faster-whisper |
| Montagem e QA | FFmpeg, ffprobe | Local | Licença de software livre | Gratuito | US$ 0 (CPU do servidor) | 2–6 min de render por episódio em 4 vCPU (estimativa a validar) | — |

**Substituições no modo orçamento (custo US$ 0):**

| Etapa | Ferramenta gratuita | Faixa grátis | Quanto cabe | O que se perde |
| --- | --- | --- | --- | --- |
| Imagem | [Cloudflare Workers AI](https://developers.cloudflare.com/workers-ai/platform/pricing/): FLUX.1 schnell (licença Apache 2.0) ou FLUX.2 klein 4B (licença a confirmar) | 10.000 *neurons* por dia, renovados às 00:00 UTC | Pela tabela de preços, uma imagem de 1024 px gasta \~58 *neurons* no schnell (4 passos) e \~104 no klein: cerca de 170 ou 95 imagens/dia | Menos detalhe e menos consistência de personagem que o Gemini; formato vertical exige recorte ou ampliação |
| Animação | Nenhuma: só movimento de câmera e transições no FFmpeg | — | — | Os "momentos animados" do briefing ficam para quando houver verba (\~US$ 1,40 por episódio no Kling) |
| Voz | [Google Chirp 3 HD](https://cloud.google.com/text-to-speech/pricing) | 1 milhão de caracteres/mês | \~250 episódios/mês a 4 mil caracteres | Exige conta de faturamento com cartão: configure alerta de orçamento e cota para nunca passar do grátis |
| Música | Começar sem trilha, ou só com faixas cuja licença cubra explicitamente as quatro redes | — | — | Quando sobrar verba, um mês de ElevenLabs Starter (US$ 6) gera uma biblioteca própria de \~40 min de música com uso comercial |
| LLM | Claude Code Action com o token do Pro | Limite do plano (não publicado em tokens) | A medir no piloto | Sem teto de gasto a estourar, mas o pipeline para quando o limite acaba |

Não use a biblioteca de áudio do YouTube nos vídeos que vão para as outras redes sem confirmar a licença: o briefing pede um master único e válido nas quatro plataformas.

**Pronúncia em pt-BR:** um dicionário no banco (termo → forma falada) é aplicado antes do TTS. Exemplos: "*Octopus vulgaris*" → "ócto-pus vul-gá-ris"; "10⁶" → "um milhão". Com Google e Azure use SSML (`<sub>`, `<phoneme>`); com ElevenLabs, dicionários de pronúncia. Todo termo novo de um roteiro aprovado entra numa lista para você ouvir na revisão.

**Proveniência:** cada asset grava ferramenta, modelo e versão, data, prompt, seed quando houver, link e data da leitura dos termos vigentes. Antes de ativar qualquer modelo novo, uma linha de "licença verificada" precisa existir no banco.

## 8. Integrações das quatro redes

YouTube e Instagram aceitam publicação automática na sua própria conta, sem auditoria; TikTok só por parceiro aprovado ou rascunho; Bilibili, só manual. Tudo consultado na documentação oficial em 03/11/2026.

| Rede | API oficial e status | Autorização | Limites e formato | Rótulo de IA | Automação possível | Plano B manual |
| --- | --- | --- | --- | --- | --- | --- |
| YouTube | [Data API v3 `videos.insert`](https://developers.google.com/youtube/v3/docs/videos/insert). Desde 02/11/2026, projetos não verificados **não** ficam mais presos a vídeos privados ([histórico de revisões](https://developers.google.com/youtube/v3/revision_history)) | OAuth 2.0 do seu canal num projeto Google Cloud. Publique a tela de consentimento como "em produção": em modo de teste, os tokens de atualização expiram em 7 dias | Cota própria de uploads: 100 chamadas/dia. Agendamento com `privacyStatus=private` + `publishAt` | Campo `status.containsSyntheticMedia` | **Total** | YouTube Studio no celular |
| Instagram (Reels) | [Instagram API com Login do Instagram](https://developers.facebook.com/docs/instagram-platform/content-publishing), `media_type=REELS` | Conta profissional; permissões `instagram_business_basic` e `instagram_business_content_publish`. Para usuários com papel no app, o acesso Standard é automático, sem App Review ([níveis de acesso](https://developers.facebook.com/docs/graph-api/overview/access-levels)) | 100 posts por API a cada 24 h. O vídeo precisa estar numa URL pública (URL pré-assinada do R2). [Especificação](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media): MP4/MOV, H.264, 23–60 fps, até 300 MB, 3 s a 15 min. Sem agendamento nativo: o seu job publica na hora | A Meta exige rótulo para vídeo fotorrealista ou áudio realista; "Reel narrado com voz de IA realista" é um dos exemplos. Não achei parâmetro de rótulo na API: avisar na legenda e testar no piloto | **Total** (rótulo a confirmar) | App do Instagram |
| TikTok | [Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started). Cliente sem auditoria só posta em modo privado e para até 5 usuários/24 h. As [diretrizes](https://developers.tiktok.com/doc/content-sharing-guidelines) citam como inaceitável "ferramenta para subir conteúdo nas contas que você ou sua equipe gerenciam" | App + revisão de escopo + auditoria; a auditoria tende a reprovar ferramenta interna | Rascunho na caixa de entrada (`video.upload`): até 5 pendentes/24 h e você finaliza no app | Campo `is_aigc` na postagem direta; rótulo obrigatório para conteúdo realista | **Via parceiro:** [Buffer API](https://developers.buffer.com/guides/posts-and-scheduling), parceiro oficial do TikTok, com chave pessoal; plano gratuito com 3 canais e 10 posts agendados por canal ([preços](https://buffer.com/pricing)) | Postar no app a partir do arquivo baixado |
| Bilibili | A [plataforma aberta](https://openhome.bilibili.com/) tem upload de vídeo no servidor, mas o cadastro de desenvolvedor exige licença comercial e carta oficial de empresa, e o envio de vídeo depende de lista de permissão | Inviável para pessoa física no Brasil | O app internacional relançado em 08/2026 aceita login Google sem verificação de identidade ([Semafor](https://semafor.com/article/08/19/2026/chinas-youtube-bilibili-plans-global-expansion-english-language-site)); o site chinês historicamente exigia documento de estrangeiros | A norma chinesa em vigor desde 01/09/2025 exige rótulo visível e metadado em conteúdo gerado por IA ([CAC](https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm)) | **Nenhuma** pela via oficial | Upload manual guiado por uma *issue* com arquivo e metadados prontos (\~5 min) |

**Recomendação para o Bilibili:** deixar para a fase 4. O público é majoritariamente chinês, a narração é em português e a monetização para criadores estrangeiros ainda não está documentada. Valide primeiro com 10 uploads manuais se há audiência.

**Sobre o Buffer para TikTok:** é o caminho oficial que sobra, mas confirme no piloto (a) se o post sai direto ou vira notificação para finalizar no app e (b) se dá para marcar "conteúdo gerado por IA". Se algum dos dois falhar, o TikTok vira etapa manual de 2 minutos.

**Publicação sem duplicidade:**

- Cada publicação tem uma chave de idempotência `episódio + plataforma + hash do master` e um estado próprio: `AGENDADA → ENVIANDO → PUBLICADA` ou `FALHOU`.
- Antes de qualquer nova tentativa a partir de `ENVIANDO`, o publicador consulta a plataforma pelo ID salvo (YouTube: vídeo; Instagram: contêiner de mídia; Buffer: post). Só reenvia se confirmar que nada saiu.
- A descrição leva um código curto do episódio no fim (ex.: `#ep0142`), que permite achar o post se o ID se perder.

**Horário de publicação:** não existe horário universal. Comece com dois horários alternados por semana (ex.: 12h e 19h) e, depois de 4 semanas, compare retenção e alcance nas primeiras 24 h de cada faixa. O YouTube Studio e o Instagram mostram quando o seu público está online — use esses dados, não listas genéricas.

## 9. Modelo de dados e máquina de estados

Dezessete tabelas cobrem tudo que o briefing pede. A mudança principal em relação à máquina proposta: **falha é estado da etapa, não do episódio** — o episódio fica parado onde estava, com a etapa marcada como falha, em vez de "perder" a posição no fluxo. No modo orçamento, as mesmas entidades viram campos do `episode.json` e arquivos da pasta do episódio.

| Tabela | Campos essenciais | Para quê |
| --- | --- | --- |
| `Topic` | pilar, assunto, subtema, chave normalizada (única), status (ideia, reserva, usado) | Banco de pautas e detecção de repetição |
| `Episode` | código (`ep0142`), tema, data planejada, status, versão atual de roteiro e master, teto de custo, `rowversion` | Agregado principal |
| `StageRun` | etapa, tentativa, status (rodando, ok, falha temporária, falha permanente), chave de idempotência, modelo, tokens, custo, erro, início e fim | Logs, retries e observabilidade |
| `Source` | URL, título, autor/instituição, data de publicação, data de acesso, DOI, tipo, hash e cópia da página no R2 | Fontes auditáveis |
| `Claim` | texto, tipo (fato, hipótese, estimativa, opinião, dramatização), status (verde, amarelo, vermelho) | Afirmações do roteiro |
| `ClaimSource` | afirmação, fonte, trecho literal, trecho encontrado (sim/não), relação (sustenta, contradiz, parcial) | Ligação afirmação ↔ fonte |
| `ScriptVersion` | nº da versão, texto, gancho, título, duração estimada, SHA-256, autor, versão anterior, motivo | Histórico do roteiro |
| `Scene` | ordem, início/fim, fala, prompt de imagem, movimento de câmera, anima (sim/não), notas anatômicas | Storyboard |
| `MediaAsset` | tipo (imagem, clipe, voz, música, legenda, master, derivado, capa), versão, chave no R2, SHA-256, duração, resolução, ferramenta, modelo, prompt, seed, licença, custo, substitui | Arquivos e proveniência |
| `LicenseRecord` | ferramenta, URL dos termos, data da leitura, uso comercial, atribuição exigida | Prova de licença |
| `Approval` | tipo (roteiro, vídeo), alvo, SHA-256 do alvo, decisão, comentário, checklist, usuário, data/hora, canal, válida/invalidada | Aprovações vinculadas à versão |
| `Publication` | plataforma, aprovação (obrigatória), arquivo, chave de idempotência (única), horário, status, ID e URL na plataforma, tentativas, último erro | Publicação por rede |
| `PlatformMetric` | publicação, janela (1 h, 24 h, 7 d, 28 d), visualizações, alcance, retenção, curtidas, comentários, compartilhamentos, salvamentos, seguidores ganhos, JSON bruto | Métricas comparadas por janela |
| `CostLedger` + `Budget` | fornecedor, unidades, preço unitário, custo; teto mensal e por episódio | Controle de gasto |
| `AuditEvent` + `OutboxEvent` | entidade, ação, antes/depois, autor; eventos a despachar | Auditoria e disparo confiável de jobs |

> (Diagrama ou gráfico no documento original: máquina de estados do episódio · 14 estados no caminho principal.)

No código, os estados usam os nomes do briefing (`ROTEIRO_PENDENTE`, `VIDEO_APROVADO`…); `PRONTO_PARA_PUBLICAR` foi absorvido por `VIDEO_APROVADO`, que funciona como a reserva.

**Regras de transição:**

1. Toda mudança de status passa por um único método, que consulta a tabela de transições permitidas e usa concorrência otimista (`rowversion`). Qualquer outra transição é erro.
2. Entrar em `ROTEIRO_PENDENTE` exige zero afirmações vermelhas e toda frase factual ligada a uma afirmação.
3. Nova versão de roteiro depois de aprovado: invalida a aprovação, cancela jobs de produção em andamento e volta para `ROTEIRO_PENDENTE`.
4. Novo master: invalida a aprovação de vídeo, cancela publicações ainda não enviadas e volta para `VIDEO_PENDENTE`.
5. `Publication` só é criada com aprovação de vídeo válida cujo hash é igual ao do arquivo.
6. Antes de cada etapa paga: gasto do mês + estimativa da etapa acima do teto → episódio `BLOQUEADO` (motivo: custo) e alerta.
7. `VIDEO_APROVADO` é a reserva: episódios prontos esperando um horário. A meta de 5 em reserva é uma contagem desse status.
8. Falha temporária repete com espera crescente (1, 5, 15 min, até 3 vezes); depois vira falha permanente da etapa e o episódio fica `BLOQUEADO` até você decidir.

## 10. Estimativa de custos

No modo orçamento o custo é fixo: **US$ 20/mês (cerca de R$ 106), só o Claude Pro**, em qualquer volume — desde que o limite do Pro aguente. Com backend próprio e serviços pagos, vai de cerca de R$ 560 a R$ 3.150/mês conforme volume e qualidade. São estimativas com premissas explícitas; o piloto deve medir o custo real por episódio.

> (Diagrama ou gráfico no documento original: cálculo próprio com os preços e premissas desta seção · R$/mês.)

No modo orçamento, o volume não muda o custo, mas muda o risco de bater o limite do Pro; nos outros cenários, a animação é o que mais pesa.

**Premissas:**

- **Câmbio efetivo:** US$ 1 = R$ 5,30 (cotação perto de R$ 5,01 em 07/10/2026, mais IOF de cartão e spread); € 1 = R$ 6,25 (média PTAX de setembro/2026 em R$ 5,95, mais as mesmas taxas).
- **Volume:** 3, 5 e 7 por semana = 13, 22 e 30 episódios por mês.
- **Episódio:** 75 s em média, roteiro de \~1.300 caracteres; com regerações, \~4.000 caracteres de voz.
- **LLM (cenários pagos):** \~300 mil tokens de entrada e \~30 mil de saída por episódio somando pesquisa, checagem, roteiro, storyboard e metadados, mais \~15 buscas. Sonnet 5.5 custa US$ 2/US$ 10 por milhão de tokens e Opus 5.5, US$ 4/US$ 20 ([preços](https://platform.claude.com/docs/en/about-claude/pricing)). Planejamento e relatório semanais: \~US$ 8,70/mês.
- **GitHub Actions (modo orçamento):** \~35 min de runner por episódio → \~1.050 min/mês em 7/semana, dentro dos \~2.000 inclusos.

**Custo variável por episódio (cenários pagos):**

| Item | Econômico | Intermediário | Avançado |
| --- | --- | --- | --- |
| Cenas e regerações | 12 cenas, ×1,5 | 14 cenas + ficha do personagem, ×2 | 16 cenas + ficha, ×2,5 |
| Clipes animados | 2 × 5 s, 2 tentativas (Kling 2.5 Turbo) | 4 × 5 s, 2 tentativas (Kling 2.5 Turbo) | 6 × 5 s, 2,5 tentativas (Kling v3 Pro) |
| LLM | US$ 1,20 (Sonnet) | US$ 2,00 (Sonnet, mais passadas) | US$ 4,00 (Opus) |
| Imagens (Gemini 2K, US$ 0,0504) | US$ 0,91 | US$ 1,60 | US$ 2,30 |
| Animação | US$ 1,40 | US$ 2,80 | US$ 10,50 |
| Voz e música | US$ 0 (Google grátis; biblioteca própria) | Coberto pelo plano ElevenLabs | Coberto pelo plano ElevenLabs |
| **Total por episódio** | **US$ 3,51 (R$ 18,60)** | **US$ 6,40 (R$ 33,90)** | **US$ 16,80 (R$ 89,00)** |

**Custos fixos mensais (R$):**

| Item | Orçamento | Econômico | Intermediário | Avançado |
| --- | --- | --- | --- | --- |
| Claude (assinatura de desenvolvimento) | 106 (Pro, é o próprio motor) | 106 (Pro, só desenvolvimento; fora da soma) | 106 (fora da soma) | 106 (fora da soma) |
| Servidor Hetzner CPX32 + backup (+20%) | 0 (GitHub Actions) | 270 | 270 | 270 |
| Cloudflare R2 | 0 (10 GB grátis) | 0 | 10 | 20 |
| ElevenLabs Creator (voz + música) | 0 | 0 | 117 | 117 |
| Buffer Essentials (1 canal TikTok) | 0 (plano grátis) | 0 (plano grátis) | 27 | 27 |
| LLM de planejamento e relatório | 0 (no Pro) | 46 | 46 | 46 |
| Domínio | 0 | 4 | 4 | 4 |
| **Total fixo** | **106** | **320** | **474** | **484** |

APIs do YouTube, do Instagram e do Telegram não cobram. Nos cenários pagos, a assinatura Pro fica fora da soma porque você já a usa para desenvolver.

**Tetos sugeridos (configuráveis no `Budget`):**

| Cenário | Teto por episódio | Teto mensal |
| --- | --- | --- |
| Orçamento | US$ 0 em serviços pagos (cotas zeradas no Google e na Cloudflare) | US$ 20 |
| Econômico | US$ 5 | R$ 900 |
| Intermediário | US$ 8 | R$ 1.600 |
| Avançado | US$ 20 | R$ 3.300 |

**Primeiro upgrade com melhor retorno quando houver verba:** imagens no Gemini (\~US$ 1 por episódio, R$ 70–160/mês conforme volume). É o item que mais muda a qualidade percebida. Depois, 2 clipes animados por episódio (\~US$ 1,40). O servidor próprio só se paga quando o GitHub virar gargalo.

**Max x Pro:** o Max (US$ 100) inclui US$ 100/mês de crédito de API ([detalhes](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)) e 5× o uso do Pro. Em 7/semana no cenário intermediário, o LLM custaria \~US$ 69/mês de API. Logo, o Max só compensa quando o orçamento total passar de \~US$ 100.

## 11. Plano de MVP

Seis fases curtas em sequência, cada uma com um portão mensurável; só avance quando o portão passar. As fases 0 a 4 cabem nos US$ 20; a fase 5 só acontece se os dados justificarem gastar mais. Prazos supondo noites e fins de semana.

1. **Fase 0 — Calibrar à mão (1 semana).** Criar contas (canal do YouTube, Instagram profissional, TikTok, Buffer, projeto Google Cloud com alerta de orçamento, Cloudflare). Fazer 1 episódio inteiro no Claude Code local, rodando cada etapa manualmente, para afinar prompts e a bíblia visual. Registrar as licenças.
   - Portão: um vídeo que você publicaria; tempo e consumo do Pro anotados.
2. **Fase 1 — Roteiro automático (2–3 semanas).** Skills de pesquisa, roteiro e checagem; `Factory.Cli validar`; workflow `roteiro-diario` abrindo PR.
   - Portão: 10 pacotes gerados; pelo menos 7 aprovados com no máximo um ajuste; auditoria manual de 3 roteiros sem nenhum fato sem fonte; consumo do Pro por episódio medido em `/usage`.
3. **Fase 2 — Produção automática (2–3 semanas).** Imagens, voz, legendas, render e QA técnico; PR de vídeo com player e checklist.
   - Portão: 6 vídeos aprovados; render abaixo de 15 min; no máximo uma correção por vídeo; zero falha de QA técnico chegando até você.
4. **Fase 3 — Publicação (2 semanas).** YouTube e Instagram por API, TikTok pelo Buffer, métricas diárias. Ritmo de 3 por semana.
   - Portão: 4 semanas sem duplicidade nem publicação indevida; os testes negativos abaixo passando.
5. **Fase 4 — Escala (4+ semanas).** Subir para 5 e depois 7 por semana; formar a reserva de 5 episódios; testar o Bilibili com 10 uploads manuais.
   - Portão: o Pro aguenta o ritmo sem bloquear seu uso de desenvolvimento; seu tempo semanal fica abaixo de 4 h; métricas mostram algum formato vencedor.
6. **Fase 5 — Investir (quando os dados pedirem).** Primeiro imagens no Gemini, depois clipes animados, por fim a migração para a arquitetura-alvo (servidor, banco, painel).
   - Gatilhos: limite do Pro batendo toda semana, minutos do GitHub acima de 80%, ou a necessidade de um painel de verdade.

**Testes obrigatórios antes de ligar a publicação:**

- Alterar o master depois da aprovação → publicação bloqueada.
- Aprovação feita por outro usuário, ou PR mesclado sem revisão → bloqueada.
- Derrubar o job no meio do upload e reexecutar → nenhum post duplicado.
- Esgotar a cota de imagens ou o limite do Pro → episódio para com alerta, sem cobrança.
- Token de plataforma expirado → alerta e fila preservada.
- Restaurar o estado a partir do backup (Git e R2) num repositório novo.

## 12. Riscos e pontos de atenção

Os três riscos que mais podem matar o projeto não são técnicos: perder a monetização por "conteúdo inautêntico", errar um fato que viraliza e depender de um limite de assinatura que a Anthropic pode mudar. Os demais têm prevenção e recuperação simples.

| Risco | Prevenção | Detecção | Recuperação e plano B |
| --- | --- | --- | --- |
| Conteúdo tratado como inautêntico ([política do YouTube](https://support.google.com/youtube/answer/1311392?hl=en): vale para o canal inteiro) | Variar estrutura narrativa, personagem e ritmo; revisão humana real; nada de template idêntico | Queda brusca de alcance; aviso do YouTube Studio | Reduzir cadência, revisar o formato e pedir nova análise |
| Fato errado ou sem fonte | Roteirista sem web; checador com trecho literal; 2 fontes para números; vermelho bloqueia | Tabela de afirmações no pacote; comentários do público | Correção fixada nos comentários; editar ou remover o vídeo; registrar a falha no checador |
| Imagem biologicamente errada | Notas anatômicas por cena; ficha do personagem | QA visual assistivo + sua revisão | Regerar só a cena (novo master → nova aprovação) |
| Personagem inconsistente | Ficha de referência, prompt de estilo fixo, mesma seed quando possível | QA visual compara com a ficha | Regerar cenas fora do padrão |
| Pronúncia ruim | Dicionário de pronúncia; termos novos destacados na revisão | Sua escuta | Corrigir o dicionário e regerar só a voz |
| Rótulo de IA ausente | Regra por plataforma no publicador; aviso fixo na descrição | Checklist da aprovação 2 | Editar o post e marcar o rótulo |
| Licença ambígua | `LicenseRecord` obrigatório antes de ativar um modelo | Publicador recusa asset sem licença | Trocar o asset por um de fonte licenciada |
| API de rede social indisponível ou não aprovada | Buffer para TikTok; publicação manual documentada | Erro do publicador → alerta | Baixar o master e publicar à mão |
| Publicação duplicada | Chave de idempotência; consulta pelo ID antes de reenviar | Código `#epNNNN` repetido no canal | Apagar o duplicado; corrigir o publicador |
| Render falho ou arquivo corrompido | ffprobe + verificação de hash após upload no R2 | QA técnico | Rerender automático (até 2 vezes) |
| Pacote das 07h atrasado | Início às 05:30; job de SLA às 06:50 | Alerta | Usar episódio da reserva |
| Agente em loop consumindo cota | `--max-turns`, `timeout-minutes`, teto de tokens e de buscas | Custo ou duração acima do normal | Job morto pelo timeout; etapa marcada como falha |
| Estado perdido após reinício | Estado sempre no Git ou no banco, nunca na memória do job | — | Jobs idempotentes retomam da última etapa concluída |
| Vazamento de chaves | GitHub Secrets / variáveis fora do Git; varredura de segredos no repositório; escopo mínimo em cada token | Alerta do GitHub de segredo exposto | Revogar e rotacionar; checar uso indevido |
| Mudança nos limites ou termos do Pro | Não otimizar além do necessário; interface `ILlm` trocável | Bloqueio por limite; anúncios da Anthropic | Plano B: API paga com teto, ou Gemini em faixa grátis para tarefas simples |
| Fornecedor de mídia fora do ar | Interfaces por serviço; um segundo provedor já testado | Erros seguidos do mesmo fornecedor | Trocar por configuração |
| Cobrança surpresa em faixa grátis | Alertas de orçamento e cotas zeradas no Google Cloud e na Cloudflare | Alerta de faturamento | Desativar a chave |

**Outros pontos de atenção:**

- **Termos do Pro:** a automação é sua, para conteúdo seu, pelo binário oficial — isso está dentro do que a Anthropic documenta. Mas os termos lembram que os limites pressupõem uso individual comum e que podem ser aplicados sem aviso. Não revenda nem compartilhe esse pipeline com terceiros usando a sua assinatura.
- **Privacidade:** o pipeline não coleta dados de espectadores; métricas agregadas das plataformas não identificam pessoas. Mantenha assim.
- **Saúde:** temas do corpo humano com aviso fixo de caráter educativo; o checador recusa qualquer recomendação individual de tratamento.
- **Monetização:** o YouTube exige 1.000 inscritos e 10 milhões de visualizações válidas de Shorts em 90 dias (ou 4.000 horas de exibição em vídeos longos) ([requisitos](https://support.google.com/youtube/answer/72851?hl=en)). Trate receita como hipótese, não como premissa.

## 13. Perguntas em aberto

Só o que depende de você; para cada uma, a premissa que adotei até você responder.

- [ ] **Claude Pro:** já está ativo, e você aceita dividir o limite entre desenvolvimento e produção? *Premissa: sim; nos dias de desenvolvimento pesado, a produção pode atrasar.*
- [ ] **Repositório privado ou público?** Público dá proteção de branch e minutos ilimitados de graça, mas expõe roteiros antes de publicar. *Premissa: privado, com a checagem de aprovação no código.*
- [ ] **Titularidade das contas:** pessoa física ou MEI/CNPJ? Afeta recebimento de monetização e impostos (consulte um contador). *Premissa: pessoa física no piloto.*
- [ ] **Cartão nas faixas gratuitas:** Google Cloud e Cloudflare podem exigir forma de pagamento mesmo sem cobrar. Você aceita cadastrar, com alertas e cotas zeradas? *Premissa: sim.*
- [ ] **Público infantil:** o YouTube exige declarar se o vídeo é "feito para crianças", o que limita comentários e anúncios. Conteúdo de animais tende a atrair crianças. *Premissa: público geral (13+), linguagem acessível, e você decide caso a caso.*
- [ ] **Música:** começar sem trilha ou gastar US$ 6 uma única vez para criar uma biblioteca? *Premissa: sem trilha no primeiro mês.*
- [ ] **Voz:** gênero e estilo da voz da marca, escolhidos entre as vozes pt-BR do Chirp 3 HD. *Premissa: você ouve 5 opções na fase 0.*
- [ ] **Prazo da aprovação do roteiro:** até que horas, e dia sem reserva fica sem post? *Premissa: 12h, e sim, fica sem post.*
- [ ] **Bilibili:** adiar para a fase 4? *Premissa: sim.*
- [ ] **Nome da marca:** necessário antes de criar as contas na fase 0.

## 14. Decisão final

**Construa primeiro o modo orçamento: um repositório no GitHub com skills do Claude Code rodando pela GitHub Action com o seu Pro, mais uma ferramenta .NET (`Factory.Cli`) para validar, produzir e publicar.** Isso cabe nos US$ 20, preserva as duas aprovações com garantia técnica e gera código que será reaproveitado quando houver um servidor próprio.

**Ordem de construção:**

1. Um episódio feito à mão no Claude Code local, para calibrar prompts, estilo visual e voz.
2. Skills de pesquisa, roteiro e checagem + `Factory.Cli validar` + workflow que abre o PR de roteiro.
3. `Factory.Cli produzir`: imagens (Workers AI), voz (Google), legendas, render FFmpeg, QA técnico, PR de vídeo.
4. `Factory.Cli publicar`: YouTube e Instagram por API, TikTok pelo Buffer, com a checagem de aprovação + hash e os testes negativos.
5. Métricas diárias num arquivo CSV no repositório; você analisa com o Claude no fim de semana.

**Não construa ainda:**

- Servidor próprio, painel web, SQL Server e Hangfire: só na fase 5, quando um gatilho da seção 11 disparar.
- Animação generativa e imagens pagas: primeiro prove que o formato retém público.
- Automação do Bilibili (não há via oficial para pessoa física) e auditoria própria no TikTok (as diretrizes vetam ferramenta interna).
- Temporal, n8n ou Scheduled Tasks da nuvem como motor do pipeline.
- Analista automático de métricas, vídeos longos e outros idiomas: depois de 2 meses de dados.

O que você precisa resolver para começar a fase 0: o nome da marca e as respostas da seção 13.

## Fontes

Todas consultadas em 03/11/2026.

**Anthropic / Claude**

- [Claude Code — Scheduled tasks (antes "routines")](https://code.claude.com/docs/en/routines)
- [Claude Code GitHub Actions](https://code.claude.com/docs/en/github-actions)
- [Claude Code — Legal and compliance](https://code.claude.com/docs/en/legal-and-compliance)
- [Use the Claude Agent SDK with your Claude plan](https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan)
- [API credits for Max and Team plans](https://platform.claude.com/docs/en/about-claude/api-credits-for-subscribers)
- [Preços da Claude API](https://platform.claude.com/docs/en/about-claude/pricing) · [Planos Claude](https://claude.com/pricing)
- [SDK oficial C#](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/csharp)

**Plataformas**

- [YouTube `videos.insert`](https://developers.google.com/youtube/v3/docs/videos/insert) · [Histórico de revisões da API](https://developers.google.com/youtube/v3/revision_history)
- [YouTube — política de monetização e conteúdo inautêntico](https://support.google.com/youtube/answer/1311392?hl=en) · [Requisitos do YPP](https://support.google.com/youtube/answer/72851?hl=en)
- [Instagram — Content Publishing](https://developers.facebook.com/docs/instagram-platform/content-publishing) · [Especificações de mídia](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media) · [Níveis de acesso Meta](https://developers.facebook.com/docs/graph-api/overview/access-levels)
- [TikTok Content Posting API](https://developers.tiktok.com/doc/content-posting-api-get-started) · [Direct Post](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) · [Upload para rascunho](https://developers.tiktok.com/doc/content-posting-api-reference-upload-video) · [Content Sharing Guidelines](https://developers.tiktok.com/doc/content-sharing-guidelines)
- [Buffer API — Posts & Scheduling](https://developers.buffer.com/guides/posts-and-scheduling) · [Preços do Buffer](https://buffer.com/pricing)
- [Bilibili — plataforma aberta](https://openhome.bilibili.com/) (documentação espelhada em [apifox](https://apifox.com/apidoc/docs-site/1106400)) · [Semafor sobre a expansão internacional](https://semafor.com/article/08/19/2026/chinas-youtube-bilibili-plans-global-expansion-english-language-site) · [CAC — norma de rótulo de conteúdo gerado por IA](https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm)

**Mídia e infraestrutura**

- [Gemini API — preços](https://ai.google.dev/gemini-api/docs/pricing) · [Termos da Gemini API](https://ai.google.dev/gemini-api/terms)
- [fal — preços](https://fal.ai/pricing) · [Black Forest Labs — preços](https://bfl.ai/pricing)
- [Cloudflare Workers AI — preços](https://developers.cloudflare.com/workers-ai/platform/pricing/) · [Cloudflare R2 — preços](https://developers.cloudflare.com/r2/pricing/)
- [Google Cloud Text-to-Speech — preços](https://cloud.google.com/text-to-speech/pricing)
- [ElevenLabs — preços de API](https://elevenlabs.io/pricing/api) · [ElevenLabs — uso comercial](https://elevenlabs.io/docs/help-center/legal/can-i-publish-the-content-i-generate-on-the-platform)
- [GitHub Actions — cobrança](https://docs.github.com/en/billing/concepts/product-billing/github-actions)
- [Hetzner Cloud](https://www.hetzner.com/cloud/regular-performance) · [Hangfire — licenças](https://www.hangfire.io/pricing/) · [Temporal — preços](https://temporal.io/pricing)
- Câmbio: [Suno (USD/BRL, 07/10/2026)](https://www.suno.com.br/analitica/moedas) · [Numerando (EUR/BRL PTAX 2026)](https://www.numerando.com.br/indices/euro/2026)
