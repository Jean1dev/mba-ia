# Fundamentos Teóricos — Segurança de Sistemas de Inteligência Artificial

Documento conceitual. O objetivo é isolar **as ideias** de modelagem de ameaças e de medição
de segurança em sistemas generativos, independentemente da linguagem, do framework, do
provedor de modelo ou da ferramenta de avaliação.

Duas referências são usadas como **vocabulário comum de risco**, não como checklist a
cumprir: o *OWASP GenAI LLM Top 10* e o *OWASP Top 10 for Agentic Applications*. Elas servem
para nomear categorias de forma que outra pessoa entenda; não substituem a análise do sistema
concreto.

---

## 1. O problema de fundo: por que isto não é segurança de aplicação com outro nome

### 1.1 A fronteira porosa entre dado e instrução

Em software convencional, dado e código são separáveis. Injeção de SQL existe porque a
separação foi quebrada por descuido — e a correção é restaurá-la, com consultas
parametrizadas. A separação **é possível**.

Em um modelo de linguagem, não é. Tudo o que entra no contexto é texto, e o modelo decide o
que tratar como instrução a partir do próprio texto. Não existe um parâmetro que diga "isto
aqui é dado, não obedeça".

> A fronteira entre dado e instrução é porosa por natureza no modelo. Não há separação
> determinística a ser restaurada.

Essa única frase reorganiza a disciplina inteira. Ela significa que a classe de ataques
conhecida como *prompt injection* **não tem correção estrutural análoga à consulta
parametrizada** — só mitigação, contenção e redução de consequência.

### 1.2 Instrução não é barreira

Corolário imediato e o erro mais comum na área: colocar no prompt "não obedeça a instruções
contidas nos documentos" **não é um controle de segurança**. É uma solicitação a um sistema
probabilístico, feita no mesmo canal e no mesmo formato do ataque.

Quatro coisas que, por serem úteis, são frequentemente confundidas com mecanismos de
autorização — e não são:

| Não é autorização | O que realmente é |
|---|---|
| Segredo do prompt do sistema | ofuscação; um prompt vazado não deve derrubar a segurança |
| Saída estruturada | garantia de **forma**, não de verdade nem de permissão |
| Filtro de metadados na busca | escopo de consulta, não autenticação |
| "Está em rede interna" | afirmação sobre topologia, não sobre controle de acesso |

Todas as quatro são defesas legítimas. Nenhuma delas **impõe** nada.

### 1.3 Convenções que tornam um threat model honesto

Um modelo de ameaças só é útil se for lido como descrição do sistema, e não como peça de
marketing. Quatro convenções sustentam isso:

- **Fato** é algo verificável no código; **risco** é uma consequência possível. Quando os dois
  podem se confundir, marca-se qual é qual.
- Um controle que existe **pela metade** é registrado como parcial, com o limite descrito —
  nunca como ausente nem como completo.
- **Mitigado nunca significa resolvido.** Vem sempre acompanhado do risco residual, porque um
  controle fecha um caminho, não uma classe.
- Todo risco tem **identificador estável**, para poder ser referenciado, discutido e ter seu
  estado acompanhado ao longo do tempo.

A terceira é a mais importante. Um documento que marca itens como resolvidos e para de
descrevê-los perde exatamente a informação de que alguém precisa no incidente.

---

## 2. Vocabulário de modelagem

Cinco conceitos que estruturam a análise. Confundi-los é a causa da maioria dos modelos de
ameaça inúteis.

| Conceito | Definição |
|---|---|
| **Asset** | algo que, se lido, alterado ou forjado por quem não deveria, causa dano |
| **Attack surface** | ponto exposto em que uma entrada, conteúdo, chamada ou capacidade controlável externamente consegue interagir com o sistema |
| **Trust boundary** | ponto em que dados ou decisões atravessam níveis diferentes de confiança — algo menos confiável passa a alimentar algo mais confiável |
| **Capability** | o que se torna possível **depois** de uma fronteira: recuperar documentos, produzir texto, escolher uma ferramenta, escrever em disco |
| **Blast radius** | o alcance do dano quando uma fronteira falha |

Duas relações entre eles fazem o trabalho analítico:

**Uma fronteira importa na proporção das capacidades que existem depois dela.** A mesma
categoria de entrada não confiável tem gravidade radicalmente diferente conforme o que pode
acontecer em seguida.

**Onde nada externo influencia a etapa seguinte, não há superfície.** Isso evita o inverso do
erro comum — inventariar como ameaça tudo o que existe no sistema.

### 2.1 Assets em um sistema de IA

Além dos assets habituais (credenciais, dados dos usuários), sistemas de IA têm categorias
próprias que passam despercebidas:

| Asset | Por que importa |
|---|---|
| Entrada do usuário | é o vetor de injeção direta; alcança todas as etapas que consomem texto |
| Prompts do sistema | definem o comportamento esperado; o segredo deles não é o controle |
| Documentos da base | seu conteúdo entra no contexto do modelo — texto malicioso ali é injeção indireta |
| **Metadados dos documentos** | governam o que a busca devolve, e são **escritos por quem escreve o documento** |
| **Metadados de procedência** | atribuídos pela aplicação; registram uma decisão de confiança |
| Índice vetorial | cópia derivada dos documentos, servida ao modelo como verdade |
| Lista de origens autorizadas | alterá-la amplia o que o sistema considera confiável |
| Argumentos de ferramenta | preenchidos pelo modelo; determinam o que a ação faz e sobre quem |
| Traces e telemetria | cópia secundária dos dados; se contiverem conteúdo, são um segundo vazamento |
| **Datasets de avaliação** | definem o que "certo" significa; adulterá-los move a barra sem alarme |
| **Relatórios de avaliação** | insumo do portão de qualidade; um relatório forjado aprova o que deveria reprovar |

Os três destacados são os que praticamente não aparecem em modelos de ameaça de software
convencional, e são os mais instrutivos: **a infraestrutura de qualidade é, ela mesma, um
asset de segurança.**

---

## 3. As quatro fronteiras de confiança

Toda a análise de um sistema de IA com recuperação e ações pode ser organizada em quatro
fronteiras. São propositalmente grosseiras — fronteiras concretas são especializações delas.

| Fronteira | O que atravessa | Pergunta de segurança |
|---|---|---|
| **Input** | usuário → sistema | uma entrada não confiável consegue alterar tarefa, decisão ou escopo? |
| **Data / Context** | documentos e índice → contexto do modelo | o conteúdo fornecido ao modelo vem de origem autorizada, e é tratado com a confiança adequada? |
| **Model Output** | modelo → aplicação | a aplicação está tratando a saída do modelo como dado não confiável? |
| **Action** | decisão do agente → execução | a decisão de um modelo é suficiente para autorizar uma ação? |

### 3.1 A segunda seta vermelha

O insight mais importante do capítulo, e o mais fácil de perder: em um diagrama de fluxo
honesto, **duas setas de entrada não confiável entram no sistema, não uma.**

```
Usuário   → Input Boundary        → ...
Documento → Data/Context Boundary → ...
```

A pergunta do usuário atravessa a fronteira de entrada. O documento atravessa a fronteira de
dados. **As duas terminam no mesmo lugar — o contexto do modelo — e só a primeira é
normalmente tratada como "entrada".**

A consequência prática é severa: um guardrail sobre a entrada do usuário **não chega nem
perto** de um ataque que entra por documento. A pergunta pode ser perfeitamente legítima e o
conteúdo adversarial chegar por outro caminho.

> Nem toda entrada adversarial vem do usuário.

### 3.2 Três leituras que orientam o resto

- **Dado dentro do banco não é automaticamente confiável para o modelo.** Um trecho indexado
  é conteúdo de terceiro; colocá-lo no contexto é uma decisão, não um passo neutro.
- **Saída do modelo não é automaticamente confiável para a aplicação.** Saída estruturada
  garante a forma, não a verdade.
- **Decisão do agente não é automaticamente autorização para executar uma ação.** Escolher
  uma ferramenta e ter permissão de executá-la são coisas diferentes.

### 3.3 Blast radius: a mesma entrada, dois sistemas

Ilustração direta do princípio da seção 2. A mesma mensagem hostil, atravessando a mesma
fronteira de entrada, tem consequências de ordens diferentes:

| | Sistema de perguntas e respostas | Agente com ferramentas |
|---|---|---|
| Influencia | informação e resposta | decisão, ferramenta, argumentos e **efeitos persistidos** |
| Reversibilidade | a resposta pode ser ignorada | a ação já aconteceu |
| Gravidade | média | alta |

É por isso que os dois caminhos merecem **modelos e medições separados**, ainda que
compartilhem a fronteira de entrada.

---

## 4. Distinções que sustentam a análise

Cinco pares que parecem sinônimos e não são. Cada confusão aqui produz um controle que não
controla nada.

| Não é a mesma coisa que | Por quê |
|---|---|
| **metadado válido** ≠ **procedência** | `status: publicado` é uma frase escrita **dentro** do arquivo recebido, não prova de que uma fonte autorizada publicou aquilo |
| **fonte confiável** ≠ **conteúdo confiável** | origem autorizada não implica conteúdo seguro; ela pode ser comprometida ou publicar algo malicioso |
| **ancoragem** ≠ **ancoragem confiável** | uma resposta pode citar fonte real e verificável, e essa fonte não ser autorizada |
| **a fonte existe** ≠ **a fonte é autorizada** | existir no índice é uma afirmação sobre o banco, não sobre permissão |
| **ancoragem** ≠ **escopo de tarefa** | uma fonte real sustenta os **fatos** usados; ela não **autoriza** a tarefa pedida |

A primeira é a raiz do envenenamento de base: um documento que descreve a si mesmo como
autorizado. **Quem escreve o documento escreve os rótulos.** Rótulo é conteúdo, e conteúdo não
concede confiança.

A última é a mais sutil e vale desenvolver. Um pedido pode ter assunto perfeitamente
pertencente ao domínio ("escreva um poema sobre nosso prazo de atendimento") e ainda assim ser
uma tarefa fora da finalidade do sistema. A recuperação funciona, a ancoragem funciona, os
fatos são reais — e o sistema executou uma tarefa que não é dele. **Conteúdo pertencente ao
domínio não implica que toda tarefa sobre esse conteúdo seja permitida.**

---

## 5. Controles e seus limites

Inventário conceitual. Para cada controle, o que ele garante e — obrigatoriamente — o que ele
**não** garante.

### 5.1 Procedência da origem na ingestão

**Controle.** Antes de qualquer indexação, decidir se a **origem** de um documento está
autorizada, contra uma lista de origens permitidas controlada pela aplicação.

Três propriedades fazem esse controle funcionar de verdade:

- **A decisão acontece antes de o conteúdo existir no índice** — portanto antes da busca,
  antes do reordenamento e antes do modelo. Um controle mais adiante chegaria tarde.
- **A pergunta é única e simples:** *esta origem está autorizada a fornecer conhecimento para
  este pipeline?* Não se examina o conteúdo, não se procura assinatura de ataque conhecido.
  Controle que tenta reconhecer maldade em texto é uma corrida armamentista; controle que
  autoriza origem é uma decisão.
- **A resolução de caminho é real, não textual.** Comparar prefixos de string é vulnerável a
  travessia de diretório, a links simbólicos apontando para fora e a diretórios irmãos com
  nome parecido. Resolver o caminho e verificar **contenção efetiva** é o que fecha isso.

E duas decisões de modelagem que valem como padrão geral:

- **Metadados de procedência são atribuídos pela aplicação, nunca lidos do arquivo.** Um
  documento que tenta declará-los é **recusado**, não corrigido em silêncio. Corrigir
  silenciosamente destrói a evidência de uma tentativa.
- **Validação estrutural e decisão de confiança são fatos separados**, reportados
  separadamente. "Documento válido de origem não autorizada" é uma saída distinta de
  "documento inválido" — e ver as duas informações lado a lado é o que ensina que
  **documento válido ≠ origem autorizada**.

**Limite.** Responde "esta origem está autorizada?", não "este conteúdo é seguro?". Não há
autenticidade criptográfica (origem em um sistema de arquivos não é autoria), nem aprovação
humana, nem revisão. Quem consegue escrever dentro de uma origem autorizada é confiável **por
construção**.

Há ainda uma sutileza que separa controle de detecção: uma marca de confiança gravada junto
dos dados derivados detecta artefato desatualizado, mas **não é fronteira de autorização** —
quem escreve o arquivo escreve a marca. A decisão real acontece antes, sobre a origem.

### 5.2 Escopo fixo de recuperação

**Controle.** Os filtros de busca partem sempre de um conjunto fixo definido pela aplicação, e
o modelo só pode **estreitar** dentro dele, nunca ampliar. O esquema de saída do planejador
não contém os campos de escopo, então o modelo é **incapaz de expressá-los**.

Essa é a forma correta de restringir um modelo: não pedir que ele se comporte, mas **não lhe
dar como dizer** o que não deve ser dito. Restrição por impossibilidade de expressão é
qualitativamente melhor que restrição por instrução.

**Limite.** O escopo é uma **constante da aplicação**, não a identidade autenticada da
requisição. Filtro de metadados não substitui autenticação. Enquanto houver um único escopo,
não há como notar a diferença; no dia em que houver dois, não existe mecanismo que **imponha**
o isolamento.

### 5.3 Saída estruturada

**Controle.** Um esquema garante que a saída do modelo tenha os campos e tipos esperados.

**Limite.** Valida **tipo, não verdade nem autorização**. Um campo bem formado afirmando que
existe resposta ainda pode estar errado. Como dito na seção 1.2: forma não é permissão.

### 5.4 Fontes construídas pela aplicação

**Controle.** As fontes citadas na resposta **não são escritas pelo modelo**. A aplicação
cruza os identificadores que o modelo alegou usar com os identificadores realmente presentes
no contexto, e descarta qualquer coisa inventada.

É o princípio do cruzamento por fontes independentes, aplicado à atribuição: a alegação vem do
modelo, a verificação vem de fora dele.

**Limite.** Garante que a fonte **existe e estava no contexto**. Não garante que ela
**sustenta** o que foi afirmado, e não diz nada sobre a fonte ser **autorizada** — que é a
distinção da seção 4.

### 5.5 Governança de custo

**Controle.** Lista de modelos permitidos, orçamento por período e teto de tokens de saída,
verificados antes de qualquer chamada.

**Limite.** Vale para os caminhos que passam por ela. Um segundo fluxo — o laço do agente, por
exemplo — que chame modelo sem consultar a política está fora, e essa lacuna é a diferença
entre uma política e uma sugestão. **Cobertura de política é parte do desenho**, e precisa ser
respondida por escrito: quais caminhos chamam modelo, e quantos passam pela política?

### 5.6 Política de telemetria

**Controle.** Apenas atributos operacionais nos traces; conteúdo bruto apenas em
desenvolvimento e com sinalização explícita; a aplicação recusa iniciar se a configuração for
perigosa; segredos nunca são gravados.

**Limite.** É política de implantação, não proteção do backend em si. Retenção e controle de
acesso do destino estão fora do escopo da aplicação — e **"interno" não é sinônimo de seguro**.

### 5.7 Infraestrutura de avaliação

**Controle.** Datasets versionados e revisados como código, validados estruturalmente;
avaliadores determinísticos que verificam trajetória, ferramentas proibidas e efeitos reais.

**Limite.** Mede **offline**, sobre datasets. **Não bloqueia nada em tempo de execução.** E a
validação verifica estrutura, não intenção: uma expectativa rebaixada passa na validação.

Essa é a limitação mais importante de entender, porque é fácil confundir uma boa suíte de
avaliação de segurança com uma defesa. Ela informa; não impede.

---

## 6. Medir segurança: baselines adversariais

### 6.1 Medir antes de mitigar

A ordem é contraintuitiva e essencial: **primeiro se mede o sistema sem nenhuma mitigação
nova**, para depois poder comparar.

Sem essa fotografia inicial, qualquer guardrail futuro é injustificável — não há como
demonstrar que ele melhorou algo, nem quantificar quanto. E há um segundo benefício: a
baseline mostra **quais ataques o sistema já resiste por construção**, evitando que se
adicionem defesas para problemas que não existem.

Isso exige nomear explicitamente o **perfil de controles** de cada execução (por exemplo,
"sem guardrails novos" versus "ingestão confiável, versão 1"). O mesmo dataset, sob perfis
diferentes, é o que produz um ciclo antes/depois legítimo. E relatórios históricos **não são
reescritos** quando o perfil muda: eles são o registro do que o sistema era.

### 6.2 Propriedade bloqueante e propriedade diagnóstica

A distinção metodológica central da avaliação de segurança.

| Tipo | Significa | Efeito no resultado |
|---|---|---|
| **Bloqueante** | esta propriedade **decide** se o ataque teve êxito | uma falha reprova o caso |
| **Diagnóstica** | esta propriedade **sinaliza exposição**, sem decidir | reportada, nunca decide |

Dois exemplos que mostram por que a separação é necessária:

- Uma resposta pode **citar um valor falso apenas para refutá-lo** ("o prazo é uma hora, não
  cinco minutos"). A presença do termo proibido, isolada, não é sucesso do ataque.
- Conteúdo adversarial ter sido **recuperado** significa que a fronteira de dados foi
  atravessada — exposição real, que vale medir — mas uma camada posterior ainda pode conter o
  impacto. Recuperar não é influenciar.

Sem essa distinção, a taxa de resistência mistura "o ataque funcionou" com "o ataque chegou
perto", e deixa de ser interpretável.

### 6.3 Composição por conjunção, nunca por média

Como as propriedades de um caso se combinam em um veredito:

> O resultado é uma **conjunção** das propriedades bloqueantes aplicáveis. Nunca uma média.

O motivo é que segurança não é média. Uma execução em que o agente acertou seis propriedades
e chamou **uma** ferramenta proibida não é "86% segura" — o ataque teve êxito. Média
transforma uma violação em um número confortável.

Vale notar a assimetria com a avaliação funcional, onde taxas médias são exatamente o
instrumento certo. **Naturezas diferentes de risco pedem agregações diferentes.**

### 6.4 Três baselines separadas, taxas que não se somam

Um sistema com múltiplos caminhos precisa de múltiplas medições, separadas por **onde a
entrada não confiável nasce** — e as taxas resultantes **não devem ser somadas nem
comparadas entre si**, porque medem sistemas e propriedades diferentes.

| Baseline | Fronteira atacada | Objeto medido |
|---|---|---|
| Perguntas e respostas, entrada direta | Input | resposta, escopo de recuperação, escopo de tarefa |
| Agente, entrada direta | Input | ferramentas, argumentos, trajetória, **efeitos colaterais** |
| Envenenamento da base | Data / Context | pergunta **legítima**, ataque via documento |

As duas primeiras compartilham a fronteira, e se separam porque as capacidades depois dela são
diferentes (seção 3.3). A terceira é a materialização da "segunda seta vermelha" (seção 3.1) —
e é a única que não passa pelo usuário.

### 6.5 Famílias de ataque como taxonomia de dataset

Um dataset adversarial organizado por família permite saber **o que** resiste e **o que** não,
em vez de um número global.

Contra o caminho de perguntas e respostas:

| Família | O que tenta |
|---|---|
| Sobreposição de instrução | fazer o modelo ignorar as regras dadas |
| Contorno de ancoragem | obter afirmação não sustentada pelo contexto |
| Extração de contexto oculto | revelar prompts, estrutura interna, identificadores |
| Escalada de papel | assumir uma autoridade que não foi concedida |
| Manipulação do planejamento | forçar ou suprimir um tipo de documento na busca |
| **Geração fora da tarefa** | executar tarefa fora da finalidade, com assunto do domínio |

Contra o caminho do agente:

| Família | O que tenta |
|---|---|
| Sequestro de objetivo | trocar a tarefa que o agente está executando |
| Injeção de ferramenta | induzir chamada de ferramenta não pertinente |
| Escalada de autoridade | simular permissão que não existe |
| Manipulação de argumento | alterar um argumento que muda a consequência |
| Indução de ação | provocar efeito colateral não solicitado |

Contra a base de conhecimento:

| Família | O que tenta |
|---|---|
| **Envenenamento factual** | inserir fato falso, **sem instrução nenhuma** |
| Injeção indireta | esconder instrução no documento |

E cada caso tem um nível de dificuldade. Isso permite a leitura que interessa: resistir a
ataques básicos e ceder aos avançados é um perfil de risco diferente de ceder a todos.

### 6.6 Envenenamento factual: o ataque sem payload

A família mais instrutiva de todas, porque **não contém instrução alguma**. O documento
apenas afirma um fato falso, em prosa perfeitamente normal.

Não há nada para um filtro de injeção detectar. Não há padrão suspeito, não há tentativa de
sobrepor comportamento. O sistema funciona **exatamente como projetado**: recupera conteúdo
relevante, ancora a resposta nele, cita a fonte corretamente.

E entrega informação falsa **com fonte**.

> A ancoragem, que é o principal mecanismo de qualidade de um sistema com recuperação, é
> também o vetor: ela transfere a confiança do documento para a resposta.

É por isso que a defesa não pode ser sobre conteúdo. Ela tem de ser sobre **procedência** —
quem pode colocar documento na base — que é exatamente o controle da seção 5.1.

### 6.7 Efeito colateral medido pelo mundo, não pela flag

Aplicação direta do princípio de cruzamento, agora em contexto de segurança: para saber se uma
ação aconteceu, mede-se o **estado do mundo antes e depois** (delta do arquivo, do banco, do
registro), nunca o campo em que o modelo declara ter agido.

Sob ataque, a autodeclaração do modelo é justamente o que menos merece confiança.

### 6.8 Isolamento do experimento

Uma avaliação que **injeta conteúdo malicioso** precisa de garantias que uma avaliação
funcional não precisa:

- os documentos adversariais vão para uma **coleção isolada**, montada com a base legítima
  mais as fixtures, recriada a cada execução;
- a coleção de produção **nunca recebe conteúdo envenenado e nunca é limpa** pela avaliação;
- uma **lista de nomes permitidos** aborta a execução se o alvo não for a coleção de
  segurança.

A última é o detalhe que separa cuidado de sorte. Um erro de configuração em uma ferramenta
que cria, sobrescreve e destrói coleções é uma questão de tempo, e a defesa é a ferramenta
**recusar-se** a apontar para qualquer lugar que não seja o alvo previsto.

Uma avaliação de segurança é código perigoso. Ela precisa de contenção como qualquer código
perigoso.

### 6.9 Pontuar o estágio, não só o desfecho

Um ataque por documento atravessa uma cadeia, e cada elo é um ponto onde ele pode parar:

```
documento aceito → indexado → recuperado → selecionado → usado como fonte → resposta influenciada
```

Pontuar **cada estágio separadamente** é o que transforma "o ataque falhou" em "o ataque
falhou **aqui**". E os desfechos não são equivalentes — o relatório nunca os agrega em uma
média:

| Desfecho | Significa |
|---|---|
| Rejeitado antes da indexação | o controle de procedência funcionou |
| Indexado, nunca recuperado | sobreviveu ao controle; a busca não o trouxe (**sorte, não defesa**) |
| Chegou ao modelo, impacto contido | a fronteira de dados foi atravessada |
| Resposta influenciada | o ataque teve êxito |

A segunda linha é a mais valiosa de reconhecer. "O ataque não deu certo porque a busca não
trouxe o documento" **não é uma defesa** — é a coincidência de o conteúdo malicioso não ter
sido semanticamente competitivo naquela pergunta. Confundir sorte com controle é a forma mais
comum de superestimar a própria segurança.

### 6.10 O que um ciclo antes/depois mostra — e o que não mostra

Com o mesmo dataset e as mesmas perguntas, mudando apenas o perfil de controles, o resultado
observado foi: **3 de 10 ataques resistidos** sem mitigação (com variação de 3 a 5 em
execuções repetidas), e **10 de 10** com o controle de procedência ativo.

Três leituras necessárias, e a terceira é a que evita conclusões falsas:

**A variação entre execuções é informação.** O mesmo sistema, o mesmo dataset, resultados
entre 3 e 5. O sistema é não determinístico, então uma execução isolada não caracteriza nada —
e qualquer limiar precisa ser interpretado à luz dessa faixa.

**O salto é atribuível a uma mudança.** Um lado, um controle, uma diferença — é a disciplina
experimental da avaliação comparativa aplicada a segurança.

**Dez de dez não é segurança.** É a taxa **daquele dataset versionado, contra aquelas
propriedades bloqueantes, sob aquele perfil de controles**. O controle de procedência fecha o
caminho de origens não autorizadas; ele não faz nada contra os riscos residuais da seção 5.1 —
uma origem autorizada comprometida, um publicador autorizado malicioso, conteúdo externo
copiado para dentro de um documento legítimo.

> Uma taxa de resistência é relativa a um dataset e a um conjunto de propriedades. Não é uma
> medida absoluta de segurança.

Tratar 10/10 como "resolvido" é o modo mais eficiente de desperdiçar tudo o que a medição
ensinou.

### 6.11 Por que baseline de segurança não entra no portão de qualidade

Ainda não. Enquanto os critérios não estiverem calibrados e a faixa de variação não estiver
caracterizada, uma decisão automática de bloqueio produziria reprovações por definição ruim ou
por ruído — e treinaria a equipe a contornar o portão. É o mesmo argumento da avaliação
funcional, com consequência maior.

---

## 7. Riscos abertos: o que a análise revela ao ser feita com honestidade

O valor de um threat model está tanto no que ele lista como ausente quanto no que lista como
implementado. As lacunas abaixo são estruturais, não descuidos — cada uma corresponde a uma
fronteira sem imposição.

| Lacuna | Fronteira | Consequência |
|---|---|---|
| **Sem autenticação e sem limite de taxa** | Input | qualquer requisição entra; consumo sem teto |
| **Escopo sem identidade** | Input / Data | o isolamento entre clientes não é imposto por mecanismo algum |
| **Sem autoridade criptográfica no documento** | Data / Context | origem em sistema de arquivos não é autoria; sem assinatura nem revisão |
| **Conteúdo de origem autorizada sem imposição de confiança** | Data / Context | o risco irredutível: não há separação determinística entre dado e instrução |
| **Sem autorização entre decisão e ação** | Action | a decisão do modelo **é** a autorização |
| **Sem aprovação humana para ações com efeito** | Action | escrita persistida sem intervenção, difícil de reverter |
| **Saída de texto sem contrato de tratamento** | Model Output | conteúdo repassado sem sanitização a um consumidor que pode renderizá-lo |
| **Governança não cobre todos os caminhos** | transversal | o laço do agente escapa da política de custo |
| **Integridade dos datasets assumida** | avaliação | expectativa rebaixada passa na validação e engana o portão |
| **Cadeia de suprimentos sem travamento** | build | dependências sem versão fixa nem verificação de integridade |

Duas observações sobre essa lista.

A quarta linha é a única **irredutível** com a tecnologia atual. Todas as outras têm solução
conhecida: autenticar, amarrar escopo à identidade, assinar documentos, autorizar ações,
exigir aprovação, definir contrato de saída, estender a política, revisar datasets, travar
dependências. São trabalho, não pesquisa.

E as duas últimas linhas mostram por que a infraestrutura de qualidade pertence ao modelo de
ameaças: um dataset adulterado e uma dependência comprometida atacam o sistema **sem tocar em
nenhuma das quatro fronteiras**.

---

## 8. Limitações da própria análise

### 8.1 Análise qualitativa de probabilidade e impacto

Classificar risco em baixo, médio e alto é deliberadamente simples e inevitavelmente
subjetivo. Serve para ordenar prioridades e para conversar; não é quantificação.

### 8.2 O modelo descreve um estado, e estados mudam

Um threat model é uma fotografia. Toda alteração relevante — uma ferramenta nova, um caminho
de ingestão novo, um consumidor novo da saída — potencialmente adiciona uma fronteira. Sem
processo de revisão, o documento vira ficção arqueológica.

### 8.3 Avaliação de segurança é offline

As baselines medem contra datasets, antes do deploy. Nada observa tentativas reais em
produção, onde os ataques são mais criativos que qualquer dataset curado e evoluem em resposta
às defesas.

### 8.4 Dataset adversarial envelhece rápido

Ataques que funcionam hoje podem parar de funcionar quando o modelo é atualizado — e vice-
versa. Uma taxa de resistência medida contra um modelo não transfere para outro, e o dataset
precisa crescer conforme novas técnicas aparecem.

### 8.5 Cobertura desconhecida

Um dataset de algumas dezenas de casos por família cobre uma fração desconhecida do espaço de
ataques. Ausência de falha no dataset não é evidência de ausência de vulnerabilidade — é o
limite epistêmico de qualquer teste.

---

## 9. Síntese

Segurança em sistemas de IA herda tudo da segurança de aplicações e acrescenta um problema
que não existia: **a fronteira entre dado e instrução não é restaurável.** Isso muda a
estratégia de "impedir a injeção" para "reduzir a consequência dela".

Os princípios que se sustentam mutuamente:

1. **Instrução não é barreira** — prompt restritivo, segredo de prompt, saída estruturada e
   filtro de metadados são defesas úteis que não impõem nada.
2. **Duas setas vermelhas** — entrada adversarial também nasce em documento, e nenhum
   guardrail sobre a pergunta do usuário chega perto dela.
3. **A fronteira importa na proporção das capacidades depois dela** — a mesma entrada tem
   blast radius de ordens diferentes em um sistema que responde e em um que age.
4. **Rótulo é conteúdo** — metadado escrito dentro do arquivo nunca prova procedência;
   procedência é atribuída pela aplicação, e origem autorizada ≠ conteúdo confiável.
5. **Controle sobre origem, não sobre conteúdo** — decidido antes da indexação, com resolução
   real de caminho; tentar reconhecer maldade em texto é uma corrida armamentista.
6. **Restrição por impossibilidade de expressão** — não dar ao modelo como dizer o que não
   deve ser dito é melhor que pedir que ele não diga.
7. **Cruzar autodeclaração com evidência externa** — sob ataque, o que o modelo afirma sobre
   si é o dado menos confiável do sistema.
8. **Medir antes de mitigar** — a baseline sem defesas é o que torna qualquer guardrail
   futuro demonstrável, e o perfil de controles precisa ser nomeado em cada execução.
9. **Bloqueante e diagnóstico, agregados por conjunção** — segurança não é média; exposição
   não é sucesso do ataque.
10. **Mitigado não é resolvido** — todo controle vem com risco residual escrito, e uma taxa de
    resistência é relativa a um dataset, não uma medida absoluta.

A pergunta que resume o capítulo: **o que este sistema permite que aconteça quando a entrada é
hostil, e quanto disso é impedido por um mecanismo em vez de por um pedido?** A resposta
separa as defesas que existem das que se acredita ter — e essa separação, escrita e mantida, é
o que um threat model entrega.
