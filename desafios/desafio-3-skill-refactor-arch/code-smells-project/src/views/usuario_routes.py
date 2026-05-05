from flask import Blueprint, request, jsonify

def create_usuario_blueprint(usuario_ctrl):
    bp = Blueprint("usuarios", __name__)

    @bp.route("/usuarios", methods=["GET"])
    def listar_usuarios():
        return jsonify({"dados": usuario_ctrl.list_usuarios(), "sucesso": True})

    @bp.route("/usuarios/<int:usuario_id>", methods=["GET"])
    def buscar_usuario(usuario_id):
        usuario = usuario_ctrl.get_usuario(usuario_id)
        return jsonify({"dados": usuario, "sucesso": True})

    @bp.route("/usuarios", methods=["POST"])
    def criar_usuario():
        usuario = usuario_ctrl.create_usuario(request.get_json() or {})
        return jsonify({"dados": usuario, "sucesso": True}), 201

    @bp.route("/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        usuario = usuario_ctrl.login(data.get("email", ""), data.get("senha", ""))
        return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"})

    return bp
