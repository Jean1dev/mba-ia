# Documentação Completa - Fundamentos LangChain

## 📋 Visão Geral

Este repositório contém um curso completo de introdução ao LangChain, organizado em 5 módulos progressivos que cobrem desde conceitos básicos até implementações avançadas de RAG (Retrieval-Augmented Generation) e agentes inteligentes.

## 🏗️ Estrutura do Projeto

```
fundamentos-lang-chain/
├── 1-fundamentos/                    # Conceitos básicos e primeiros passos
├── 2-chains-e-processamento/         # Pipelines e processamento avançado
├── 3-agentes-e-tools/               # Agentes inteligentes e ferramentas
├── 4-gerenciamento-de-memoria/      # Histórico e sessões de conversa
├── 5-loaders-e-banco-de-dados-vetoriais/  # RAG e bancos vetoriais
├── requirements.txt                  # Dependências do projeto
├── docker-compose.yaml              # Configuração do PostgreSQL + pgvector
└── README.md                        # Documentação original
```

## 🚀 Configuração Inicial

### Pré-requisitos
- Python 3.8+
- Docker e Docker Compose
- Contas nas APIs: OpenAI e Google Gemini

### Instalação
```bash
# 1. Criar ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou venv\Scripts\activate  # Windows

# 2. Instalar dependências
pip install -r requirements.txt

# 3. Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas API keys
```

### Variáveis de Ambiente Necessárias
```env
OPENAI_API_KEY=sua_chave_openai
GOOGLE_API_KEY=sua_chave_google
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=documentos
OPENAI_MODEL=text-embedding-3-small
```

## 📚 Módulo 1: Fundamentos Básicos

### 1.1 Hello World (`1-hello-world.py`)
**Objetivo**: Primeiro contato com LangChain e OpenAI
```python
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-5-nano", temperature=0.5)
message = model.invoke("Hello World")
```

**Conceitos**: 
- Integração básica com OpenAI
- Configuração de modelo e temperatura
- Invocação simples de LLM

### 1.2 Inicialização de Chat Model (`2-init-chat-model.py`)
**Objetivo**: Configuração de modelos de chat
**Conceitos**: 
- Diferentes modelos disponíveis
- Configuração de parâmetros
- Estrutura de mensagens

### 1.3 Prompt Templates (`3-prompt-template.py`)
**Objetivo**: Criação de templates de prompt
```python
from langchain.prompts import PromptTemplate
template = PromptTemplate(
    input_variables=["name"],
    template="Hi, I'm {name}! Tell me a joke with my name!"
)
```

**Conceitos**:
- Templates com variáveis
- Reutilização de prompts
- Formatação estruturada

### 1.4 Chat Prompt Templates (`4-chat-prompt-template.py`)
**Objetivo**: Templates para conversas estruturadas
```python
from langchain_core.prompts import ChatPromptTemplate
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
])
```

**Conceitos**:
- Prompts de chat estruturados
- Roles (system, human, assistant)
- Conversas multi-turno

## 🔗 Módulo 2: Chains e Processamento

### 2.1 Iniciando com Chains (`1-iniciando-com-chains copy.py`)
**Objetivo**: Introdução ao LCEL (LangChain Expression Language)
```python
chain = prompt | model
result = chain.invoke({"input": "Hello"})
```

**Conceitos**:
- Sintaxe de pipe (|)
- Composição de componentes
- LCEL básico

### 2.2 Chains com Decorators (`2-chains-com-decorators.py`)
**Objetivo**: Criação de chains customizadas
```python
@chain
def square(input_dict: dict) -> dict:
    x = input_dict["x"]
    return {"square_result": x * x}

chain2 = square | question_template2 | model
```

**Conceitos**:
- Decorador @chain
- Funções customizadas
- Pipelines complexos

### 2.3 Runnable Lambda (`3-runnable-lambda.py`)
**Objetivo**: Funções lambda em chains
```python
from langchain_core.runnables import RunnableLambda
chain = RunnableLambda(lambda x: x.upper()) | model
```

**Conceitos**:
- RunnableLambda
- Transformações simples
- Integração com LLMs

### 2.4 Pipeline de Processamento (`4-pipeline-de-processamento.py`)
**Objetivo**: Pipelines multi-etapas
**Conceitos**:
- Processamento sequencial
- Transformações de dados
- Fluxo de trabalho

### 2.5 Sumarização (`5-sumarizacao.py`)
**Objetivo**: Técnicas de sumarização de documentos
```python
from langchain.chains.summarize import load_summarize_chain
chain = load_summarize_chain(llm, chain_type="stuff")
```

**Conceitos**:
- Sumarização "stuff"
- Processamento de documentos longos
- Chunking de texto

### 2.6 Sumarização Map-Reduce (`6-sumarizacao-com-map-reduce.py`)
**Objetivo**: Sumarização distribuída
```python
chain = load_summarize_chain(llm, chain_type="map_reduce")
```

**Conceitos**:
- Map-reduce para sumarização
- Processamento paralelo
- Eficiência em documentos grandes

### 2.7 Pipeline de Sumarização (`7-pipeline-de-sumarizacao.py`)
**Objetivo**: Pipeline completo de sumarização
**Conceitos**:
- Text splitters
- Processamento em lotes
- Otimização de performance

## 🤖 Módulo 3: Agentes e Tools

### 3.1 Agente ReAct com Tools (`1-agente-react-e-tools.py`)
**Objetivo**: Implementação de agentes que raciocinam e agem
```python
@tool("calculator", return_direct=True)
def calculator(expression: str) -> str:
    return str(eval(expression))

agent_executor = AgentExecutor.from_agent_and_tools(
    agent=agent_chain, 
    tools=tools, 
    verbose=True
)
```

**Conceitos**:
- Framework ReAct (Reasoning + Acting)
- Tools customizadas
- Agentes autônomos
- Execução de ações

### 3.2 Agente ReAct com Prompt Hub (`2-agente-react-usando-prompt-hub.py`)
**Objetivo**: Uso de prompts pré-definidos
```python
from langchain import hub
prompt = hub.pull("hwchase17/react")
```

**Conceitos**:
- Prompt Hub
- Prompts da comunidade
- Reutilização de prompts

## 🧠 Módulo 4: Gerenciamento de Memória

### 4.1 Armazenamento de Histórico (`1-armazenamento-de-historico.py`)
**Objetivo**: Implementação de histórico de conversação
```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables import RunnableWithMessageHistory

conversational_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
```

**Conceitos**:
- Histórico persistente
- Sessões de conversa
- Contexto de conversação

### 4.2 Histórico com Sliding Window (`2-historico-baseado-em-sliding-window.py`)
**Objetivo**: Gerenciamento de contexto limitado
```python
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage
```

**Conceitos**:
- Janela deslizante
- Limitação de contexto
- Otimização de memória

## 📄 Módulo 5: Loaders e Banco de Dados Vetoriais

### 5.1 Carregamento Web (`1-carregamento-usando-WebBaseLoader copy.py`)
**Objetivo**: Extração de conteúdo de páginas web
```python
from langchain_community.document_loaders import WebBaseLoader
loader = WebBaseLoader("https://example.com")
docs = loader.load()
```

**Conceitos**:
- Web scraping
- Extração de conteúdo
- Processamento de HTML

### 5.2 Carregamento de PDF (`2-carregamento-de-pdf.py`)
**Objetivo**: Processamento de documentos PDF
```python
from langchain_community.document_loaders import PyPDFLoader
loader = PyPDFLoader("documento.pdf")
docs = loader.load()
```

**Conceitos**:
- Processamento de PDF
- Extração de texto
- Metadados de documentos

### 5.3 Ingestão com pgvector (`3-ingestion-pgvector.py`)
**Objetivo**: Armazenamento de embeddings em PostgreSQL
```python
from langchain_postgres import PGVector
from langchain_openai import OpenAIEmbeddings

store = PGVector(
    embeddings=embeddings,
    collection_name=os.getenv("PGVECTOR_COLLECTION"),
    connection=os.getenv("PGVECTOR_URL"),
    use_jsonb=True,
)

store.add_documents(documents=enriched, ids=ids)
```

**Conceitos**:
- Embeddings vetoriais
- PostgreSQL com pgvector
- Armazenamento de documentos
- Chunking de texto

### 5.4 Busca Vetorial (`4-search-vector.py`)
**Objetivo**: Busca semântica em documentos
```python
results = store.similarity_search_with_score(query, k=3)
for doc, score in results:
    print(f"Score: {score:.2f}")
    print(doc.page_content)
```

**Conceitos**:
- Busca por similaridade
- Scoring de relevância
- RAG (Retrieval-Augmented Generation)

## 🛠️ Configuração do Banco de Dados

### Docker Compose
```yaml
services:
  postgres:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: rag
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
```

### Inicialização
```bash
docker compose up -d
```

## 📦 Dependências Principais

### Core LangChain
- `langchain==0.3.27` - Framework principal
- `langchain-core==0.3.74` - Componentes core
- `langchain-community==0.3.27` - Integrações da comunidade

### LLM Providers
- `langchain-openai==0.3.30` - Integração OpenAI
- `langchain-google-genai==2.1.9` - Integração Google Gemini

### Database e Vector Stores
- `langchain-postgres==0.0.15` - PostgreSQL com pgvector
- `pgvector==0.3.6` - Extensão vetorial
- `psycopg==3.2.9` - Driver PostgreSQL

### Document Processing
- `langchain-text-splitters==0.3.9` - Divisão de texto
- `pypdf==6.0.0` - Processamento PDF
- `beautifulsoup4==4.13.4` - Parsing HTML

## 🎯 Padrões de Desenvolvimento

### 1. Estrutura de Projeto
```
projeto/
├── src/
│   ├── agents/
│   ├── chains/
│   ├── tools/
│   └── utils/
├── data/
├── config/
└── tests/
```

### 2. Configuração de Ambiente
```python
from dotenv import load_dotenv
import os

load_dotenv()

# Validação de variáveis
required_vars = ["OPENAI_API_KEY", "PGVECTOR_URL"]
for var in required_vars:
    if not os.getenv(var):
        raise RuntimeError(f"Environment variable {var} is not set")
```

### 3. Padrão de Chain
```python
from langchain_core.runnables import chain

@chain
def custom_chain(input_dict: dict) -> dict:
    # Processamento
    result = process_input(input_dict)
    return {"output": result}

# Composição
pipeline = custom_chain | llm | output_parser
```

### 4. Padrão de Tool
```python
from langchain.tools import tool

@tool("tool_name")
def tool_function(input: str) -> str:
    """Descrição da ferramenta."""
    # Implementação
    return result
```

### 5. Padrão de Agente
```python
from langchain.agents import create_react_agent, AgentExecutor

agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor.from_agent_and_tools(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=3
)
```

## 🔄 Fluxo de Desenvolvimento

### 1. Análise de Requisitos
- Definir objetivo do agente/chain
- Identificar ferramentas necessárias
- Planejar fluxo de dados

### 2. Implementação
- Criar tools customizadas
- Desenvolver chains de processamento
- Implementar agentes

### 3. Teste e Validação
- Testar com dados reais
- Validar outputs
- Otimizar performance

### 4. Deploy
- Configurar ambiente de produção
- Monitorar performance
- Manter e atualizar

## 🚨 Boas Práticas

### Segurança
- Nunca expor API keys no código
- Validar inputs de usuário
- Usar eval() apenas em ambientes controlados

### Performance
- Implementar caching quando apropriado
- Usar chunking para documentos grandes
- Otimizar queries vetoriais

### Manutenibilidade
- Documentar funções e classes
- Usar type hints
- Implementar logging
- Criar testes unitários

### Escalabilidade
- Usar conexões de banco pooladas
- Implementar rate limiting
- Considerar arquitetura distribuída

## 📈 Próximos Passos

### Para Desenvolvimento de Novos Projetos

1. **Definir Arquitetura**
   - Escolher entre agentes, chains ou RAG
   - Definir fluxo de dados
   - Planejar integrações

2. **Configurar Ambiente**
   - Instalar dependências
   - Configurar variáveis de ambiente
   - Preparar banco de dados

3. **Implementar Core**
   - Criar tools necessárias
   - Desenvolver chains de processamento
   - Implementar agentes

4. **Integrar e Testar**
   - Conectar componentes
   - Testar com dados reais
   - Otimizar performance

5. **Deploy e Monitor**
   - Configurar produção
   - Implementar monitoramento
   - Manter e atualizar

## 🔗 Recursos Adicionais

- [Documentação Oficial LangChain](https://python.langchain.com/)
- [LangChain Hub](https://smith.langchain.com/hub)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google AI Studio](https://ai.google.dev/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

**Nota**: Esta documentação serve como ponto de partida para desenvolvimento de novas tarefas. Mantenha-a atualizada conforme o projeto evolui.
