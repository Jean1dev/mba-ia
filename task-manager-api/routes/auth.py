from flask import Blueprint, request, jsonify
from models.user import UserModel

auth_bp = Blueprint("auth", __name__)
user_model = UserModel()

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    # LOW: sem logging de tentativas de login (sem auditoria)
    user = user_model.authenticate(username, password)
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    # HIGH: token fake sem JWT real nem expiração
    token = f"token-{user['id']}-{user['username']}"
    return jsonify({"token": token, "user": user})

@auth_bp.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    # MEDIUM: sem validação de formato de email nem força de senha
    if not data or not all(k in data for k in ["username", "password", "email"]):
        return jsonify({"error": "username, password and email are required"}), 400
    result = user_model.create(data)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result), 201
