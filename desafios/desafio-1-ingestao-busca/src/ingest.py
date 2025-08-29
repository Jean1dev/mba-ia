import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_postgres import PGVector

load_dotenv()

def validate_environment():
    required_vars = ["OPENAI_API_KEY", "PGVECTOR_URL", "PGVECTOR_COLLECTION"]
    for var in required_vars:
        if not os.getenv(var):
            raise RuntimeError(f"Environment variable {var} is not set")

def ingest_pdf():
    validate_environment()
    
    current_dir = Path(__file__).parent.parent
    pdf_path = current_dir / "document.pdf"
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found at {pdf_path}")
    
    print("Carregando PDF...")
    docs = PyPDFLoader(str(pdf_path)).load()
    print(f"PDF carregado com {len(docs)} páginas")
    
    print("Dividindo em chunks...")
    splits = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=150, 
        add_start_index=False
    ).split_documents(docs)
    
    if not splits:
        raise RuntimeError("Nenhum chunk foi criado do PDF")
    
    print(f"Criados {len(splits)} chunks")
    
    print("Limpando metadados...")
    enriched = [
        Document(
            page_content=d.page_content,
            metadata={k: v for k, v in d.metadata.items() if v not in ("", None)}
        )
        for d in splits
    ]
    
    print("Gerando IDs únicos...")
    ids = [f"doc-{i}" for i in range(len(enriched))]
    
    print("Inicializando embeddings...")
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_MODEL", "text-embedding-3-small")
    )
    
    print("Conectando ao banco de dados...")
    store = PGVector(
        embeddings=embeddings,
        collection_name=os.getenv("PGVECTOR_COLLECTION"),
        connection=os.getenv("PGVECTOR_URL"),
        use_jsonb=True,
    )
    
    print("Armazenando documentos no banco...")
    store.add_documents(documents=enriched, ids=ids)
    
    print(f"✅ Ingestão concluída! {len(enriched)} documentos armazenados.")

if __name__ == "__main__":
    try:
        ingest_pdf()
    except Exception as e:
        print(f"❌ Erro durante a ingestão: {e}")
        exit(1)