# Gerenciamento e versionamento de prompts

Os exemplos estão organizados em duas categorias principais de gerenciamento de prompts:

### 1. Versionamento Local de Prompts
- **Sistema de Registry**: Gerenciamento local usando arquivos YAML estruturados
- **Versionamento por Diretórios**: Organização hierárquica com versões separadas
- **Validação Estática**: Testes automatizados para verificar estrutura e sintaxe

### 2. Versionamento com LangSmith
- **Sincronização Remota**: Push e pull de prompts para/da plataforma LangSmith
- **Controle de Versões**: Integração com sistema de tags e versionamento do LangSmith
- **Colaboração**: Compartilhamento e colaboração em equipe através da plataforma

## Estrutura do Projeto

O projeto está organizado com diretórios separados para prompts versionados, código fonte, testes automatizados e arquivos de configuração.

## Configuração do Ambiente

### 1. Criação do Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Linux/Mac:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### 2. Instalação de Dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração das Variáveis de Ambiente

Copie o arquivo `.env.example` para `.env` e configure as variáveis necessárias:

```bash
cp .env.example .env
```

**Variáveis de ambiente necessárias:**

```bash
# Configuração da API OpenAI (obrigatória)
OPENAI_API_KEY=sk-your-api-key-here

# Configurações do LangSmith (opcionais, necessárias apenas para integração com LangSmith)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your-langsmith-key-here
LANGCHAIN_PROJECT=prompt-management-system
```

**Descrição das variáveis:**

- `OPENAI_API_KEY`: Chave da API OpenAI (obrigatória para execução dos exemplos)
- `LANGCHAIN_TRACING_V2`: Habilita/desabilita o tracing do LangSmith
- `LANGCHAIN_ENDPOINT`: Endpoint da API do LangSmith
- `LANGCHAIN_API_KEY`: Chave da API do LangSmith (necessária para push/pull de prompts)
- `LANGCHAIN_PROJECT`: Nome do projeto no LangSmith para organização dos prompts

## Exemplos de Uso

### Versionamento Local

#### 1. Usando o Registry Local

O sistema de registry permite carregar prompts locais de forma estruturada e versionada.

#### 2. Executando Agentes Localmente

```bash
# Agente revisor de código
python src/agent_code_reviewer.py

# Agente criador de pull requests  
python src/agent_pull_request.py
```

### Versionamento com LangSmith

#### 1. Push de Prompts para LangSmith

Execute o script para sincronizar prompts locais com a plataforma LangSmith.

#### 2. Pull de Prompts do LangSmith

Execute o script para usar prompts diretamente da plataforma LangSmith.

## Sistema de Registry

O arquivo `prompts/registry.yaml` centraliza o gerenciamento dos prompts, mapeando IDs para suas respectivas versões e configurações.

## Estrutura dos Prompts

Cada prompt segue uma estrutura padronizada com campos obrigatórios como `id`, `version`, `template` e `input_variables`, além de metadados opcionais.

## Testes Automatizados

O projeto inclui um sistema completo de testes para validar os prompts:

### Executar Todos os Testes

```bash
# Executar com pytest
pytest tests/test_prompts.py -v

# Ou executar diretamente
python tests/test_prompts.py
```

## Observações sobre a versão da LangChain

Apesar da versão estável da LangChain no momento da criação do exemplo ser a 0.3, os exemplos foram realizados utilizando a versão 1.0.0a5, onde há mudanças consideráveis na API.