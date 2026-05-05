from src.config.settings import CATEGORIAS_VALIDAS

class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def list_produtos(self):
        return self.produto_model.find_all()

    def buscar_produtos(self, termo, categoria=None, preco_min=None, preco_max=None):
        return self.produto_model.search(termo, categoria, preco_min, preco_max)

    def get_produto(self, produto_id):
        produto = self.produto_model.find_by_id(produto_id)
        if not produto:
            raise LookupError("Produto não encontrado")
        return produto

    def create_produto(self, data):
        nome = (data.get("nome") or "").strip()
        preco = data.get("preco")
        estoque = data.get("estoque")
        categoria = data.get("categoria", "geral")

        if not nome or len(nome) < 2:
            raise ValueError("Nome deve ter ao menos 2 caracteres")
        if len(nome) > 200:
            raise ValueError("Nome muito longo")
        if preco is None or preco < 0:
            raise ValueError("Preço deve ser um número não-negativo")
        if estoque is None or estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}")

        return self.produto_model.insert(nome, data.get("descricao", ""), preco, estoque, categoria)

    def update_produto(self, produto_id, data):
        self.get_produto(produto_id)
        nome = (data.get("nome") or "").strip()
        preco = data.get("preco")
        estoque = data.get("estoque")
        categoria = data.get("categoria", "geral")

        if not nome:
            raise ValueError("Nome é obrigatório")
        if preco is None or preco < 0:
            raise ValueError("Preço inválido")
        if estoque is None or estoque < 0:
            raise ValueError("Estoque inválido")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}")

        return self.produto_model.update(produto_id, nome, data.get("descricao", ""), preco, estoque, categoria)

    def delete_produto(self, produto_id):
        self.get_produto(produto_id)
        self.produto_model.delete(produto_id)
