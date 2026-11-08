# Briefing para o Claude Code — Projeto de uma fábrica automatizada de conteúdo

> **Objetivo deste documento:** fornecer contexto suficiente para que você analise e recomende a melhor arquitetura técnica e operacional para uma operação de conteúdo original assistida por IA. Este é um pedido de **análise e desenho**, não de implementação. Não crie arquivos, não instale dependências, não altere configurações, não publique conteúdo e não contrate/ative serviços nesta etapa.
>
> Responda em **português brasileiro**, de maneira prática, detalhada e fundamentada. Considere as capacidades e os preços disponíveis na data em que executar esta análise. Pesquise a documentação oficial atualizada antes de afirmar que um recurso, integração ou plano existe.

---

## 1. Contexto do proprietário e forma de trabalho

- O proprietário trabalha em horário comercial e não quer transformar o projeto em um segundo emprego.
- O papel desejado é o de **gestor/diretor editorial**: planejar temas, revisar roteiros, assistir aos vídeos finais, aprovar publicações, acompanhar métricas e decidir ajustes de estratégia.
- Ele não quer aparecer em câmera nem utilizar a própria voz. A narração deve ser feita por voz sintética em português brasileiro, com licença adequada para uso comercial.
- Ele é desenvolvedor FullStack júnior, tem experiência profissional com C#, .NET, SQL Server, MVC, JavaScript e ferramentas de desenvolvimento assistido por IA. Já utiliza Claude Code. Pode acompanhar decisões técnicas, mas prefere explicações claras, arquitetura justificável e manutenção simples.
- O proprietário não se opõe a desenvolver uma aplicação própria desde o início, caso isso seja realmente a melhor opção. A IA pode auxiliar na construção do sistema. Não presuma que evitar código é sempre mais barato; compare custo total, confiabilidade, manutenção e tempo de operação.
- A prioridade é atingir o maior grau de automação **sem perder controle editorial, segurança, qualidade ou conformidade**.

## 2. Objetivo do negócio

Construir uma pequena operação de mídia digital que produza conteúdo original de entretenimento educativo/curiosidades, com auxílio de IA, e distribua cada episódio em quatro plataformas:

1. YouTube (principalmente Shorts no início; avaliar vídeos maiores quando fizer sentido).
2. Instagram (Reels).
3. TikTok.
4. Bilibili (desde que a operação de publicação, disponibilidade no Brasil e condições da plataforma sejam verificadas).

A hipótese comercial é construir uma marca e uma biblioteca de conteúdos próprios, sem depender de cortes de podcasts, lives ou vídeos de terceiros. A audiência deverá vir do valor editorial, da curiosidade, da narrativa, da identidade visual e da distribuição multiplataforma.

**Não tratar visualizações como receita garantida.** Monetização, elegibilidade, remuneração, requisitos de idade/conta, disponibilidade regional e regras de cada plataforma devem ser verificadas em fontes oficiais atuais. Não projetar receita com base em RPM inventado ou em relatos não confirmados.

O projeto pode utilizar um nome temporário para organização, mas **a marca e o nome definitivo ainda não foram escolhidos**. “Imagina Ser” foi apenas uma ideia provisória, não uma decisão.

## 3. Conceito editorial

A proposta é criar vídeos curtos, visuais e interessantes sobre animais, corpo humano, natureza, ciência, tecnologia, universo, evolução e fenômenos curiosos.

A essência é fazer o espectador descobrir algo de maneira envolvente. Não é obrigatório que todo episódio comece com “Você é...”. A narrativa pode variar entre:

- segunda pessoa / experiência imersiva;
- história cronológica ou ciclo de vida;
- pergunta intrigante;
- explicação de como algo funciona;
- comparação surpreendente;
- perspectiva de um animal, órgão, fenômeno ou objeto;
- narrativa documental curta;
- hipótese científica claramente identificada como hipótese.

Exemplos de aberturas possíveis (apenas referências de abordagem):
- “Você nasceu com uma armadura que vai carregar pelo resto da vida...” (tartaruga).
- “Existe um órgão no seu corpo trabalhando silenciosamente em centenas de funções...” (fígado).
- “Três corações, sangue azul e uma inteligência surpreendente. Como seria viver assim?” (polvo).
- “Imagine viver em um planeta onde um dia dura menos de 11 horas...” (Saturno).
- “Tudo começa com uma pequena semente que passa por uma transformação extraordinária...” (café).

Não copiar roteiros, animações, personagens, identidade, logotipo, áudio ou cenas de outros criadores. Um perfil chamado `@voceeanimal` foi mostrado como referência de formato: animação 3D estilizada, com aparência de personagem de videogame/filme de animação, cenários relativamente simples, iluminação bem trabalhada, animal em destaque e legendas grandes. Não temos confirmação de quais ferramentas esse perfil utiliza. A referência serve somente para descrever a linguagem visual desejada, não para reproduzir sua identidade ou propriedade intelectual.

## 4. Identidade visual desejada

Preferência inicial: **3D estilizado, expressivo e cinematográfico**, não fotorrealismo extremo.

Características desejadas:
- personagens e objetos visualmente atraentes, com proporções e características biologicamente/tecnicamente plausíveis;
- ambientes limpos e compreensíveis;
- iluminação agradável, composição vertical e personagem/elemento principal em destaque;
- movimentos de câmera, pequenos movimentos de personagem e animação nos momentos de maior valor narrativo;
- legendas claras, legíveis e consistentes;
- linguagem visual reconhecível entre episódios;
- consistência de aparência do mesmo animal/personagem ao longo de um vídeo;
- cenas originais geradas/licenciadas para o projeto.

Não exigir animação complexa em cada segundo. Avaliar uma abordagem híbrida: imagens geradas + animação pontual + movimentos de câmera/parallax + edição e composição. Comparar com geração direta de vídeo por IA somente quando houver vantagem clara de qualidade/tempo/custo.

A qualidade desejada é intermediária no primeiro MVP: aparência bem feita, sem tentar competir com uma produção de estúdio.

## 5. Duração e formatos

- Duração preferencial inicial: **60 a 90 segundos**.
- Alvo de produção: aproximadamente 65–90 segundos, quando a história comportar.
- Limite normal: 120 segundos.
- Até 180 segundos somente quando o tema exigir e a retenção potencial justificar.
- Não preencher tempo artificialmente. Um assunto pode ser concluído em 45–60 segundos, se isso for editorialmente melhor.
- Formato-mestre inicial: vertical 9:16, com resolução e taxa de quadros recomendadas após análise das exigências atuais das plataformas e dos custos.
- Produzir arquivo mestre limpo, sem marca d’água de plataforma. Gerar legendas incorporadas e, se útil, arquivo de legenda separado.
- Adaptar título, descrição, hashtags, capa e metadados para cada plataforma. Não simplesmente copiar metadados cegamente.
- Avaliar se um mesmo master é adequado às quatro redes ou se Bilibili/YouTube precisam de versões específicas.

## 6. Calendário editorial inicial (provisório e flexível)

A ideia é ter um eixo temático por dia para manter variedade e facilitar planejamento. Não transformar esse calendário em regra rígida: a IA deve poder sugerir trocas quando houver pauta especialmente forte, sazonalidade ou falta de fontes confiáveis.

| Dia | Pilar editorial | Exemplos |
|---|---|---|
| Segunda | Mundo animal | tartaruga, rato, polvo, morcego, besouro, formiga, capivara |
| Terça | Corpo humano e biologia | fígado, coração, cérebro, rins, células, neurônios, sentidos, digestão |
| Quarta | Natureza e ecossistemas | oceanos, florestas, fungos, ciclos naturais, relações ecológicas |
| Quinta | Ciência, tecnologia e como as coisas funcionam | vidro, eletricidade, motores, materiais, invenções e processos |
| Sexta | Universo e astronomia | planetas, luas, estrelas, buracos negros e fenômenos cósmicos |
| Sábado | Evolução e história natural | dinossauros, fósseis, espécies extintas, evolução e vida pré-histórica |
| Domingo | Fenômenos e perguntas curiosas | “E se...?”, paradoxos, fenômenos naturais e explicações surpreendentes |

O catálogo potencial de assuntos é amplo. Não assumir que uma categoria está perto de se esgotar apenas porque os tópicos mais conhecidos foram cobertos. Para evitar repetição, manter um banco pesquisável de temas, subtemas, espécies, órgãos, processos, fontes já utilizadas, episódios publicados e ideias futuras.

Exemplos de expansão:
- animais atuais → espécies pouco conhecidas → animais extintos → dinossauros → evolução e parentesco entre espécies;
- anatomia humana → órgãos → sistemas → tecidos → células → processos fisiológicos → comparação com anatomia de outros animais;
- natureza → biomas → ecossistemas → relações entre espécies → ciclos de matéria e energia;
- ciência → materiais → mecanismos → fenômenos → invenções → aplicações cotidianas.

O sistema deve ajudar a descobrir pautas, mas nunca inventar quantidade de espécies, órgãos ou fatos. Se mencionar números de catálogo científico, indicar base, data, escopo e limitações.

## 7. Cadência de produção

Objetivo operacional após validação: **um episódio por dia, sete dias por semana**, distribuído nas quatro plataformas.

A implantação pode começar com três episódios semanais para validar qualidade, custo e capacidade de produção. Depois aumentar para cinco e, quando comprovado que o processo suporta, sete por semana. A arquitetura deve suportar a meta de sete por semana desde o início, sem presumir que já conseguiremos alcançá-la no primeiro teste.

Planejamento semanal:
- No fim de semana, o proprietário e a IA organizam os temas da semana seguinte.
- A lista contém sete temas principais e algumas pautas reservas.
- Manter como meta uma reserva de cinco episódios completos, revisados e aprovados para publicação, quando a operação estiver estável.
- O sistema deve detectar pautas repetidas, assuntos já publicados e lacunas na programação.

Produção durante a semana (proposta a ser avaliada):
- A tarefa diária começa cedo, por exemplo por volta de 05h30, para preparar o roteiro do próximo episódio ainda não aprovado.
- Até 07h00 (fuso `America/Sao_Paulo`), o proprietário recebe um pacote de revisão.
- O pacote deve conter tema, título, gancho inicial, roteiro completo, duração estimada, afirmações factuais com respectivas fontes, pontos incertos, proposta de storyboard, descrição das cenas e observações de direitos/licenças.
- O proprietário aprova, rejeita ou solicita ajustes no roteiro.
- Somente após a aprovação do roteiro começa a produção audiovisual.
- Ao terminar, o sistema disponibiliza o vídeo para assistir e solicita a segunda aprovação.
- Somente após a segunda aprovação o vídeo pode ser agendado/publicado.
- O horário de publicação ainda não foi definido; recomendar como escolher com base nos dados, sem inventar um horário universal ideal.

**Importante:** não desenhar um fluxo que dependa de um agente ficar bloqueado esperando uma resposta humana durante horas. As aprovações precisam ser persistidas em banco de dados ou mecanismo durável. Uma aprovação deve disparar um novo job/evento, que continua o pipeline. Se a pessoa não aprovar até determinado horário, o episódio deve permanecer pendente ou ser substituído por um vídeo reserva — nunca publicar automaticamente.

## 8. Aprovações humanas obrigatórias

Há duas aprovações independentes:

### Aprovação 1 — Editorial/roteiro

O proprietário avalia:
- se o tema é interessante;
- se a abertura prende a atenção;
- se o roteiro está correto e compreensível;
- se a duração faz sentido;
- se as fontes são adequadas;
- se há informação controversa, incerta ou exagerada;
- se o roteiro respeita a identidade da marca.

Ações permitidas: aprovar, rejeitar, solicitar correção, trocar tema.

### Aprovação 2 — Vídeo final

O proprietário assiste ao arquivo final e verifica:
- correspondência entre narração e imagens;
- aparência e consistência dos personagens;
- erros visuais/anatomia incorreta;
- sincronização de voz, cenas e legendas;
- pronúncia em português brasileiro;
- qualidade do áudio e volume;
- cortes, transições, duração e legibilidade;
- ausência de marcas d’água e materiais sem licença;
- avisos/identificação de IA quando exigidos.

Ações permitidas: aprovar para distribuição, solicitar correção de cenas/áudio/legendas, rejeitar e arquivar.

**Não permitir publicação em nenhuma plataforma sem registro explícito da segunda aprovação.** Guardar data/hora, usuário, versão do arquivo aprovada e histórico de alterações. Se o vídeo mudar depois da aprovação, invalidar a aprovação anterior e pedir nova validação.

## 9. Pesquisa científica, checagem factual e qualidade editorial

A credibilidade é um requisito central. Conteúdo deve ser divertido, mas não pode inventar fatos para gerar viralização.

Regras:
- pesquisar antes de roteirizar;
- priorizar artigos científicos, universidades, museus, órgãos públicos, organizações científicas e fontes primárias;
- registrar URL, título, autor/instituição, data de publicação e data de acesso;
- vincular cada afirmação factual relevante a uma ou mais fontes;
- identificar afirmações controversas, dados estimados, incertezas e divergências;
- distinguir fato estabelecido, hipótese, estimativa, opinião e dramatização narrativa;
- verificar números, unidades, escalas de tempo, nomes científicos, anatomia e contexto;
- não apresentar correlação como causalidade;
- não extrapolar conclusões de estudos feitos em uma espécie para outra;
- não usar “a ciência prova” quando a evidência é limitada;
- nunca fabricar citações, DOI, estatísticas ou referências;
- se não houver fonte suficiente, reformular ou remover a afirmação;
- quando duas fontes confiáveis divergirem, apresentar a divergência ou evitar a afirmação;
- não usar somente uma segunda resposta de IA como prova independente da primeira.

O agente de checagem deve verificar as fontes e a correspondência entre fonte e afirmação; não deve apenas perguntar a outro modelo se o texto “parece correto”. Considerar validação por fontes independentes e, quando possível, consultas a bases/documentos originais.

Em temas do corpo humano, manter abordagem educativa geral. Não diagnosticar espectadores, recomendar tratamentos individualizados nem substituir orientação profissional.

## 10. Direitos autorais, licenças e políticas

O projeto deve ser construído para ser original e comercialmente utilizável.

- Não usar cortes de podcasts, lives ou vídeos de terceiros como base do negócio.
- Não baixar e republicar conteúdo de outros criadores.
- Não copiar roteiro, personagem, voz, logotipo, identidade visual, cenas ou trilha de outro canal.
- Não imitar a voz de pessoa real.
- Usar geração própria, bibliotecas com licença adequada, material em domínio público ou material com autorização documentada.
- Verificar licença comercial e condições de uso de cada ferramenta de imagem, vídeo, voz, música e efeitos sonoros.
- Armazenar informações de proveniência: ferramenta, modelo, data, prompt quando aplicável, licença/termos vigentes e origem dos assets.
- Não presumir que “gerado por IA” significa automaticamente livre de direitos ou liberado para uso comercial.
- Não presumir que creditar o autor equivale a obter autorização.
- Verificar as regras atuais de conteúdo sintético/IA, monetização, conteúdo repetitivo/inautêntico, propriedade intelectual e publicação de cada plataforma.
- Incluir identificação de conteúdo gerado/alterado por IA quando exigida.
- Não utilizar músicas incorporadas de uma plataforma no master destinado às outras; preferir áudio original ou licenciado para todas as plataformas pretendidas.

Antes de recomendar uma ferramenta ou integração, verificar termos de uso, licença comercial, restrições geográficas, APIs, limites, custos e política de retenção dos arquivos.

## 11. Plataformas e distribuição

Verificar a documentação oficial atual de cada plataforma:

- YouTube Data API / upload e agendamento, requisitos de auditoria/verificação, quotas, restrições de projetos e políticas de monetização.
- Instagram Graph API / publicação de Reels, tipos de conta aceitos, permissões e revisão do app.
- TikTok Content Posting API, Direct Post, permissões, auditoria, limites, restrições de visibilidade e regras para conteúdo com IA.
- Bilibili: disponibilidade efetiva no Brasil, cadastro e verificação de conta, formatos aceitos, APIs oficiais, possibilidade real de upload automatizado, regras de IA e condições comerciais/monetização.

Não usar automação de navegador, scraping ou métodos não oficiais para contornar limitações das plataformas. Se a API oficial não permitir determinada ação, apresentar alternativa manual segura e indicar explicitamente a limitação.

O sistema deve ser capaz de:
- produzir um master limpo;
- criar metadados adequados por plataforma;
- validar especificações do arquivo antes do upload;
- realizar upload/agendamento quando a API oficial permitir;
- registrar ID, URL, horário e status da publicação;
- detectar falhas e permitir nova tentativa sem publicar duplicado;
- guardar métricas separadas por plataforma e episódio.

## 12. Requisitos técnicos e operacionais

Analisar se é melhor começar com uma aplicação própria desde o primeiro MVP ou combinar ferramentas já prontas. O proprietário aceita desenvolver um sistema se isso aumentar a automação e reduzir o trabalho operacional a médio prazo.

Requisitos desejáveis:

1. **Execução na nuvem 24/7:** tarefas devem funcionar mesmo com o computador pessoal desligado.
2. **Agendamento persistente:** jobs não podem desaparecer após reinício ou falha.
3. **Orquestração por etapas:** pesquisa, checagem, roteiro, storyboard, produção, QA, aprovação, publicação e métricas.
4. **Estado persistente:** cada episódio e cada etapa possuem status armazenado.
5. **Fila de jobs:** tarefas demoradas podem ser retomadas, repetidas com segurança e monitoradas.
6. **Aprovação humana:** bloqueio efetivo antes da produção/publicação, conforme etapa.
7. **Idempotência:** repetir um job não deve gerar duplicações de episódio, cobrança ou publicação.
8. **Retry e tratamento de falhas:** erros temporários devem gerar tentativas controladas; erros permanentes devem ir para uma fila de falhas.
9. **Logs e observabilidade:** saber qual agente executou, quanto custou, quanto demorou, quais fontes consultou e onde falhou.
10. **Limites de custo:** orçamento diário/mensal, limite por episódio e interrupção automática se ultrapassar o teto definido.
11. **Gestão de segredos:** chaves de API e tokens fora dos arquivos Markdown, Git e prompts públicos; usar secrets manager/variáveis seguras.
12. **Armazenamento:** roteiros, fontes, prompts, imagens, áudio, vídeos, thumbnails, legendas e versões aprovadas.
13. **Histórico e auditoria:** preservar versões e decisões de aprovação.
14. **Backup e recuperação:** banco e arquivos importantes precisam de backup.
15. **Segurança:** menor privilégio, autenticação, autorização, proteção do dashboard e limites para ações externas.
16. **Notificações:** pacote de roteiro às 07h00 e alerta quando o vídeo estiver pronto para revisão. Comparar opções como painel web, e-mail, Telegram ou outra solução; não assumir canal sem avaliar privacidade, custo e facilidade.
17. **Interface de gestão:** visualização do calendário, fila, roteiro com fontes, player de vídeo, aprovar/rejeitar/solicitar ajustes, custos, erros e métricas.
18. **Operação manual de contingência:** permitir baixar o vídeo e publicar manualmente se uma API estiver indisponível.

## 13. Tecnologias a avaliar (não são imposições)

O proprietário conhece C#/.NET e SQL Server. Avaliar tecnicamente, sem assumir que essa é obrigatoriamente a melhor solução.

Comparar pelo menos:
- aplicação própria em .NET (por exemplo, ASP.NET Core + Worker Service + Hangfire/Quartz ou alternativa);
- Node.js/TypeScript ou Python para pipeline de mídia, se oferecerem vantagem concreta;
- PostgreSQL versus SQL Server;
- armazenamento S3-compatible/Azure Blob ou equivalente;
- orquestradores como n8n, Temporal, Hangfire, serviços de cloud scheduler ou alternativas;
- Claude Code Scheduled Tasks;
- Claude Agent SDK/API e uso de API de modelos;
- eventual uso de ferramentas prontas para geração de voz, imagem e vídeo;
- FFmpeg e outras ferramentas de montagem automatizada.

É importante separar:
- **Claude Code como ferramenta para desenvolver/manter o software**;
- **Claude Code Scheduled Tasks como possível mecanismo de execução agendada de agentes**;
- **API/SDK de modelo como dependência programática do produto**;
- **orquestrador/backend próprio como responsável por estado, fila, aprovações, retries e publicação**.

Não presumir que uma assinatura de Claude Code pode ser usada como API ilimitada de produção. Verificar os termos, limites, disponibilidade, autenticação, custos e condições atuais de cada modalidade. Se um recurso estiver em preview, beta, limitado por plano ou não for adequado para execução crítica, deixar isso claro.

Não escolher arquitetura apenas por familiaridade ou por ser “mais simples”. Comparar custo total de propriedade, confiabilidade, lock-in, segurança, operação e manutenção. Evitar microserviços desnecessários no MVP; preferir arquitetura modular e evolutiva.

## 14. Fluxo de dados e modelo de episódio

Propor um modelo de dados mínimo que permita representar:
- pauta/tema e categoria editorial;
- data planejada e data de publicação;
- status geral e status de cada etapa;
- fontes consultadas e afirmações sustentadas por cada fonte;
- roteiro e suas versões;
- storyboard e prompts de cenas;
- assets produzidos e licenças/proveniência;
- áudio, legendas, master e versões derivadas;
- custos por etapa e por episódio;
- aprovações, autor, data/hora e hash/versão aprovada;
- publicações por plataforma e respectivos IDs/URLs/status;
- métricas por plataforma e período;
- histórico de erros, retries e alterações.

Sugerir uma máquina de estados. Como referência inicial (pode melhorar):

`BACKLOG → PLANEJADO → PESQUISANDO → CHECANDO_FATOS → ROTEIRO_PENDENTE → ROTEIRO_APROVADO → PRODUZINDO → QA_PENDENTE → VIDEO_PENDENTE → VIDEO_APROVADO → PRONTO_PARA_PUBLICAR → AGENDADO → PUBLICADO → ANALISANDO`

Estados adicionais desejáveis: `AJUSTES_SOLICITADOS`, `REPROVADO`, `FALHA_TEMPORARIA`, `FALHA_PERMANENTE`, `CANCELADO`, `ARQUIVADO`.

Aprovações precisam estar associadas a uma versão específica. Qualquer alteração em roteiro ou vídeo após sua aprovação deve invalidar a aprovação correspondente.

## 15. Produção audiovisual: comparar opções e custos reais

Desenhar um pipeline capaz de:
1. receber roteiro aprovado;
2. gerar storyboard e prompts por cena;
3. criar imagens/personagens com consistência visual;
4. animar cenas selecionadas;
5. gerar voz sintética natural em português brasileiro;
6. ajustar pronúncia de nomes científicos, números e termos técnicos;
7. gerar trilha/efeitos sonoros licenciados ou usar biblioteca autorizada;
8. sincronizar narração, cenas e legendas;
9. montar e exportar o vídeo;
10. executar QA técnico e visual automatizado;
11. salvar arquivo para revisão humana.

Comparar modelos e serviços disponíveis atualmente. Para cada ferramenta sugerida, informar:
- o que faz e por que foi escolhida;
- se possui API utilizável programaticamente;
- se permite uso comercial;
- restrições e necessidade de crédito/atribuição;
- preço atual e unidade de cobrança;
- estimativa de custo por episódio de 60–90 segundos;
- limitações de consistência de personagem, duração, resolução, fila e tempo de geração;
- alternativa caso o serviço fique indisponível.

Não inventar preços nem afirmar licença sem fonte. Se o preço depender de créditos, mostrar fórmula e premissas. Separar custos fixos e variáveis.

Avaliar se o início deve usar predominantemente imagem + movimento de câmera/edição, animação de pequenos trechos ou vídeo generativo. A meta é qualidade consistente com o menor custo operacional razoável, não o máximo realismo.

## 16. Métricas e otimização

O painel e os relatórios precisam acompanhar, quando as plataformas disponibilizarem:
- visualizações e alcance;
- impressões e CTR (quando aplicável);
- retenção e duração média assistida;
- visualizações que escolheram assistir versus passaram adiante (quando aplicável);
- compartilhamentos, comentários, curtidas e salvamentos;
- seguidores/inscritos conquistados por episódio;
- origem geográfica e fontes de tráfego;
- receita/RPM somente quando o canal estiver elegível e os dados oficiais existirem;
- custo e tempo de produção por episódio;
- taxa de aprovação na primeira tentativa;
- quantidade de correções e falhas por etapa.

A IA deve produzir recomendações semanais fundamentadas nos dados, sem confundir correlação com causalidade. Não alterar calendário ou publicar novos formatos automaticamente sem aprovação do proprietário.

## 17. Estimativa de custos e orçamento

Montar uma estimativa mensal em reais para três cenários:
- piloto com 3 episódios por semana;
- operação intermediária com 5 episódios por semana;
- meta de 7 episódios por semana.

Separar:
- modelo de linguagem/pesquisa;
- geração de imagens;
- animação/vídeo generativo;
- TTS/voz;
- música e efeitos/licenças;
- armazenamento e transferência de arquivos;
- hospedagem/backend/banco;
- orquestração e notificações;
- custos de APIs de publicação, quando existentes;
- eventual assinatura do Claude Code/API.

Apresentar cenário econômico, intermediário e avançado. Explicitar quantidade de cenas por episódio, tentativas/regerações, duração, consumo de tokens/créditos, câmbio e premissas. Distinguir custos que já podem estar cobertos por assinaturas existentes daqueles que exigem pagamento adicional.

Propor um orçamento máximo por episódio e um limite mensal que o proprietário possa configurar. Não assumir investimento ilimitado.

## 18. Riscos que a arquitetura deve resolver

- conteúdo factual incorreto ou afirmação sem fonte;
- imagens/animações biologicamente erradas;
- personagem inconsistente entre cenas;
- pronúncia inadequada em português brasileiro;
- conteúdo genérico/repetitivo que prejudique a distribuição ou monetização;
- regras de disclosure de IA;
- licença comercial ausente ou ambígua;
- API de rede social indisponível ou não aprovada para publicação pública;
- publicação duplicada;
- falha de renderização ou arquivo corrompido;
- atraso no pacote das 07h;
- agente que consome tokens/créditos em loop;
- perda de estado depois de reiniciar serviço;
- vazamento de API keys;
- indisponibilidade de fornecedor;
- dependência excessiva de um único provedor de IA.

Para cada risco, propor prevenção, detecção, recuperação e fallback.

## 19. O que espero como resposta sua

Faça uma análise de arquitetura, sem implementar ainda. Entregue os itens abaixo em ordem:

1. **Resumo executivo:** qual arquitetura recomenda e por quê.
2. **Comparação de caminhos:** (A) somente Claude Code + Markdown + tarefas agendadas; (B) Claude Code para desenvolvimento + backend/orquestrador próprio; (C) automação low-code + serviços de IA; (D) arquitetura híbrida. Comparar custos, confiabilidade, autonomia, manutenção e limites.
3. **Arquitetura recomendada:** diagrama textual dos componentes e do fluxo, destacando o que roda na nuvem e o que depende do computador do proprietário.
4. **Papel de cada agente:** responsabilidades, entradas, saídas, ferramentas e permissões. Indicar quais precisam ser agentes de IA separados e quais podem ser scripts determinísticos.
5. **Fluxo de aprovações:** como receber o roteiro às 07h, aprovar pelo painel/Telegram/e-mail e iniciar o próximo job; como aprovar o vídeo final; como garantir que nada seja publicado sem autorização.
6. **Stack sugerida:** tecnologias específicas com justificativa e alternativas. Considerar experiência do proprietário com C#/.NET e SQL Server, sem impor a stack.
7. **Ferramentas de conteúdo:** opções atuais para pesquisa, imagem, vídeo, TTS, edição e legendas, com API/licença/custos documentados.
8. **Integrações das quatro redes:** status real das APIs oficiais, requisitos de autorização/auditoria, limites e fallback manual. Não afirmar que uma plataforma aceita publicação automática sem comprovar.
9. **Modelo de dados e máquina de estados:** entidades/tabelas essenciais e regras de transição.
10. **Estimativa de custos:** três volumes (3, 5 e 7 vídeos/semana), três cenários de qualidade, em reais, com fontes e premissas.
11. **Plano de MVP:** fases pequenas, critérios de sucesso e o que deve ser testado antes de avançar.
12. **Riscos e pontos de atenção:** incluindo termos de uso, privacidade, licenças, segurança, políticas de IA e monetização.
13. **Perguntas em aberto:** liste apenas as decisões que realmente dependem do proprietário. Não interrompa a análise por falta de respostas; declare premissas razoáveis.
14. **Decisão final:** recomendação clara do que construir primeiro e o que não construir ainda.

### Regras para sua análise

- Pesquise a documentação oficial atual de Anthropic/Claude Code, provedores de IA e APIs das plataformas. Use links diretos e datas de consulta.
- Diferencie recursos confirmados, recursos em beta/preview e hipóteses.
- Não trate um recurso de desenvolvimento como se fosse automaticamente um runtime de produção 24/7.
- Não suponha que a assinatura Claude Code inclui chamadas ilimitadas de API ou créditos de vídeo/imagem/voz.
- Não recomende scraping ou publicação por métodos que contornem as APIs/regras oficiais.
- Não recomende comprar planos ou serviços antes de comparar custo e benefício.
- Não implemente nada, não crie arquivos, não instale pacotes, não configure contas e não publique nada nesta rodada.
- Se tiver acesso ao ambiente, pode verificar somente informações não sensíveis e não destrutivas, como versão do Claude Code e recursos disponíveis. Não leia nem exponha tokens, chaves, secrets ou dados pessoais.
- Seja específico. Evite respostas genéricas como “use agentes e automações”. Mostre exatamente como os componentes se comunicariam, como o estado seria persistido e como as aprovações humanas funcionariam.

---

## 20. Resumo do que já está decidido

- Conteúdo original de entretenimento educativo/curiosidades.
- Sem rosto e sem voz própria do proprietário.
- Narração por voz sintética em português brasileiro.
- Referência visual: 3D estilizado, não fotorrealismo extremo.
- Categorias amplas: animais, corpo humano/biologia, natureza, ciência/tecnologia, universo, evolução/história natural e fenômenos.
- Não obrigar todos os episódios a começar com “Você é...”.
- Duração preferencial de 60–90 segundos; 120 segundos como limite normal; 180 segundos apenas excepcionalmente.
- Objetivo futuro de um episódio por dia, distribuído em quatro plataformas.
- Planejamento semanal no fim de semana.
- Pacote de roteiro e fontes desejado até 07h, no fuso `America/Sao_Paulo`.
- Duas aprovações humanas: roteiro e vídeo final.
- Publicação sempre condicionada à aprovação explícita do vídeo final.
- O proprietário deseja ser gestor da operação, não editor diário.
- A operação deve ser legal, original, licenciada e compatível com as políticas das plataformas.
- Claude Code já é utilizado; não há decisão de contratar Codex ou outra assinatura.
- O proprietário aceita construir aplicação própria desde o início se a análise demonstrar que é a melhor solução.
- Nome e identidade definitiva da marca ainda não foram escolhidos.

**Agora faça a análise completa solicitada e recomende a melhor solução para este contexto.**
