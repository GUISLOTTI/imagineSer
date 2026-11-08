# Registro de decisões (ADRs)

Formato: cada decisão tem número, data, status (Proposta, Aceita, Substituída), contexto curto, decisão e
consequências. Para mudar uma decisão aceita, crie um ADR novo que a substitua; não edite o antigo.

---

## ADR-0001 — Teto de US$ 20/mês com o Claude Pro como motor
- **Data:** 2026-11-04 · **Status:** Aceita
- **Contexto:** o proprietário quer gastar no máximo US$ 20/mês no início e já paga o Claude Pro.
- **Decisão:** nenhuma API paga no MVP (Claude API, Gemini, geração audiovisual). O Claude Code roda no GitHub
  Actions pela Action oficial, autenticado com `CLAUDE_CODE_OAUTH_TOKEN` do Pro (uso documentado pela Anthropic).
  Créditos de uso extra do Claude ficam desligados.
- **Consequências:** o limite do Pro (janela de 5 h + semanal, não publicado em tokens) é compartilhado com o
  desenvolvimento e pode limitar a cadência; medir toda semana. Termos: o token da assinatura só pode ser usado pelo
  binário oficial do Claude Code, nunca para chamar a API diretamente.

## ADR-0002 — Modo orçamento: GitHub Actions + Git como estado
- **Data:** 2026-11-04 · **Status:** Aceita
- **Decisão:** sem servidor próprio. Workflows do GitHub Actions orquestram; cada episódio é uma pasta versionada;
  aprovações são revisões de PR. Repositório privado no GitHub Free, sem forma de pagamento cadastrada.
- **Consequências:** ~2.000 min/mês de Actions; sem branches protegidos (só em repo público no plano Free), então
  o portão de aprovação fica no código. A arquitetura-alvo com servidor (docs/02) só quando houver orçamento.

## ADR-0003 — Publicação pelo Buffer Free nas três redes
- **Data:** 2026-11-04 · **Status:** Aceita
- **Decisão:** YouTube, Instagram e TikTok via API do Buffer (GraphQL, chave pessoal), com `isAiGenerated = true`.
  O post é criado logo após a aprovação do vídeo, já com o horário, e URL pré-assinada do R2 válida por 72 h
  (o Buffer baixa a mídia na hora de publicar, não ao criar o post).
- **Consequências:** ponto único de falha; API em beta. Plano B: API direta do YouTube (fase 4) e runbook manual.
  A API direta do TikTok não é viável para ferramenta própria (diretrizes de compartilhamento).

## ADR-0004 — Duas aprovações verificadas no código do publicador
- **Data:** 2026-11-04 · **Status:** Aceita
- **Decisão:** `publicar` exige PR de roteiro e PR de vídeo mesclados, com revisão APPROVED de `OWNER_LOGIN` no
  último commit, encadeamento roteiro→vídeo, SHA-256 do master igual ao aprovado e `PUBLICACAO_ATIVA=true`.
- **Consequências:** testes negativos obrigatórios antes de ligar a publicação (docs/06).

## ADR-0005 — Imagens no Cloudflare Workers AI (plano Workers Free)
- **Data:** 2026-11-04 · **Status:** Proposta (modelo a definir pela bancada, docs/05)
- **Decisão:** candidatos FLUX.1 schnell e FLUX.2 klein 4B (Apache 2.0). FLUX.2 dev e klein 9B excluídos
  (licença não comercial). Nunca assinar Workers Paid.
- **Consequências:** franquia de 10.000 neurons/dia; consumo real por imagem desconhecido (faixa estimada de
  58 a 326 neurons) até o teste T1. Orçamento por episódio, com fila diária de até 8.000 neurons.

## ADR-0006 — Voz no Google Cloud TTS Chirp 3 HD
- **Data:** 2026-11-04 · **Status:** Aceita, com controles (cota ajustada pelo ADR-0013)
- **Decisão:** projeto Google Cloud isolado; contador próprio de 800 mil caracteres/mês e 12 mil por episódio;
  orçamento de US$ 1 com corte de faturamento por função; autenticação por OIDC, sem chave.
- **Consequências:** exige cartão; pior caso estimado de ~US$ 6 se um bug passar pelo contador.

## ADR-0007 — Duração
- **Data:** 2026-11-04 · **Status:** Substituída pelo ADR-0012
- **Decisão:** padrão 30–90 s, alvo 45–70 s, teto absoluto 120 s (validado por código).

## ADR-0008 — Sem vídeo generativo e sem música no MVP
- **Data:** 2026-11-04 · **Status:** Aceita
- **Decisão:** visual 2.5D a partir de imagens (movimento de câmera, paralaxe, micro-animação, troca de pose,
  overlays por script); áudio = narração + efeitos sintetizados por script.

## ADR-0009 — Bilibili fora do escopo
- **Data:** 2026-11-04 · **Status:** Aceita
- **Decisão:** conta não criada; a plataforma aberta exige empresa com licença chinesa. Reavaliar depois do MVP.

## ADR-0010 — Objetivo e modo de trabalho
- **Data:** 2026-11-07 · **Status:** Aceita
- **Contexto:** o projeto é renda extra. O Gabriel trabalha em horário comercial e não quer trabalho ativo depois do
  expediente; pediu autonomia ao Claude e nenhuma complexidade desnecessária.
- **Decisão:** o Gabriel só aprova ou nega roteiros e vídeos. O tempo dele é a métrica principal (alvo: ≤ 30
  min/semana em 3 episódios). O Claude decide sozinho o que for óbvio ou bem fundamentado, registra em ADR e avisa
  em uma linha; só escala dinheiro/cartão, contas e marca, a rotina de aprovação, risco legal ou de política das
  plataformas e ações irreversíveis. Boas práticas desde o início, sem complexidade que nenhum problema real peça.
- **Consequências:** saem as tarefas manuais recorrentes do plano (ADR-0013). Receita é hipótese: depende de
  limiares de monetização (ADR-0012) e leva meses; o desenho reduz ao mínimo o custo de tentar.

## ADR-0011 — Aprovação por estoque, sem prazos
- **Data:** 2026-11-07 · **Status:** Aceita · Substitui o cronograma de `docs/01` §9 e o PR de pauta.
- **Contexto:** o cronograma por episódio (roteiro até 12h de D-2, vídeo até 22h de D-1) cai em horário comercial e
  pede atenção diária. Além disso, o PR de pauta de sábado só seria aprovado depois do roteiro de domingo, 05:30.
- **Decisão:**
  - Sábado 05:30 (Brasília), o workflow `roteiro` escolhe os temas (skill `pauta-semanal`, sem PR próprio) e abre
    PRs de roteiro até cobrir os 3 horários da semana seguinte + 1 reserva.
  - Aprovar = seguir. Pedir mudanças com comentário = o Claude ajusta no mesmo PR. Fechar sem merge = descartar; o
    próximo tema vira roteiro automaticamente.
  - Roteiro aprovado → `produzir` → PR de vídeo. Vídeo aprovado → `publicar` agenda no próximo horário livre (ter,
    qui, sáb; 12h e 19h alternados nas 4 primeiras semanas).
  - Não há prazo. Horário sem vídeo aprovado fica vazio; nada é publicado sem as duas aprovações.
  - Meta: uma ação por PR, pelo app do GitHub no celular.
- **Consequências:** o workflow `pauta-semanal` deixa de existir (6 workflows). O fluxo exato aprovar → mesclar e a
  validade da URL do R2 para horários distantes ficam para as Fases 1 e 3.

## ADR-0012 — Duração acima de 1 minuto
- **Data:** 2026-11-07 · **Status:** Aceita · Substitui o ADR-0007.
- **Contexto:** o objetivo é receita. Segundo guias de terceiros consultados em 07/11/2026 (a página oficial do
  TikTok não carregou; confirmar no TikTok Studio), o Creator Rewards do TikTok só conta vídeos de mais de 1 minuto,
  exige 10 mil seguidores e 100 mil visualizações em 30 dias, e o Brasil aparece na lista de países. Os Shorts entram
  no YPP com 1.000 inscritos e 10 milhões de visualizações válidas em 90 dias
  ([YouTube](https://support.google.com/youtube/answer/72851)). O briefing original já preferia 60–90 s.
- **Decisão:** padrão 61–90 s, alvo 62–75 s. Abaixo de 61 s só como exceção justificada no PR de roteiro; teto
  absoluto de 120 s, validado por código.
- **Consequências:** cerca de 10–12 imagens únicas por episódio em vez de 8–10; o T1 confirma se cabe em ≤ 1,2 dia
  de franquia. Continua valendo comparar a retenção por faixa de duração após 4 semanas.

## ADR-0013 — Simplificações e ajustes operacionais
- **Data:** 2026-11-07 · **Status:** Aceita · Altera trechos de `docs/01` (§4, §6, §7, §9, §10).
- **Decisão:**
  1. **Buffer:** `publicar` e `reconciliar` recebem a chave (o `reconciliar` precisa ler o status dos posts).
  2. **Cron:** só `roteiro` (semanal, sábado 05:30) e `reconciliar` (07h, 15h, 23h). O das 23h (02:00 UTC, depois
     da renovação da franquia às 00:00 UTC) retoma a fila de imagens; sai o cron das 00:05 UTC do `produzir`.
  3. **Sem tarefas manuais recorrentes:** nada de planilha semanal de métricas nem anotação do uso do Pro. O Claude
     calcula o que der pelo repositório (aprovações, minutos, neurons, caracteres); as métricas de audiência ficam
     automáticas pela API do YouTube na Fase 4.
  4. **Google:** a cota de requisições por minuto é dimensionada para que cota × `timeout-minutes` do job ×
     tamanho máximo da requisição fique abaixo de 200 mil caracteres. Só assim o "pior caso de ~US$ 6" vale mesmo
     com um bug que fure o contador. A função de corte de faturamento entra na Fase 2, quando a voz passa a rodar
     sozinha; o teste de vozes da Fase 0 tem poucas chamadas manuais.
  5. **Segredos no PC:** `.gitignore` + hook (agora também no PowerShell) bastam; `gitleaks` vira opcional.
  6. **CI:** PRs abertos pelo bot com o `GITHUB_TOKEN` não disparam outros workflows; por isso o `validar` roda dentro
     do próprio job que gera os arquivos, e o `ci` cobre só mudanças de código.
  7. **Post manual pelo Buffer:** só o Gabriel, como contingência (runbook); a regra 4 vale para a automação.
  8. **Fase 0:** o episódio feito à mão já usa rascunhos das skills; elas viram definitivas na Fase 1.

## ADR-0014 — Python como auxiliar de mídia
- **Data:** 2026-11-07 · **Status:** Aceita
- **Contexto:** recorte do personagem (rembg), tempo de cada palavra para as legendas e ampliação de imagem têm
  bibliotecas maduras em Python e nenhuma equivalente em .NET. A stack era só .NET.
- **Decisão:** a bancada (Fase 0) é escrita em Python. Na produção, a `Factory.Cli` continua orquestrando e chama
  scripts Python pequenos, com dependências fixadas, só para essas tarefas. Licença de cada biblioteca e modelo
  conferida antes de adotar (`docs/05`).
- **Consequências:** o runner instala Python e dependências (com cache, para poupar minutos). Se o Chirp 3 HD devolver
  o tempo das palavras, o alinhamento forçado nem entra (a confirmar na Fase 0).
