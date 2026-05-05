from flask import Blueprint, request, jsonify

def create_auth_blueprint(auth_ctrl):
    bp = Blueprint("auth", __name__)

    @bp.route("/api/v1/auth/login", methods=["POST"])
    def login():
        data = request.json or {}
        result = auth_ctrl.login(data.get("username"), data.get("password"))
        return jsonify(result)

    @bp.route("/api/v1/auth/register", methods=["POST"])
    def register():
        user = auth_ctrl.register(request.json or {})
        return jsonify(user), 201

    return bp
