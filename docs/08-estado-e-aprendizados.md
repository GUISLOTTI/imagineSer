# Estado e aprendizados

Atualizado ao fim de cada tarefa. Três partes: estado das contas, medições (números reais, com método) e lições.
Quando passar de ~200 linhas, mover medições e lições antigas para `docs/arquivo/`.

## Estado das contas — 07/11/2026

| Item | Estado | Próxima ação |
| --- | --- | --- |
| Claude | Créditos de uso extra desligados ✔ | — |
| GitHub | Repositório privado `GUISLOTTI/imagineSer` ✔ | Confirmar que não há forma de pagamento; ajustes de Actions na Fase 1 |
| Cloudflare | Conta e token pendentes | Gabriel cria o token quando os scripts da bancada estiverem prontos |
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

Formato: data · o que · método · resultado · arquivo de dados. Nenhuma ainda (a bancada começa na Fase 0).

## Lições

| Data | Lição | Origem | Virou regra em |
| --- | --- | --- | --- |
| 07/11/2026 | No Windows, o Git converte LF em CRLF e quebra scripts bash; `*.sh` fica fixo em LF | Primeiro commit | `.gitattributes` |
| 07/11/2026 | Neste PC o Claude Code tem Bash e PowerShell; hooks e bloqueios precisam cobrir os dois | Teste do hook | `.claude/settings.json` |
| 07/11/2026 | Guias de terceiros sobre monetização divergem entre si; só decidir com página oficial ou medição | Pesquisa de monetização | ADR-0015 |
