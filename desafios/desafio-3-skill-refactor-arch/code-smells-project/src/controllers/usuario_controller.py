import bcrypt

class UsuarioController:
    def __init__(self, usuario_model):
        self.usuario_model = usuario_model

    def list_usuarios(self):
        return self.usuario_model.find_all()

    def get_usuario(self, usuario_id):
        usuario = self.usuario_model.find_by_id(usuario_id)
        if not usuario:
            raise LookupError("Usuário não encontrado")
        return usuario

    def create_usuario(self, data):
        nome = (data.get("nome") or "").strip()
        email = (data.get("email") or "").strip()
        senha = data.get("senha", "")

        if not nome or not email or not senha:
            raise ValueError("Nome, email e senha são obrigatórios")

        senha_hash = bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()
        usuario = self.usuario_model.insert(nome, email, senha_hash)
        if not usuario:
            raise ValueError("Email já cadastrado")
        return usuario

    def login(self, email, senha):
        if not email or not senha:
            raise ValueError("Email e senha são obrigatórios")
        usuario = self.usuario_model.find_by_email(email)
        if not usuario or not self.usuario_model.verify_password(senha, usuario["senha"]):
            raise PermissionError("Email ou senha inválidos")
        return {k: v for k, v in usuario.items() if k != "senha"}
