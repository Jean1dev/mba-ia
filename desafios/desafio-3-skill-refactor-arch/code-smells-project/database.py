import sqlite3
import os

db_connection = None
db_path = "loja.db"

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path, check_same_thread=False)
        db_connection.row_factory = sqlite3.Row
        cursor = db_connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                descricao TEXT,
                preco REAL,
                estoque INTEGER,
                categoria TEXT,
                ativo INTEGER DEFAULT 1,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                email TEXT,
                senha TEXT,
                tipo TEXT DEFAULT 'cliente',
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                status TEXT DEFAULT 'pendente',
                total REAL,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS itens_pedido (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER,
                produto_id INTEGER,
                quantidade INTEGER,
                preco_unitario REAL
            )
        """)
        db_connection.commit()

        cursor.execute("SELECT COUNT(*) FROM produtos")
        if cursor.fetchone()[0] == 0:
            produtos = [
                ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
                ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
                ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
                ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
                ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
                ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
                ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
                ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
                ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
                ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
            ]
            cursor.executemany(
                "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
                produtos
            )

            usuarios = [
                ("Admin", "admin@loja.com", "admin123", "admin"),
                ("João Silva", "joao@email.com", "123456", "cliente"),
                ("Maria Santos", "maria@email.com", "senha123", "cliente"),
            ]
            cursor.executemany(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                usuarios
            )
            db_connection.commit()

    return db_connection
