import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    DATABASE_URL = os.environ.get("DATABASE_URL", "ecommerce.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    PORT = int(os.environ.get("PORT", "5000"))
