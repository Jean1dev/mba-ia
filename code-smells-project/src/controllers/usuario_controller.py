import bcrypt
import secrets

class UsuarioController:
    def __init__(self, usuario_model):
        self.usuario_model = usuario_model

    def list_usuarios(self):
        return self.usuario_model.find_all()

    def create_usuario(self, data):
        nome = data.get("nome", "")
        email = data.get("email", "")
        senha = data.get("senha", "")

        if not nome or not email or not senha:
            raise ValueError("Campos obrigatórios: nome, email, senha")

        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        usuario = self.usuario_model.insert(nome, email, senha_hash)
        if not usuario:
            raise ValueError("Email já cadastrado")
        return usuario

    def login(self, email, senha):
        if not email or not senha:
            raise ValueError("Email e senha são obrigatórios")
        usuario = self.usuario_model.find_by_email(email)
        if not usuario:
            raise PermissionError("Credenciais inválidas")
        if not self.usuario_model.verify_password(senha, usuario["senha"]):
            raise PermissionError("Credenciais inválidas")
        safe_user = {k: v for k, v in usuario.items() if k != "senha"}
        token = secrets.token_hex(32)
        return {"token": token, "usuario": safe_user}
