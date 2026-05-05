from flask import Blueprint, request, jsonify

def create_pedido_blueprint(pedido_ctrl):
    bp = Blueprint("pedidos", __name__)

    @bp.route("/pedidos", methods=["GET"])
    def listar_todos_pedidos():
        return jsonify({"dados": pedido_ctrl.list_pedidos(), "sucesso": True})

    @bp.route("/pedidos/usuario/<int:usuario_id>", methods=["GET"])
    def listar_pedidos_usuario(usuario_id):
        return jsonify({"dados": pedido_ctrl.list_pedidos_usuario(usuario_id), "sucesso": True})

    @bp.route("/pedidos", methods=["POST"])
    def criar_pedido():
        resultado = pedido_ctrl.criar_pedido(request.get_json() or {})
        return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

    @bp.route("/pedidos/<int:pedido_id>/status", methods=["PUT"])
    def atualizar_status_pedido(pedido_id):
        data = request.get_json() or {}
        pedido_ctrl.atualizar_status(pedido_id, data.get("status", ""))
        return jsonify({"sucesso": True, "mensagem": "Status atualizado"})

    @bp.route("/relatorios/vendas", methods=["GET"])
    def relatorio_vendas():
        return jsonify({"dados": pedido_ctrl.relatorio_vendas(), "sucesso": True})

    return bp
