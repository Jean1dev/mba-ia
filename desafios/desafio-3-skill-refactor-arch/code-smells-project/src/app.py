from flask import Flask, jsonify
from flask_cors import CORS

from src.config.settings import Config
from src.database import init_db, get_connection
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.models.pedido_model import PedidoModel
from src.controllers.produto_controller import ProdutoController
from src.controllers.usuario_controller import UsuarioController
from src.controllers.pedido_controller import PedidoController
from src.views.produto_routes import create_produto_blueprint
from src.views.usuario_routes import create_usuario_blueprint
from src.views.pedido_routes import create_pedido_blueprint
from src.middlewares.error_handler import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    db = get_connection()

    produto_model = ProdutoModel(db)
    usuario_model = UsuarioModel(db)
    pedido_model = PedidoModel(db)
    pedido_model.db = db

    produto_ctrl = ProdutoController(produto_model)
    usuario_ctrl = UsuarioController(usuario_model)
    pedido_ctrl = PedidoController(pedido_model, produto_model)

    app.register_blueprint(create_produto_blueprint(produto_ctrl))
    app.register_blueprint(create_usuario_blueprint(usuario_ctrl))
    app.register_blueprint(create_pedido_blueprint(pedido_ctrl))

    register_error_handlers(app)

    @app.route("/")
    def index():
        return jsonify({
            "mensagem": "Bem-vindo à API da Loja",
            "versao": "2.0.0",
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        })

    @app.route("/health")
    def health():
        try:
            db.execute("SELECT 1")
            return jsonify({"status": "ok", "database": "connected"})
        except Exception:
            return jsonify({"status": "error", "database": "disconnected"}), 500

    return app


if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=Config.DEBUG, host="0.0.0.0", port=Config.PORT)
