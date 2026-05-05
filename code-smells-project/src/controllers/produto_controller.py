MIN_NOME_LENGTH = 3

class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def list_produtos(self):
        return self.produto_model.find_all()

    def get_produto(self, produto_id):
        produto = self.produto_model.find_by_id(produto_id)
        if not produto:
            raise LookupError("Produto não encontrado")
        return produto

    def create_produto(self, data):
        nome = data.get("nome", "")
        preco = data.get("preco", 0)
        estoque = data.get("estoque", 0)
        descricao = data.get("descricao", "")

        if len(nome) < MIN_NOME_LENGTH:
            raise ValueError(f"Nome deve ter ao menos {MIN_NOME_LENGTH} caracteres")
        if preco <= 0:
            raise ValueError("Preço deve ser positivo")
        if estoque < 0:
            raise ValueError("Estoque não pode ser negativo")

        return self.produto_model.insert(nome, preco, estoque, descricao)

    def update_produto(self, produto_id, data):
        self.get_produto(produto_id)
        return self.produto_model.update(
            produto_id,
            data.get("nome"), data.get("preco"),
            data.get("estoque", 0), data.get("descricao", "")
        )

    def delete_produto(self, produto_id):
        self.get_produto(produto_id)
        self.produto_model.delete(produto_id)
