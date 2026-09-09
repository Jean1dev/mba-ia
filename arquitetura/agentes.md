# Fundamentos Teóricos — Agentes, Ferramentas e Avaliação de Trajetória

Documento conceitual. O objetivo é isolar **as ideias**, independentemente da linguagem, do
framework de agentes, do formato de chamada de ferramenta ou do provedor de modelo.

O tema central é uma mudança de objeto de medida: tudo o que se avalia em um sistema de
perguntas e respostas é a **resposta**. Em um agente, o objeto é a **trajetória** — quais
ferramentas o modelo escolheu, em que ordem, com quais argumentos.

---

## 1. O que muda quando o sistema decide

### 1.1 Caminho fixo versus escolha

Um pipeline tem um caminho só: a entrada percorre etapas predeterminadas e produz uma saída.
Quem decidiu a sequência foi quem escreveu o código.

Um agente não tem caminho. A cada volta, o modelo decide entre agir, consultar, perguntar de
volta ou recusar. **A sequência de execução passa a ser saída do modelo, não do
programador.**

| | Pipeline | Agente |
|---|---|---|
| Sequência de etapas | escrita no código | decidida pelo modelo |
| Espaço de execuções | um caminho | combinatório |
| Efeitos colaterais | conhecidos de antemão | dependentes da decisão |
| Objeto de avaliação | a resposta | a trajetória |

A terceira linha é a que muda a natureza do risco. Um pipeline que erra devolve texto errado.
Um agente que erra pode **executar uma ação que ninguém pediu** — e ações têm consequências
que não se desfazem lendo a resposta com desconfiança.

### 1.2 Resposta certa não é caminho certo

O argumento decisivo para deslocar o objeto de medida. Considere um agente que responde:

> "Você usou 1320 GB de ingestão, 88% da cota."

Ele pode ter consultado o sistema de consumo, ou pode ter inventado o número. **A resposta é
idêntica nos dois casos.** Nenhuma avaliação que olhe apenas a saída final consegue separá-los.

Só a trajetória separa. E a distinção não é acadêmica: um agente que acerta pelo caminho
errado é **um sistema diferente** do que se pensa ter — e é um sistema que não se pode
alterar com segurança, porque o comportamento observado não é o comportamento real.

> Um agente que chega à resposta certa pelas ferramentas erradas é outro sistema. Só o
> segundo é seguro de mudar depois.

### 1.3 Chamar demais é erro

Conceito que simplesmente **não existe** em avaliação de resposta. Se o texto final está
certo, tanto faz quantas buscas foram feitas.

Para um agente, não tanto faz:

- cada chamada custa tempo e dinheiro;
- cada chamada consome contexto, degradando as decisões seguintes;
- **algumas chamadas mudam o mundo.**

Uma ação executada além do necessário é uma falha ainda que a resposta esteja perfeita. Isso
introduz uma categoria de critério — **ferramentas proibidas por caso** — sem equivalente na
avaliação de saída.

---

## 2. Ferramentas: projeto para observabilidade e avaliação

### 2.1 Três naturezas de ferramenta

Um conjunto mínimo de ferramentas que cobre o que um agente faz, e cada uma tem perfil de
risco próprio:

| Natureza | O que faz | Risco dominante |
|---|---|---|
| **Consultar** | busca conhecimento (pode ser um pipeline inteiro por dentro) | informação errada, custo |
| **Ler estado** | lê dado transacional vivo | exposição de dado, escopo indevido |
| **Agir** | escreve, cria, altera algo no mundo | **efeito irreversível** |

A separação importa porque **só a terceira produz efeito colateral**, e é a que se observa de
perto. Tratar as três com o mesmo rigor é ou excesso de cerimônia nas duas primeiras, ou
falta de cuidado na última.

### 2.2 Ferramenta pequena é ferramenta avaliável

Critério de desenho com consequência direta na mensurabilidade:

> Uma ferramenta que faz uma coisa legível é uma ferramenta cuja chamada dá para dizer,
> depois, se foi certa ou errada.

Uma ferramenta que recebe severidade e um resumo é verificável — dá para afirmar que a
severidade estava errada. Uma ferramenta genérica de "tratar a solicitação do usuário" não é:
a decisão real acontece dentro dela, invisível, e o único sinal que sobra é a saída final.

Granularidade de ferramenta é, portanto, uma decisão de **avaliabilidade**, não apenas de
organização de código.

### 2.3 A descrição da ferramenta é interface, não documentação

O modelo escolhe qual ferramenta chamar lendo as descrições. Isso as torna parte do
comportamento do sistema, com um status próximo do de código.

E a parte mais útil de uma descrição costuma ser o que ela **proíbe**:

> Use apenas quando o usuário pedir explicitamente. Responder a uma pergunta, por urgente
> que ela pareça, não é um pedido de ação.

Essa frase existe porque "meu sistema caiu, qual é o prazo de atendimento?" é uma **pergunta**
com aparência de urgência, e é exatamente onde um agente mal instruído executa uma ação por
conta própria. Descrever o caso limítrofe é mais eficaz que descrever o caso típico.

### 2.4 Duas validações, em dois lugares diferentes

A assinatura de uma ferramenta vira um esquema que o modelo lê **antes** de chamar. Isso cria
dois níveis de validação com naturezas distintas:

| Nível | Valida | Quando |
|---|---|---|
| **Esquema** | o que pode ser expresso como tipo (um conjunto fechado de valores, obrigatoriedade) | antes de a função rodar |
| **Função** | o que o tipo não alcança ("o resumo não pode ser vazio", "este identificador não existe") | durante a execução |

> O esquema valida o que ele consegue expressar; a função valida o resto.

Há um corolário prático: **duplicar no corpo da função uma verificação que o esquema já
garante produz código inalcançável**. A tentação de chamar isso de "defesa em profundidade" é
forte e, nesse caso, incorreta — o caminho simplesmente não existe.

### 2.5 Erro como dado versus erro como exceção

Distinção com consequência direta no laço do agente:

- **Erro devolvido como dado** ("identificador desconhecido") volta ao contexto e o modelo
  pode **reagir na mesma volta** — corrigir o argumento, tentar outra ferramenta, pedir
  esclarecimento.
- **Exceção** interrompe a execução e é tratada pelo runtime, fora do alcance do modelo.

As duas coisas são úteis, e a escolha entre elas é semântica: falha da qual o modelo pode se
recuperar é dado; violação de contrato é exceção. E as duas precisam ser avaliadas de formas
diferentes, porque a primeira faz parte do comportamento esperado e a segunda não.

### 2.6 Higiene do contexto: o que a ferramenta devolve

Uma ferramenta que envolve um pipeline complexo devolve **apenas o resultado** — a resposta e
as fontes. Prompts, trechos recuperados e diagnósticos ficam de fora.

Duas razões independentes:

- **Economia** — contexto é finito e caro; encher a transcrição de diagnóstico degrada todas
  as decisões seguintes.
- **Higiene** — transcrição de agente não é lugar para conteúdo interno. Ela é registrada,
  inspecionada e frequentemente exportada.

Há também uma perda a reconhecer: se a ferramenta devolve apenas prosa, o agente não tem como
distinguir "a busca não encontrou nada" de "a busca encontrou e a resposta é esta". Um campo
estruturado sinalizando ausência de resultado é informação que a ferramenta tem e joga fora —
e a ambiguidade reaparece como erro de comportamento do agente mais adiante.

---

## 3. Resultado estruturado e o princípio do cruzamento

### 3.1 Autodeclaração não é evidência

Se o agente devolve um resultado estruturado dizendo que executou uma ação, isso é **uma
afirmação do modelo sobre si mesmo**. Modelos erram ao narrar o que fizeram — e erram
justamente nos casos em que mais se precisa saber.

A trajetória real vem do registro que o **framework** mantém das chamadas efetuadas, nunca do
texto que o modelo escreveu sobre si.

> Uma trajetória reconstruída da narração do modelo está medindo a narração.

### 3.2 Capturas separadas para poder cruzar

Aqui está o ponto de projeto mais elegante do capítulo. Se o campo "ação executada" fosse
*derivado* da trajetória, ele seria sempre consistente com ela — e não haveria nada a
verificar.

Mantendo as duas capturas **independentes**, uma verificação se torna possível:

| Fonte | Origem |
|---|---|
| "executei a ação", identificador do resultado | o modelo |
| a ferramenta aparece na lista de chamadas | o framework |

Um modelo que afirma "abri o chamado TCK-12345" sem nunca ter chamado a ferramenta passa nas
duas primeiras e **falha na terceira**. Essa é a detecção de uma ação inventada, e ela só
existe porque as capturas são separadas.

> Redundância intencional entre fontes independentes é o que permite detectar
> inconsistência. Derivar um dado do outro elimina a verificação.

O padrão é geral: sempre que um sistema de IA afirma ter feito algo, procure a evidência
externa correspondente — e projete o sistema para que essa evidência exista.

---

## 4. O dataset de comportamento

### 4.1 Comportamento esperado, não resposta esperada

Um dataset de perguntas e respostas guarda **respostas esperadas**. Um dataset de agente
guarda **comportamento esperado**. Os campos refletem isso:

| Campo | O que cobra |
|---|---|
| **Ferramentas esperadas** | as que deveriam ser chamadas |
| **Ferramentas proibidas** | as que **não** deveriam — chamar demais é erro tão real quanto de menos |
| **Argumentos esperados** | os argumentos que importam, não todos |
| **Trajetória esperada** | a sequência |
| **Tipo de casamento** | como comparar a sequência (exato, em ordem, ordem livre) |
| **Teto de passos** | o freio contra o agente que fica tentando |
| **Desfecho** | responder, perguntar de volta, recusar, agir |

### 4.2 Famílias que existem para pegar erro de escolha

Um conjunto de famílias que cobre o espaço de decisão:

| Família | O que verifica |
|---|---|
| Consulta a conhecimento | usa a ferramenta de busca, **e só** |
| Leitura de estado | usa a ferramenta de estado, **e só** |
| Ação clara | executa, com os argumentos pedidos |
| Pedido ambíguo | **não** executa; pergunta de volta |
| Fora de escopo | recusa sem chamar nada |

As duas últimas são as difíceis, e são o motivo de o agente existir como objeto de estudo.
Elas não medem qualidade de resposta — medem **contenção**. Um agente que executa uma ação
diante de um pedido ambíguo cometeu o erro que tem consequência.

### 4.3 Pares de confusão: regra versus estado

Técnica de construção de dataset que vale como padrão geral. Duas perguntas quase idênticas
na superfície, com fontes de verdade completamente diferentes:

- *"O que acontece se eu ultrapassar a cota?"* → é **regra**, está em um documento
- *"Quanto eu já usei da minha cota?"* → é **estado**, está em um sistema

Um agente que responde consumo lendo documentação **inventa número**. Um agente que responde
política lendo o consumo **não tem o que dizer**. E os dois erros passariam por uma avaliação
que só olha a resposta final, porque nos dois casos sai um texto plausível.

Marcar esses pares explicitamente (com uma etiqueta própria) documenta a intenção do caso — e
impede que alguém, ao revisar, os considere duplicados e remova um.

### 4.4 Maquinário que nada testa

Regra de validação incomum e muito boa: **reprovar o dataset se nenhum caso exercitar mais de
um passo**.

Se todos os casos esperam uma única ferramenta, então os campos de trajetória e de modo de
casamento nunca são exercitados. O código existe, tem testes, parece funcionar — e nenhum
caso o executa de fato. É infraestrutura que dá a impressão de cobertura sem entregá-la.

O princípio generaliza: **se um mecanismo de avaliação existe, algum caso precisa depender
dele.** Caso contrário, ele é decoração.

### 4.5 Nomes vindos do código

Os nomes de ferramenta válidos são derivados das ferramentas que o agente realmente tem, não
digitados no dataset. Um caso que espera uma ferramenta inexistente não é um caso que falha —
é um caso **imensurável**.

Renomear uma ferramenta então quebra a validação do dataset **imediatamente**, em vez de
produzir uma métrica misteriosamente zerada dois meses depois.

### 4.6 Desfechos que se excluem

Validação de consistência interna: alguns desfechos são mutuamente exclusivos. Não se pode
esperar simultaneamente que o agente pergunte de volta **e** execute a ação; nem que recuse
**e** execute. Um caso de recusa ou de clarificação não pode esperar ferramenta nenhuma.

Isso parece obviedade, e é exatamente o tipo de obviedade que aparece em datasets escritos à
mão sob pressa — produzindo casos impossíveis de satisfazer.

---

## 5. Pontuação determinística da trajetória

### 5.1 Por que sem juiz-modelo

O objeto medido já é bastante não determinístico. Um medidor com variância própria tornaria
duas rodadas incomparáveis, e a pergunta central de avaliação de agente é comparativa: *este
prompt novo degradou a escolha de ferramentas?*

Felizmente, quase tudo o que importa em uma trajetória é **verificável por comparação**:
quais ferramentas, em que ordem, com quais argumentos, quantos passos, houve efeito. Nada
disso precisa de julgamento.

### 5.2 As propriedades

| Propriedade | O que cobra |
|---|---|
| Seleção de ferramentas | as esperadas foram chamadas |
| Ferramentas proibidas | as proibidas **não** foram |
| Integridade dos argumentos | os argumentos que importam estão corretos |
| Casamento da trajetória | a sequência é a esperada |
| Teto de passos | não passou do limite de chamadas |
| Clarificação | perguntou de volta quando devia |
| Recusa | recusou sem chamar nada |
| Execução da ação | agiu **e** a evidência confirma |
| Termos esperados | a resposta contém a informação cobrada |

Três merecem detalhe, porque são as que **não existiriam** em uma avaliação de resposta.

### 5.3 Ferramentas proibidas: a propriedade sem tolerância

Já argumentado na seção 1.3. O que vale acrescentar é a consequência para o limiar: essa é a
propriedade que **não admite grau**. Uma taxa de acerto de 90% em seleção de ferramentas é
uma discussão razoável; 90% em "não executou ação proibida" significa que uma em dez
execuções fez algo que não devia.

> Propriedades sobre efeitos colaterais são binárias. Ou aconteceu, ou não.

### 5.4 Argumentos: subconjunto, não igualdade

O dataset fixa **o que importa** e deixa o resto livre. Se a expectativa é que a severidade
seja um valor específico, cobra-se a severidade — e não o resumo, nem o identificador
derivado do contexto.

Exigir o objeto de argumentos inteiro obrigaria o dataset a ditar o texto do resumo, que é
justamente a parte que o agente deve escrever sozinho.

> Cobra-se a decisão, não a redação.

É o mesmo princípio dos termos literais em avaliação de resposta, aplicado a argumentos.

### 5.5 A propriedade de cruzamento

A verificação de que a ação aconteceu exige **três coisas juntas**: o modelo afirma que agiu,
existe um identificador de resultado, **e** a ferramenta aparece na trajetória.

As duas primeiras vêm do modelo; a terceira vem de fora dele. É a aplicação prática da
seção 3.2, e é o que transforma um princípio de projeto em uma propriedade mensurável.

### 5.6 Três modos de comparar uma sequência

| Modo | Passa quando | Para quê |
|---|---|---|
| **Exato** | a sequência é idêntica | caso de uma ferramenta só, ou de nenhuma |
| **Em ordem** | as esperadas aparecem na ordem, extras tolerados | caso encadeado |
| **Ordem livre** | todas aparecem, ordem irrelevante | quando a ordem não carrega significado |

O modo "em ordem" é o conceitualmente mais rico, e a razão aparece no caso encadeado:

> *"Estamos perto do limite? Se estiver acima de 85%, execute a ação."*

O esperado é consultar o estado e **depois** agir. Se o agente agisse **antes** de consultar,
teria acertado o conjunto de ferramentas e **errado o raciocínio**: a segunda chamada só se
justifica pelo resultado da primeira.

**Ordem, aqui, é semântica.** Ela codifica dependência causal entre passos. Só o modo "em
ordem" captura isso — o modo de ordem livre passaria, e o exato reprovaria por qualquer passo
extra legítimo.

### 5.7 Efeito colateral exige isolamento entre rodadas

Ferramentas que escrevem acumulam estado. Sem reinicialização, a segunda rodada pontua contra
artefatos da primeira, e as métricas passam a depender do histórico de execuções.

Duas abordagens: reinicializar o estado antes de cada rodada, ou identificar cada rodada e
filtrar. A primeira é mais simples e não exige alterar a ferramenta — o que importa quando a
ferramenta é o objeto sob teste. **Avaliação de sistema com efeito colateral precisa de um
ambiente descartável**, e isso é requisito de infraestrutura, não detalhe.

---

## 6. Ler os resultados: três tipos de falha

Uma rodada de avaliação de agente produz falhas de naturezas diferentes, e classificá-las é
metade do valor da atividade.

### 6.1 Falha do critério

Um caso: o agente recusa uma pergunta fora de escopo de forma impecável — nenhuma ferramenta
chamada, nada inventado, resposta educada e correta. E **reprova**, porque o evaluator exigia
que o campo "tarefa concluída" fosse falso.

Só que o agente está certo: **recusar é tratar a solicitação por inteiro.** Nada ficou
pendente. O campo que deveria ser falso é o de clarificação, onde algo de fato ficou em
aberto.

É o padrão **certa como escrita, errada como definida**, o mesmo que aparece na avaliação por
componente e no juiz-modelo. E a correção pertence a uma versão nova do critério, não a um
ajuste feito depois de ver o resultado.

Reconhecer esse tipo de falha é o que impede duas reações erradas: "consertar" um agente que
está correto, e desconfiar de uma suíte que está funcionando.

### 6.2 Falha herdada de uma camada inferior

Outro caso: o agente escolheu a ferramenta certa, e **a ferramenta não encontrou a
informação**. A falha é da camada de recuperação, três níveis abaixo, e já era conhecida da
avaliação por componente.

O agente errou apenas no desdobramento: em vez de dizer que a informação não está disponível,
perguntou outra coisa. E a origem dessa ambiguidade é rastreável — a ferramenta devolve prosa
sem um sinal estruturado de "não encontrei" (seção 2.6).

Avaliação em camadas paga aqui: sem a camada inferior, essa falha seria atribuída ao agente.

### 6.3 Falha genuinamente discutível

Terceiro caso: o pedido traz a severidade mas não diz qual é o problema. O agente pediu
detalhe; o dataset esperava a ação executada.

Quem está certo depende do produto. Um registro de chamado dizendo "usuário tem uma dúvida"
é quase inútil para quem vai atender — o que sugere que o agente está certo e o **caso
precisa ser reescrito**.

Esse tipo de resultado é sinal de saúde do processo: a avaliação está expondo uma ambiguidade
real do produto, não um defeito do sistema.

### 6.4 Resultados que confirmam ausência de risco

Vale registrar o oposto também. Se a propriedade de ferramentas proibidas fecha em 100% e o
teto de passos nunca é atingido, isso **é um resultado**, não ausência de resultado: era o
risco principal, e não se concretizou. Medição que confirma segurança tem valor igual à que
encontra defeito — e sem ela a segurança é suposição.

---

## 7. O prompt como superfície de regressão

Um episódio que resume por que essa avaliação existe. A primeira versão da instrução dizia:

> Se faltar severidade, impacto ou um resumo, faça uma pergunta de esclarecimento.

O modelo leu como **checklist obrigatório** e, diante de um pedido que **já trazia**
severidade e descrição do problema, pediu "impacto detalhado e um resumo breve". Correto pela
letra da instrução, errado pelo produto.

A correção foi separar o que **falta** do que **já foi dado**:

> Para executar a ação você precisa de duas coisas: a severidade e o que está quebrado.
> Quando o usuário fornece as duas, isso é suficiente — escreva o resumo você mesmo. Não peça
> detalhes que ele já deu.

Nenhuma linha de código mudou. Só o prompt.

Duas conclusões:

- **Prompt é código com relação à regressão, e não é com relação à revisão.** Uma alteração
  de uma frase muda o comportamento do sistema, e não aparece em nenhum teste de tipos, lint
  ou compilação.
- É exatamente esse tipo de regressão que uma avaliação de trajetória captura sem ninguém
  testar à mão — e que uma avaliação de resposta talvez nem note, porque a pergunta de
  esclarecimento é um texto perfeitamente bem escrito.

---

## 8. Limitações conhecidas e evolução natural

### 8.1 Não há autorização entre decisão e execução

A decisão do modelo **é**, na prática, a autorização. Não existe camada externa que consulte
uma política — "este contexto pode executar esta ferramenta com estes argumentos?" — nem
etapa de confirmação humana para ações com efeito.

O tratamento aprofundado desse risco está no capítulo de segurança: escolher uma ferramenta e
ter permissão para executá-la são coisas diferentes.

### 8.2 Argumentos não estão amarrados a identidade

Se um argumento identifica o escopo em que a ferramenta opera (qual cliente, qual conta) e
esse argumento é **livremente preenchido pelo modelo**, então o escopo é uma sugestão. O
correto é derivá-lo da identidade autenticada da requisição, fora do alcance do modelo.

### 8.3 O teto de passos é critério de avaliação, não limite de execução

O teto existe no dataset, medindo se o agente estourou. Não existe no runtime, impedindo que
ele estoure. São coisas diferentes, e a segunda é a que protege em produção.

### 8.4 Avaliação é offline

Toda a medição acontece contra um dataset, antes do deploy. Nada observa trajetórias reais em
produção, onde as entradas são mais variadas e mais criativas do que qualquer dataset curado.

### 8.5 O espaço de trajetórias é combinatório

Com poucas ferramentas e poucos passos, enumerar os casos interessantes é factível. Conforme
o número de ferramentas cresce, o espaço de sequências possíveis explode, e um dataset escrito
à mão cobre uma fração decrescente dele. Não há solução simples — há geração de casos,
teste baseado em propriedades e avaliação sobre tráfego real, todos com custo próprio.

### 8.6 Ausência de memória e de coordenação

O objeto estudado é deliberadamente mínimo: um laço, poucas ferramentas, sem memória entre
sessões e sem múltiplos agentes. Cada uma dessas ausências, quando preenchida, adiciona um
eixo inteiro de avaliação — estado que persiste entre execuções e decisões distribuídas entre
agentes são problemas qualitativamente novos.

---

## 9. Síntese

Um agente não é um pipeline com mais capacidades. É um sistema em que **a sequência de
execução deixou de ser escrita por um programador** — e isso desloca o objeto de avaliação da
resposta para a trajetória.

Os princípios que se sustentam mutuamente:

1. **Resposta certa não é caminho certo** — a mesma saída pode vir de uma consulta real ou de
   um número inventado, e só a trajetória distingue.
2. **Chamar demais é erro** — noção inexistente em avaliação de resposta, essencial quando
   uma das chamadas muda o mundo.
3. **Ferramenta pequena é ferramenta avaliável** — granularidade é decisão de
   mensurabilidade; a descrição é interface, e o que ela proíbe é a parte útil.
4. **O esquema valida o que consegue expressar; a função valida o resto** — e erro como dado
   é diferente de exceção, porque um o modelo pode corrigir.
5. **Autodeclaração não é evidência** — a trajetória vem do registro do framework, e capturas
   separadas são o que permite cruzar e detectar ação inventada.
6. **O dataset guarda comportamento, não resposta** — com ferramentas proibidas, argumentos
   por subconjunto, sequência e teto de passos.
7. **Pontuação determinística para objeto não determinístico** — quase tudo em uma trajetória
   é verificável sem julgamento, e isso é o que torna duas rodadas comparáveis.
8. **Ordem pode ser semântica** — quando um passo só se justifica pelo resultado do anterior,
   a sequência codifica raciocínio.
9. **Classificar a falha antes de consertar** — critério errado, camada inferior e caso
   discutível pedem ações completamente diferentes.

A pergunta que resume o capítulo: **como se verifica que um sistema fez o que disse ter
feito?** A resposta é não acreditar nele: capturar a evidência por um canal independente,
projetar as ferramentas para que cada chamada seja legível, e escrever o comportamento
esperado antes de medi-lo.
