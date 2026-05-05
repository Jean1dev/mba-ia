# MVC Architecture Guidelines

## Target Structure

### Python / Flask

```
src/
├── config/
│   └── settings.py          # All configuration, loaded from env vars
├── models/
│   └── <domain>_model.py    # Data access only — no business logic
├── controllers/
│   └── <domain>_controller.py  # Business logic and orchestration
├── views/
│   └── routes.py            # HTTP layer only — map URL to controller
├── middlewares/
│   ├── auth.py              # Authentication/authorization
│   └── error_handler.py     # Global error handling
└── app.py                   # Composition root — wires everything together
```

### Node.js / Express

```
src/
├── config/
│   └── settings.js          # All configuration from process.env
├── models/
│   └── <Domain>Model.js     # Data access only
├── controllers/
│   └── <Domain>Controller.js  # Business logic
├── routes/
│   └── <domain>.routes.js   # Express Router definitions
├── middlewares/
│   ├── auth.js              # Auth middleware
│   └── errorHandler.js      # Global error handler
└── app.js                   # App factory + composition root
```

---

## Layer Responsibilities

### Config (`config/settings.py` or `config/settings.js`)
- Load ALL configuration from environment variables
- Provide defaults for non-sensitive values only
- Never contain hardcoded secrets
- Export a single config object

**Python example:**
```python
import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "change-in-production")
    DATABASE_URL = os.environ.get("DATABASE_URL", "app.db")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
```

**Node.js example:**
```javascript
module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'change-in-production',
    port: parseInt(process.env.PORT) || 3000,
    dbPath: process.env.DB_PATH || './app.db',
    corsOrigins: process.env.CORS_ORIGINS || '*',
};
```

---

### Models (`models/<domain>_model.py`)
**Allowed:**
- SQL queries (parameterized only)
- Row-to-dict mapping
- Simple data transformations (formatting, field selection)

**Forbidden:**
- Business rules (pricing, status transitions, inventory checks)
- HTTP concerns (request/response)
- Calling other models' business methods

**Python example:**
```python
class ProdutoModel:
    def __init__(self, db):
        self.db = db  # injected dependency

    def find_all(self):
        rows = self.db.execute("SELECT * FROM produtos").fetchall()
        return [dict(r) for r in rows]

    def find_by_id(self, produto_id):
        row = self.db.execute(
            "SELECT * FROM produtos WHERE id = ?", (produto_id,)
        ).fetchone()
        return dict(row) if row else None

    def insert(self, nome, preco, estoque, descricao):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, preco, estoque, descricao) VALUES (?, ?, ?, ?)",
            (nome, preco, estoque, descricao)
        )
        self.db.commit()
        return self.find_by_id(cursor.lastrowid)
```

---

### Controllers (`controllers/<domain>_controller.py`)
**Allowed:**
- Business logic and rules
- Orchestrating model calls
- Validation logic
- Calling multiple models

**Forbidden:**
- Direct SQL queries
- HTTP request/response objects
- Importing Flask/Express directly

**Python example:**
```python
class ProdutoController:
    def __init__(self, produto_model):
        self.produto_model = produto_model

    def list_produtos(self):
        return self.produto_model.find_all()

    def create_produto(self, data):
        if not data.get("nome") or len(data["nome"]) < 3:
            raise ValueError("Nome deve ter ao menos 3 caracteres")
        if data.get("preco", 0) <= 0:
            raise ValueError("Preco deve ser positivo")
        return self.produto_model.insert(
            data["nome"], data["preco"],
            data.get("estoque", 0), data.get("descricao", "")
        )
```

---

### Views / Routes (`views/routes.py` or `routes/<domain>.routes.js`)
**Allowed:**
- Mapping URLs to controller methods
- Extracting request data and passing to controllers
- Formatting controller results as HTTP responses
- Applying middleware

**Forbidden:**
- Business logic
- Direct model access
- SQL queries

**Python example:**
```python
from flask import Blueprint, request, jsonify
from controllers.produto_controller import ProdutoController

produtos_bp = Blueprint("produtos", __name__)
controller = ProdutoController(produto_model)  # injected

@produtos_bp.route("/api/v1/produtos", methods=["GET"])
def list_produtos():
    produtos = controller.list_produtos()
    return jsonify(produtos)

@produtos_bp.route("/api/v1/produtos", methods=["POST"])
def create_produto():
    try:
        produto = controller.create_produto(request.json)
        return jsonify(produto), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
```

---

### Middlewares

**Auth middleware (Python):**
```python
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        # validate token...
        return f(*args, **kwargs)
    return decorated
```

**Global error handler (Python):**
```python
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"error": str(e)}), 400
```

**Global error handler (Node.js):**
```javascript
function errorHandler(err, req, res, next) {
    if (err.name === 'ValidationError') {
        return res.status(400).json({ error: err.message });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
}
module.exports = errorHandler;
```

---

### App Entry Point (`app.py` or `src/app.js`)
**Role:** Composition root — wire all layers together
- Import and configure all modules
- Register blueprints/routers
- Initialize database
- Start server

**Python example:**
```python
from flask import Flask
from flask_cors import CORS
from config.settings import Config
from database import init_db, get_connection
from models.produto_model import ProdutoModel
from controllers.produto_controller import ProdutoController
from views.routes import create_blueprints
from middlewares.error_handler import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=Config.CORS_ORIGINS)

    conn = get_connection()
    produto_model = ProdutoModel(conn)
    produto_ctrl = ProdutoController(produto_model)

    blueprints = create_blueprints(produto_ctrl)
    for bp in blueprints:
        app.register_blueprint(bp)

    register_error_handlers(app)
    return app

if __name__ == "__main__":
    init_db()
    app = create_app()
    app.run(debug=Config.DEBUG)
```
