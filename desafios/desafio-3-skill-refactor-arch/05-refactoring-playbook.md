# Refactoring Playbook

## PT-01: Extract Config — Eliminate Hardcoded Secrets

**Before:**
```python
app.config['SECRET_KEY'] = 'super-secret-key-123'
self.email_password = 'senha123'
```
```javascript
const config = { paymentGatewayKey: "pk_live_1234567890abcdef", dbPass: "senha_super_secreta_prod_123" }
```

**After:**
```python
# src/config/settings.py
import os
class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-in-production")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
    PAYMENT_GATEWAY_KEY = os.environ.get("PAYMENT_GATEWAY_KEY", "")
```
```javascript
// src/config/settings.js
module.exports = {
    paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',
    jwtSecret: process.env.JWT_SECRET || 'dev-only-change-in-production',
    port: parseInt(process.env.PORT) || 3000,
};
```

---

## PT-02: Fix SQL Injection — Parameterized Queries

**Before (all are SQL Injection):**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}' AND senha = '{senha}'")
query += " AND nome LIKE '%" + termo + "%'"
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES ('" +
    nome + "', '" + email + "', '" + senha + "')"
)
cursor.execute("UPDATE pedidos SET status = '" + novo_status + "' WHERE id = " + str(pedido_id))
```

**After:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha_hash))

# Dynamic search with parameters
params = [f"%{termo}%", f"%{termo}%"]
query = "SELECT * FROM produtos WHERE (nome LIKE ? OR descricao LIKE ?)"
if categoria:
    query += " AND categoria = ?"
    params.append(categoria)
cursor.execute(query, params)

cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
    (nome, email, senha_hash)
)
cursor.execute("UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id))
```

---

## PT-03: Remove Dangerous Admin Endpoints

**Before:**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = dados.get("sql", "")
    cursor.execute(query)  # Arbitrary SQL execution

@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    cursor.execute("DELETE FROM itens_pedido")
    cursor.execute("DELETE FROM produtos")
    # ...no authentication
```

**After:** Remove these endpoints entirely. If a database management tool is needed, use a proper admin panel with authentication (Flask-Admin, etc.) or restrict to development environment only.

---

## PT-04: Fix Password Hashing

**Before:**
```python
# MD5 — broken
self.password = hashlib.md5(pwd.encode()).hexdigest()
def check_password(self, pwd):
    return self.password == hashlib.md5(pwd.encode()).hexdigest()
```
```javascript
// Home-rolled — not a real hash
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);
    }
    return hash.substring(0, 10);
}
```

**After:**
```python
import bcrypt

def set_password(self, pwd):
    self.password = bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_password(self, pwd):
    return bcrypt.checkpw(pwd.encode(), self.password.encode())
```
```javascript
const bcrypt = require('bcrypt');
const SALT_ROUNDS = 10;

async function hashPassword(pwd) { return bcrypt.hash(pwd, SALT_ROUNDS); }
async function verifyPassword(pwd, hash) { return bcrypt.compare(pwd, hash); }
```

---

## PT-05: Remove Sensitive Data from API Responses

**Before:**
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        'password': self.password,   # NEVER expose hash
        'role': self.role,
    }

# health endpoint
return jsonify({
    "secret_key": "minha-chave-super-secreta-123",  # NEVER expose
    "db_path": "loja.db",
    "debug": True
})
```

**After:**
```python
def to_dict(self):
    return {
        'id': self.id,
        'name': self.name,
        'email': self.email,
        # password field omitted
        'role': self.role,
        'active': self.active,
    }

# health endpoint — only operational info
return jsonify({"status": "ok", "database": "connected"})
```

---

## PT-06: Fix N+1 Queries — Use JOIN or Batch Queries

**Before (nested cursors):**
```python
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

**After (single JOIN):**
```python
rows = db.execute("""
    SELECT p.*, i.produto_id, i.quantidade, i.preco_unitario, pr.nome as produto_nome
    FROM pedidos p
    LEFT JOIN itens_pedido i ON i.pedido_id = p.id
    LEFT JOIN produtos pr ON pr.id = i.produto_id
    WHERE p.usuario_id = ?
""", (usuario_id,)).fetchall()
```

**Before (Node.js callback hell):**
```javascript
courses.forEach(c => {
    this.db.all("SELECT * FROM enrollments WHERE course_id = ?", [c.id], (err, enrollments) => {
        enrollments.forEach(enr => {
            this.db.get("SELECT name FROM users WHERE id = ?", [enr.user_id], (err, user) => {
                this.db.get("SELECT amount FROM payments WHERE enrollment_id = ?", [enr.id], (err, payment) => {
                    // deeply nested
                });
            });
        });
    });
});
```

**After (single JOIN with better-sqlite3):**
```javascript
const report = db.prepare(`
    SELECT c.title, u.name as student, p.amount, p.status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
`).all();
```

---

## PT-07: Split God Class into MVC Layers

**Before:**
```javascript
class AppManager {
    constructor() { this.db = new sqlite3.Database(':memory:') }
    initDb() { /* schema + seed */ }
    setupRoutes(app) {
        app.post('/api/checkout', (req, res) => {
            // 50 lines of business logic + DB calls
        });
        app.get('/api/admin/financial-report', (req, res) => {
            // nested callbacks
        });
    }
}
```

**After:**
```javascript
// src/models/CourseModel.js
class CourseModel {
    constructor(db) { this.db = db; }
    findById(id) { return this.db.prepare('SELECT * FROM courses WHERE id = ?').get(id); }
}

// src/controllers/CheckoutController.js
class CheckoutController {
    constructor(courseModel, enrollmentModel) { ... }
    checkout(userId, courseId, cardNumber) { /* business logic only */ }
}

// src/routes/checkout.routes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        const result = await checkoutController.checkout(...);
        res.json(result);
    } catch(err) { next(err); }
});
```

---

## PT-08: Centralized Error Handler

**Before (duplicated in every route):**
```python
except Exception as e:
    print("ERRO: " + str(e))
    return jsonify({"erro": str(e)}), 500
```

**After:**
```python
# src/middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(ValueError)
    def validation_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 400

    @app.errorhandler(LookupError)
    def not_found_error(e):
        return jsonify({"erro": str(e), "sucesso": False}), 404

    @app.errorhandler(500)
    def server_error(e):
        app.logger.error(f"Unhandled error: {e}")
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
```

---

## Phase 3 Execution Order

1. Create directory structure: `src/config/`, `src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`
2. Create `config/settings.py` — extract all hardcoded values (PT-01)
3. Create model files — fix all SQL injection (PT-02), one per domain
4. Create controller files — move business logic, use PT-07
5. Create route files — thin HTTP layer, use PT-05 for response sanitization
6. Create middlewares — auth + error handler (PT-08)
7. Rewrite `app.py` as composition root
8. Remove old flat files (`models.py`, `controllers.py`, `AppManager.js`, `utils.js`)
9. Validate: start app, test 2+ endpoints

## Validation Commands

```bash
# Python/Flask
pip install -r requirements.txt
python src/app.py &
sleep 2
curl -s http://localhost:5000/produtos | python -m json.tool
curl -s http://localhost:5000/health

# Node.js/Express
npm install
node src/app.js &
sleep 2
curl -s http://localhost:3000/api/courses
```
