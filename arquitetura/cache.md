# Fundamentos Teóricos — Cache Semântico em Sistemas de Inteligência Artificial

Documento conceitual do projeto. O objetivo aqui é isolar **as ideias**, independentemente
da linguagem, do framework, do banco de dados ou do provedor de modelo utilizados na
implementação. Toda a discussão abaixo continua válida se a stack for trocada por completo.

---

## 1. O problema de fundo: por que cachear inferência de IA

### 1.1 A natureza de uma chamada a um modelo de linguagem

Uma chamada a um modelo generativo tem três propriedades que a diferenciam de uma
chamada de função comum:

| Propriedade | Consequência prática |
|---|---|
| **Custo monetário por execução** | Cada requisição é tarifada (normalmente por token processado). O custo é linear no volume, não amortizado. |
| **Latência alta e variável** | A resposta depende de um serviço externo, com tempo de resposta de ordens de grandeza acima de um acesso local. |
| **Não-determinismo** | A mesma entrada pode produzir saídas diferentes em execuções distintas. |

O cache ataca as três: elimina o custo, reduz a latência a um acesso local e — efeito
menos óbvio, mas relevante — **impõe determinismo artificial**, já que a mesma entrada
passa a devolver sempre a mesma saída enquanto o item estiver em cache.

### 1.2 A premissa que torna o cache viável

Cachear só faz sentido sob uma hipótese: **a distribuição das entradas é concentrada**.
Em atendimento, suporte, triagem e classificação, um pequeno conjunto de intenções cobre
a maior parte do volume real (comportamento tipicamente descrito por uma distribuição de
cauda longa, ou lei de Zipf). Se cada requisição fosse genuinamente única, a taxa de
acerto tenderia a zero e o cache seria apenas overhead.

O projeto assume esse cenário: tickets de suporte se repetem, e se repetem sobretudo
**em significado**, não em forma literal.

### 1.3 Trabalho determinístico versus trabalho generativo

Um princípio de arquitetura atravessa todo o projeto: **nem toda etapa de um fluxo de IA
precisa de IA**. Normalização de texto, cálculo de chave, comparação com um limiar,
consulta a índice — tudo isso é determinístico, barato e auditável. A chamada ao modelo
é o único ponto caro e incerto, e deve ser tratada como recurso escasso, acionado apenas
quando nenhuma alternativa determinística resolve.

---

## 2. Conceitos fundamentais de cache

### 2.1 Vocabulário

- **Hit** — a entrada solicitada já existe no cache; devolve-se o valor armazenado.
- **Miss** — a entrada não existe; é preciso executar a operação cara e, em geral,
  popular o cache com o resultado.
- **Chave (key)** — identificador determinístico derivado da entrada.
- **Valor (value)** — a resposta previamente computada.
- **Taxa de acerto (hit rate)** — proporção de requisições resolvidas por cache. É a
  métrica central de eficácia.

### 2.2 O padrão *cache-aside*

O projeto adota o padrão **cache-aside** (também chamado *lazy loading*):

1. A aplicação consulta o cache antes de qualquer trabalho caro.
2. Em caso de hit, retorna imediatamente.
3. Em caso de miss, a própria aplicação executa a operação cara.
4. A aplicação grava o resultado no cache e retorna.

A característica definidora é que **o cache não sabe como produzir o valor**. Ele é um
repositório passivo; a orquestração é responsabilidade da aplicação. Isso o distingue de:

- **Read-through** — o cache é quem busca na origem quando não tem o dado.
- **Write-through / write-behind** — toda escrita passa pelo cache, de forma síncrona ou
  assíncrona.

Cache-aside foi escolhido por ser o mais simples de raciocinar e o que deixa a decisão de
"o que merece ser cacheado" nas mãos da aplicação — decisão que, em IA, é semântica e não
pode ser delegada à infraestrutura.

### 2.3 Cache é otimização, não fonte de verdade

Consequência de projeto que o sistema respeita em todos os caminhos: **a falha do cache
não pode ser a falha da requisição**. Se a camada de persistência do cache estiver
indisponível ou devolver dado corrompido, o sistema degrada para o caminho caro (chamar o
modelo) e responde normalmente. Isso é **degradação graciosa**: perde-se eficiência,
nunca a funcionalidade.

O mesmo raciocínio vale na escrita: se a gravação do resultado no cache falhar, a resposta
já produzida é entregue mesmo assim, com o insucesso registrado em telemetria.

---

## 3. Identidade de uma requisição: normalização e chave

### 3.1 Normalização

Duas mensagens podem ser **textualmente diferentes e operacionalmente idênticas**:

```
"Quero cancelar meu plano"
"quero  cancelar meu plano   "
```

Sem tratamento, geram chaves distintas e causam um miss desnecessário. A **normalização**
é a função que colapsa variações irrelevantes em uma forma canônica — no projeto, colapso
de espaços em branco, remoção de bordas e uniformização de caixa.

A normalização é uma decisão de modelagem, não um detalhe: ela define **o que o sistema
considera "a mesma pergunta"**. Normalizar demais funde entradas que deveriam ser
distintas; normalizar de menos fragmenta o cache e derruba a taxa de acerto.

### 3.2 Derivação da chave por resumo criptográfico

A chave é obtida aplicando uma função de *hash* sobre uma serialização determinística da
identidade da requisição. As propriedades exploradas são:

- **Determinismo** — a mesma entrada gera sempre a mesma chave.
- **Tamanho fixo** — a chave não cresce com o tamanho da mensagem.
- **Baixa probabilidade de colisão** — entradas distintas praticamente nunca compartilham
  chave.

Um cuidado técnico importante: a serialização precisa ser **canônica** (ordem estável dos
campos), caso contrário a mesma identidade lógica poderia produzir chaves diferentes
apenas por ordenação de atributos.

---

## 4. Fingerprint: o contexto faz parte da identidade

### 4.1 O problema da invalidação

A frase clássica de que invalidação de cache é um dos problemas difíceis da computação se
aplica aqui de forma particularmente aguda. Em um sistema de IA, uma resposta em cache
**não depende apenas da entrada do usuário**. Ela depende também de:

- a **instrução do sistema** (o prompt) usada para produzi-la;
- as **regras de negócio** vigentes (taxonomia de categorias, políticas de classificação);
- a **capacidade do modelo** empregado.

Se qualquer um desses elementos mudar, as respostas armazenadas passam a refletir um
comportamento que o sistema **não tem mais**. O cache torna-se um repositório de decisões
obsoletas — e, pior, silenciosamente obsoletas.

### 4.2 Fingerprint como identidade composta

A solução adotada é ampliar a noção de identidade. A chave não é derivada só do texto,
mas de um **fingerprint** — um conjunto de dimensões que, juntas, descrevem *sob quais
condições aquela resposta foi produzida*:

```
fingerprint = (versão do prompt, versão das regras, capacidade do modelo, texto normalizado)
```

### 4.3 Invalidação por versionamento

O efeito é elegante: **não existe operação de invalidação**. Ao incrementar a versão do
prompt ou das regras, todas as chaves mudam automaticamente e o cache antigo deixa de ser
alcançável, sem que nada precise ser apagado. Isso é *invalidação lógica* ou *namespacing
por versão*.

Vantagens conceituais:

- **Atomicidade** — a troca de comportamento é instantânea e completa.
- **Reversibilidade** — voltar a versão anterior reativa o cache anterior, ainda intacto.
- **Coexistência** — versões diferentes podem operar em paralelo sem contaminação mútua,
  o que viabiliza testes A/B e implantações graduais.

O custo é o **cold start**: cada nova versão recomeça com cache vazio e um período
transitório de custo elevado. Também há acúmulo de dados órfãos, que exige uma política
de expurgo separada.

### 4.4 Configuração mutável em tempo de execução

O projeto expõe as dimensões do fingerprint como configuração alterável em execução. A
implicação teórica é que **o comportamento de cache passa a ser um parâmetro operacional**,
não uma constante de implantação: é possível observar, ajustar e comparar regimes de cache
sem reiniciar o sistema.

---

## 5. Do cache exato ao cache semântico

### 5.1 O limite do cache exato

O cache exato reconhece igualdade **sintática** (após normalização). Ele falha por
completo diante de:

```
"Quero cancelar meu plano"
"Preciso cancelar minha assinatura"
"Como faço para encerrar o contrato?"
```

Três formas, uma intenção. Em linguagem natural, a variação de superfície é a regra, não a
exceção — e é exatamente por isso que o cache exato, sozinho, tem taxa de acerto baixa em
entradas humanas livres.

### 5.2 A mudança de critério

O cache semântico substitui a pergunta

> "esta entrada é **igual** a alguma já vista?"

por

> "esta entrada é **suficientemente parecida em significado** com alguma já vista?"

Essa troca tem três consequências profundas:

1. A comparação deixa de ser exata e passa a ser **aproximada**;
2. A busca deixa de ser um acesso por chave e passa a ser uma **busca por proximidade**;
3. O resultado deixa de ser certo e passa a ser **probabilístico** — e portanto sujeito a
   erro.

O cache exato nunca erra: se a chave bate, a resposta é literalmente a mesma. O cache
semântico **pode errar**. Gerenciar esse erro é o tema central das seções seguintes.

---

## 6. Representação vetorial (embeddings)

### 6.1 Hipótese distribucional

Embeddings são vetores numéricos de alta dimensão que representam o conteúdo de um texto.
Sua base teórica é a **hipótese distribucional** da linguística: palavras e expressões que
ocorrem em contextos semelhantes tendem a ter significados semelhantes. Modelos treinados
sobre grandes corpora aprendem a projetar textos em um espaço onde essa relação vira
**geometria**.

### 6.2 O espaço semântico

Propriedades relevantes desse espaço:

- **Dimensionalidade fixa** — todo texto, de qualquer tamanho, vira um vetor com o mesmo
  número de dimensões. Há compressão com perda: nem tudo do texto sobrevive.
- **Proximidade ≈ similaridade** — textos com significados próximos ficam próximos no
  espaço.
- **Continuidade** — não existem apenas "igual" e "diferente"; existe um contínuo de
  proximidade, e é ele que permite estabelecer um critério ajustável.

### 6.3 Consequências práticas

Três pontos costumam ser subestimados:

1. **O embedding pertence ao modelo que o gerou.** Vetores produzidos por modelos
   diferentes vivem em espaços incomparáveis. Trocar o modelo de embedding invalida todo
   o acervo — é uma mudança de mesma gravidade que trocar a versão do prompt.
2. **A dimensionalidade é um contrato estrutural.** O armazenamento precisa conhecê-la de
   antemão; misturar dimensões diferentes na mesma coleção não é possível.
3. **A geração do embedding também tem custo.** É mais barata que a inferência
   generativa, mas não é gratuita — o que justifica reaproveitar o vetor já calculado ao
   longo da requisição em vez de recomputá-lo, como o projeto faz entre a etapa de busca e
   a de gravação.

### 6.4 Similaridade como medida angular

A comparação usual entre embeddings é a **similaridade de cosseno**, que mede o ângulo
entre dois vetores e ignora suas magnitudes. Isso é desejável: o que interessa é a
*direção semântica* do texto, não sua intensidade ou comprimento.

Trabalha-se de forma equivalente com **distância** (quanto menor, mais próximo) ou
**similaridade** (quanto maior, mais próximo), sendo uma o complemento da outra. A
distância é a grandeza natural para ordenação; a similaridade é mais intuitiva para
definir um critério de aceitação.

---

## 7. Busca por similaridade

### 7.1 Vizinhos mais próximos

A operação fundamental é o **k-vizinhos-mais-próximos** (k-NN): dado o vetor da nova
entrada, recuperar os *k* vetores armazenados mais próximos dele. Conceitualmente é uma
ordenação por distância seguida de truncamento.

A busca exata exige, no pior caso, comparar com todos os itens — custo linear no tamanho
do acervo, inviável em escala. Daí a existência de **busca aproximada** (ANN, *approximate
nearest neighbor*), que troca garantia de exatidão por tempo de resposta sublinear
através de estruturas de índice especializadas.

Esse é mais um ponto onde o sistema aceita **aproximação em troca de eficiência** — e vale
notar que a aproximação aqui se soma à aproximação já introduzida pelo próprio embedding.

### 7.2 Filtragem antes da proximidade

Um ponto de projeto importante: a busca por similaridade **não ocorre sobre todo o
acervo**, e sim sobre o subconjunto compatível com o fingerprint atual. Isto é, filtra-se
primeiro por versão de prompt, versão de regras e capacidade do modelo; só então se busca
o vizinho mais próximo.

A justificativa é conceitual, não de desempenho: um item gerado sob outro conjunto de
regras **não é candidato válido**, por mais semanticamente próximo que seja. Similaridade
textual não supera incompatibilidade de contexto de geração. O fingerprint delimita o
universo; o embedding ordena dentro dele.

### 7.3 Candidato não é resposta

A busca responde "quais são os mais parecidos", nunca "algum deles serve". O resultado é
um conjunto de **candidatos ordenados**. A decisão de reutilização é uma etapa separada,
com critério próprio — separação que o projeto materializa em endpoints distintos, um para
buscar e outro para decidir.

---

## 8. Threshold: transformando proximidade em decisão

### 8.1 O papel do limiar

O **threshold** é o valor mínimo de similaridade a partir do qual um candidato é
considerado reutilizável. É a fronteira que converte uma medida contínua em uma decisão
binária: aceitar ou rejeitar.

Ele é o parâmetro mais sensível de todo o sistema. Não existe valor universalmente
correto: o valor adequado depende do domínio, do modelo de embedding, do custo de errar e
da tolerância do negócio.

### 8.2 Os dois tipos de erro

O problema é formalmente um **problema de classificação binária** (reutilizar ou não), com
os dois erros clássicos:

| Erro | O que acontece | Custo |
|---|---|---|
| **Falso positivo** — threshold baixo demais | Aceita-se um candidato que apenas *parece* próximo. Devolve-se uma resposta errada. | Alto e **silencioso**: o usuário recebe algo plausível porém incorreto, sem qualquer sinal de erro. |
| **Falso negativo** — threshold alto demais | Rejeita-se um candidato que serviria. Chama-se o modelo desnecessariamente. | Baixo e **visível**: custo e latência a mais, resposta correta. |

O exemplo canônico de falso positivo — "cancelar meu plano" versus "cancelar minha
reunião" — mostra o cerne da questão: **alta similaridade de superfície não implica
equivalência de intenção**. As frases compartilham estrutura e vocabulário, mas pedem
ações opostas.

### 8.3 A assimetria que orienta a calibragem

Os dois erros **não custam a mesma coisa**. Um falso negativo desperdiça dinheiro; um
falso positivo entrega informação errada e corrói a confiança no sistema — e não deixa
rastro evidente. Por isso a regra prática é **começar conservador (threshold alto) e
relaxar com base em evidência**, e não o contrário.

Em vocabulário de recuperação de informação, é o trade-off **precisão × cobertura**:
elevar o threshold aumenta a precisão das reutilizações e reduz a cobertura do cache;
baixá-lo faz o inverso. O threshold é, literalmente, o botão que escolhe entre economia e
segurança.

### 8.4 Threshold como parâmetro observável

Por ser empírico, o limiar precisa ser (a) ajustável sem reimplantação e (b) **visível na
resposta**. O sistema devolve, em cada requisição, o threshold aplicado, a similaridade do
melhor candidato, a decisão tomada e a justificativa. Isso torna a decisão **auditável**:
é possível reconstruir por que uma resposta foi reutilizada ou não — condição necessária
para calibrar o valor com dados reais em vez de intuição.

---

## 9. A cascata de cache

### 9.1 Camadas por custo crescente

O fluxo principal organiza as estratégias em uma **hierarquia por custo**, tentando sempre
a alternativa mais barata e mais segura antes da mais cara:

| Ordem | Camada | Critério | Custo | Risco de erro |
|---|---|---|---|---|
| 1 | Cache exato | Igualdade de fingerprint | Mínimo (acesso local) | Nenhum |
| 2 | Cache semântico | Similaridade ≥ threshold | Médio (embedding + busca) | Existe |
| 3 | Modelo | — | Alto | — |

A ordenação **não é arbitrária**: ela é simultaneamente crescente em custo e crescente em
risco. A camada mais barata é também a mais confiável, o que torna a ordem natural em
ambos os critérios.

### 9.2 Curto-circuito

Cada camada, ao acertar, encerra o processamento imediatamente. Um acerto no cache exato
sequer gera embedding ou consulta o acervo vetorial. Essa **avaliação preguiçosa** é o que
garante que o custo de uma requisição seja proporcional à camada que a resolveu, e não à
profundidade total do pipeline.

O paralelo com hierarquia de memória em arquitetura de computadores (registradores → cache
→ memória principal → disco) é direto e intencional: níveis sucessivamente maiores,
mais lentos e mais caros, consultados apenas quando os anteriores falham.

### 9.3 Política de escrita

O sistema grava no cache semântico **apenas no caminho do modelo**, e apenas ali. A regra
decorre de uma observação simples: nas outras camadas não há informação nova a preservar.

- Acerto exato → o item já existe; regravar seria duplicação pura.
- Acerto semântico → reutilizou-se um item existente; nada foi produzido.
- Chamada ao modelo → **surgiu conhecimento novo**, e só ele merece ser persistido.

Isso mantém uma invariante desejável: **o tamanho do acervo cresce na medida exata do
número de chamadas ao modelo**, jamais do volume de tráfego. O cache não incha com
repetição.

### 9.4 Auto-alimentação

O efeito combinado é um sistema que **melhora com o uso**. Cada miss que chega ao modelo
enriquece o acervo e amplia a região do espaço semântico coberta pelo cache. A taxa de
acerto tende a crescer ao longo do tempo, com retornos decrescentes conforme o espaço de
intenções recorrentes vai sendo coberto.

Fenômenos correlatos que decorrem dessa dinâmica:

- **Cold start** — no início (ou após uma troca de versão) o acervo está vazio e todo o
  tráfego é caro.
- **Aquecimento (warm-up)** — pode-se popular o acervo previamente com pares
  pergunta-resposta conhecidos, encurtando o período frio. O projeto prevê essa
  possibilidade ao expor a criação manual de itens.
- **Propagação de erro** — se uma resposta incorreta entra no acervo, ela passa a ser
  servida para todas as entradas semanticamente próximas. O erro deixa de ser pontual e
  vira sistemático, o que eleva a importância da política de admissão discutida adiante.

---

## 10. Observabilidade e explicabilidade

Um sistema com decisões probabilísticas em camadas é opaco por natureza. O projeto trata
observabilidade como requisito, não como acessório: cada resposta carrega a **procedência**
(qual camada resolveu), a **evidência** (similaridade obtida, limiar aplicado, candidato
escolhido), a **justificativa textual** da decisão, o **custo** (tempo decorrido, contagem
acumulada de chamadas ao modelo) e o **resultado da gravação**.

Três finalidades justificam esse esforço:

1. **Depuração** — sem procedência explícita, é impossível distinguir "o modelo
   classificou errado" de "o cache devolveu a resposta de outra pergunta".
2. **Calibragem** — ajustar o threshold exige o histórico de similaridades observadas e
   decisões tomadas.
3. **Confiança** — em contextos regulados ou críticos, entregar uma resposta reaproveitada
   sem explicitar que ela foi reaproveitada é um problema de transparência.

Isso conecta o projeto a uma discussão mais ampla de **IA explicável**: não basta acertar,
é preciso poder demonstrar por que se chegou àquela resposta.

---

## 11. Saída estruturada e contrato de dados

O sistema não trata a saída do modelo como texto livre. Ele impõe um **esquema**:
categoria pertencente a um conjunto fechado, um grau de confiança e uma justificativa
curta.

Três razões teóricas sustentam essa escolha:

1. **Cacheabilidade** — dados estruturados podem ser serializados, armazenados,
   comparados e revalidados. Texto livre é difícil de verificar ao ser recuperado.
2. **Contenção do não-determinismo** — restringir a saída a um conjunto enumerado reduz
   drasticamente o espaço de respostas possíveis e mitiga alucinação de categorias
   inexistentes.
3. **Validação na leitura** — o esquema permite revalidar o item ao recuperá-lo do
   acervo. Um registro corrompido ou incompatível com o esquema atual é detectado e
   tratado como miss, em vez de ser propagado ao usuário.

Esse último ponto merece destaque: **dados persistidos envelhecem**. Um item gravado sob
um esquema anterior pode não ser mais válido. Revalidar na leitura é o que impede que a
evolução do contrato quebre o sistema retroativamente.

De forma complementar, o uso de temperatura mínima na geração busca **reduzir a variância**
das respostas. Em tarefas de classificação, criatividade é ruído: quanto mais determinística
a saída, mais estável é o comportamento e mais confiável é o que se armazena.

---

## 12. Limitações conhecidas e evolução natural

Reconhecer o que o sistema **ainda não faz** é parte do valor didático do projeto.

### 12.1 Ausência de política de admissão

Atualmente, toda resposta do modelo é armazenada. Um sistema maduro decidiria **o que
merece entrar no cache**, com critérios como:

- **Confiança mínima** — não armazenar classificações em que o próprio modelo demonstrou
  baixa certeza, evitando cristalizar dúvidas.
- **Sensibilidade do conteúdo** — entradas com dados pessoais ou sigilosos não deveriam
  ser persistidas nem, muito menos, reutilizadas entre usuários.
- **Volatilidade da resposta** — informação que depende de estado que muda (saldo, status
  de pedido, disponibilidade) não é cacheável por natureza, ainda que a pergunta se
  repita.

### 12.2 Ausência de ciclo de vida

Não há expiração nem remoção. Faltam:

- **TTL (time-to-live)** — validade temporal, que limita a idade máxima de uma resposta.
- **Políticas de despejo (eviction)** — LRU, LFU e variantes, para conter o crescimento
  quando a capacidade é limitada.
- **Expurgo de versões obsoletas** — os itens de versões antigas do fingerprint ficam
  inalcançáveis, mas continuam ocupando espaço.

### 12.3 Ausência de isolamento entre consumidores

Não há noção de usuário ou organização. Em um ambiente multi-inquilino, a reutilização de
respostas entre inquilinos distintos é, ao mesmo tempo, uma falha de isolamento e um risco
de vazamento — o inquilino deveria ser mais uma dimensão do fingerprint.

### 12.4 Assimetria entre as camadas de armazenamento

O cache exato é volátil e local ao processo; o cache semântico é persistente e
compartilhado. Isso significa que o cache exato se perde a cada reinício e não é
compartilhado entre instâncias — em um ambiente distribuído, a mesma entrada geraria
misses em réplicas diferentes. A evolução natural é externalizar também a camada exata
para um armazenamento compartilhado.

### 12.5 Concorrência

Requisições idênticas simultâneas encontram o cache vazio ao mesmo tempo e disparam
múltiplas chamadas redundantes ao modelo — fenômeno conhecido como **cache stampede** ou
*thundering herd*. Mitigações usuais envolvem travas por chave ou coalescência de
requisições em voo.

### 12.6 Ausência de avaliação sistemática

Não há conjunto de referência que permita medir empiricamente a qualidade do cache. Um
sistema maduro manteria um conjunto rotulado de pares (entrada, resposta correta) para
medir taxa de acerto, taxa de falso positivo e economia real sob diferentes thresholds —
transformando a calibragem em processo mensurável em vez de tentativa e erro.

---

## 13. Síntese

O projeto demonstra, de forma incremental, que **cache em sistemas de IA é um problema
qualitativamente diferente de cache tradicional**.

No cache clássico, a identidade é exata, a decisão é binária e não há erro possível: ou a
chave existe ou não existe. Em sistemas de IA, a identidade útil é **semântica**, a
comparação é **aproximada** e a decisão de reutilizar é uma **aposta calibrada** — com
custo real quando erra.

A arquitetura resultante articula alguns princípios que se sustentam mutuamente:

1. **Estratificação por custo** — tenta-se sempre o mais barato e mais seguro primeiro.
2. **Identidade contextual** — a resposta pertence às condições sob as quais foi gerada, e
   o fingerprint torna isso explícito.
3. **Invalidação por versionamento** — troca-se de comportamento mudando o espaço de
   chaves, sem apagar nada.
4. **Aproximação com fronteira explícita** — o threshold materializa, em um único
   parâmetro observável e ajustável, o trade-off entre economia e correção.
5. **Cache como otimização, nunca como fonte de verdade** — qualquer falha degrada para o
   caminho caro, jamais para o erro.
6. **Decisão auditável** — toda resposta carrega procedência, evidência e justificativa.

A pergunta central do domínio, e a que resume o projeto inteiro, é: **quando duas
perguntas diferentes merecem a mesma resposta?** Não existe resposta universal. Existe um
critério explícito, mensurável e ajustável — e a qualidade do sistema é, em última
instância, a qualidade desse critério.
