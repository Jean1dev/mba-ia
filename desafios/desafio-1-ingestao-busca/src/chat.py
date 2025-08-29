from search import get_answer
import os
from dotenv import load_dotenv

load_dotenv()

def validate_setup():
    required_vars = ["OPENAI_API_KEY", "PGVECTOR_URL", "PGVECTOR_COLLECTION"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variáveis de ambiente não configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Configure as variáveis no arquivo .env")
        return False
    
    return True

def main():
    print("🤖 Chat RAG - Sistema de Perguntas e Respostas")
    print("=" * 50)
    
    if not validate_setup():
        return
    
    print("✅ Sistema inicializado com sucesso!")
    print("💡 Digite 'sair' para encerrar o chat")
    print("=" * 50)
    
    while True:
        try:
            print("\n❓ Faça sua pergunta:")
            question = input("PERGUNTA: ").strip()
            
            if question.lower() in ['sair', 'exit', 'quit']:
                print("👋 Até logo!")
                break
            
            if not question:
                print("⚠️  Por favor, digite uma pergunta.")
                continue
            
            print("\n🔄 Processando...")
            answer = get_answer(question)
            
            print(f"\n💬 RESPOSTA: {answer}")
            print("-" * 50)
            
        except KeyboardInterrupt:
            print("\n\n👋 Chat interrompido pelo usuário. Até logo!")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("Tente novamente ou digite 'sair' para encerrar.")

if __name__ == "__main__":
    main()