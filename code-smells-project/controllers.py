# HIGH: Controllers com lógica de negócio pesada misturada com tratamento HTTP
from flask import request, jsonify
from models import ProdutoModel, UsuarioModel, PedidoModel

produto_model = ProdutoModel()
usuario_model = UsuarioModel()
pedido_model = PedidoModel()

# HIGH: sem injeção de dependência, instâncias globais
# HIGH: sem qualquer autenticação/autorização nos endpoints

def get_produtos():
    # MEDIUM: sem tratamento de erros
    produtos = produto_model.get_all()
    return jsonify(produtos)

def get_produto(id):
    produto = produto_model.get_by_id(id)
    if not produto:
        return jsonify({"error": "Produto nao encontrado"}), 404
    return jsonify(produto)

def create_produto():
    data = request.json
    # MEDIUM: validação mínima - deveria usar schema validation
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400
    result = produto_model.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

def update_produto(id):
    data = request.json
    if not data:
        return jsonify({"error": "Dados invalidos"}), 400
    result = produto_model.update(id, data)
    return jsonify(result)

def delete_produto(id):
    produto_model.delete(id)
    return jsonify({"message": "Produto removido"})

def get_usuarios():
    # CRITICAL: retorna senhas em texto para qualquer requisição (sem auth)
    usuarios = usuario_model.get_all()
    return jsonify(usuarios)

def create_usuario():
    data = request.json
    result = usuario_model.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")
    usuario = usuario_model.login(email, senha)
    if not usuario:
        return jsonify({"error": "Credenciais invalidas"}), 401
    # HIGH: token fake sem expiração nem JWT real
    token = f"fake-token-{usuario['id']}-{usuario['email']}"
    return jsonify({"token": token, "usuario": usuario})

def criar_pedido():
    data = request.json
    usuario_id = data.get("usuario_id")
    itens = data.get("itens", [])
    # HIGH: sem verificar se usuario_id é válido ou se o usuário está autenticado
    if not usuario_id or not itens:
        return jsonify({"error": "usuario_id e itens sao obrigatorios"}), 400
    result = pedido_model.criar_pedido(usuario_id, itens)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201

def get_pedidos_usuario(usuario_id):
    pedidos = pedido_model.get_by_usuario(usuario_id)
    return jsonify(pedidos)
