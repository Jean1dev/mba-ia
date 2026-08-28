# Fundamentos Teóricos do Projeto

Este documento descreve os conceitos de Recuperação Aumentada por Geração (RAG) que
sustentam o projeto, independentemente das tecnologias usadas para implementá-lo.
Cada seção nomeia o conceito, o problema que ele resolve e a decisão de projeto adotada.

---

## 1. O problema de fundo

Um modelo de linguagem guarda dois tipos de conhecimento:

- **Conhecimento paramétrico**: o que ficou codificado nos pesos durante o treinamento.
  É estático, sem data de validade explícita e impossível de auditar.
- **Conhecimento não paramétrico**: o que é fornecido no momento da pergunta, dentro da
  janela de contexto. É atualizável, verificável e específico do domínio.

Perguntas sobre documentação privada de uma organização não podem ser respondidas pelo
conhecimento paramétrico: a informação nunca esteve no treinamento. Quando forçado a
responder mesmo assim, o modelo **alucina** — produz texto plausível e infundado.

RAG é a estratégia que converte o problema de *geração* em um problema de *recuperação
seguida de geração*: buscar em uma base externa os trechos relevantes e exigir que a
resposta se apoie apenas neles. O termo técnico para essa exigência é **grounding**
(ancoragem): toda afirmação deve ser rastreável até um trecho recuperado.

### Por que não colocar tudo no prompt

A alternativa ingênua é enviar a base inteira em cada pergunta. O projeto mantém essa
alternativa implementada como linha de base justamente para expor seus três limites:

1. **Limite de janela**: a base cresce, a janela não.
2. **Custo**: o custo por pergunta é proporcional ao volume enviado, e quase todo ele é
   irrelevante para aquela pergunta.
3. **Degradação por diluição**: quanto mais contexto irrelevante, pior a precisão do
   modelo em localizar a informação certa (fenômeno conhecido como *lost in the middle*).

RAG existe para tornar o contexto **seletivo**: pouco texto, mas o texto certo.

---

## 2. Arquitetura em duas fases

Todo sistema RAG se divide em duas fases com regimes de execução distintos:

| Fase | Quando roda | O que produz | Custo dominante |
|---|---|---|---|
| **Indexação** (offline) | Quando a base muda | Representações vetoriais persistidas | Embeddings |
| **Consulta** (online) | A cada pergunta | Resposta ancorada + fontes | Inferência do modelo |

A separação é uma decisão arquitetural explícita neste projeto: **a fase de consulta
nunca escreve no índice**. Isso garante que o comportamento em tempo de execução seja
puramente de leitura, que o índice seja reproduzível a partir dos documentos, e que
falhas de ingestão não contaminem o atendimento.

---

## 3. Fase de indexação

### 3.1 Documento como unidade governada

Cada documento carrega **metadados estruturados** obrigatórios, separados do corpo do
texto: identificação (título, versão), governança (status de publicação, visibilidade) e
segmentação de domínio (locatário, produto, tipo de documento, plano ao qual se aplica).

A obrigatoriedade é validada na ingestão, que falha ruidosamente quando algo falta. O
princípio é **falhar cedo**: um documento sem metadados corretos não fica invisível na
busca sem que ninguém perceba — ele impede a ingestão.

Esses metadados cumprem três papéis teóricos distintos:

- **Filtragem** — restringem o espaço de busca antes da similaridade.
- **Autorização** — expressam quem pode ver o quê.
- **Proveniência** — permitem citar a origem exata de cada afirmação.

### 3.2 Fragmentação (chunking)

A unidade de recuperação não é o documento, é o **fragmento** (*chunk*). A razão é dupla:
a similaridade vetorial perde resolução quando o texto é longo e heterogêneo (o vetor
vira uma média de vários assuntos), e o contexto final precisa ser curto.

O chunking é o principal ponto de tensão do RAG, governado por um trade-off:

- **Fragmentos pequenos** → alta precisão semântica, risco de cortar a informação ao meio.
- **Fragmentos grandes** → contexto preservado, vetor menos discriminativo e mais ruído.

A estratégia adotada é **hierárquica em dois estágios**:

1. **Divisão estrutural**: o texto é cortado pelas fronteiras semânticas que o autor já
   definiu — os títulos e subtítulos. Isso respeita a organização lógica do documento em
   vez de impô-la de fora.
2. **Divisão por tamanho com sobreposição**: seções ainda longas são cortadas em pedaços
   de tamanho limitado, com uma faixa de texto repetida entre pedaços consecutivos.

A **sobreposição** (*overlap*) é uma apólice de seguro contra o corte infeliz: se uma
definição ficaria dividida exatamente na fronteira, a repetição garante que ela apareça
inteira em pelo menos um dos fragmentos.

Parâmetros usados: tamanho-alvo de 900 caracteres, sobreposição de 150 (≈17%).

### 3.3 Enriquecimento contextual do fragmento

Um fragmento tirado do meio de um documento é **órfão de contexto**: uma tabela de tempos
de resposta não diz de qual produto ou de qual plano ela fala, porque isso estava no
título, três seções acima.

O ponto teórico crucial é que **metadados armazenados ao lado do texto não participam do
embedding**. O vetor é calculado apenas sobre o texto. Logo, filtrar por metadado funciona,
mas *buscar semanticamente* por ele não.

A solução é **prefixar o fragmento com um cabeçalho de contexto** — título, tipo, produto,
plano, versão e seção — antes de gerar o vetor. Assim a informação de contexto entra na
representação vetorial e o fragmento se torna autoexplicativo tanto para a busca quanto
para o prompt final. Essa técnica é conhecida na literatura como *contextual retrieval*.

O projeto mantém a opção de desligar o cabeçalho, para que o efeito da técnica sobre a
qualidade da recuperação possa ser medido comparativamente.

### 3.4 Representação vetorial e busca semântica

Cada fragmento é convertido em um vetor denso de alta dimensão por um **modelo de
embeddings**. A hipótese fundamental é a **hipótese distribucional**: textos com
significado semelhante ocupam posições próximas nesse espaço.

Isso é o que diferencia a busca semântica da busca léxica clássica: a pergunta "e se der
problema grave?" pode recuperar um trecho sobre "incidentes de severidade P1" sem
compartilhar nenhuma palavra com ele.

A proximidade é medida por uma função de similaridade entre vetores. A consequência
prática é que a busca é sempre **aproximada e ordenada por grau**: não existe resposta
binária "encontrou ou não", existe um ranqueamento de candidatos.

### 3.5 Indexação incremental e idempotência

Reprocessar toda a base a cada alteração é caro e desnecessário. O projeto implementa
sincronização incremental sobre três mecanismos:

- **Impressão digital do documento**: um hash criptográfico do arquivo completo. Qualquer
  edição, por menor que seja, muda o hash.
- **Identificador determinístico do fragmento**: derivado do arquivo, do hash e da posição.
  O mesmo conteúdo sempre gera o mesmo identificador, e conteúdo alterado gera
  identificadores novos.
- **Manifesto**: o registro do estado da última indexação.

Comparando o estado atual com o manifesto, cada documento é classificado em um de quatro
estados — novo, alterado, removido ou inalterado — e apenas os três primeiros geram
trabalho. Documentos inalterados não consomem nenhuma chamada de embedding.

A propriedade garantida é a **idempotência**: executar a indexação duas vezes seguidas
não duplica nada e não custa nada. E a **consistência**: remover um documento remove seus
fragmentos do índice, em vez de deixá-los órfãos respondendo perguntas com informação
que não existe mais.

---

## 4. Fase de consulta

O fluxo tem quatro etapas, das quais três invocam o modelo de linguagem:

```
pergunta → planejamento → recuperação → reranqueamento → geração → resposta + fontes
             (modelo)      (vetorial)      (modelo)       (modelo)
```

### 4.1 Planejamento da consulta (query understanding)

**Premissa**: a pergunta que o usuário digita raramente é a melhor consulta para um banco
vetorial. Ela é curta, dependente de contexto implícito e frequentemente ambígua.

Antes de buscar, o modelo interpreta a pergunta e produz um **plano de consulta**
estruturado com cinco decisões:

| Campo | Função teórica |
|---|---|
| Pergunta normalizada | Reescrita autoexplicativa; é o texto efetivamente vetorizado |
| Termos exatos | Literais (códigos, siglas, percentuais) anexados ao texto de busca |
| Tipos de documento | Filtro de metadado sobre a categoria |
| Plano | Filtro de metadado sobre o segmento |
| Necessita esclarecimento | Interrompe o fluxo e devolve uma pergunta ao usuário |

Três conceitos estão embutidos aqui:

**Reescrita de consulta (*query rewriting*)**: transformar a pergunta em uma formulação
mais próxima, no espaço vetorial, dos documentos que a respondem. A pergunta original
continua sendo a que o modelo final responde — a normalizada serve apenas para buscar.
Separar as duas evita que a reescrita distorça a intenção do usuário.

**Preservação de literais**: embeddings tendem a diluir termos raros e alfanuméricos. Um
código de severidade ou uma sigla técnica podem desaparecer na reescrita. Anexá-los
explicitamente ao texto de busca é um remendo deliberado contra essa perda.

**Desambiguação com abstenção**: quando a pergunta admite mais de uma leitura razoável e
cada leitura leva a uma resposta diferente, o sistema pergunta em vez de adivinhar. A
distinção fina, definida no prompt, é entre:

- pergunta que aponta para um segmento específico sem nomeá-lo → ambígua, esclarecer;
- pergunta que não menciona segmento algum → leitura única cuja resposta cobre todos.

### 4.2 Filtragem por metadados: pré-filtro eliminatório

O filtro roda **antes** da busca semântica, como uma cláusula restritiva. A consequência
teórica é severa: **o que não passa no filtro não pode ser recuperado**, mesmo contendo
exatamente a resposta.

Isso instancia diretamente o trade-off clássico de recuperação de informação:

- **Precisão** — proporção do recuperado que é relevante. Filtro aumenta.
- **Revocação (*recall*)** — proporção do relevante que foi recuperado. Filtro reduz.

Como o filtro vem de uma inferência probabilística do modelo, um erro dele é
**silencioso e irrecuperável** dentro daquela consulta. A política de projeto é, por
isso, deliberadamente **generosa**: o planejador lista *todos* os tipos que poderiam
conter a resposta, e quando não há certeza a lista fica vazia — nenhum filtro é aplicado.
Na dúvida, buscar em tudo.

Duas consequências de projeto derivam disso:

- **Documentos universais**: itens que valem para todos os segmentos são marcados como
  tal e o filtro é construído para nunca descartá-los.
- **Catálogo descritivo no prompt**: o planejador só enxerga a base através da descrição
  que recebe. Por isso o catálogo descreve o que cada tipo *realmente contém*, não o que
  o nome sugere.

### 4.3 Separação de autoridade: modelo versus aplicação

Este é o princípio de segurança central do projeto.

Os filtros dividem-se em duas classes:

- **Filtros de conteúdo** (categoria, segmento) — sugeridos pelo modelo. Errar aqui
  degrada a qualidade.
- **Filtros de segurança** (locatário, produto, status de publicação) — fixos na
  aplicação. Errar aqui é vazamento de dados.

O modelo **nunca** decide sobre a segunda classe. Isolamento entre locatários, controle
de acesso e visibilidade de rascunhos são responsabilidade determinística da aplicação.
Delegar isso a um componente probabilístico, influenciável pelo texto de entrada, seria
abrir mão do controle de acesso — e é o vetor natural de ataques de injeção de prompt.

O mesmo princípio reaparece em outros dois pontos do pipeline (montagem de fontes e
validação de identificadores): o modelo *propõe*, a aplicação *dispõe*.

### 4.4 Contrato entre planejador e índice

Os valores possíveis de categoria e segmento formam um **contrato** entre dois
componentes: a saída estruturada garante que o planejador nunca invente um valor
inexistente.

O outro lado do contrato é o risco real: se o índice passa a conter uma categoria que o
planejador desconhece, ele nunca poderá selecioná-la, e todos os documentos dessa
categoria **desaparecem silenciosamente de qualquer busca filtrada**.

A mitigação é uma **verificação de contrato na inicialização**: os valores distintos
presentes no índice são comparados com os que o planejador conhece, e o sistema recusa-se
a iniciar quando há divergência. Uma falha silenciosa de qualidade é convertida em uma
falha ruidosa de inicialização.

### 4.5 Recuperação: otimizar revocação

A busca retorna os *k* fragmentos mais próximos que passaram no filtro. O valor de *k* é
deliberadamente generoso (8): o objetivo desta etapa é **não perder o fragmento certo**,
não escolher o melhor. Cortar cedo demais elimina a resposta antes que qualquer
componente tenha chance de avaliá-la.

### 4.6 Reranqueamento: otimizar precisão

A recuperação em dois estágios (*two-stage retrieval*) separa dois objetivos que uma única
etapa não consegue atender bem:

| Estágio | Objetivo | Critério |
|---|---|---|
| Recuperação vetorial | Revocação | Proximidade geométrica, barata, aproximada |
| Reranqueamento | Precisão | Julgamento de relevância, caro, contextual |

O reranqueador recebe os candidatos e a pergunta e seleciona no máximo 4, preferindo
fragmentos específicos a genéricos e os que contêm os termos literais. A justificativa
teórica é que a similaridade de embeddings mede *semelhança de assunto*, não *utilidade
para responder* — duas noções que divergem com frequência.

**O reranqueador também é um portão de abstenção.** Quando nenhum candidato sustenta a
resposta, ele devolve uma seleção vazia e o sistema responde "não encontrei" **sem chamar
o modelo de geração**. O efeito é duplo: economia e, sobretudo, segurança — contexto
irrelevante nunca chega ao prompt final, eliminando a oportunidade de o modelo construir
uma resposta plausível a partir de material inadequado.

### 4.7 Geração ancorada

O prompt final instrui o modelo a responder **exclusivamente** com base no contexto,
proibindo conhecimento prévio e invenção de fontes. A saída é estruturada em três campos:

- o texto da resposta;
- um sinalizador booleano de suficiência do contexto;
- a lista de identificadores dos fragmentos efetivamente utilizados.

A **saída estruturada** é, teoricamente, mais do que conveniência de formato: ela
transforma um julgamento que estaria implícito na prosa ("acho que não sei responder") em
um campo verificável pela aplicação.

### 4.8 Abstenção como requisito de primeira classe

Um sistema de RAG confiável precisa saber dizer "não sei". Este projeto materializa a
abstenção em **três portões independentes**, em pontos distintos do fluxo:

| Portão | Etapa | Condição |
|---|---|---|
| Esclarecimento | Planejamento | Pergunta ambígua |
| Ausência de candidatos | Recuperação / reranqueamento | Nada relevante encontrado |
| Contexto insuficiente | Geração | Candidatos não sustentam a resposta |

A redundância é intencional: cada portão captura um modo de falha diferente, e falhar em
silêncio é considerado pior do que não responder.

### 4.9 Proveniência: fontes montadas pela aplicação

O modelo indica *quais* fragmentos usou, mas **não escreve as fontes**. A aplicação cruza
os identificadores declarados com os fragmentos que realmente estavam no contexto e monta
a citação a partir dos metadados verificados. Identificadores inventados são descartados.

A distinção é essencial: uma citação escrita pelo modelo é *texto gerado* e pode ser
alucinada como qualquer outra frase. Uma citação montada pela aplicação é *fato
verificado*. Isso torna toda resposta **auditável** — é sempre possível abrir o documento
citado e conferir.

---

## 5. Princípios transversais

### 5.1 Determinismo onde há classificação

Temperatura zero em todas as chamadas. O raciocínio: planejador e reranqueador não são
componentes criativos, são **classificadores**. A mesma pergunta deve produzir o mesmo
plano e a mesma seleção, inclusive na decisão de pedir esclarecimento. Variabilidade
nessas etapas torna o sistema não reproduzível e impossível de avaliar.

### 5.2 Observabilidade sem vazamento

Cada execução recebe um identificador único de requisição, mede o tempo de cada etapa e
agrega o consumo de tokens por modelo. Um registro estruturado é emitido por execução.

O princípio que governa *o que* é registrado é **minimização de dados**: contagens, tempos
e nomes de arquivo, nunca prompts, conteúdo de fragmentos, respostas ou credenciais. O
objetivo é permitir auditoria do comportamento do pipeline sem criar um repositório
secundário de informação sensível.

Complementarmente, erros são registrados internamente com tipo e mensagem, mas expostos
externamente como falha genérica — não vazar detalhes de implementação em mensagens de
erro é prática básica de segurança.

### 5.3 Decomposição em módulos executáveis isoladamente

Cada etapa pode ser executada sozinha: a recuperação sem o modelo de chat, o chat sem
recuperação, o documento inteiro no prompt, o pipeline completo. Somam-se a isso
sinalizadores para desligar o cabeçalho de contexto e o reranqueamento.

Isso é **método experimental** aplicado à engenharia: para atribuir efeito a um
componente, é preciso poder removê-lo mantendo o resto constante. A arquitetura foi
desenhada para permitir *ablação* — comparar a mesma pergunta com e sem cada peça.

### 5.4 Linhas de base comparativas

Dois modos existem exclusivamente como referência de comparação:

- **Chat sem recuperação** — mede o que o conhecimento paramétrico consegue responder
  sozinho e, principalmente, torna visível a alucinação sobre documentação privada.
- **Chat com documento inteiro no prompt** — funciona para bases pequenas e demonstra
  empiricamente os limites de janela e custo que motivam o RAG.

Sem linhas de base, qualquer resultado do RAG é incomparável.

### 5.5 Reutilização do núcleo entre interfaces

O pipeline é uma implementação única, consumida por uma interface de terminal e por uma
interface de rede. As interfaces decidem apenas a apresentação; a lógica de recuperação e
de ancoragem é idêntica.

Isso garante **paridade de comportamento** — o que foi validado em uma interface vale para
a outra — e evita divergência entre caminhos de código com as mesmas garantias de
segurança.

---

## 6. Limitações reconhecidas

O projeto documenta explicitamente o que não implementa, o que também é postura teórica
relevante:

- **Busca híbrida**: combinar recuperação densa (semântica) com esparsa (léxica, por
  frequência de termos). A busca densa é fraca justamente em identificadores exatos,
  siglas e nomes próprios — a anexação de termos literais é um paliativo, não a solução.
- **Memória conversacional**: cada pergunta é tratada isoladamente. Perguntas de
  acompanhamento com referências anafóricas ("e no outro plano?") exigiriam reescrita
  ciente do histórico.
- **Avaliação quantitativa**: não há, nesta configuração, conjunto de referência nem
  métricas automáticas de fidelidade e relevância.
- **Fragmentação semântica adaptativa**: o corte por tamanho é sintático dentro de cada
  seção.

---

## 7. Glossário

| Termo | Definição operacional |
|---|---|
| **RAG** | Recuperar trechos de uma base externa e gerar a resposta condicionada a eles |
| **Grounding** | Exigência de que toda afirmação seja sustentada pelo contexto recuperado |
| **Alucinação** | Afirmação fluente e plausível sem suporte factual |
| **Chunk** | Fragmento de documento; unidade mínima de recuperação |
| **Overlap** | Texto repetido entre fragmentos vizinhos, contra cortes infelizes |
| **Embedding** | Representação vetorial densa na qual proximidade aproxima semelhança semântica |
| **Precisão** | Fração do recuperado que é relevante |
| **Revocação** | Fração do relevante que foi recuperado |
| **Top-k** | Quantidade de candidatos retornados pela busca |
| **Reranking** | Segundo estágio que reordena e filtra candidatos por utilidade real |
| **Pré-filtro** | Restrição por metadados aplicada antes da busca vetorial |
| **Abstenção** | Recusa explícita e deliberada de responder |
| **Proveniência** | Rastro verificável da origem de cada afirmação |
| **Idempotência** | Propriedade de que repetir a operação não altera o resultado |
