# Guia editorial — Imagine Ser

Fonte: briefing original (docs/00) e plano v2 (docs/01). Este guia é a referência das skills `pauta-semanal`,
`pesquisar`, `roteirizar` e `checar-fatos`.

## Proposta

Fazer o espectador **descobrir** algo de forma envolvente: entretenimento educativo, visual 3D estilizado,
narração em pt-BR, legendas grandes. Conteúdo original; nada de cortes ou material de outros criadores.

## Pilares (calendário flexível)

| Pilar | Exemplos |
| --- | --- |
| Mundo animal | tartaruga, polvo, morcego, besouro, formiga, capivara |
| Corpo humano e biologia | fígado, coração, cérebro, rins, células, sentidos |
| Natureza e ecossistemas | oceanos, florestas, fungos, ciclos naturais |
| Ciência, tecnologia e como funciona | vidro, eletricidade, motores, materiais |
| Universo e astronomia | planetas, luas, estrelas, buracos negros |
| Evolução e história natural | dinossauros, fósseis, espécies extintas |
| Fenômenos e perguntas curiosas | "E se...?", paradoxos, fenômenos naturais |

Em 3 episódios/semana, a pauta alterna pilares para manter variedade. Trocar de tema é permitido quando houver pauta
mais forte ou falta de fontes confiáveis. Sempre checar `pautas/publicados.json` para não repetir.

## Formatos narrativos (variar; não repetir o mesmo em episódios seguidos)

Segunda pessoa/imersivo · ciclo de vida · pergunta intrigante · como funciona · comparação surpreendente ·
perspectiva de um animal/órgão/objeto · documental curto · hipótese claramente identificada como hipótese.
Não começar todo episódio com "Você é...". Variedade de estrutura é também proteção contra a política de
"conteúdo inautêntico" do YouTube, que vale para o canal inteiro.

## Estrutura de um episódio (alvo 62–75 s; padrão 61–90 s, ADR-0012)

1. **Gancho (0–3 s):** uma imagem forte + uma frase que cria curiosidade.
2. **Contexto (3–12 s):** o que é, onde está, por que importa.
3. **Descobertas (2–3 batidas):** cada uma com um fato sustentado por fonte.
4. **Virada:** o fato mais surpreendente, guardado para o fim.
5. **Fechamento:** uma frase que amarra; convite leve (sem pedir like de forma genérica).

## Imagem e som (ADR-0017 e ADR-0018)

- **Animação 3D feita por código**, câmera sempre em movimento; cada frase da narração tem uma ação na tela (algo
  aparece, se monta, muda ou reage). Etiquetas presas aos objetos e legenda grande palavra a palavra.
- **Som caprichado é regra (decisão do Gabriel, 14/11/2026):** toda ação importante na tela tem um **som-chave**
  sincronizado ao quadro (ventosa grudando, bolha, pop de etiqueta, whoosh de câmera, nota de contagem subindo na
  escala). Sons-chave são o que prende o público: capriche neles antes de qualquer outro detalhe.
- Fundo contínuo de ambiente (mar, floresta, corpo, espaço), baixo e sem silêncio morto; nada de música (regra 7).
- Repetição com variação: o mesmo som repetido muda um pouco de tom a cada vez (como as ventosas subindo).
- Momentos de piada ou virada ganham som próprio e um respiro antes.
- Origem: sons sintetizados pelo nosso código (`bancada/som/`) ou bibliotecas com licença registrada; volume final
  normalizado (alvo inicial −16 LUFS).
- **A voz manda.** Enquanto a narração fala, efeitos e ambiente abaixam sozinhos (efeitos −6 dB, ambiente −9 dB,
  começando 40 ms antes da palavra) e abrem espaço na faixa de 1–4 kHz, onde mora a clareza da fala (−5 dB). Voz no
  centro; efeitos no lado onde está o objeto. Sons-chave caem na palavra que ilustram ou no respiro logo depois; o
  roteiro deixa respiros curtos para os momentos de vitrine (ex.: as ventosas estourando depois de "ventosas").

## Regras factuais

- Pesquisar antes de roteirizar; priorizar artigos científicos, universidades, museus, órgãos públicos e fontes
  primárias.
- Registrar URL, título, autor/instituição, data de publicação, data de acesso e **trecho literal**.
- Distinguir fato estabelecido, hipótese, estimativa, opinião e dramatização narrativa.
- Números: unidade, escala e contexto; duas fontes independentes (domínios diferentes) para cada número.
- Não apresentar correlação como causa; não extrapolar de uma espécie para outra; não dizer "a ciência prova" com
  evidência limitada.
- Fontes divergentes: mostrar a divergência ou evitar a afirmação.
- Nunca fabricar citação, DOI, estatística ou referência. Sem fonte: reformular ou remover.
- Outra resposta de IA não é prova; a prova é o trecho literal da fonte.
- Corpo humano: educativo e geral; nunca diagnóstico nem recomendação de tratamento.

## Tom e linguagem

Português brasileiro, frases curtas para fala, vocabulário acessível a partir de ~13 anos, sem gírias datadas.
Nomes científicos com pronúncia no dicionário `config/pronuncia.json`. Números por extenso quando a fala ficar mais
natural.
