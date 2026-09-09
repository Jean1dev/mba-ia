# Fundamentos Teóricos — Avaliação de Sistemas de Inteligência Artificial

Documento conceitual. O objetivo é isolar **as ideias** de medição de qualidade em sistemas
generativos, independentemente da linguagem, do framework de avaliação, da plataforma de
experimentos ou do provedor de modelo.

O tema é o inverso do que se costuma esperar: o pipeline que produz respostas é a parte
pequena. **Medir se ele está certo é a parte grande.**

---

## 1. O problema de fundo: não existe passa/falha natural

### 1.1 Teste e avaliação são atividades diferentes

Um teste de software clássico compara a saída observada com a saída esperada e devolve um
booleano. Isso pressupõe duas coisas que uma saída em linguagem natural não oferece:
determinismo e resposta única correta.

| | Teste | Avaliação |
|---|---|---|
| Objeto | comportamento determinístico | comportamento probabilístico |
| Resultado | passa ou falha | pontuação em um contínuo |
| Repetição | mesma entrada, mesmo resultado | mesma entrada, resultados diferentes |
| Critério | igualdade | adequação, segundo um critério escrito |

A consequência é que os dois **coexistem**, com escopos distintos. O que é determinístico
continua sendo testado por igualdade — a forma da resposta da API, a coerência entre campos,
a validação de um arquivo de dados. O que é generativo é *avaliado*, com pontuação, e a
pontuação é comparada com um limiar decidido pela aplicação.

Confundir os dois produz os dois erros clássicos: testar conteúdo generativo por igualdade
(suíte que falha aleatoriamente e que ninguém confia) e avaliar por modelo aquilo que uma
comparação de campo resolveria (custo alto e medidor com variância própria).

### 1.2 A pergunta muda ao longo do ciclo de vida

Uma armadilha comum é tratar "avaliação" como uma coisa só. São perguntas diferentes, e cada
uma exige um instrumento diferente:

1. A resposta tem a **forma** que prometemos? — contrato
2. **Onde** a informação se perdeu? — diagnóstico por componente
3. A resposta é **fiel** ao contexto que a sustenta? — métricas de referência livre
4. Ela atende ao que **este produto** considera boa resposta? — rubrica própria
5. Ela está **melhor ou pior** do que a versão anterior? — comparação
6. Esse build **sobe**? — decisão

A ordem não é arbitrária: cada camada só faz sentido se a anterior já está resolvida. Medir
a redação de uma resposta cujo contexto nunca continha a informação certa é medir a
consequência em vez da causa.

### 1.3 Produzir não é pontuar

Distinção que evita a maior parte da confusão sobre custo e determinismo:

- **Produzir** a resposta exige rodar o sistema real, e o sistema real chama modelo. Isso é
  inevitável em toda camada que avalia saída de verdade.
- **Pontuar** pode ser feito com modelo (fidelidade, rubrica) ou por comparação
  determinística de campos (a fonte citada está no conjunto aceito? o termo obrigatório
  aparece? a trajetória foi essa?).

Quando a pergunta é comparativa, a escolha do pontuador é crítica: **se o medidor tem
variância própria, não se sabe se a diferença entre duas rodadas veio do sistema ou do
instrumento.** Comparação pede pontuação determinística.

---

## 2. O dataset como especificação executável

### 2.1 Escrever o critério antes de medir

Um conjunto de casos de avaliação é, na prática, **a especificação do comportamento
esperado em forma executável**. Ele não descreve como o sistema funciona; descreve o que
conta como acerto. Por isso vive versionado junto do código, é revisado como código, e é o
artefato mais valioso do conjunto — mais até que os evaluators, que são substituíveis.

### 2.2 Casos negativos não são opcionais

Um dataset composto apenas de perguntas respondíveis **premia um sistema que responde
sempre** — inclusive quando deveria se recusar. A recusa correta é um comportamento tão
desejado quanto a resposta correta, e um sistema que nunca recusa é um sistema que alucina
quando não sabe.

Três famílias cobrem o espaço de desfechos de um sistema de perguntas e respostas:

| Família | Verifica |
|---|---|
| **Respondível** | achou o documento certo e afirmou o fato certo |
| **Recusa** | reconheceu o que **não** está na base, em vez de inventar |
| **Clarificação** | percebeu a ambiguidade e perguntou de volta |

A terceira família é a mais frequentemente esquecida, e é a que mede maturidade: perguntar
de volta é uma decisão, não uma falha.

### 2.3 Aceito não é o mesmo que esperado

Uma informação pode estar legitimamente em mais de um documento. Se o critério exige *um*
arquivo específico como fonte, ele transforma resposta correta em falha.

A modelagem correta é um **conjunto de fontes aceitáveis**: citar qualquer uma delas é estar
certo. O nome do campo importa didaticamente — `aceito` em vez de `esperado` — porque nomear
o critério errado leva a implementar o critério errado.

### 2.4 Cobrar o fato, não a redação

Exigir que a resposta contenha certos **termos literais** (um valor, um prazo, um percentual)
cobra a informação sem punir variação de estilo. É deliberadamente diferente de comparar a
resposta com um texto de referência, que puniria qualquer reformulação.

E há um limite conceitual que precisa ficar explícito: uma lista de termos obrigatórios é um
**checklist**, não um **gabarito**. Ela diz o que não pode faltar; não diz qual seria a
resposta completa e correta. A diferença determina quais métricas são calculáveis (seção 5.2).

### 2.5 Expectativa imensurável é defeito de dataset

O dataset precisa ser validado como qualquer outro dado de entrada, e a validação tem duas
naturezas.

A primeira é **consistência interna**: identificadores únicos, desfechos que se excluem
mutuamente não marcados juntos, campos coerentes com a família do caso.

A segunda é mais interessante — **contrato com o código**. Se um caso espera uma fonte que
não existe na base, ou um tipo de documento que o sistema não sabe filtrar, ou uma ferramenta
que o agente não possui, esse caso não é um caso que falha: é um caso **imensurável**. Ele
vai pontuar zero para sempre, pelo motivo errado, e ninguém saberá disso meses depois.

Um dataset validado contra as definições reais do código quebra **na hora** em que alguém
renomeia algo, em vez de virar uma métrica misteriosamente zerada.

### 2.6 Critério é imutável; critério novo é versão nova

A regra mais importante e a mais desconfortável:

> Mudar as expectativas depois de ver o resultado invalida toda comparação anterior.

Se a barra pode ser ajustada depois da medição, ela não é uma barra — é um espelho. Quando um
critério se revela mal definido (e isso acontece), a correção pertence a uma **versão nova**
do dataset, com nome novo, mantendo a antiga intacta. Comparação entre versões diferentes é
uma comparação que **não deve ser feita**, e o sistema de avaliação deve saber recusá-la.

---

## 3. A cascata de avaliação

As camadas se organizam por **custo crescente**, e a ordem é também de proximidade à causa:

| Ordem | Camada | Pergunta | Pontua com | Custo |
|---|---|---|---|---|
| 1 | Contrato | a forma prometida se mantém? | comparação | nenhum |
| 2 | Componente | onde a informação se perdeu? | comparação | modelo (parcial) |
| 3 | Referência livre | a resposta é fiel ao contexto? | modelo | modelo (alto) |
| 4 | Rubrica própria | atende ao critério deste produto? | modelo | modelo (alto) |
| 5 | Comparação | melhor ou pior que a versão anterior? | comparação | modelo (muito alto) |
| 6 | Portão | esse build sobe? | nada | nenhum |

Duas leituras dessa tabela:

**A camada mais barata é a mais confiável.** Contrato não tem variância, custa zero e roda em
segundos. Não é uma camada menor por isso — é a que se roda a cada alteração.

**A camada que decide não mede nada.** O portão (seção 8) apenas lê o que as outras
produziram. Isso o torna executável em ambientes sem credencial, sem banco e sem modelo, o
que é precondição para que ele possa ficar na frente de um merge.

---

## 4. Camada 1 — Testes de contrato

### 4.1 Forma é determinística; conteúdo não

O que uma interface promete é verificável por igualdade: quais campos existem, quais tipos
têm, quais combinações são coerentes, qual código de status uma entrada inválida produz.
Nada disso depende do que o modelo decidiu responder.

Exemplos de invariantes de forma, todas independentes de conteúdo:

- resposta afirmada implica ao menos uma fonte;
- recusa implica lista de fontes vazia;
- clarificação implica que não houve afirmação de resposta;
- diagnóstico ausente por padrão e presente quando solicitado;
- entrada vazia produz erro de cliente **e o pipeline nunca é acionado**.

### 4.2 O dublê e a injeção de dependência

Para testar a forma sem custo e sem variância, o pipeline real é substituído por um dublê que
devolve, sob demanda, cada um dos desfechos possíveis. Isso exige uma propriedade de projeto
que normalmente se descobre tarde: **a aplicação precisa permitir a substituição da
dependência**.

Um detalhe concreto e transferível: se o pipeline é construído no carregamento do módulo, não
há como colocar o dublê antes de o objeto real existir. Construí-lo sob demanda, na primeira
chamada, é o que torna a substituição possível. Testabilidade é decisão de arquitetura, não
de suíte de testes.

### 4.3 Invariantes que não podem falhar são métricas mortas

Um erro instrutivo: escrever uma verificação de que o campo de texto é texto e o campo
booleano é booleano, quando um validador de esquema já garante isso. A métrica passa
sempre — 37 de 37, para sempre — e ocupa uma coluna do relatório sem carregar informação.

> Métrica que não pode falhar é ruído com aparência de rigor.

A correção é verificar o que o esquema **não** garante: coerência **entre** campos. Afirmar
uma resposta sem nenhuma fonte é uma contradição que nenhum sistema de tipos pega.

---

## 5. Camada 2 — Avaliação por componente

### 5.1 Causa e consequência

Quando a resposta final está errada, a pergunta útil não é "quão errada" — é **onde quebrou**.
Um pipeline com várias etapas tem vários lugares onde a informação certa pode ter se
perdido, e todos produzem o mesmo sintoma.

A camada de componente roda as etapas **até antes da geração da resposta** e pontua cada uma
separadamente: o planejamento decidiu certo? os filtros permitiam que a informação fosse
encontrada? a busca trouxe a fonte aceita? o reordenamento a preservou? o fluxo parou onde
devia parar?

Além do valor diagnóstico, é a mais barata das camadas que custam, porque a geração da
resposta — a chamada mais cara do fluxo — não acontece.

### 5.2 Não aplicável não é o mesmo que passou

Este é o princípio metodológico mais importante de toda a avaliação, e o mais fácil de
violar sem perceber.

Um caso de recusa correta **não tem fonte aceita para recuperar**. Se o evaluator devolvesse
"passou" para ele, a métrica de recuperação seria inflada por casos que nunca foram
testados. Se devolvesse "falhou", puniria o sistema por ter acertado.

A resposta certa é uma terceira: **não aplicável** — nenhuma pontuação é registrada.

A consequência prática é que **os denominadores variam entre métricas**, e o relatório precisa
mostrar isso explicitamente:

```
Cobertura de tipos de documento:   19/29  (8 n/a)
Fonte recuperada:                  28/29  (8 n/a)
Clarificação evita busca:            3/4  (33 n/a)
```

Sem a coluna de não-aplicáveis, `3/4` parece um desastre e é, na verdade, uma métrica que só
fazia sentido em quatro casos. Denominador implícito é a forma mais eficiente de mentir com
números verdadeiros.

### 5.3 Agrupar falhas por métrica, não por caso

A pergunta que o relatório responde é **qual componente está sangrando**. Falhas listadas por
caso obrigam o leitor a reconstruir esse agrupamento mentalmente. É uma escolha de
apresentação que decorre diretamente do propósito da camada.

### 5.4 O score diz onde a informação se perdeu, não de quem é a culpa

Limite honesto da ferramenta, e vale entender com um exemplo real. Em um caso, a busca não
trouxe o documento com a informação. A métrica acusou a busca. Mas a causa foi uma decisão da
etapa **anterior**: o planejamento liberou um tipo de documento amplo, e os trechos desse
documento ocuparam todas as vagas disponíveis, expulsando o único trecho que continha a
resposta.

O planejamento passou na métrica dele. A busca falhou na dela. A cadeia causal atravessa as
duas.

> A avaliação por componente localiza **onde a informação desapareceu**. Atribuir causa
> continua sendo trabalho humano.

E isso ainda é incomparavelmente melhor do que saber apenas que "o sistema não respondeu".

### 5.5 Métrica certa como escrita, errada como definida

Padrão que se repete em todas as camadas e merece nome próprio. Uma métrica exigia que
*todos* os tipos de documento esperados aparecessem no plano. Ela reprovou treze casos — e
doze deles chegaram ao documento certo de qualquer forma.

A implementação estava fiel à definição. **A definição é que media a coisa errada**: o que
importa não é o plano listar todos os tipos plausíveis, é o filtro não eliminar o documento
que responde.

Duas conclusões:

- Uma métrica reprovando muito é evidência ambígua: pode ser o sistema, pode ser o critério.
  Investigar qual dos dois é parte do trabalho.
- A correção pertence a uma **versão nova** do dataset (seção 2.6). Ajustar a definição depois
  de ver o resultado é exatamente o que a disciplina proíbe.

---

## 6. Camada 3 — Métricas de referência livre

### 6.1 O que exige um modelo para medir

Algumas propriedades não são comparação de campo. "Esta resposta afirma apenas o que o
contexto sustenta" exige **ler** a resposta, decompô-la em afirmações e verificar cada uma
contra o contexto. Não há como fazer isso sem um modelo.

Três propriedades cobrem boa parte do que interessa em um sistema ancorado em documentos:

| Métrica | Pergunta | Precisa de gabarito? |
|---|---|---|
| **Fidelidade** | a resposta afirma só o que o contexto sustenta? | não |
| **Relevância da resposta** | ela responde à pergunta que foi feita? | não |
| **Precisão do contexto** | o que foi recuperado era relevante? | não |

São chamadas de **referência livre** justamente porque dispensam uma resposta ideal escrita
por humanos. É o que as torna aplicáveis a datasets que não têm gabarito — a maioria.

Aqui, também, casos de recusa correta **não entram**: medir fidelidade de uma recusa dá zero e
pune o acerto (é a aplicação direta do princípio da seção 5.2).

### 6.2 A métrica que não se pode medir

Existe uma quarta propriedade óbvia — **cobertura do contexto**: do que era relevante, quanto
foi recuperado? Ela é deliberadamente deixada de fora, e o motivo é o ponto mais importante
desta seção.

Precisão pergunta "do que eu trouxe, quanto prestava?" — respondível olhando o que foi
trazido. Cobertura pergunta "do que prestava, quanto eu trouxe?" — e para responder isso é
preciso conhecer **de antemão a lista completa** do que prestava, ou seja, uma resposta de
referência.

Um checklist de termos obrigatórios não é essa lista (seção 2.4). Esticar um no outro seria
**fabricar a verdade que a avaliação deveria conferir**.

> Use a métrica que os seus dados sustentam. Não fabrique dado para caber na métrica.

Essa frase é o resumo da postura correta em avaliação. A tentação oposta — inventar um
gabarito para poder exibir uma métrica conhecida — produz números que parecem rigorosos e não
medem nada.

### 6.3 Separar tipos de falha

Nota zero misturaria coisas de naturezas completamente diferentes. Um relatório útil separa:

| Categoria | Significa | Conserta-se onde |
|---|---|---|
| **Não produziu resposta** | o pipeline rodou e não respondeu | recuperação ou ancoragem |
| **Erro de execução** | estourou naquele caso (limite de taxa, tempo esgotado) | infraestrutura; dá para re-rodar só ele |
| **Erro de medição** | a métrica falhou; pontuação fica indefinida | o instrumento |

E há um requisito de robustez que decorre disso: um erro no vigésimo quinto caso **não pode
descartar os vinte e quatro anteriores**. Avaliação é caro; perder uma rodada inteira por uma
instabilidade de rede é inaceitável.

### 6.4 O canal de avaliação que a produção não tem

Problema real e elegante. Métricas de fidelidade precisam do **texto** do contexto. Mas a
política de telemetria e de interface proíbe que conteúdo de documento saia pela API.

A solução não é uma flag. É estrutural: o pipeline aceita um **callback** por onde o chamador
recebe os textos, e o resultado enriquecido — com os contextos — é um tipo **diferente** do
resultado normal do pipeline.

A consequência é a garantia forte: **a API não pode serializar um campo que não existe no
tipo que ela devolve**. O vazamento não é evitado por disciplina de quem escreve o código; é
impossível de expressar.

> Restrição que o sistema de tipos garante é melhor que restrição que a revisão de código
> precisa lembrar.

### 6.5 Dependência no caminho crítico merece leitura

Duas armadilhas reais com uma biblioteca de métricas, ambas transferíveis como hábito:

**Incompatibilidade transitiva.** A biblioteca não carregava por causa de uma dependência
*da dependência*. O paliativo que circula na internet — fixar a versão da biblioteca de cima
— não resolve, porque o problema está uma camada abaixo. Diagnosticar a árvore de
dependências, e não a folha, é o que produz a correção certa.

**Telemetria embutida no caminho crítico.** A biblioteca enviava um evento de uso, de forma
síncrona e sem tratamento de erro, após cada chamada de modelo — de dentro de código
assíncrono. O efeito é que uma instabilidade de rede em um serviço de terceiros derrubava o
lote inteiro de avaliação.

> Quando você coloca uma biblioteca nova no caminho crítico, abra e veja o que ela faz.

---

## 7. Camada 4 — Juiz-modelo e rubrica própria

### 7.1 O movimento inverso

Métricas de biblioteca medem propriedades que **outra pessoa** definiu. Um juiz-modelo é o
movimento oposto: **você escreve o que "resposta boa" significa neste produto**, e um modelo
aplica a definição.

Isso é poderoso e perigoso na mesma medida. A qualidade da medição passa a ser exatamente a
qualidade do critério escrito.

### 7.2 A rubrica é o contrato

Pedir "dê uma nota de 0 a 1" a um modelo é convite para receber 0.8 em tudo. Uma rubrica
utilizável tem, para **cada** critério, os pontos de ancoragem descritos: o que caracteriza
a nota máxima, o que caracteriza a intermediária, o que caracteriza a mínima.

Critérios que cobrem dimensões independentes de uma resposta ancorada:

| Critério | Mede |
|---|---|
| **Ancoragem** | tudo o que foi afirmado é sustentado pelo contexto |
| **Relevância** | responde à pergunta feita |
| **Completude** | cobre o que a pergunta pedia — e que **estava** no contexto |
| **Suporte das fontes** | as fontes citadas sustentam o que foi dito |
| **Clareza** | vai direto à resposta |

Duas decisões de projeto embutidas aí:

**A nota geral não é a média.** Ancoragem e relevância pesam mais que estilo. Média simples
declara que prolixidade e invenção são defeitos equivalentes — o que é falso em praticamente
qualquer produto.

**O juiz é proibido de usar conhecimento externo.** Se o contexto não diz, não está
sustentado, por mais verdadeiro que a afirmação seja no mundo. Sem essa restrição, o juiz
mede o conhecimento dele, não a ancoragem do sistema.

### 7.3 O veredito precisa ter forma

A saída do juiz é validada contra um esquema. O ganho não é ergonômico: um juiz que resolve
escrever um ensaio **falha na validação**, em vez de produzir uma pontuação inutilizável que
ninguém percebe. Falha visível é infinitamente melhor que número silenciosamente errado.

### 7.4 O limiar pertence à aplicação, não ao juiz

Decisão sutil e importante: **o critério de corte não é informado ao juiz**.

Se fosse, o juiz ancoraria as notas em torno da linha, e duas rodadas com cortes diferentes
deixariam de ser comparáveis. O juiz responde à pergunta dele — "você entregaria isso?" — e o
corte é aplicado depois, pela aplicação.

Manter o veredito do juiz no relatório, lado a lado com a decisão do corte, tem valor
diagnóstico: **quando os dois discordam, isso é descalibração**, e vale investigar.

### 7.5 Calibrar antes de confiar

O resultado mais instrutivo possível: o juiz deu nota máxima em todos os critérios de todos
os casos.

Um juiz que **nunca discrimina não carrega informação**. E esse resultado tem duas
explicações opostas que, de fora, são idênticas: ou o sistema é muito bom, ou a rubrica é
frouxa. Nada no número distingue as duas.

A técnica que distingue é a **calibração por sondas**: respostas escritas à mão, cada uma
errada de **um** jeito específico — uma que inventa um fato, uma que fala de outro assunto,
uma incompleta, uma prolixa. O juiz é aplicado a elas, e o que se verifica é se ele **reprova
o que deveria reprovar**.

Três detalhes metodológicos que fazem a diferença:

**As sondas são versionadas antes de rodar.** Critério que se pode editar depois de ver o
resultado não é critério — é a mesma regra da seção 2.6, aplicada ao instrumento.

**A cobrança é por critério, não pela nota geral.** A sonda prolixa deve reprovar em clareza e
**deixar a nota geral em paz**, porque a rubrica diz que estilo pesa menos. Uma sonda que
cobrasse a nota geral ali contradiria a rubrica que ela deveria testar.

**A rubrica é versionada.** Ela evolui, e o relatório carimba a versão usada. Sem isso,
comparando dois relatórios meses depois, não há como separar "o sistema melhorou" de "eu
afrouxei o critério".

### 7.6 O que a calibração encontra

No caso real, dois problemas — ambos invisíveis enquanto tudo pontuava máximo:

**Um critério frouxo.** A definição de clareza dizia apenas "claro e objetivo", fácil demais
de satisfazer: a resposta deliberadamente prolixa passava com nota máxima. Reescrita, virou
uma nova versão da rubrica.

**Um critério imensurável.** O juiz recebia as fontes como nomes de arquivo e o contexto sem
atribuição — sem nenhuma forma de ligar um trecho à sua origem. Ou seja, o critério de
suporte das fontes **não podia ser avaliado com os dados fornecidos**.

Esse segundo caso introduz uma categoria de resultado que vale ter: a **lacuna conhecida**.
A sonda é marcada como tal, reporta o buraco e **não reprova a rodada**. É honesto — o
critério existe, sabe-se que não é medível hoje, e sabe-se o que seria preciso para medi-lo.

> A calibração não deu selo de qualidade. Ela achou um critério frouxo e um critério
> impossível.

É esse o resultado esperado de uma boa calibração. Um juiz que passa na calibração de
primeira geralmente tem sondas fáceis demais.

### 7.7 Independência entre o modelo que responde e o que julga

Vale poder configurá-los separadamente. O motivo é o dia em que o modelo de produção mudar:
se o juiz muda junto, a comparação antes/depois fica contaminada por duas variáveis. O
critério deve poder ficar parado enquanto o sistema se move.

---

## 8. Camada 5 — Comparação entre versões

### 8.1 A pergunta que antecede o deploy

As camadas anteriores respondem "isso está bom?". Antes de subir uma mudança, a pergunta é
outra: **está melhor ou pior do que o que já está no ar?**

Um número sozinho não responde. `28/29` é ótimo ou alarmante dependendo do que a rodada
anterior marcou. **Qualidade em sistemas generativos é uma grandeza relativa a um histórico.**

### 8.2 Uma diferença por comparação

Princípio experimental básico, violado com frequência: uma comparação só é interpretável se
houver **exatamente uma** diferença entre os lados. Duas mudanças simultâneas produzem um
resultado que não se sabe a quem atribuir.

Corolário de projeto agradável: variantes comparáveis são mais fáceis de construir quando o
sistema já expõe suas decisões como parâmetros. Uma etapa que pode ser ligada e desligada por
configuração é uma etapa cujo valor pode ser medido.

### 8.3 Medidor determinístico para objeto não determinístico

Nesta camada os critérios **não usam modelo para julgar**. O sistema continua chamando modelo
— ele precisa responder as perguntas —, mas quem dá a nota é comparação de campo: o desfecho
foi o esperado, a fonte citada está no conjunto aceito, os termos obrigatórios aparecem, os
campos são coerentes entre si.

O motivo já foi dito e vale repetir porque é a razão inteira da escolha: **se o medidor tem
variância própria, a diferença entre duas rodadas não é atribuível**.

### 8.4 O que uma comparação entrega

O formato do resultado é o ponto:

```
Métrica                  variante A   variante B    diferença
Comportamento esperado   34/37        33/37         -1
Fonte aceita             28/29        27/29         -1
Termos obrigatórios      26/29        24/29         -2
Latência média           4527 ms      3509 ms       -1018 ms
Tokens totais            118222       68120         -50102
Custo estimado           0.0204 USD   0.0122 USD    -0.0082 USD
```

Isso é **o formato de uma decisão de engenharia**: remover uma etapa economiza 42% dos tokens
e um segundo por pergunta, e custa quatro regressões de qualidade.

Nenhum lado é obviamente certo, e é aí que está o valor. Um sistema interno de baixo volume e
um sistema com milhões de chamadas por dia resolvem esse trade-off de formas opostas. **A
ferramenta não decide; ela cria o que discutir**, no lugar de opinião.

### 8.5 Recusar comparar o incomparável

Uma comparação precisa saber quando **não** deve ser feita. Dois casos concretos:

- rodadas que cobrem **conjuntos diferentes de casos** (uma parcial contra uma completa) —
  o diferencial seria numericamente válido e semanticamente vazio;
- rodadas sobre **versões diferentes do dataset** — é a regra da seção 2.6 sendo aplicada.

É a mesma lição do versionamento de rubrica, generalizada: **um sistema de medição precisa
carregar a informação necessária para invalidar suas próprias comparações**.

### 8.6 Escolher a rodada certa é parte do problema

Detalhe operacional com consequência real. Relatórios acumulam, com nomes que incluem
timestamps, e caçar o par certo entre uma dúzia é como se acaba comparando os dois errados.
Comparar **por nome de variante**, resolvendo automaticamente para a rodada mais recente de
cada e **imprimindo qual foi escolhida**, elimina uma classe inteira de erro silencioso.

### 8.7 Agregados precisam ser enviados para existir depois

Pontuações caso a caso permitem inspeção; **agregados por rodada** permitem tendência. Se os
agregados não forem gravados no momento da execução, comparar duas rodadas separadas por
semanas na interface do backend será impossível — os números nunca existiram lá.

Há um ciclo curto (a comparação impressa, agora) e um ciclo longo (a série histórica, meses
depois). Os dois precisam ser alimentados na mesma execução.

### 8.8 Política antes de escrever

Uma sutileza que só aparece quando avaliação e governança convivem: se uma política
operacional (orçamento esgotado, por exemplo) faz o sistema recusar todas as execuções, e
isso é gravado sob o nome real do experimento, o histórico passa a conter **uma regressão que
nunca aconteceu**, e ela permanece lá para sempre.

Verificar a política **antes** de qualquer escrita no histórico é o que evita contaminar a
série temporal com um artefato operacional.

---

## 9. Camada 6 — Do número à decisão: quality gates

### 9.1 O portão não mede nada

A última camada apenas **lê os relatórios que já existem** e devolve um booleano. Não chama
modelo, não abre banco, não precisa de credencial, não importa nada do resto da aplicação.

Isso é requisito, não elegância:

> Um portão que precisa da stack inteira para dizer "não" é um portão que ninguém coloca na
> frente de um merge.

A ausência de dependências é o que torna o portão executável em qualquer ambiente de
integração contínua — e portanto o que torna a decisão automatizável.

### 9.2 Limiares versionados, ao lado dos datasets

Os limiares ficam em um arquivo versionado, pelo mesmo motivo dos datasets:

> Uma barra que você abaixa depois de ver o resultado não é barra.

E nem todos os limiares são iguais. Alguns admitem tolerância (uma taxa de acerto de 75%);
outros não admitem grau nenhum. "Uma ação proibida foi executada" não tem meio termo: ou
aconteceu, ou não. Distinguir os dois tipos no arquivo de configuração é modelar
corretamente a natureza do risco.

### 9.3 Quatro estados, não dois

Um portão maduro tem mais que aprovado e reprovado:

| Estado | Significa | Ação |
|---|---|---|
| **Aprovado** | métrica acima do limiar | seguir |
| **Reprovado** | métrica abaixo do limiar | a qualidade caiu |
| **Ausente** | métrica configurada não aparece no relatório | o nome mudou ou a rodada é degenerada |
| **Ignorado** | suíte opcional sem relatório | nada |

**Ausente é diferente de reprovado**, e é a distinção que justifica quatro estados. As duas
reprovam o build, mas por motivos que exigem ações completamente diferentes: uma pede
investigação de qualidade, a outra pede investigação de configuração. Nenhuma das duas é "a
qualidade caiu".

E o conceito de suíte **obrigatória** versus **opcional** resolve o caso do relatório que
não existe: obrigatória sem relatório reprova; opcional sem relatório é ignorada.

### 9.4 Adaptadores, porque formatos divergem

Relatórios produzidos por camadas diferentes, em momentos diferentes, não falam a mesma
língua: nomes prefixados aqui, chave de agregados diferente ali. A escolha é entre reescrever
o histórico ou escrever **adaptadores** — funções minúsculas que traduzem cada formato para o
vocabulário do portão.

A segunda opção é o que permite ao portão ler o histórico que **já existe**, em vez de começar
do zero. Compatibilidade retroativa em dados de avaliação vale mais do que parece: o valor de
uma série histórica é proporcional ao seu comprimento.

### 9.5 A armadilha do "relatório mais recente"

Resolver automaticamente para o relatório mais recente é conveniente e perigoso: o mais
recente pode ser uma **rodada de fumaça de um único caso**, feita para depurar. Todas as
métricas vêm ausentes — ou, pior, uma métrica calculada sobre um caso pode gatear um merge.

É exatamente a mesma classe de problema da seção 8.5, e a mesma classe de solução: o sistema
precisa saber reconhecer uma rodada que não deveria decidir nada.

### 9.6 Quando não ligar o portão

O resultado mais instrutivo de uma primeira execução: o portão reprovou o build por causa de
uma métrica cuja **definição** estava errada — o critério, não o sistema (é o padrão da
seção 5.5, colhido pela última camada).

> Um portão que reprova por definição ruim treina a equipe a ignorar o portão.

Que é precisamente o argumento para **não** conectar a decisão automática antes de os
critérios estarem calibrados. Automatizar uma decisão sobre uma medição não confiável não
produz rigor; produz um obstáculo que as pessoas aprendem a contornar.

---

## 10. Limitações conhecidas e evolução natural

### 10.1 Ruído não é medido

O sistema avaliado não é determinístico: rodadas idênticas produzem números levemente
diferentes. Sem uma noção de **variação basal** — obtida rodando a mesma configuração várias
vezes —, não há como distinguir uma regressão real de flutuação. Isso torna qualquer limiar
uma escolha parcialmente arbitrária.

### 10.2 Avaliação é offline

Todas as camadas medem sobre datasets, antes do deploy. Nenhuma delas observa qualidade em
produção, sobre tráfego real, com distribuição real de perguntas. Um dataset é uma amostra
curada, e sistemas de IA são especialmente sensíveis a deslocamento de distribuição.

### 10.3 O dataset envelhece

Casos escritos hoje refletem o produto de hoje. Conforme a base de conhecimento cresce e o
produto muda, parte deles descreve um comportamento que já não é o desejado. Não há processo
definido para aposentar ou revisar casos.

### 10.4 Integridade do dataset é assumida

O portão confia nos relatórios; os relatórios confiam nos datasets. Editar uma expectativa
para casar com um comportamento pior passa na validação estrutural e **rebaixa a barra sem
alarme**. Validação verifica estrutura, não intenção — a defesa real é revisão humana das
alterações.

### 10.5 Custo limita a frequência

As camadas que custam levam minutos e dinheiro. Isso empurra para execução parcial, que por
sua vez deixa métricas sem casos aplicáveis, que o portão reporta como ausentes. O
compromisso entre custo e completude não tem solução limpa; tem gestão.

---

## 11. Síntese

Avaliar um sistema de IA não é testar um sistema comum com mais casos. É uma disciplina com
objeto próprio: um sistema cuja saída é correta em graus, cuja execução não se repete e cujas
falhas nascem em etapas distintas com sintomas idênticos.

Os princípios que se sustentam mutuamente:

1. **O dataset é a especificação** — versionado, revisado como código, validado contra as
   definições reais do sistema, e imutável depois de medido.
2. **Casos negativos são obrigatórios** — recusa e clarificação são comportamentos desejados,
   e um dataset só de perguntas fáceis premia quem responde sempre.
3. **Camadas por custo crescente** — contrato, componente, referência livre, rubrica,
   comparação, decisão; cada uma responde a uma pergunta diferente.
4. **Não aplicável não é passou** — a alternativa infla métricas com casos nunca testados, e
   é por isso que os denominadores variam.
5. **Produzir não é pontuar** — e comparação exige pontuador determinístico, sob pena de não
   se saber se a diferença veio do sistema ou do instrumento.
6. **Use a métrica que os dados sustentam** — não fabrique gabarito para caber em uma métrica
   conhecida.
7. **Calibre o medidor antes de confiar nele** — um juiz que nunca discrimina não carrega
   informação, e a calibração é o que separa "o sistema é bom" de "o critério é frouxo".
8. **Qualidade é relativa a um histórico** — um número isolado não decide um deploy; e o
   sistema de medição precisa saber recusar comparações inválidas.
9. **A decisão automática vem por último** — depois dos critérios estarem calibrados, nunca
   antes.

A pergunta que resume o capítulo: **como se sabe que um sistema que não repete a si mesmo
está melhor hoje do que estava ontem?** A resposta não é um número. É um critério escrito
antes de medir, um instrumento calibrado contra erros conhecidos e um histórico que permite
comparar — e a qualidade da avaliação é a qualidade dessas três coisas.
