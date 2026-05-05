# Refactoring Playbook

## Transformation Patterns

### PT-01: Extract Config from Hardcoded Values

**Before (Python):**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
CORS(app)
```

**After:**
```python
# config/settings.py
import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")
    DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# app.py
from config.settings import Config
app.config.from_object(Config)
CORS(app, origins=Config.CORS_ORIGINS)
```

**Before (Node.js):**
```javascript
const JWT_SECRET = 'lms-secret-key-nao-mude-isso';
const PORT = 3000;
```

**After:**
```javascript
// config/settings.js
module.exports = {
    jwtSecret: process.env.JWT_SECRET || 'dev-only-change-in-production',
    port: parseInt(process.env.PORT) || 3000,
};
```

---

### PT-02: Fix SQL Injection — Use Parameterized Queries

**Before (Python):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(produto_id))
conn.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")
```

**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
```

**Before (Node.js):**
```javascript
db.prepare(`SELECT * FROM users WHERE id = ${id}`).get()
```

**After:**
```javascript
db.prepare('SELECT * FROM users WHERE id = ?').get(id)
```

---

### PT-03: Split God Class into Domain Models

**Before:** Single `models.py` or `AppManager.js` with all domains

**After:** One file per domain, single responsibility

```
models/
├── produto_model.py    # Only products DB access
├── usuario_model.py    # Only users DB access
└── pedido_model.py     # Only orders DB access
```

Each model receives the DB connection via constructor (dependency injection):
```python
class ProdutoModel:
    def __init__(self, db):
        self.db = db
```

---

### PT-04: Move Business Logic from Controller to Controller Layer

**Before (route handler with business logic):**
```python
def criar_pedido():
    data = request.json
    total = 0
    for item in data["itens"]:
        produto = produto_model.get_by_id(item["produto_id"])
        if produto["estoque"] < item["quantidade"]:
            return jsonify({"error": "Estoque insuficiente"}), 400
        total += produto["preco"] * item["quantidade"]
    # ... more business logic
```

**After (route calls controller; controller has the logic):**
```python
# routes/pedido_routes.py
@pedidos_bp.route("/api/v1/pedidos", methods=["POST"])
def criar_pedido():
    try:
        result = pedido_controller.criar_pedido(request.json)
        return jsonify(result), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

# controllers/pedido_controller.py
class PedidoController:
    def criar_pedido(self, data):
        usuario_id = data.get("usuario_id")
        itens = data.get("itens", [])
        if not usuario_id or not itens:
            raise ValueError("usuario_id e itens são obrigatórios")
        # business logic here
        return self.pedido_model.criar_pedido(usuario_id, itens)
```

---

### PT-05: Fix N+1 Queries — Use JOIN or Batch Query

**Before:**
```python
for produto in produtos:
    conn = get_connection()
    vendas = conn.execute("SELECT COUNT(*) FROM itens_pedido WHERE produto_id = ?", (produto["id"],))
```

**After:**
```python
rows = db.execute("""
    SELECT p.*, COUNT(i.id) as total_vendas
    FROM produtos p
    LEFT JOIN itens_pedido i ON i.produto_id = p.id
    GROUP BY p.id
""").fetchall()
```

**Node.js before:**
```javascript
const matriculas = db.prepare('SELECT * FROM matriculas WHERE aluno_id = ?').all(alunoId);
return matriculas.map(m => {
    const curso = db.prepare('SELECT titulo FROM cursos WHERE id = ?').get(m.curso_id);
    return { ...m, curso };
});
```

**Node.js after:**
```javascript
return db.prepare(`
    SELECT m.*, c.titulo as curso_titulo, c.preco as curso_preco
    FROM matriculas m
    JOIN cursos c ON c.id = m.curso_id
    WHERE m.aluno_id = ?
`).all(alunoId);
```

---

### PT-06: Extract Auth Middleware — Eliminate DRY Violations

**Before (Node.js — repeated in every route):**
```javascript
app.post('/checkout', (req, res) => {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ error: 'Token necessário' });
    const user = appManager.verificarToken(token);
    if (!user) return res.status(401).json({ error: 'Token inválido' });
    // route logic
});
```

**After:**
```javascript
// middlewares/auth.js
function requireAuth(req, res, next) {
    const token = req.headers.authorization?.replace('Bearer ', '');
    if (!token) return res.status(401).json({ error: 'Authentication required' });
    const user = verifyToken(token);
    if (!user) return res.status(401).json({ error: 'Invalid token' });
    req.user = user;
    next();
}
module.exports = { requireAuth };

// routes/checkout.routes.js
router.post('/checkout', requireAuth, checkoutController.process);
router.get('/minhas-matriculas', requireAuth, matriculaController.list);
```

**Python (decorator pattern):**
```python
# middlewares/auth.py
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return jsonify({"error": "Authentication required"}), 401
        user = verify_token(token)
        if not user:
            return jsonify({"error": "Invalid token"}), 401
        request.current_user = user
        return f(*args, **kwargs)
    return decorated

# views/routes.py
@pedidos_bp.route("/api/v1/pedidos", methods=["POST"])
@require_auth
def criar_pedido():
    ...
```

---

### PT-07: Add Centralized Error Handler

**Python:**
```python
# middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Server error: {e}")
        return jsonify({"error": "Internal server error"}), 500

    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"error": str(e)}), 400
```

**Node.js:**
```javascript
// middlewares/errorHandler.js
function errorHandler(err, req, res, next) {
    if (err.name === 'ValidationError') {
        return res.status(400).json({ error: err.message });
    }
    if (err.name === 'UnauthorizedError') {
        return res.status(401).json({ error: 'Invalid token' });
    }
    console.error(err.stack);
    res.status(500).json({ error: 'Internal server error' });
}
module.exports = errorHandler;

// app.js — register LAST
app.use(errorHandler);
```

---

### PT-08: Secure Password Handling

**Before (plaintext or MD5):**
```python
# Storing plaintext
conn.execute("INSERT INTO users (password) VALUES (?)", (password,))

# MD5 only (broken)
senha_hash = hashlib.md5(senha.encode()).hexdigest()
```

**After (bcrypt):**
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())
```

**Add to requirements.txt:** `bcrypt==4.1.2`

---

## Phase 3 Execution Checklist

When executing Phase 3, follow this order:

1. **Create directory structure** — `src/config/`, `src/models/`, `src/controllers/`, `src/views/` or `src/routes/`, `src/middlewares/`
2. **Extract config** — create `config/settings.py` or `config/settings.js`
3. **Create models** — one per domain, using PT-03 and PT-02
4. **Create controllers** — one per domain, move business logic from routes using PT-04
5. **Create routes/views** — thin HTTP layer using PT-06
6. **Create middlewares** — auth and error handler using PT-06 and PT-07
7. **Rewrite app entry point** — composition root wiring everything
8. **Remove old files** — delete God classes and flat files replaced by new structure
9. **Validate** — run the application and test each endpoint

## Validation Steps

### Python/Flask
```bash
# Install dependencies
pip install -r requirements.txt

# Start application
python app.py &
sleep 2

# Test key endpoints
curl -s http://localhost:<PORT>/api/v1/<resource> | python -m json.tool
curl -s -X POST http://localhost:<PORT>/api/v1/... -H "Content-Type: application/json" -d '...'
```

### Node.js/Express
```bash
# Install dependencies
npm install

# Start application
node src/app.js &
sleep 2

# Test key endpoints
curl -s http://localhost:<PORT>/<resource>
```

### Validation success criteria:
- Application boots without errors or exceptions
- All original endpoints return 200 (or appropriate status) with valid JSON
- No Python tracebacks or Node.js unhandled rejections
- Structure follows MVC pattern (verify directory tree)
