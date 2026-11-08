# Segurança — referência para implementação

Detalhes e fontes: `docs/01-plano-mvp-v2.md`, seção 6.

## Checklist de contas (fazer na Semana 0, sem cobrança possível)

- [x] Claude: créditos de uso extra **desligados** (claude.ai/settings/usage). Conferido em 07/11/2026.
- [ ] GitHub: **nenhuma** forma de pagamento cadastrada (o Actions bloqueia ao esgotar a franquia, sem cobrar).
- [ ] GitHub: "Allow GitHub Actions to create and approve pull requests" ligado (necessário para os PRs do bot).
- [ ] GitHub: variáveis de repositório `OWNER_LOGIN` (seu login) e `PUBLICACAO_ATIVA=false` até a Fase 3.
- [ ] Cloudflare: plano **Workers Free**; token de API só com Workers AI.
- [ ] Cloudflare R2 (Fase 2): regras de ciclo de vida (intermediários 14 dias, masters 90 dias); chaves por bucket e
      por papel.
- [ ] Google Cloud (na vez da voz): projeto só para TTS; só a API Text-to-Speech ativa; orçamento de US$ 1 com
      alertas 50/90/100%; cota de requisições dimensionada (ADR-0013). Fase 2: função de corte de faturamento e
      federação OIDC com o GitHub.
- [ ] Buffer: plano Free; 3 canais conectados; chave da API guardada só como GitHub Secret.

## Portão de aprovação (`publicar`)

Antes de cada post, exigir, nesta ordem, e abortar com `FALHA_PERMANENTE` + issue se qualquer item falhar:

1. PR de roteiro do episódio mesclado, com revisão `APPROVED` de `OWNER_LOGIN` cujo `commit_id` é o último commit.
2. PR de vídeo do episódio mesclado, mesma regra.
3. `video.json` lido **pela API no commit aprovado** aponta para o hash do roteiro aprovado.
4. Master baixado do R2 com SHA-256 igual ao aprovado; chave `masters/epNNNN/<sha256>.mp4`, nunca sobrescrita.
5. `PUBLICACAO_ATIVA=true`.

Testes negativos (todos devem bloquear): master trocado após aprovação; PR mesclado sem revisão; aprovação num
commit antigo; aprovação por outro usuário ou bot; `PUBLICACAO_ATIVA=false`.

## Idempotência da publicação

`publicacoes.json` por episódio: `AGENDADA → ENVIANDO → CRIADA_NO_BUFFER → PUBLICADA | FALHOU`.
Chave: epNNNN + rede + sha256. Gravar `ENVIANDO` e fazer push **antes** de chamar o Buffer; gravar o ID logo depois.
Ao retomar de `ENVIANDO` sem ID: procurar `#epNNNN` nos posts do canal no Buffer; adotar se existir.
Workflow `publicar` com `concurrency` e `cancel-in-progress: false`.

## Recuperação

- Saídas endereçadas pelo hash das entradas; pular se já existir no R2.
- `episode.json` atualizado a cada etapa no branch do episódio.
- Etapa em andamento grava `rodando_ate`; `reconciliar` (07h, 15h, 23h) reenfileira vencidas; após 3 tentativas,
  `BLOQUEADO` + issue.
- Fila de imagens retoma às 00:05 UTC; erro 3036 não gera retry imediato.

## Segredos

| Segredo | Onde | Job | Escopo |
| --- | --- | --- | --- |
| `CLAUDE_CODE_OAUTH_TOKEN` | GitHub Secret | pauta, roteiro, ajuste | assinatura; renovar a cada 90 dias |
| `CF_AI_TOKEN` | GitHub Secret | produzir | só Workers AI |
| `R2_*` | GitHub Secret | produzir (escrita), publicar e reconciliar (leitura) | por bucket e papel |
| Google | nenhum (OIDC) | produzir | conta de serviço mínima |
| `BUFFER_API_KEY` | GitHub Secret | publicar, reconciliar | sem escopos no Buffer: isolar |

Regras: segredo só no passo que usa; `permissions:` mínimas; ações fixadas por SHA; jobs do Claude com o
`GITHUB_TOKEN` padrão (não altera workflows) e ferramentas restritas; hook do Claude Code bloqueando leitura de
`.env` no Bash e no PowerShell; `gitleaks` opcional (ADR-0013).
