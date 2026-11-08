# Imagine Ser

Vídeos curtos e originais de curiosidades (animais, corpo humano, natureza, ciência, universo, evolução, fenômenos),
narrados por voz sintética em pt-BR, publicados em YouTube Shorts, Instagram Reels e TikTok (@imagineser.oficial).
O proprietário (Gabriel) é o diretor editorial: aprova roteiros e vídeos; não aparece nem narra.

**Objetivo:** renda extra sem virar segundo emprego. O Gabriel só aprova ou nega (roteiro e vídeo), sem prazos;
todo o resto é automático. O tempo dele é a métrica principal: alvo ≤ 30 min/semana em 3 episódios (ADR-0010).

Fase atual: **Semana 0 — transplante e bancada de testes**. Nenhum código de produção existe ainda.

## Regras inegociáveis

1. **Orçamento:** teto de US$ 20/mês, que é o Claude Pro já pago. Proibido no MVP: Claude API paga, Gemini API paga,
   qualquer geração de vídeo/imagem/voz paga, servidor, domínio. Não sugira contratar nada sem pedir.
2. **Franquias gratuitas só com limite rígido:** corte por plano (Workers Free, GitHub sem forma de pagamento) ou
   contador próprio da `Factory.Cli` que bloqueia ANTES de chamar a API. Nunca remova ou aumente um limite de
   `config/limites.json` sem um ADR aprovado.
3. **Duas aprovações humanas:** nada é publicado sem (a) PR de roteiro e (b) PR de vídeo, ambos mesclados e com
   revisão APPROVED do login `OWNER_LOGIN` no último commit, e hash do master conferido no upload. A verificação
   mora no código do publicador (`docs/06-seguranca.md`), não na configuração do repositório.
4. **Publicação só pelo workflow `publicar`.** Nunca rode `publicar` localmente nem crie posts no Buffer por outro caminho.
   Exceção: o próprio Gabriel pode postar pela interface do Buffer, como contingência.
5. **Somente vias oficiais:** APIs oficiais e o Buffer (parceiro oficial). Nada de scraping, automação de navegador
   ou endpoints não documentados.
6. **Fatos:** nunca invente fato, número, citação, DOI ou fonte. Toda frase factual do roteiro aponta para uma
   afirmação em `afirmacoes.json` com trecho literal da fonte. Sem fonte suficiente: reformule ou remova.
7. **Originalidade e licenças:** nada de material de terceiros sem licença registrada; todo asset grava proveniência
   (ferramenta, modelo, data, prompt, seed, termos). Sem música no MVP. Todo post sai com `isAiGenerated = true`.
8. **Segredos:** nunca leia, imprima, commite ou cole em prompt arquivos `.env`, tokens ou chaves. Segredos vivem em
   GitHub Secrets; o Google usa OIDC (sem chave). No PC, o `.env` (criado pelo Gabriel) é lido só pelos scripts.

## Arquitetura em uma tela

- Tudo roda no **GitHub Actions** (repositório privado, GitHub Free). O **estado** é o Git: uma pasta por episódio em
  `episodes/` (`episode.json`, `dossie.md`, `afirmacoes.json`, `roteiro.md`, `storyboard.json`, `metadados.json`,
  `video.json`, `publicacoes.json`).
- **Agentes = skills do Claude Code** (`.claude/skills/`), executadas pela GitHub Action oficial com o token do Pro.
  Elas só escrevem arquivos; a saída é validada por schema (`schemas/`).
- **`Factory.Cli` (.NET 10)** faz tudo que tem efeito externo: validar, produzir (imagens, voz, legendas, render,
  QA), publicar, reconciliar, contadores de uso.
- **Serviços:** Cloudflare Workers AI Free (imagens FLUX), Cloudflare R2 (mídia), Google Cloud TTS Chirp 3 HD (voz),
  Buffer Free (publicação nas 3 redes).
- **Fluxo (por estoque, ADR-0011):** roteiros semanais (Claude) → PR 1 → aprova ou nega → produzir → PR 2 →
  aprova ou nega → publicar no próximo horário livre (Buffer) → reconciliar 3×/dia. Sem prazos: horário sem vídeo
  aprovado fica vazio. Cadência inicial: 3 episódios/semana.

## Stack e convenções

- .NET 10, C#. Solução em `src/` com `Factory.Domain` (regras puras, sem I/O), `Factory.Infrastructure` (clientes
  externos atrás de interfaces), `Factory.Media` (FFmpeg, legendas, QA) e `Factory.Cli`. Testes xUnit em `tests/`.
- Python 3 só como auxiliar de mídia (bancada, recorte, alinhamento), chamado pela `Factory.Cli` (ADR-0014).
- Identificadores C# em inglês (`EpisodeState`, `ApprovalGate`). Nomes de comandos da CLI, arquivos de episódio,
  docs, mensagens de commit e descrições de PR em português.
- Comandos (quando existirem): `dotnet build`, `dotnet test`, `dotnet run --project src/Factory.Cli -- <comando>`.
- Workflows em `.github/workflows/`: permissões mínimas por job, ações de terceiros fixadas por SHA, segredo só no
  passo que usa, `timeout-minutes` sempre. Jobs do Claude usam o `GITHUB_TOKEN` padrão (não pode alterar workflows).

## Como trabalhar comigo (Gabriel)

- Explique o porquê antes do quê; seja direto, inclusive quando a notícia for ruim.
- **Autonomia:** decida sozinho o que for óbvio ou tiver recomendação bem fundamentada; registre num ADR e me conte
  em uma linha. Só me chame para: dinheiro/cartão, contas e marca, minha rotina de aprovação, risco legal ou de
  política das plataformas, ou ação irreversível.
- **Simplicidade:** boas práticas desde o início, mas nenhuma complexidade sem um problema real que a justifique.
- Conflito entre docs: resolva pela opção mais simples e segura e registre num ADR; pergunte só nos casos acima.
- Decisão nova ou mudança de decisão → registre em `docs/03-decisoes.md` (ADR). Regra permanente → uma linha aqui.
- Antes de afirmar preço, limite ou recurso de serviço externo, verifique a documentação oficial atual e cite.
- Pronto = compila, testes passam, docs atualizados, nenhum limite ou regra acima violado.

## Como evoluímos (contexto e melhoria contínua)

- **Medir antes de decidir (ADR-0015):** escolher entre ferramentas, modelos, vozes, técnicas, durações ou horários
  exige teste real registrado em `docs/08` (data, método, números). Validado = doc oficial citada com data ou
  medição nossa; guia de terceiros só gera hipótese. Sem isso, o ADR fica "Proposta".
- **O estado mora nos arquivos, não na conversa:** ao fim de cada tarefa, atualize "Próximos passos" abaixo e
  `docs/08` (estado, medições, lições) e faça um commit pequeno e verificado (`feat:`, `fix:`, `docs:`, `chore:`).
  Uma sessão nova deve conseguir continuar só lendo este arquivo.
- **Contexto enxuto:** este arquivo fica abaixo de 150 linhas, só com o que vale sempre; detalhes vão para `docs/`
  e `.claude/rules/`. Leia a seção que precisa, não o doc inteiro. Sessão longa ou troca de assunto: `/compact`
  com foco, ou sessão nova.
- **Erro vira lição, lição repetida vira regra:** todo bug, negativa ou ajuste pedido pelo Gabriel entra em
  `docs/08` com causa e correção; o que se repetir vira regra na skill afetada ou aqui. O mesmo erro não chega duas
  vezes ao Gabriel. Na Fase 1, os motivos das negativas nos PRs passam a alimentar as skills automaticamente.
- **Só se entrega o que rodou:** script, skill ou workflow só vai para o Gabriel depois de executado de verdade.
- **Ao fechar uma fase:** revise este arquivo e os docs e corte o que ficou obsoleto.

## Mapa dos documentos (leia sob demanda)

- `docs/01-plano-mvp-v2.md` — plano vigente: decisões, bancada visual, produção, voz, plataformas, segurança,
  validação, custos, cronograma, plano de implementação. **Vale sobre os demais docs, exceto os ADRs de
  `docs/03` posteriores a 04/11/2026, que prevalecem sobre ele.**
- `docs/02-analise-v1-referencia.md` — análise original; só para a arquitetura-alvo futura (servidor, cenários pagos).
- `docs/00-briefing-original.md` — requisitos do proprietário.
- `docs/03-decisoes.md` — ADRs.
- `docs/04-guia-editorial.md` — pilares, formatos narrativos, regras factuais.
- `docs/05-bancada-visual.md` — protocolo dos testes T1–T5 de imagem.
- `docs/06-seguranca.md` — portão de aprovação, idempotência, recuperação, segredos, checklist de contas.
- `docs/07-fontes.md` — onde estão as fontes e quando reverificar.
- `docs/08-estado-e-aprendizados.md` — estado das contas, medições reais e lições. **Leia no início da sessão.**

## Próximos passos (Semana 0 → Fase 0)

Repositório: `github.com/GUISLOTTI/imagineSer` (privado). Estado das contas em `docs/08`.

1. Claude: scripts da bancada visual T1–T5 (`docs/05-bancada-visual.md`) em `bancada/`. Gabriel: token da
   Cloudflare no `.env` quando o Claude cobrar (scripts prontos).
2. Gabriel: conectar o YouTube ao Buffer quando o canal tiver o @ (Claude lembra).
3. Claude: 5 vozes Chirp 3 HD para o Gabriel ouvir (aí entra o Google Cloud, com cartão).
4. Claude: um episódio feito à mão com rascunhos das skills (calibra prompts); Gabriel aprova ou nega.
5. ADRs de imagem e voz com números medidos → Fase 1: solução .NET, schemas e skills definitivas (`docs/01` §10).
