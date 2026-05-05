# CRITICAL: SECRET_KEY hardcoded diretamente no código-fonte
from flask import Flask
from flask_cors import CORS
from database import init_db
from controllers import (
    get_produtos, get_produto, create_produto, update_produto, delete_produto,
    get_usuarios, create_usuario, login,
    criar_pedido, get_pedidos_usuario
)

app = Flask(__name__)
# CRITICAL: credencial hardcoded
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
# HIGH: CORS liberado para qualquer origem sem restrição
CORS(app)

# MEDIUM: sem versionamento de API (ex: /api/v1/)
# Produtos
app.add_url_rule("/produtos", view_func=get_produtos, methods=["GET"])
app.add_url_rule("/produtos", view_func=create_produto, methods=["POST"])
app.add_url_rule("/produtos/<int:id>", view_func=get_produto, methods=["GET"])
app.add_url_rule("/produtos/<int:id>", view_func=update_produto, methods=["PUT"])
app.add_url_rule("/produtos/<int:id>", view_func=delete_produto, methods=["DELETE"])

# Usuários
app.add_url_rule("/usuarios", view_func=get_usuarios, methods=["GET"])
app.add_url_rule("/usuarios", view_func=create_usuario, methods=["POST"])
app.add_url_rule("/login", view_func=login, methods=["POST"])

# Pedidos
app.add_url_rule("/pedidos", view_func=criar_pedido, methods=["POST"])
app.add_url_rule("/pedidos/usuario/<int:usuario_id>", view_func=get_pedidos_usuario, methods=["GET"])

if __name__ == "__main__":
    init_db()
    # LOW: debug=True em produção
    app.run(debug=True, port=5000)
