import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_postgres import PGVector
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

PROMPT_TEMPLATE = """
CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""

def validate_environment():
    required_vars = ["OPENAI_API_KEY", "PGVECTOR_URL", "PGVECTOR_COLLECTION"]
    for var in required_vars:
        if not os.getenv(var):
            raise RuntimeError(f"Environment variable {var} is not set")

def get_vector_store():
    validate_environment()
    
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_MODEL", "text-embedding-3-small")
    )
    
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )
    
    return store

def search_documents(query: str, k: int = 10):
    store = get_vector_store()
    
    results = store.similarity_search_with_score(query, k=k)
    
    if not results:
        return []
    
    return results

def format_context(results):
    if not results:
        return "Nenhuma informação relevante encontrada."
    
    context_parts = []
    for i, (doc, score) in enumerate(results, 1):
        context_parts.append(f"--- Documento {i} (relevância: {score:.3f}) ---")
        context_parts.append(doc.page_content.strip())
        context_parts.append("")
    
    return "\n".join(context_parts)

def search_prompt(question=None):
    try:
        validate_environment()
        
        llm = ChatOpenAI(
            model="gpt-5-nano",
            temperature=0.1
        )
        
        prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
        
        chain = prompt | llm
        
        return chain
        
    except Exception as e:
        print(f"Erro ao inicializar o sistema de busca: {e}")
        return None

def get_answer(question: str):
    try:
        print("🔍 Buscando documentos relevantes...")
        results = search_documents(question, k=10)
        
        if not results:
            return "Não tenho informações necessárias para responder sua pergunta."
        
        print(f"📄 Encontrados {len(results)} documentos relevantes")
        
        context = format_context(results)
        
        chain = search_prompt()
        if not chain:
            return "Erro ao processar a pergunta."
        
        print("🤖 Gerando resposta...")
        response = chain.invoke({
            "contexto": context,
            "pergunta": question
        })
        
        return response.content
        
    except Exception as e:
        print(f"Erro durante a busca: {e}")
        return "Ocorreu um erro ao processar sua pergunta."