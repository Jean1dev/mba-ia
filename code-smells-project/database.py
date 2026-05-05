import sqlite3

DB_PATH = "ecommerce.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            preco REAL NOT NULL,
            estoque INTEGER DEFAULT 0,
            descricao TEXT
        );
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL,
            admin INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS pedidos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            total REAL,
            status TEXT DEFAULT 'pendente',
            criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS itens_pedido (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pedido_id INTEGER NOT NULL,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL
        );
        INSERT OR IGNORE INTO produtos (nome, preco, estoque, descricao) VALUES
            ('Notebook Pro', 4500.00, 10, 'Notebook de alta performance'),
            ('Mouse Gamer', 150.00, 50, 'Mouse com 6 botoes'),
            ('Teclado Mecanico', 350.00, 30, 'Teclado com switches blue');
        INSERT OR IGNORE INTO usuarios (nome, email, senha, admin) VALUES
            ('Admin', 'admin@loja.com', 'admin123', 1),
            ('Joao Silva', 'joao@email.com', 'senha123', 0);
    """)
    conn.commit()
    conn.close()
