class PedidoModel:
    def __init__(self, db):
        self.db = db

    def find_by_id(self, pedido_id):
        pedido = self.db.execute(
            "SELECT * FROM pedidos WHERE id=?", (pedido_id,)
        ).fetchone()
        if not pedido:
            return None
        itens = self.db.execute(
            "SELECT * FROM itens_pedido WHERE pedido_id=?", (pedido_id,)
        ).fetchall()
        return {"pedido": dict(pedido), "itens": [dict(i) for i in itens]}

    def find_by_usuario(self, usuario_id):
        rows = self.db.execute(
            "SELECT * FROM pedidos WHERE usuario_id=?", (usuario_id,)
        ).fetchall()
        return [dict(r) for r in rows]

    def insert(self, usuario_id, total):
        cursor = self.db.execute(
            "INSERT INTO pedidos (usuario_id, total, status) VALUES (?, ?, ?)",
            (usuario_id, total, "pendente")
        )
        return cursor.lastrowid

    def insert_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        self.db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario)
        )
