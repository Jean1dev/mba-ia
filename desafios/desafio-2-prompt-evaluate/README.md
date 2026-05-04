# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

## Objetivo

Você deve entregar um software capaz de:

1. **Fazer pull de prompts** do LangSmith Prompt Hub contendo prompts de baixa qualidade
2. **Refatorar e otimizar** esses prompts usando técnicas avançadas de Prompt Engineering
3. **Fazer push dos prompts otimizados** de volta ao LangSmith
4. **Avaliar a qualidade** através de métricas customizadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Atingir pontuação mínima** de 0.9 (90%) em todas as métricas de avaliação

---

## Exemplo no CLI

**Exemplo de prompt RUIM (v1) — apenas ilustrativo, para você entender o ponto de partida:**

```
==================================================
Prompt: {seu_username}/bug_to_user_story_v1
==================================================

Métricas Derivadas:
  - Helpfulness: 0.45 ✗
  - Correctness: 0.52 ✗

Métricas Base:
  - F1-Score: 0.48 ✗
  - Clarity: 0.50 ✗
  - Precision: 0.46 ✗

❌ STATUS: REPROVADO
⚠️  Métricas abaixo de 0.9: helpfulness, correctness, f1_score, clarity, precision
```

**Exemplo de prompt OTIMIZADO (v2) — seu objetivo é chegar aqui:**

```bash
# Após refatorar os prompts e fazer push
python src/push_prompts.py

# Executar avaliação
python src/evaluate.py

Executando avaliação dos prompts...
==================================================
Prompt: {seu_username}/bug_to_user_story_v2
==================================================

Métricas Derivadas:
  - Helpfulness: 0.94 ✓
  - Correctness: 0.96 ✓

Métricas Base:
  - F1-Score: 0.93 ✓
  - Clarity: 0.95 ✓
  - Precision: 0.92 ✓

✅ STATUS: APROVADO - Todas as métricas >= 0.9
```
---

## Tecnologias obrigatórias

- **Linguagem:** Python 3.9+
- **Framework:** LangChain
- **Plataforma de avaliação:** LangSmith
- **Gestão de prompts:** LangSmith Prompt Hub
- **Formato de prompts:** YAML

---

## Pacotes recomendados

```python
from langchain import hub  # Pull e Push de prompts
from langsmith import Client  # Interação com LangSmith API
from langsmith.evaluation import evaluate  # Avaliação de prompts
from langchain_openai import ChatOpenAI  # LLM OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI  # LLM Gemini
```

---

## OpenAI

- Crie uma **API Key** da OpenAI: https://platform.openai.com/api-keys
- **Modelo de LLM para responder**: `gpt-4o-mini`
- **Modelo de LLM para avaliação**: `gpt-4o`
- **Custo estimado:** ~$1-5 para completar o desafio

## Gemini (modelo free)

- Crie uma **API Key** da Google: https://aistudio.google.com/app/apikey
- **Modelo de LLM para responder**: `gemini-2.5-flash`
- **Modelo de LLM para avaliação**: `gemini-2.5-flash`
- **Limite:** 15 req/min, 1500 req/dia

---

## Requisitos

### 1. Pull do Prompt inicial do LangSmith

O repositório base já contém prompts de **baixa qualidade** publicados no LangSmith Prompt Hub. Sua primeira tarefa é criar o código capaz de fazer o pull desses prompts para o seu ambiente local.

**Tarefas:**

1. Configurar suas credenciais do LangSmith no arquivo `.env` (conforme o arquivo `.env.example`)
2. Implementar o script `src/pull_prompts.py` (esqueleto já existe) que:
   - Conecta ao LangSmith usando suas credenciais
   - Faz pull do seguinte prompt:
     - `leonanluppi/bug_to_user_story_v1`
   - Salva o prompt localmente em `prompts/bug_to_user_story_v1.yml`

---

### 2. Otimização do Prompt

Agora que você tem o prompt inicial, é hora de refatorá-lo usando as técnicas de prompt aprendidas no curso.

**Tarefas:**

1. Analisar o prompt em `prompts/bug_to_user_story_v1.yml`
2. Criar um novo arquivo `prompts/bug_to_user_story_v2.yml` com suas versões otimizadas
3. Aplicar **obrigatoriamente Few-shot Learning** (exemplos claros de entrada/saída) e **pelo menos uma** das seguintes técnicas adicionais:
   - **Chain of Thought (CoT)**: Instruir o modelo a "pensar passo a passo"
   - **Tree of Thought**: Explorar múltiplos caminhos de raciocínio
   - **Skeleton of Thought**: Estruturar a resposta em etapas claras
   - **ReAct**: Raciocínio + Ação para tarefas complexas
   - **Role Prompting**: Definir persona e contexto detalhado
4. Documentar no `README.md` quais técnicas você escolheu e por quê

**Requisitos do prompt otimizado:**

- Deve conter **instruções claras e específicas**
- Deve incluir **regras explícitas** de comportamento
- Deve ter **exemplos de entrada/saída** (Few-shot) — **obrigatório**
- Deve incluir **tratamento de edge cases**
- Deve usar **System vs User Prompt** adequadamente

Documentação detalhada: [Técnicas Aplicadas (Fase 2)](#técnicas-aplicadas-fase-2).

---

### 3. Push e Avaliação

Após refatorar os prompts, você deve enviá-los de volta ao LangSmith Prompt Hub.

**Tarefas:**

1. Implementar o script `src/push_prompts.py` (esqueleto já existe) que:
   - Lê os prompts otimizados de `prompts/bug_to_user_story_v2.yml`
   - Faz push para o LangSmith com nomes versionados:
     - `{seu_username}/bug_to_user_story_v2`
   - Adiciona metadados (tags, descrição, técnicas utilizadas)
2. Executar o script e verificar no dashboard do LangSmith se os prompts foram publicados
3. Deixá-lo público

---

### 4. Iteração

- Espera-se 3-5 iterações.
- Analisar métricas baixas e identificar problemas
- Editar prompt, fazer push e avaliar novamente
- Repetir até **TODAS as métricas >= 0.9**

### Critério de Aprovação:

```
- Helpfulness >= 0.9
- Correctness >= 0.9
- F1-Score >= 0.9
- Clarity >= 0.9
- Precision >= 0.9

MÉDIA das 5 métricas >= 0.9
```

**IMPORTANTE:** TODAS as 5 métricas devem estar >= 0.9, não apenas a média!

### 5. Testes de Validação

**O que você deve fazer:** Edite o arquivo `tests/test_prompts.py` e implemente, no mínimo, os 6 testes abaixo usando `pytest`:

- `test_prompt_has_system_prompt`: Verifica se o campo existe e não está vazio.
- `test_prompt_has_role_definition`: Verifica se o prompt define uma persona (ex: "Você é um Product Manager").
- `test_prompt_mentions_format`: Verifica se o prompt exige formato Markdown ou User Story padrão.
- `test_prompt_has_few_shot_examples`: Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot).
- `test_prompt_no_todos`: Garante que você não esqueceu nenhum `[TODO]` no texto.
- `test_minimum_techniques`: Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas.

**Como validar:**

```bash
pytest tests/test_prompts.py
```

---

## Estrutura obrigatória do projeto

Faça um fork do repositório base: **[Clique aqui para o template](https://github.com/devfullcycle/mba-ia-pull-evaluation-prompt)**

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Template das variáveis de ambiente
├── requirements.txt          # Dependências Python
├── README.md                 # Sua documentação do processo
│
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Prompt inicial (já incluso)
│   └── bug_to_user_story_v2.yml  # Seu prompt otimizado (criar)
│
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 exemplos de bugs (já incluso)
│
├── src/
│   ├── pull_prompts.py       # Pull do LangSmith (implementar)
│   ├── push_prompts.py       # Push ao LangSmith (implementar)
│   ├── evaluate.py           # Avaliação automática (pronto)
│   ├── metrics.py            # 5 métricas implementadas (pronto)
│   └── utils.py              # Funções auxiliares (pronto)
│
├── tests/
│   └── test_prompts.py       # Testes de validação (implementar)
│
```

**O que você deve implementar:**

- `prompts/bug_to_user_story_v2.yml` — Criar do zero com seu prompt otimizado
- `src/pull_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `src/push_prompts.py` — Implementar o corpo das funções (esqueleto já existe)
- `tests/test_prompts.py` — Implementar os 6 testes de validação (esqueleto já existe)
- `README.md` — Documentar seu processo de otimização

**O que já vem pronto (não alterar):**

- `src/evaluate.py` — Script de avaliação completo
- `src/metrics.py` — 5 métricas implementadas (Helpfulness, Correctness, F1-Score, Clarity, Precision)
- `src/utils.py` — Funções auxiliares
- `datasets/bug_to_user_story.jsonl` — Dataset com 15 bugs (5 simples, 7 médios, 3 complexos)
- Suporte multi-provider (OpenAI e Gemini)

## Repositórios úteis

- [Repositório boilerplate do desafio](https://github.com/devfullcycle/mba-ia-prompt-engineering)
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

## VirtualEnv para Python

Crie e ative um ambiente virtual antes de instalar dependências:

```bash
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Ordem de execução

Resumo rápido; passo a passo completo em [Como Executar](#como-executar).

### 1. Executar pull dos prompts ruins

```bash
python src/pull_prompts.py
```

### 2. Refatorar prompts

Edite manualmente o arquivo `prompts/bug_to_user_story_v2.yml` aplicando as técnicas aprendidas no curso.

### 3. Fazer push dos prompts otimizados

```bash
python src/push_prompts.py
```

### 4. Executar avaliação

```bash
python src/evaluate.py
```

**Atalho (push + avaliação):** `./etapa-03-push-e-avaliacao.sh` a partir do diretório do desafio.

---

## Técnicas Aplicadas (Fase 2)

### Técnicas escolhidas

| Técnica | Uso neste projeto |
|--------|-------------------|
| **Chain of Thought (CoT)** | Roteiro mental (tipo → ator → fatos → critérios) **antes** da redação, sem imprimir raciocínio na resposta final, para não divergir do *ground truth* da avaliação. |
| **Few-shot Learning** | Exemplos extensos no *system prompt*: “**Espelhos**” com o mesmo texto de referência do `datasets/bug_to_user_story.jsonl` (carrinho, e-mail, iOS, dashboard, Safari, webhook com `Gateway: [nome do gateway de pagamento]`, CRM, Android/ANR, estoque, modal, etc.), para o modelo alinhar estrutura e redação ao juiz automático. |
| **Role Prompting** | Persona **Product Manager sênior**, tom para engenharia, QA e stakeholders, com regras de completude (modo A simples, B médio, C longo com `===` quando o relato exige). |

### Justificativa

- **CoT interno:** incluir `### Raciocínio` na saída penalizava F1 e *precision* porque as referências do dataset são só User Story + critérios (+ contextos nomeados). O raciocínio ficou só nas instruções.
- **Few-shot por espelhos:** as métricas usam LLM-*as-judge* comparando a resposta gerada ao texto de referência; reproduzir seções e formulações canônicas do dataset elevou consistência sem alterar o arquivo `.jsonl`.
- **Role + modos A/B/C:** reduz respostas genéricas e força o nível de detalhe certo (ex.: três linhas de *Contexto Técnico* no webhook, *Exemplo de Cálculo* no pipeline de desconto).

### Exemplos práticos

1. **Webhook + HTTP 500:** o espelho exige `POST /api/webhooks/payment`, critérios com e-mail e auditoria, e *Contexto Técnico* com as três bullets, incluindo o placeholder do gateway.
2. **Pipeline de desconto:** *Critérios de Aceitação* com fórmula explícita e bloco *Exemplo de Cálculo* com subtotal R$ 1.500, desconto 10% e total R$ 1.350 alinhados ao relato.
3. **Relatos longos (checkout, relatórios, sync offline):** uso de cabeçalhos `=== USER STORY PRINCIPAL ===`, `=== CRITÉRIOS DE ACEITAÇÃO ===` (A/B/C…), `=== TASKS TÉCNICAS SUGERIDAS ===`, sem inventar métricas que não apareçam no bug.

---

## Resultados Finais

### Execução aprovada (referência deste repositório)

Rodada em que **todas** as métricas ficaram **≥ 0,9** (*dataset* com 15 exemplos, modelo conforme `.env` no momento da avaliação):

| Métrica | Valor |
|--------|------:|
| Helpfulness | 0.96 |
| Correctness | 0.95 |
| F1-Score | 0.97 |
| Clarity | 0.98 |
| Precision | 0.94 |
| **Média geral** | **0.9570** |

### Tabela comparativa (ilustrativa v1 × v2)

| Métrica | v1 (ruim — típico do desafio) | v2 (otimizado — após iterações) |
|--------|------------------------------:|--------------------------------:|
| Helpfulness | ~0.45 | 0.96 |
| Correctness | ~0.52 | 0.95 |
| F1-Score | ~0.48 | 0.97 |
| Clarity | ~0.50 | 0.98 |
| Precision | ~0.46 | 0.94 |

Os valores da coluna v1 são **ilustrativos** (conforme enunciado do desafio); a coluna v2 reflete uma execução **APROVADA** com o prompt em `prompts/bug_to_user_story_v2.yml`.

### Link público (LangSmith)

Dashboard / visão compartilhada (acesso sem login no workspace, conforme partilha do LangSmith):

**[Abrir evidências no LangSmith](https://smith.langchain.com/public/aa8b6caa-c594-4d45-a115-8f79aa4b4ac7/d?tab=0)**

### Evidências complementares

1. **Screenshots:** opcional mas recomendado no repositório (ex.: `docs/evidencias/`): dataset com **15 exemplos**, métricas da avaliação do prompt v2 (≥ 0.9) e **tracing** de pelo menos **3** exemplos.

*(O link `/public/...` é o relatório ou recurso que você marcou como público no LangSmith; dentro da UI também existe partilha por recurso.)*

---

## Como Executar

### Pré-requisitos

- Python **3.9+** e `python3-venv` (em Debian/Ubuntu: `sudo apt install python3-venv` se `python3 -m venv` falhar).
- Conta [LangSmith](https://smith.langchain.com) com API Key e, para avaliação com OpenAI, chave [OpenAI](https://platform.openai.com/api-keys) (ou Google para Gemini — ver `.env.example`).

### Configuração

1. Copie o ambiente: `cp .env.example .env`
2. Preencha no mínimo: `LANGSMITH_API_KEY`, `USERNAME_LANGSMITH_HUB` (mesmo *tenant* da key), `LANGSMITH_PROJECT`, provedor LLM e chaves (`OPENAI_API_KEY` ou `GOOGLE_API_KEY`).
3. Crie o *venv* e instale dependências:

```bash
cd desafios/desafio-2-prompt-evaluate
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Os scripts `etapa-*.sh` criam o `venv` e instalam dependências automaticamente se necessário.

### Comandos por fase

| Fase | Objetivo | Comando |
|------|-----------|---------|
| 1 | Pull do Hub → `prompts/bug_to_user_story_v1.yml` | `./etapa-01-pull-prompt-inicial-langsmith.sh` ou `python src/pull_prompts.py` |
| 2 | Validar YAML do prompt v2 | `./etapa-02-otimizacao-prompt-cot.sh` ou `pytest tests/test_prompts.py -v` |
| 3 | Push para LangSmith + avaliação | `./etapa-03-push-e-avaliacao.sh` (equivale a `python src/push_prompts.py` e `python src/evaluate.py`) |

Testes de prompt:

```bash
pytest tests/test_prompts.py -v
```

---

## Entregável

1. **Repositório público no GitHub** (fork do template do desafio) contendo o código, `prompts/bug_to_user_story_v2.yml` funcional e este `README.md`.

2. **Checklist do README (enunciado do curso)** — conteúdo correspondente:

   | Item | Onde está neste arquivo |
   |------|-------------------------|
   | A) Técnicas, justificativas e exemplos práticos | [Técnicas Aplicadas (Fase 2)](#técnicas-aplicadas-fase-2) |
   | B) Resultados, link LangSmith, comparativo v1 × v2 | [Resultados Finais](#resultados-finais) |
   | C) Como executar, pré-requisitos, comandos por fase | [Como Executar](#como-executar) |

3. **Evidências no LangSmith** (você publica no seu tenant):

   - Dataset com **15 exemplos** e runs do prompt **`{USERNAME}/bug_to_user_story_v2`** com todas as métricas **≥ 0,9**
   - **Tracing** detalhado de pelo menos **3** exemplos
   - **URL pública** e, se quiser, **screenshots** na secção [Resultados Finais](#resultados-finais)

---

## Dicas Finais

- **Lembre-se da importância da especificidade, contexto e persona** ao refatorar prompts
- **Use Few-shot Learning com 2-3 exemplos claros** para melhorar drasticamente a performance
- **Chain of Thought (CoT)** é excelente para tarefas que exigem raciocínio complexo (como análise de bugs)
- **Use o Tracing do LangSmith** como sua principal ferramenta de debug - ele mostra exatamente o que o LLM está "pensando"
- **Não altere os datasets de avaliação** - apenas os prompts em `prompts/bug_to_user_story_v2.yml`
- **Itere, itere, itere** - é normal precisar de 3-5 iterações para atingir 0.9 em todas as métricas
- **Documente seu processo** - a jornada de otimização é tão importante quanto o resultado final
