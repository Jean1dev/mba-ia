import bcrypt
import secrets

class AuthController:
    def __init__(self, user_model):
        self.user_model = user_model

    def login(self, username, password):
        if not username or not password:
            raise ValueError("username e password são obrigatórios")
        user = self.user_model.find_by_username(username)
        if not user:
            raise PermissionError("Credenciais inválidas")
        if not self.user_model.verify_password(password, user["password"]):
            raise PermissionError("Credenciais inválidas")
        safe_user = {"id": user["id"], "username": user["username"], "email": user["email"]}
        token = secrets.token_hex(32)
        return {"token": token, "user": safe_user}

    def register(self, data):
        username = data.get("username", "")
        email = data.get("email", "")
        password = data.get("password", "")
        if not all([username, email, password]):
            raise ValueError("username, password e email são obrigatórios")
        if len(password) < 6:
            raise ValueError("Senha deve ter ao menos 6 caracteres")
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = self.user_model.insert(username, email, password_hash)
        if not user:
            raise ValueError("Username ou email já cadastrado")
        return user
