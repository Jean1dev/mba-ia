#!/usr/bin/env python3
"""
Script de teste para verificar se a configuração está correta
"""

import os
from dotenv import load_dotenv

def test_environment():
    print("🔍 Testando configuração do ambiente...")
    
    load_dotenv()
    
    required_vars = [
        "OPENAI_API_KEY",
        "PGVECTOR_URL", 
        "PGVECTOR_COLLECTION"
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"✅ {var}: {'*' * 10 if 'KEY' in var else value}")
    
    if missing_vars:
        print(f"\n❌ Variáveis faltando: {', '.join(missing_vars)}")
        print("📝 Configure o arquivo .env baseado no env.example")
        return False
    
    print("\n✅ Todas as variáveis de ambiente estão configuradas!")
    return True

def test_pdf_file():
    print("\n📄 Testando arquivo PDF...")
    
    pdf_path = "document.pdf"
    if os.path.exists(pdf_path):
        size = os.path.getsize(pdf_path)
        print(f"✅ PDF encontrado: {pdf_path} ({size:,} bytes)")
        return True
    else:
        print(f"❌ PDF não encontrado: {pdf_path}")
        return False

def test_docker():
    print("\n🐳 Testando Docker...")
    
    try:
        import subprocess
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=postgres_rag", "--format", "{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and "Up" in result.stdout:
            print("✅ Container PostgreSQL está rodando")
            return True
        else:
            print("❌ Container PostgreSQL não está rodando")
            print("💡 Execute: docker compose up -d")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar Docker: {e}")
        return False

def main():
    print("🧪 Teste de Configuração - Desafio 1")
    print("=" * 50)
    
    env_ok = test_environment()
    pdf_ok = test_pdf_file()
    docker_ok = test_docker()
    
    print("\n" + "=" * 50)
    print("📊 Resumo dos Testes:")
    print(f"   Ambiente: {'✅' if env_ok else '❌'}")
    print(f"   PDF: {'✅' if pdf_ok else '❌'}")
    print(f"   Docker: {'✅' if docker_ok else '❌'}")
    
    if all([env_ok, pdf_ok, docker_ok]):
        print("\n🎉 Tudo configurado! Você pode executar:")
        print("   1. python src/ingest.py")
        print("   2. python src/chat.py")
    else:
        print("\n⚠️  Corrija os problemas acima antes de continuar")

if __name__ == "__main__":
    main()
