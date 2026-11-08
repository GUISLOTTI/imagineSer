---
paths:
  - "src/**"
  - "tests/**"
---

# Regras para o código .NET

- `Factory.Domain` não faz I/O: nada de HTTP, disco, relógio direto (injete `TimeProvider`) ou variáveis de ambiente.
- Todo serviço externo fica atrás de uma interface em `Factory.Domain` ou `Factory.Infrastructure`
  (`IImageGenerator`, `ITextToSpeech`, `IObjectStorage`, `IPublisher`, `IApprovalSource`), para trocar sem refatorar.
- Toda chamada que pode custar algo passa antes pelo controlador de limites (`UsageGuard`), que lê
  `config/limites.json` e o arquivo de uso do mês, e **recusa antes de chamar** a API.
- Etapas idempotentes: a chave de cada saída é o hash das entradas; se a saída já existe no R2, pule.
- Erros: transitórios (HTTP 429/5xx, timeout) → retry com espera crescente, no máximo 3; permanentes → falha da etapa
  com mensagem clara. Erro 3036 do Workers AI não é retry: espere a renovação diária (00:00 UTC).
- Testes obrigatórios antes de qualquer merge que toque nestes pontos: transições de estado, portão de aprovação
  (incluindo os testes negativos de `docs/06-seguranca.md`), idempotência de publicação, limites de uso.
- Nunca registre em log o conteúdo de segredos nem URLs pré-assinadas completas.
