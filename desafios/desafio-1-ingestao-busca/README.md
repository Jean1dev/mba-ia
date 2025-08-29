# Desafio 1 - Ingestão e Busca RAG

Sistema de Retrieval-Augmented Generation (RAG) que permite fazer perguntas sobre um documento PDF usando LangChain, PostgreSQL com pgvector e OpenAI.

## 🚀 Funcionalidades

- **Ingestão**: Carrega e processa documentos PDF
- **Busca Semântica**: Encontra informações relevantes usando embeddings
- **Chat CLI**: Interface de linha de comando para perguntas e respostas
- **RAG**: Gera respostas baseadas apenas no conteúdo do documento

## 📋 Pré-requisitos

- Python 3.8+
- Docker e Docker Compose
- Conta na OpenAI com API key

## 🛠️ Configuração

### 1. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
OPENAI_API_KEY=sua_chave_openai_aqui
PGVECTOR_URL=postgresql://postgres:postgres@localhost:5432/rag
PGVECTOR_COLLECTION=documentos
OPENAI_MODEL=text-embedding-3-small
```

### 2. Instalar Dependências

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## 🚀 Execução

### Opção 1: Demonstração (Sem API Key)

Para testar o sistema sem configurar uma API key real:

```bash
python demo.py
```

### Opção 2: Sistema Completo (Com API Key)

1. **Subir o Banco de Dados:**
   ```bash
   docker compose up -d
   ```

2. **Executar Ingestão do PDF:**
   ```bash
   python src/ingest.py
   ```

3. **Iniciar o Chat:**
   ```bash
   python src/chat.py
   ```

## 💬 Como Usar

Após iniciar o chat, você pode fazer perguntas como:

```
❓ Faça sua pergunta:
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
```

O sistema irá:
1. 🔍 Buscar documentos relevantes no banco vetorial
2. 📄 Encontrar os 10 chunks mais similares
3. 🤖 Gerar uma resposta baseada no contexto encontrado

## 📁 Estrutura do Projeto

```
├── docker-compose.yml          # Configuração do PostgreSQL + pgvector
├── requirements.txt            # Dependências Python
├── env.example                # Template de variáveis de ambiente
├── document.pdf               # PDF para ingestão
├── demo.py                    # Script de demonstração
├── test_setup.py              # Script de teste de configuração
├── src/
│   ├── ingest.py              # Script de ingestão do PDF
│   ├── search.py              # Script de busca semântica
│   └── chat.py                # CLI para interação
└── README.md                  # Esta documentação
```

## 🔧 Detalhes Técnicos

### Ingestão
- **Chunking**: 1000 caracteres com overlap de 150
- **Embeddings**: OpenAI text-embedding-3-small
- **Armazenamento**: PostgreSQL com pgvector

### Busca
- **Similaridade**: Busca os 10 documentos mais relevantes
- **LLM**: GPT-5-nano para geração de respostas
- **Contexto**: Resposta baseada apenas no conteúdo do PDF

### Segurança
- Validação de variáveis de ambiente
- Tratamento de erros robusto
- Respostas limitadas ao contexto do documento

## 🧪 Testes

### Verificar Configuração
```bash
python test_setup.py
```

### Executar Demonstração
```bash
python demo.py
```

## 🐛 Solução de Problemas

### Erro de Conexão com Banco
```bash
# Verificar se o container está rodando
docker ps

# Reiniciar se necessário
docker compose restart
```

### Erro de API Key
```bash
# Verificar se a variável está configurada
echo $OPENAI_API_KEY

# Ou verificar o arquivo .env
cat .env
```

### Erro de Dependências
```bash
# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

## 📝 Exemplos de Uso

### Pergunta Dentro do Contexto
```
PERGUNTA: Qual o faturamento da Empresa SuperTechIABrazil?
RESPOSTA: O faturamento foi de 10 milhões de reais.
```

### Pergunta Fora do Contexto
```
PERGUNTA: Quantos clientes temos em 2024?
RESPOSTA: Não tenho informações necessárias para responder sua pergunta.
```

## 🔗 Tecnologias Utilizadas

- **LangChain**: Framework para aplicações de IA
- **OpenAI**: Embeddings e geração de texto
- **PostgreSQL + pgvector**: Banco de dados vetorial
- **Docker**: Containerização do banco de dados
- **Python**: Linguagem de programação

## 📄 Licença

Este projeto é parte do curso de IA e desenvolvimento de agentes.