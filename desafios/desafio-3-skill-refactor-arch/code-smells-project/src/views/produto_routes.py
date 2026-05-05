from flask import Blueprint, request, jsonify

def create_produto_blueprint(produto_ctrl):
    bp = Blueprint("produtos", __name__)

    @bp.route("/produtos", methods=["GET"])
    def listar_produtos():
        return jsonify({"dados": produto_ctrl.list_produtos(), "sucesso": True})

    @bp.route("/produtos/busca", methods=["GET"])
    def buscar_produtos():
        termo = request.args.get("q", "")
        categoria = request.args.get("categoria")
        preco_min = float(request.args.get("preco_min")) if request.args.get("preco_min") else None
        preco_max = float(request.args.get("preco_max")) if request.args.get("preco_max") else None
        resultados = produto_ctrl.buscar_produtos(termo, categoria, preco_min, preco_max)
        return jsonify({"dados": resultados, "total": len(resultados), "sucesso": True})

    @bp.route("/produtos/<int:produto_id>", methods=["GET"])
    def buscar_produto(produto_id):
        produto = produto_ctrl.get_produto(produto_id)
        return jsonify({"dados": produto, "sucesso": True})

    @bp.route("/produtos", methods=["POST"])
    def criar_produto():
        produto = produto_ctrl.create_produto(request.get_json() or {})
        return jsonify({"dados": produto, "sucesso": True, "mensagem": "Produto criado"}), 201

    @bp.route("/produtos/<int:produto_id>", methods=["PUT"])
    def atualizar_produto(produto_id):
        produto = produto_ctrl.update_produto(produto_id, request.get_json() or {})
        return jsonify({"dados": produto, "sucesso": True, "mensagem": "Produto atualizado"})

    @bp.route("/produtos/<int:produto_id>", methods=["DELETE"])
    def deletar_produto(produto_id):
        produto_ctrl.delete_produto(produto_id)
        return jsonify({"sucesso": True, "mensagem": "Produto deletado"})

    return bp
