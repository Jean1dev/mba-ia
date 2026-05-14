# MVC Architecture Guidelines

## Target Structure

### Python / Flask

```
src/
├── config/
│   └── settings.py          # All config from env vars — no hardcoded values
├── models/
│   └── <domain>_model.py    # Data access only — parameterized queries, DI
├── controllers/
│   └── <domain>_controller.py  # Business logic and orchestration — no HTTP
├── views/
│   └── <domain>_routes.py   # HTTP layer only — extract data, call controller, return JSON
├── middlewares/
│   ├── auth.py              # Authentication decorator/middleware
│   └── error_handler.py     # Global error handling
└── app.py                   # Composition root — wires everything together
```

### Node.js / Express

```
src/
├── config/
│   └── settings.js          # All config from process.env
├── models/
│   └── <Domain>Model.js     # Data access only
├── controllers/
│   └── <Domain>Controller.js  # Business logic
├── routes/
│   └── <domain>.routes.js   # Express Router definitions
├── middlewares/
│   ├── auth.js
│   └── errorHandler.js
└── app.js                   # App factory + composition root
```

---

## Layer Responsibilities

### Config (`config/settings.py`)

- Load ALL values from environment variables
- Provide safe defaults only for non-sensitive values
- **Never** contain hardcoded secrets, passwords, or API keys

```python
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    DATABASE_URL = os.environ.get("DATABASE_URL", "app.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    PORT = int(os.environ.get("PORT", "5000"))
    SMTP_USER = os.environ.get("SMTP_USER", "")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
```

```javascript
module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'dev-only-change-in-production',
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || './app.db',
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
};
```

---

### Models (`models/<domain>_model.py`)

**Allowed:**
- Parameterized SQL queries only (`?` placeholders)
- Row-to-dict conversion
- Basic data formatting

**Forbidden:**
- Business rules (discount calculation, stock validation)
- HTTP request/response objects
- Calling other models' business methods

```python
class ProdutoModel:
    def __init__(self, db):
        self.db = db

    def find_all(self):
        rows = self.db.execute("SELECT * FROM produtos WHERE ativo = 1").fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, produto_id):
        row = self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(row) if row else None

    def search(self, termo, categoria=None, preco_min=None, preco_max=None):
        params = [f"%{termo}%", f"%{termo}%"]
        query = "SELECT * FROM produtos WHERE (nome LIKE ? OR descricao LIKE ?)"
        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        return [dict(r) for r in self.db.execute(query, params).fetchall()]

    def insert(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)
```

---

### Controllers (`controllers/<domain>_controller.py`)

**Allowed:**
- Business rules and validation
- Orchestrating multiple model calls
- Domain-specific logic (discount calculation, stock checks)

**Forbidden:**
- Direct SQL queries
- `request`, `jsonify`, or any HTTP import
- Returning HTTP status codes

```python
CATEGORIAS_VALIDAS = {"informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"}

class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def list_produtos(self):
        return self.produto_model.find_all()

    def get_produto(self, produto_id):
        produto = self.produto_model.find_by_id(produto_id)
        if not produto:
            raise LookupError("Produto não encontrado")
        return produto

    def create_produto(self, data):
        nome = data.get("nome", "").strip()
        preco = data.get("preco")
        estoque = data.get("estoque")
        categoria = data.get("categoria", "geral")

        if not nome or len(nome) < 2:
            raise ValueError("Nome é obrigatório e deve ter ao menos 2 caracteres")
        if preco is None or preco < 0:
            raise ValueError("Preço deve ser um número não-negativo")
        if estoque is None or estoque < 0:
            raise ValueError("Estoque não pode ser negativo")
        if categoria not in CATEGORIAS_VALIDAS:
            raise ValueError(f"Categoria inválida. Válidas: {sorted(CATEGORIAS_VALIDAS)}")

        return self.produto_model.insert(nome, data.get("descricao", ""), preco, estoque, categoria)
```

---

### Views / Routes (`views/<domain>_routes.py`)

**Allowed:**
- Mapping URLs to controller methods
- Extracting and parsing request data
- Formatting controller results as HTTP responses
- Applying middleware decorators

**Forbidden:**
- Business logic
- SQL queries
- Calling models directly

```python
from flask import Blueprint, request, jsonify

def create_produto_blueprint(produto_ctrl):
    bp = Blueprint("produtos", __name__)

    @bp.route("/produtos", methods=["GET"])
    def list_produtos():
        return jsonify({"dados": produto_ctrl.list_produtos(), "sucesso": True})

    @bp.route("/produtos/<int:produto_id>", methods=["GET"])
    def get_produto(produto_id):
        produto = produto_ctrl.get_produto(produto_id)
        return jsonify({"dados": produto, "sucesso": True})

    @bp.route("/produtos", methods=["POST"])
    def criar_produto():
        produto = produto_ctrl.create_produto(request.get_json() or {})
        return jsonify({"dados": produto, "sucesso": True}), 201

    return bp
```

---

### Middlewares

**Global error handler (Python):**
```python
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"erro": "Recurso não encontrado", "sucesso": False}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Internal error: {e}")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500

    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(LookupError)
    def not_found_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 404
```

**Global error handler (Node.js):**
```javascript
function errorHandler(err, req, res, next) {
    if (err.name === 'ValidationError' || err.status === 400) {
        return res.status(400).json({ error: err.message });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
}
module.exports = errorHandler;
```

---

### App Entry Point (Composition Root)

```python
from flask import Flask
from flask_cors import CORS
from src.config.settings import Config
from src.database import init_db, get_connection
from src.models.produto_model import ProdutoModel
from src.controllers.produto_controller import ProdutoController
from src.views.produto_routes import create_produto_blueprint
from src.middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db = get_connection()
    produto_model = ProdutoModel(db)
    produto_ctrl = ProdutoController(produto_model)

    app.register_blueprint(create_produto_blueprint(produto_ctrl))
    register_error_handlers(app)
    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=Config.DEBUG, port=Config.PORT)
```
