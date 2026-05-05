import sqlite3
from src.config.settings import Config

_db_connection = None

def get_connection():
    global _db_connection
    if _db_connection is None:
        _db_connection = sqlite3.connect(Config.DATABASE_URL, check_same_thread=False)
        _db_connection.row_factory = sqlite3.Row
    return _db_connection

def init_db():
    db = get_connection()
    cursor = db.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            descricao TEXT,
            preco REAL NOT NULL,
            estoque INTEGER NOT NULL DEFAULT 0,
            categoria TEXT NOT NULL DEFAULT 'geral',
            ativo INTEGER DEFAULT 1,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            tipo TEXT DEFAULT 'cliente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            status TEXT DEFAULT 'pendente',
            total REAL NOT NULL,
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL
        );
    """)
    db.commit()

    cursor.execute("SELECT COUNT(*) FROM produtos")
    if cursor.fetchone()[0] == 0:
        import bcrypt
        cursor.executemany(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            [
                ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
                ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
                ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
                ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
            ]
        )
        usuarios = [
            ("Admin", "admin@loja.com", bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode(), "admin"),
            ("João Silva", "joao@email.com", bcrypt.hashpw(b"123456", bcrypt.gensalt()).decode(), "cliente"),
        ]
        cursor.executemany(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            usuarios
        )
        db.commit()
