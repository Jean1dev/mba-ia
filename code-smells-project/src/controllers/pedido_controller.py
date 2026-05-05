class PedidoController:
    def __init__(self, pedido_model, produto_model):
        self.pedido_model = pedido_model
        self.produto_model = produto_model

    def criar_pedido(self, data):
        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])

        if not usuario_id or not itens:
            raise ValueError("usuario_id e itens são obrigatórios")

        total = 0
        itens_validados = []

        for item in itens:
            produto = self.produto_model.find_by_id(item.get("produto_id"))
            if not produto:
                raise LookupError(f"Produto {item.get('produto_id')} não encontrado")
            if produto["estoque"] < item.get("quantidade", 0):
                raise ValueError(f"Estoque insuficiente para '{produto['nome']}'")
            total += produto["preco"] * item["quantidade"]
            itens_validados.append({
                "produto_id": item["produto_id"],
                "quantidade": item["quantidade"],
                "preco_unitario": produto["preco"]
            })

        pedido_id = self.pedido_model.insert(usuario_id, total)
        for item in itens_validados:
            self.pedido_model.insert_item(
                pedido_id, item["produto_id"],
                item["quantidade"], item["preco_unitario"]
            )
            self.produto_model.update_estoque(item["produto_id"], -item["quantidade"])

        self.pedido_model.db.commit()
        return self.pedido_model.find_by_id(pedido_id)

    def get_pedidos_usuario(self, usuario_id):
        return self.pedido_model.find_by_usuario(usuario_id)
