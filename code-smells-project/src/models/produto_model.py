class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        rows = self.db.execute("""
            SELECT p.*, COUNT(i.id) as total_vendas
            FROM produtos p
            LEFT JOIN itens_pedido i ON i.produto_id = p.id
            GROUP BY p.id
        """).fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, produto_id):
        row = self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(row) if row else None

    def insert(self, nome, preco, estoque, descricao):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, preco, estoque, descricao) VALUES (?, ?, ?, ?)",
            (nome, preco, estoque, descricao)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)

    def update(self, produto_id, nome, preco, estoque, descricao):
        self.db.execute(
            "UPDATE produtos SET nome=?, preco=?, estoque=?, descricao=? WHERE id=?",
            (nome, preco, estoque, descricao, produto_id)
        )
        self.db.commit()
        return self.find_by_id(produto_id)

    def delete(self, produto_id):
        self.db.execute("DELETE FROM produtos WHERE id=?", (produto_id,))
        self.db.commit()

    def update_estoque(self, produto_id, delta):
        self.db.execute(
            "UPDATE produtos SET estoque = estoque + ? WHERE id=?", (delta, produto_id)
        )
