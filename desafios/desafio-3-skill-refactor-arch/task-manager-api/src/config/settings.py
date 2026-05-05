import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    PORT = int(os.environ.get("PORT", "5000"))
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")

VALID_STATUSES = frozenset({"pending", "in_progress", "done", "cancelled"})
VALID_ROLES = frozenset({"user", "admin", "manager"})
