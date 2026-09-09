# Fundamentos Teóricos — Observabilidade e Governança em Sistemas de Inteligência Artificial

Documento conceitual. O objetivo é isolar **as ideias**, independentemente da linguagem, do
framework de instrumentação, do backend de traces ou do provedor de modelo. Toda a discussão
continua válida se a stack for trocada por completo — e essa afirmação, aqui, não é retórica:
a tese central do capítulo é justamente que a aplicação não deve conhecer o backend.

---

## 1. O problema de fundo: por que observar IA é diferente

### 1.1 Três propriedades que quebram o instrumental clássico

Monitoramento tradicional pressupõe que o sistema é determinístico e que a corretude é
verificável localmente: dada a entrada, existe uma saída certa, e o que interessa medir é
disponibilidade, latência e taxa de erro. Uma chamada a um modelo generativo viola as três
premissas:

| Propriedade | Consequência para a observabilidade |
|---|---|
| **Não-determinismo** | Reproduzir um incidente executando de novo **não** garante o mesmo resultado. O registro da execução original passa a ser a única evidência disponível. |
| **Custo por execução** | Cada requisição consome orçamento. Volume deixa de ser só uma questão de capacidade e passa a ser uma questão financeira, portanto uma grandeza a instrumentar. |
| **Decisão opaca** | Não existe stack trace de um raciocínio. Quando a resposta está errada, nada no processo indica *onde* ela se tornou errada. |

A terceira é a mais grave. Em um pipeline com várias etapas — planejar a busca, recuperar,
reordenar, responder — uma resposta ruim pode nascer em qualquer uma delas, e todas
"funcionaram" no sentido operacional: nenhuma lançou exceção, nenhuma estourou tempo.

### 1.2 As três perguntas que a telemetria precisa responder

1. **O que aconteceu nesta execução?** Quais etapas rodaram, o que cada uma decidiu, quanto
   tempo levou.
2. **Quanto isso custou?** Tokens por modelo, custo estimado, consumo acumulado.
3. **Por que esta resposta e não outra?** Qual plano de busca, quais filtros, quantos e
   quais candidatos, o que sobreviveu ao corte.

Sistemas convencionais respondem bem a (1) e ignoram (2) e (3). Em IA as três são
obrigatórias, e a terceira é o que transforma telemetria em **explicabilidade**.

### 1.3 Log, métrica e trace: papéis distintos

- **Log** é o registro de um evento pontual. Barato, textual, difícil de agregar.
- **Métrica** é um número agregado ao longo do tempo. Ótimo para tendência, incapaz de
  explicar um caso individual.
- **Trace** é a **estrutura causal** de uma execução: quais operações aconteceram, aninhadas,
  em que ordem e por quanto tempo.

Para um pipeline de IA o trace é o instrumento primário, porque a pergunta relevante quase
nunca é "quantos erros por minuto" e quase sempre "o que exatamente aconteceu naquela
requisição". Métrica diz que algo piorou; trace diz onde.

---

## 2. Tracing aplicado a um pipeline de IA

### 2.1 Vocabulário

- **Span** — uma unidade de trabalho com início, fim, nome, atributos e status. É a peça
  atômica.
- **Trace** — a árvore de spans de uma execução, ligada por relação pai-filho.
- **Contexto de propagação** — o mecanismo que permite a um span saber quem é seu pai, mesmo
  atravessando funções, threads ou processos.
- **Atributo** — par chave-valor que descreve a operação.
- **Evento** — algo que ocorreu *dentro* de um span, com marca de tempo própria.

### 2.2 O pipeline como árvore

A modelagem natural é **um span raiz para a execução inteira e um span filho por etapa**:

```
ai.rag.pipeline                      (raiz: request_id, feature, tenant, resultado, tempo total)
├── ai.rag.query_planning            (o que o plano decidiu)
├── ai.rag.retrieval                 (quantos candidatos, com quais filtros)
├── ai.rag.reranking                 (quantos sobreviveram)  [existe só se a etapa rodou]
└── ai.rag.answer_generation         (modelo, tokens, houve resposta)
```

Duas propriedades emergem dessa forma, e nenhuma delas é acidental:

**Atribuição de latência.** Com um span por etapa, "a requisição levou 4,5 segundos" vira
"3,1 s foram reranking". Sem a decomposição, o tempo total é um número sem endereço.

**Ausência informativa.** Um span que **não existe** é um dado. Se `reranking` não aparece,
ou a etapa estava desligada, ou o fluxo terminou antes dela. A estrutura do trace carrega
informação sobre o caminho percorrido, não apenas sobre os tempos.

### 2.3 Granularidade é decisão de projeto

Spans demais produzem ruído e custo de armazenamento; spans de menos produzem um trace que
não explica nada. O critério útil é: **um span por etapa que pode falhar de um jeito
próprio, ou cujo custo se quer atribuir separadamente**. Etapas determinísticas e baratas
(normalizar texto, montar um filtro) não merecem span; toda chamada a modelo merece.

---

## 3. Instrumentação e backend: a fronteira que sustenta tudo

### 3.1 O acoplamento que se quer evitar

A forma ingênua de instrumentar é importar o SDK da ferramenta escolhida e chamá-lo direto
no código do domínio. O resultado é que **a decisão de qual ferramenta usar fica gravada em
toda a base de código**. Trocar de ferramenta passa a ser refatoração.

### 3.2 Padrão aberto como fronteira de dependência

A alternativa é depender apenas de um **padrão de instrumentação** — uma API neutra, com
vocabulário próprio de spans e atributos — e deixar o destino dos dados como configuração.
A aplicação diz "abra um span chamado X com estes atributos"; quem recebe isso é decidido
fora dela.

Isso é **inversão de dependência aplicada à telemetria**. A regra prática que decorre:

> A aplicação depende do padrão, nunca do SDK de um backend específico. Para onde os traces
> vão é decisão de **configuração**, não de código.

O teste dessa afirmação é empírico e vale como hábito: procurar o nome da ferramenta no
código do domínio. Se ele aparece, o acoplamento existe. Se aparece apenas na montagem de um
endereço e de um cabeçalho de autenticação, a fronteira está de pé — trocar o destino é
trocar variável de ambiente, e o mesmo trace aparece em outro lugar **sem uma linha alterada**.

### 3.3 Falar a língua do ecossistema: convenções semânticas

Existe um segundo nível de padronização, além da API: os **nomes** dos atributos.
Convenções semânticas são vocabulários acordados para descrever tipos recorrentes de
operação — requisição HTTP, consulta a banco e, mais recentemente, chamada a modelo
generativo (modelo requisitado, modelo respondido, tokens de entrada, tokens de saída).

O ganho é concreto e um pouco surpreendente na primeira vez que se vê: um backend que
reconhece essas convenções classifica sozinho o span como **uma geração de modelo**, com
tokens e custo calculados, enquanto os outros spans permanecem genéricos. Ninguém informou
isso ao backend — ele leu o vocabulário.

A regra que sai daí:

> Use o vocabulário do padrão para o que o padrão já nomeia; use um prefixo próprio
> (`app.*`) para o que é específico do seu domínio.

Nome próprio para conceito padronizado é perda gratuita de interoperabilidade. Nome
padronizado para conceito próprio é mentira semântica.

### 3.4 O custo de um backend não é uniforme

Duas ferramentas que recebem o mesmo trace podem ter arquiteturas radicalmente diferentes.
Um visualizador de traces pode caber em um único processo; uma plataforma que armazena
milhões de traces, calcula custo por modelo e mantém datasets de avaliação tende a exigir
um banco relacional, um banco colunar, uma fila, um armazenamento de blobs e workers —
porque a ingestão é assíncrona por necessidade.

A lição arquitetural é que **complexidade operacional de um backend é proporcional às
garantias que ele oferece**, e nem todo estágio do desenvolvimento precisa de todas as
garantias. Um caminho sensato tem três degraus:

| Degrau | Para quê | Custo operacional |
|---|---|---|
| Saída no console | verificar que a instrumentação existe e está correta | nenhum |
| Visualizador mínimo | ver a árvore, os tempos e os atributos | um processo |
| Plataforma completa | histórico, custo por modelo, avaliação, comparação | vários processos |

E como o código depende do padrão, subir ou descer degraus não é migração.

---

## 4. O que se pode observar: o limite do dado

### 4.1 Metadado operacional versus conteúdo

Há duas naturezas de informação em uma execução de IA:

- **Metadado operacional** — identificadores, contagens, sinalizadores, filtros aplicados,
  tempos, tokens, nome do modelo. Descreve a operação.
- **Conteúdo** — a pergunta do usuário, os prompts, o contexto montado, o texto dos
  documentos recuperados, a resposta. Descreve o assunto.

A distinção é a base de toda a política: **metadado é observabilidade; conteúdo é dado
sensível**. Contagens e tempos podem viajar para qualquer ambiente; texto bruto do usuário
não.

O critério prático é perguntar o que se perde ao não enviar. Sem os tempos por etapa não se
sabe onde a latência mora. Sem a pergunta do usuário ainda se sabe que houve uma pergunta,
que ela produziu tal plano, recuperou tantos chunks e gerou resposta em tanto tempo. A
telemetria continua útil; o vazamento não acontece.

### 4.2 Atributo e evento não são a mesma coisa

Quando conteúdo *precisa* ser capturado — em desenvolvimento, para depurar —, ele não deve
entrar como atributo, e sim como **evento**. A razão é conceitual, não estética:

- **Atributo** descreve a operação, viaja em todo ambiente, e é por onde se filtra e se
  agrega. É a chave de consulta.
- **Evento** é algo que aconteceu dentro do span, com natureza de dado distinta, opcional e
  separável.

Manter conteúdo bruto fora dos atributos impede que ele se torne, silenciosamente, parte da
superfície de consulta e agregação — e portanto parte de tudo o que se exporta, se
compartilha e se retém.

### 4.3 Telemetria é uma cópia secundária dos dados

Este é o ponto que mais frequentemente escapa. Ao instrumentar, cria-se **um segundo lugar
onde os dados vivem**, com sua própria política de retenção, seu próprio controle de acesso
e seus próprios usuários. Um sistema que trata dados sensíveis com cuidado no caminho
principal e os despeja em traces não protegeu nada: apenas mudou o endereço do problema.

Corolários:

- Segredos (chaves de API, credenciais de banco) **nunca** são atributo, em nenhuma
  circunstância.
- Ao anunciar a configuração de telemetria na subida, imprimem-se os **nomes** dos
  cabeçalhos, nunca os valores — o valor é a credencial.
- "O backend é interno" não é um controle de segurança. É uma afirmação sobre topologia de
  rede, não sobre autorização.

### 4.4 Duas regras menores, de consequência grande

**Erro sem stack trace.** Quando uma etapa falha, o span é marcado com status de erro
contendo tipo e mensagem da exceção. Rastreamento de pilha frequentemente carrega valores de
variáveis locais — isto é, conteúdo.

**Valor que não existe não é enviado.** Atributo ausente é diferente de atributo com valor
vazio ou nulo. O primeiro é honesto; o segundo polui agregações e induz leituras erradas.

---

## 5. Política de telemetria por ambiente

### 5.1 O que é aceitável observar depende de onde a aplicação roda

Não existe uma configuração de observabilidade correta para todos os ambientes, porque as
restrições são diferentes: em desenvolvimento os dados são fictícios e o interesse é máximo
detalhe; em produção os dados são reais e o interesse é volume controlado com risco mínimo.

Um único parâmetro de ambiente pode governar duas decisões independentes:

| Decisão | Pergunta |
|---|---|
| **Quanto** coletar | qual fração das execuções é registrada |
| **O que** se permite coletar | conteúdo bruto é autorizado neste ambiente? |

O ponto importante é que **reduzir risco em produção não significa observar menos**. A
telemetria operacional permanece integral: identificadores, contagens, filtros, tempos,
modelo, tokens. O que muda é o volume (amostragem) e a permissão para conteúdo.

### 5.2 Amostragem: a decisão vale para o trace inteiro

Registrar todas as execuções em alto volume é caro. Amostragem resolve, mas introduz uma
questão de coerência: se cada span decidisse individualmente se é gravado, o resultado
seriam traces pela metade — a raiz sem as etapas, ou etapas sem raiz.

A propriedade desejada é que a decisão seja tomada **uma vez, na raiz, e herdada por todos
os descendentes**. Um trace incompleto é pior que trace nenhum: ele parece um sistema que
pulou etapas.

### 5.3 Política verificada na subida, não em tempo de uso

Uma configuração perigosa (captura de conteúdo ligada em produção) não deve "não fazer
nada": deve **impedir a aplicação de iniciar**, com mensagem explícita. A diferença entre as
duas abordagens é enorme na prática:

- Flag que é ignorada fora de desenvolvimento cria a crença de que ligá-la é inofensivo, e
  cria a expectativa errada de que ela funciona.
- Validação que recusa a subida transforma um risco silencioso em uma falha imediata e
  legível.

É o princípio de **falhar cedo e alto** aplicado a política de dados: a porta não é
"ineficaz" no ambiente errado, ela **não abre**.

### 5.4 O interruptor e o custo de estar desligado

Toda a instrumentação precisa de um único ponto de desligamento — e, desligada, o custo deve
ser praticamente nulo. Isso é viável porque uma API de instrumentação bem projetada devolve,
quando não há destino configurado, objetos que aceitam todas as chamadas e não gravam nada.

O ganho de projeto é que **o código do domínio não precisa de condicionais de
observabilidade**. Ele sempre abre spans e sempre registra atributos; se há um destino
configurado, os dados existem; se não há, as chamadas são inertes. Instrumentação
condicional espalhada pelo domínio é a forma mais confiável de produzir telemetria
inconsistente.

### 5.5 Isolamento da instrumentação

Nomes de span, nomes de atributo e a montagem do destino ficam **em um módulo só**. O
domínio chama duas ou três funções e nada mais sabe. Consequências: renomear um atributo é
mudança em um lugar; auditar tudo o que a aplicação emite é ler um arquivo; e o vocabulário
não deriva com o tempo, como sempre acontece quando cada ponto do código escolhe seus
próprios nomes.

---

## 6. Correlação: o identificador que atravessa as camadas

Cada execução recebe um identificador único, e ele aparece **nos três lugares**: na linha de
log estruturado, como atributo do span raiz e no diagnóstico devolvido a quem chamou.

Isso resolve o problema que aparece no primeiro incidente real: alguém relata uma resposta
errada. Sem identificador compartilhado, é impossível ligar o relato ao trace, e o trace ao
log. Com ele, o caminho é direto — e a investigação parte de evidência, não de tentativa de
reprodução (que, num sistema não determinístico, pode simplesmente não reproduzir).

Um detalhe de fronteira que vale nomear: recursos de inspeção **local** (imprimir o prompt no
terminal do desenvolvedor) não são observabilidade. Não existem na interface de rede, não vão
para span nenhum e não devem ser confundidos com telemetria de produção. São duas atividades
com propósitos e riscos diferentes.

---

## 7. Da observabilidade à governança

### 7.1 Painel e freio

Observabilidade mostra **o que aconteceu**. Governança decide **o que ainda pode acontecer**.
É a diferença entre um painel e um freio, e um não substitui o outro: um gráfico de custo
crescente informa; ele não impede a próxima requisição caríssima.

### 7.2 Onde a decisão mora

O ponto de aplicação é o começo absoluto do fluxo: **antes** de qualquer etapa que gere
custo — antes de planejar, antes de gerar embedding, antes de qualquer chamada a modelo. Uma
política aplicada no meio do pipeline autoriza depois de já ter gasto.

Três regras cobrem a maior parte do risco operacional, e cada uma responde a um tipo
distinto de descontrole:

| Regra | Risco que endereça |
|---|---|
| **Lista de modelos permitidos** | alguém coloca em produção um modelo caro sem revisão. A troca de um identificador de modelo é uma mudança de uma linha com impacto financeiro de ordens de grandeza. |
| **Orçamento por período** | consumo cresce sem teto. Limita o dano acumulado, não a requisição individual. |
| **Teto de tokens de saída** | uma resposta longa demais. Limita o custo por chamada, aplicado no próprio modelo. |

As duas primeiras são **decisões de admissão**; a terceira é uma **restrição de execução**.
Confundi-las produz políticas que verificam o que não podem controlar.

### 7.3 O ledger e o ciclo fechado

Para saber se o orçamento foi atingido é preciso um histórico de consumo. Toda execução que
realmente chamou o modelo grava um registro com identificador, momento, escopo (inquilino,
funcionalidade), modelo, tokens e custo estimado.

O ciclo se fecha: **usar consome orçamento, orçamento consumido bloqueia o uso**. E o
registro obedece à mesma regra de conteúdo das seções anteriores — contagens e custo, nunca
pergunta, prompt, contexto ou resposta.

### 7.4 Bloqueio de política não é falha de sistema

Uma decisão de projeto sutil e importante: quando a política bloqueia, o usuário recebe uma
**resposta controlada**, não um erro. A requisição foi processada com sucesso; o resultado é
que ela não podia ser atendida.

Tratar bloqueio como erro tem duas consequências ruins. Operacionalmente, contamina as
métricas de erro com eventos que não são defeito, e dispara alertas para um sistema que está
funcionando exatamente como projetado. Semanticamente, mente sobre o que aconteceu.

> Bloqueio de política não é falha; é o sistema funcionando.

### 7.5 Governança pressupõe medição

O ponto mais elegante da relação entre os dois temas: **a governança não precisou de
instrumentação nova**. Os tokens já eram medidos, o escopo já era conhecido, os tempos já
eram registrados. A política apenas deu **consequência** ao que já se media.

Isso sugere uma ordem de construção. Instrumente primeiro, mesmo sem saber ainda que
decisões tomará; medição sem consequência é apenas um painel, mas consequência sem medição é
impossível. E, uma vez que a política existe, sua decisão volta para a telemetria — decisão
tomada, motivo, orçamento, gasto acumulado — fechando o laço: o que se mede alimenta o que
se decide, e o que se decide volta a ser medido.

### 7.6 Cobertura da política é parte do desenho

Uma política vale para os caminhos que passam por ela. Caminhos alternativos — ferramentas de
laboratório, comparações manuais, e sobretudo **outros fluxos de produção** que chamam modelo
por conta própria — ficam fora, e isso precisa ser uma escolha registrada, não uma
descoberta. A pergunta "quais caminhos deste sistema chamam modelo, e quantos passam pela
política?" tem que ter resposta escrita.

---

## 8. Limitações conhecidas e evolução natural

Reconhecer o que a implementação **ainda não faz** é parte do valor didático.

### 8.1 Contabilidade não é faturamento

Uma tabela de preços embutida no código, um arquivo local lido por inteiro a cada
requisição, sem transação nem coordenação entre processos: isso é uma **simulação
arquitetural**, útil para mostrar onde a decisão mora e como ela se conecta ao que já era
medido. Um sistema real precisa de contador transacional em banco ou cache distribuído,
preços versionados como configuração e reconciliação com a fatura do provedor.

### 8.2 Custo estimado não é custo real

Tokens contados localmente e multiplicados por uma tabela dão uma estimativa. Cache do
provedor, descontos, arredondamentos e cobranças por outras dimensões fazem o número
divergir. Estimativa serve para decidir; não serve para cobrar.

### 8.3 Concorrência na política

Requisições simultâneas leem o mesmo consumo acumulado e todas concluem que há orçamento.
O teto pode ser ultrapassado por uma margem proporcional à concorrência. É o mesmo tipo de
problema de leitura-e-escrita não atômica que aparece em qualquer contador compartilhado.

### 8.4 Amostragem versus investigação de casos raros

Amostragem uniforme registra 10% de tudo — inclusive 10% dos casos interessantes. Um sistema
maduro usa amostragem enviesada: registrar sempre erros, sempre execuções lentas, sempre
bloqueios de política, e amostrar apenas o tráfego normal.

### 8.5 Retenção e acesso ao backend

Onde os traces param, por quanto tempo ficam e quem pode lê-los é decisão de implantação, e
fica fora do escopo da aplicação — mas não fora do escopo do risco.

---

## 9. Síntese

Observabilidade em sistemas de IA não é a extensão natural do monitoramento clássico; é uma
resposta a um problema diferente. O sistema é não determinístico, então a execução original é
a única evidência; custa dinheiro por requisição, então custo é grandeza de primeira classe;
e decide de forma opaca, então procedência e evidência precisam ser explícitas.

Os princípios que se sustentam mutuamente:

1. **Trace como instrumento primário** — a estrutura causal da execução, com um span por
   etapa que pode falhar ou custar de forma própria.
2. **Padrão como fronteira** — a aplicação depende de uma API neutra de instrumentação;
   o destino é configuração, nunca código.
3. **Vocabulário emprestado onde ele existe** — convenções semânticas fazem o ecossistema
   entender a telemetria sem combinar nada; nome próprio só para o que é próprio.
4. **Metadado é observabilidade, conteúdo é dado sensível** — e telemetria é uma cópia
   secundária dos dados, com todos os deveres que isso implica.
5. **Política por ambiente, verificada na subida** — o que é aceitável observar depende de
   onde se roda, e configuração perigosa impede o início em vez de ser ignorada.
6. **Correlação por identificador único** — o mesmo id no log, no trace e no diagnóstico é o
   que torna um relato investigável.
7. **Governança dá consequência ao que se mede** — a decisão mora antes do primeiro custo, e
   bloqueio de política é resultado legítimo, não erro.

A pergunta que resume o capítulo: **o que precisa estar registrado para que uma resposta
errada seja explicável depois, sem que o registro se torne, ele mesmo, um problema?** A
resposta é uma linha traçada com cuidado entre o que descreve a operação e o que descreve o
assunto — e a qualidade do sistema observável é a qualidade dessa linha.
