import sqlite3
from src.config.settings import Config

def get_db():
    conn = sqlite3.connect(Config.DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            owner_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'todo',
            priority INTEGER DEFAULT 1,
            project_id INTEGER NOT NULL,
            assignee_id INTEGER,
            due_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        INSERT OR IGNORE INTO users (username, password, email) VALUES
            ('admin', '$2b$12$placeholder_admin_hash', 'admin@tasks.com'),
            ('user1', '$2b$12$placeholder_user1_hash', 'user1@tasks.com');
        INSERT OR IGNORE INTO projects (name, description, owner_id) VALUES
            ('Projeto Alpha', 'Primeiro projeto de teste', 1),
            ('Projeto Beta', 'Segundo projeto', 1);
        INSERT OR IGNORE INTO tasks (title, description, status, priority, project_id, assignee_id) VALUES
            ('Implementar login', 'Criar sistema de autenticacao', 'todo', 2, 1, 1),
            ('Criar testes', 'Adicionar testes unitarios', 'in_progress', 1, 1, 2),
            ('Deploy producao', 'Subir aplicacao em producao', 'todo', 3, 2, 1);
    """)
    conn.commit()
    conn.close()
