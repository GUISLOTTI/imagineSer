---
paths:
  - ".github/**"
---

# Regras para workflows do GitHub Actions

- Mudança em workflow sempre com aprovação explícita do Gabriel e explicação do impacto em minutos e segurança.
- `permissions:` mínimas por job; nunca `write-all`.
- Ações de terceiros fixadas por SHA de commit, com o número da versão em comentário.
- Segredo só no `env` do passo que o usa. Jobs do Claude Code recebem apenas `CLAUDE_CODE_OAUTH_TOKEN` e usam
  `github_token: ${{ secrets.GITHUB_TOKEN }}` (o token padrão não altera `.github/workflows/`).
- Jobs do Claude Code: `--max-turns` e `--allowedTools` explícitos; sem Bash genérico.
- `timeout-minutes` em todo job; `concurrency` por episódio; `publicar` com `cancel-in-progress: false`.
- Orçamento de minutos: o GitHub arredonda cada job para cima por minuto. Nada de cron de hora em hora; os únicos
  crons são `roteiro` (sábado 05:30) e `reconciliar` (07h, 15h, 23h), que também retoma a fila de imagens
  (ADR-0013). Estime os minutos/mês de qualquer workflow novo.
- Cron em UTC: 05:30 em Brasília = `30 8 * * *`.
