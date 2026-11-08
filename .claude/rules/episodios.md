---
paths:
  - "episodes/**"
  - "pautas/**"
---

# Regras para arquivos de episódio

- Pasta: `episodes/AAAA-MM-DD-epNNNN-assunto/` (data = publicação prevista). O código `#epNNNN` vai no fim de toda
  descrição de post e serve para achar o post se o ID se perder.
- Todo arquivo segue o schema correspondente em `schemas/`; rode `validar` depois de qualquer edição.
- `roteiro.md`: cada frase factual termina com a marca da afirmação, ex.: `[A3]`. Sem marca = frase não factual
  (dramatização) e precisa ser claramente narrativa.
- `afirmacoes.json`: tipo (fato, hipótese, estimativa, opinião, dramatização), status (verde, amarelo, vermelho),
  fontes com URL, título, autor/instituição, data de publicação, data de acesso e **trecho literal**.
- Vermelho bloqueia o PR de roteiro. Amarelo exige nota explicando a dúvida para o Gabriel decidir.
- Nunca edite `video.json`, `publicacoes.json` ou hashes à mão; só a `Factory.Cli` escreve neles.
- Duração (ADR-0012): padrão 61–90 s (alvo 62–75 s); fora disso só com justificativa no PR; teto absoluto 120 s.
- Corpo humano: abordagem educativa geral, sem diagnóstico ou recomendação individual; aviso fixo na descrição.
