# Curso de Prompt Engineering

Este repositório contém os exercícios práticos e exemplos da disciplina de Prompt Engineering do MBA em Engenharia de Software com IA.

## Instruções de Configuração

### 1. Criar e Ativar Ambiente Virtual

```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No macOS/Linux:
source venv/bin/activate

# No Windows:
venv\Scripts\activate
```

### 2. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 3. Configuração do Ambiente

Copie o arquivo de exemplo e configure suas chaves de API:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione sua chave da API OpenAI:

```
OPENAI_API_KEY=sua_chave_api_aqui
```

## Executando os Scripts

Execute qualquer script usando o seguinte padrão de comando:

```bash
python 1-tipos-de-prompts/<nome_do_script>.py
```

### Exemplos

```bash
# Executar exemplo de prompting zero-shot
python 1-tipos-de-prompts/1-zero-shot.py

# Executar exemplo Chain of Thought
python 1-tipos-de-prompts/3-CoT.py

# Executar exemplo do framework ReAct
python 1-tipos-de-prompts/6-ReAct.py

# Executar exemplo de encadeamento de prompts
python 1-tipos-de-prompts/7-Prompt-channing.py
```

## Arquivos de Saída

Alguns scripts geram arquivos de saída:

- `prompt_chaining_result.md` - Gerado pelo script de encadeamento de prompts com resultados detalhados de cada modelo no pipeline

## Requisitos

- Python 3.8+
- Chave da API OpenAI
- Conexão com a internet para chamadas da API

## Dependências

Principais bibliotecas usadas neste curso:

- `langchain` - Framework para aplicações LLM
- `langchain-openai` - Integração OpenAI para LangChain
- `python-dotenv` - Gerenciamento de variáveis de ambiente
- `openai` - Cliente Python da OpenAI

Para a lista completa de dependências, veja `requirements.txt`.
