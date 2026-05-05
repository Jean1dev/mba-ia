from flask import Blueprint, request, jsonify

def create_produto_blueprint(produto_ctrl):
    bp = Blueprint("produtos", __name__)

    @bp.route("/api/v1/produtos", methods=["GET"])
    def list_produtos():
        return jsonify(produto_ctrl.list_produtos())

    @bp.route("/api/v1/produtos/<int:produto_id>", methods=["GET"])
    def get_produto(produto_id):
        produto = produto_ctrl.get_produto(produto_id)
        return jsonify(produto)

    @bp.route("/api/v1/produtos", methods=["POST"])
    def create_produto():
        produto = produto_ctrl.create_produto(request.json or {})
        return jsonify(produto), 201

    @bp.route("/api/v1/produtos/<int:produto_id>", methods=["PUT"])
    def update_produto(produto_id):
        produto = produto_ctrl.update_produto(produto_id, request.json or {})
        return jsonify(produto)

    @bp.route("/api/v1/produtos/<int:produto_id>", methods=["DELETE"])
    def delete_produto(produto_id):
        produto_ctrl.delete_produto(produto_id)
        return jsonify({"message": "Produto removido com sucesso"})

    return bp


def create_usuario_blueprint(usuario_ctrl):
    bp = Blueprint("usuarios", __name__)

    @bp.route("/api/v1/usuarios", methods=["GET"])
    def list_usuarios():
        return jsonify(usuario_ctrl.list_usuarios())

    @bp.route("/api/v1/usuarios", methods=["POST"])
    def create_usuario():
        usuario = usuario_ctrl.create_usuario(request.json or {})
        return jsonify(usuario), 201

    @bp.route("/api/v1/login", methods=["POST"])
    def login():
        result = usuario_ctrl.login(
            (request.json or {}).get("email"),
            (request.json or {}).get("senha")
        )
        return jsonify(result)

    return bp


def create_pedido_blueprint(pedido_ctrl):
    bp = Blueprint("pedidos", __name__)

    @bp.route("/api/v1/pedidos", methods=["POST"])
    def criar_pedido():
        result = pedido_ctrl.criar_pedido(request.json or {})
        return jsonify(result), 201

    @bp.route("/api/v1/pedidos/usuario/<int:usuario_id>", methods=["GET"])
    def get_pedidos_usuario(usuario_id):
        return jsonify(pedido_ctrl.get_pedidos_usuario(usuario_id))

    return bp
