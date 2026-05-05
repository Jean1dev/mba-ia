class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        rows = self.db.execute("SELECT * FROM produtos WHERE ativo = 1").fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, produto_id):
        row = self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, termo, categoria=None, preco_min=None, preco_max=None):
        params = [f"%{termo}%", f"%{termo}%"]
        query = "SELECT * FROM produtos WHERE ativo = 1 AND (nome LIKE ? OR descricao LIKE ?)"
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        return [dict(r) for r in self.db.execute(query, params).fetchall()]

    def insert(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)

    def update(self, produto_id, nome, descricao, preco, estoque, categoria):
        self.db.execute(
            "UPDATE produtos SET nome=?, descricao=?, preco=?, estoque=?, categoria=? WHERE id=?",
            (nome, descricao, preco, estoque, categoria, produto_id)
        )
        self.db.commit()
        return self.find_by_id(produto_id)

    def delete(self, produto_id):
        self.db.execute("UPDATE produtos SET ativo=0 WHERE id=?", (produto_id,))
        self.db.commit()

    def update_estoque(self, produto_id, delta):
        self.db.execute(
            "UPDATE produtos SET estoque = estoque + ? WHERE id=?", (delta, produto_id)
        )
