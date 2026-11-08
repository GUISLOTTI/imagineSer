# Prompt para a primeira sessão no terminal

Abra o terminal na raiz do repositório, rode `claude`, confira com `/context` que o `CLAUDE.md` aparece em
"Memory files" e cole o texto abaixo.

---

Olá. Este repositório é o projeto Imagine Ser. Todo o contexto que construímos numa conversa anterior está em
`CLAUDE.md` e na pasta `docs/`. Nesta primeira sessão **não escreva código nem crie arquivos fora de `docs/`**.

1. Leia, nesta ordem: `CLAUDE.md`, `docs/01-plano-mvp-v2.md`, `docs/03-decisoes.md`, `docs/06-seguranca.md`,
   `docs/05-bancada-visual.md`, `docs/04-guia-editorial.md`. Consulte `docs/00-briefing-original.md` e
   `docs/02-analise-v1-referencia.md` só se precisar.
2. Me devolva, em português:
   - um resumo de no máximo 15 linhas do que vamos construir e das regras inegociáveis;
   - qualquer contradição ou lacuna que você encontrar entre os documentos (não resolva sozinho: pergunte);
   - as pendências da seção 11 do plano que ainda bloqueiam a Fase 0.
3. Proponha um plano detalhado só da **Semana 0 e da Fase 0** (bancada visual, vozes, teste do Buffer), com o que
   eu faço manualmente nos painéis e o que você automatiza com scripts em `bancada/`. Espere minha aprovação.
4. Teste o hook de bloqueio: tente ler um arquivo `.env` de exemplo e confirme que foi bloqueado.

Regras desta sessão: explique o porquê antes do quê; verifique na documentação oficial qualquer preço ou limite
antes de afirmá-lo; nada que gere cobrança.
