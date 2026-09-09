# Arquitetura de Aplicações com IA

Documentos conceituais da matéria. Cada arquivo isola **as ideias** de um capítulo,
independentemente da linguagem, do framework ou do provedor de modelo usados na
implementação — a intenção é que continuem válidos com a stack trocada por completo.

## Os documentos

| Documento | Assunto | Pergunta central |
|---|---|---|
| [rag.md](rag.md) | Recuperação aumentada por geração | como fazer o contexto ser seletivo: pouco texto, mas o texto certo? |
| [cache.md](cache.md) | Cache semântico | quando duas perguntas diferentes merecem a mesma resposta? |
| [observabilidade.md](observabilidade.md) | Telemetria e governança operacional | o que precisa estar registrado para uma resposta errada ser explicável depois? |
| [avaliacao.md](avaliacao.md) | Avaliação de qualidade e quality gates | como saber que um sistema que não repete a si mesmo está melhor hoje? |
| [agentes.md](agentes.md) | Agentes, ferramentas e trajetória | como verificar que o sistema fez o que disse ter feito? |
| [seguranca.md](seguranca.md) | Modelagem de ameaças e baselines adversariais | quanto do risco é impedido por um mecanismo, e quanto por um pedido? |

## Ordem de leitura

Os capítulos são cumulativos e cada um pressupõe o anterior:

```
rag → observabilidade → avaliação → agentes → segurança
```

- **rag** estabelece o pipeline: ingestão, planejamento, recuperação, reordenamento, resposta.
- **observabilidade** instrumenta esse pipeline — e a governança de custo só é possível porque
  a instrumentação já media tokens.
- **avaliação** mede a qualidade da resposta em camadas de custo crescente, e termina no portão
  que transforma números em decisão de deploy.
- **agentes** troca o objeto de medida: da resposta para a trajetória, porque a sequência de
  execução passou a ser decidida pelo modelo.
- **segurança** relê tudo pela ótica do adversário, e mostra que a infraestrutura de avaliação
  é, ela mesma, um asset a proteger.

**cache.md** é independente dos outros e pode ser lido a qualquer momento.

### As limitações de um capítulo são o capítulo seguinte

Vale ler a seção "Limitações reconhecidas" do `rag.md` sabendo que ela é, em boa parte, o
roteiro do que vem depois:

| Limitação declarada no `rag.md` | Onde é endereçada |
|---|---|
| "não há conjunto de referência nem métricas automáticas de fidelidade e relevância" | `avaliacao.md` — dataset versionado, métricas de referência livre, rubrica própria |
| observabilidade limitada a log estruturado e tempos por etapa | `observabilidade.md` — tracing, convenções semânticas, política por ambiente |
| custo medido em tokens, sem consequência | `observabilidade.md` — governança: orçamento, allowlist e ledger |
| a separação de autoridade entre modelo e aplicação, tratada como princípio | `seguranca.md` — a mesma ideia como fronteira de confiança, com risco residual escrito |

O caminho inverso também vale: cada capítulo novo abre limitações próprias, e a seção final
de cada documento as declara.

## Ideias que atravessam mais de um capítulo

| Ideia | Onde aparece |
|---|---|
| **Estratificação por custo** — tente sempre o mais barato e mais seguro primeiro | cascata de cache; cascata de avaliação; ordem das camadas de telemetria |
| **Determinístico versus generativo** — nem toda etapa de um fluxo de IA precisa de IA | trabalho determinístico no cache; pontuação por comparação na avaliação; propriedades determinísticas de trajetória |
| **Metadado é operação, conteúdo é dado sensível** | atributo versus evento na telemetria; canal de avaliação que a API não tem; rótulo não concede procedência |
| **Autodeclaração não é evidência** — cruze com uma fonte independente | fontes construídas pela aplicação; trajetória lida do framework; efeito medido pelo delta do mundo |
| **Critério imutável depois de medido** — barra que se abaixa não é barra | versão do dataset; versão da rubrica; perfil de controles de segurança |
| **Não aplicável não é passou** | denominadores variáveis na avaliação; propriedade diagnóstica versus bloqueante |
| **Certa como escrita, errada como definida** | métrica de cobertura de tipos; critério de recusa do agente; portão reprovando por definição ruim |
| **Restrição por impossibilidade de expressão** | esquema do planejador sem campos de escopo; contexto que a API não tem como serializar |
| **Mitigado não é resolvido** | risco residual de cada controle; taxa de resistência relativa ao dataset |
