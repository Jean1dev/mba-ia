class PedidoModel:
    def __init__(self, db):
        self.db = db

    def find_all_with_items(self):
        pedidos = self.db.execute("SELECT * FROM pedidos").fetchall()
        return [self._add_items(dict(p)) for p in pedidos]

    def find_by_usuario(self, usuario_id):
        pedidos = self.db.execute(
            "SELECT * FROM pedidos WHERE usuario_id = ?", (usuario_id,)
        ).fetchall()
        return [self._add_items(dict(p)) for p in pedidos]

    def _add_items(self, pedido):
        rows = self.db.execute("""
            SELECT i.produto_id, i.quantidade, i.preco_unitario, p.nome as produto_nome
            FROM itens_pedido i
            JOIN produtos p ON p.id = i.produto_id
            WHERE i.pedido_id = ?
        """, (pedido["id"],)).fetchall()
        pedido["itens"] = [dict(r) for r in rows]
        return pedido

    def insert(self, usuario_id, total):
        cursor = self.db.execute(
            "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, 'pendente', ?)",
            (usuario_id, total)
        )
        return cursor.lastrowid

    def insert_item(self, pedido_id, produto_id, quantidade, preco_unitario):
        self.db.execute(
            "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
            (pedido_id, produto_id, quantidade, preco_unitario)
        )

    def update_status(self, pedido_id, status):
        self.db.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id)
        )
        self.db.commit()

    def get_stats(self):
        total = self.db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]
        faturamento = self.db.execute("SELECT COALESCE(SUM(total), 0) FROM pedidos").fetchone()[0]
        por_status = {
            row["status"]: row["count"]
            for row in self.db.execute(
                "SELECT status, COUNT(*) as count FROM pedidos GROUP BY status"
            ).fetchall()
        }
        return {"total": total, "faturamento": faturamento, "por_status": por_status}
