import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    DATABASE_URL = os.environ.get("DATABASE_URL", "loja.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

CATEGORIAS_VALIDAS = frozenset({"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"})
STATUS_PEDIDO_VALIDOS = frozenset({"pendente", "aprovado", "enviado", "entregue", "cancelado"})

DESCONTO_FATURAMENTO = [
    (10000, 0.10),
    (5000,  0.05),
    (1000,  0.02),
]
