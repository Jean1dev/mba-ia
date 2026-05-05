# Anti-Patterns Catalog

## Severity Scale

- **CRITICAL:** Security vulnerabilities or architecture failures blocking correct operation (SQL injection, hardcoded secrets, unauthenticated dangerous endpoints, broken crypto)
- **HIGH:** Strong MVC/SOLID violations that severely impede maintainability and testing (God class, business logic in routes, plaintext passwords, exposed sensitive data in responses)
- **MEDIUM:** Code quality or moderate performance issues (N+1 queries, callback hell, global mutable state, missing validation, no error handler)
- **LOW:** Readability, naming, magic values, dead code

---

## CRITICAL

### AP-01: Hardcoded Credentials / Secrets
**Detection signals:**
- `SECRET_KEY = "..."` with literal string (not `os.environ`)
- `paymentGatewayKey: "pk_live_..."` in source file
- `email_password = 'senha123'` or any password literal
- `dbPass: "senha_super_secreta..."` in config object
- Any key/secret not loaded from environment variables

```python
# Python example
app.config['SECRET_KEY'] = 'super-secret-key-123'          # CRITICAL
self.email_password = 'senha123'                            # CRITICAL
```
```javascript
// Node.js example
const config = { paymentGatewayKey: "pk_live_1234..." }    // CRITICAL
```

### AP-02: SQL Injection
**Detection signals:**
- String concatenation in SQL: `"SELECT * FROM t WHERE id = " + str(id)`
- f-string interpolation: `f"SELECT * FROM t WHERE email = '{email}'"`
- Template literals: `` `SELECT * FROM t WHERE id = ${id}` ``
- Dynamic query building by appending unescaped user input to a string

```python
# All of these are SQL Injection
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}' AND senha = '{senha}'")
query += " AND nome LIKE '%" + termo + "%'"
```

### AP-03: Unauthenticated Dangerous Admin Endpoint
**Detection signals:**
- Route that accepts arbitrary SQL and executes it: `/admin/query`
- Route that wipes the database with no auth check: `/admin/reset-db`
- Any destructive operation accessible without authentication

```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    query = dados.get("sql", "")
    cursor.execute(query)   # CRITICAL — arbitrary code execution
```

### AP-04: Broken / Home-rolled Cryptography
**Detection signals:**
- MD5 for password hashing: `hashlib.md5(pwd.encode()).hexdigest()`
- Base64 used as "encryption": `Buffer.from(pwd).toString('base64')`
- Any custom loop that builds a "hash" from repeated base64 encoding
- XOR or Caesar cipher for passwords

```python
self.password = hashlib.md5(pwd.encode()).hexdigest()   # CRITICAL
```
```javascript
function badCrypto(pwd) {
    let hash = "";
    for(let i = 0; i < 10000; i++) {
        hash += Buffer.from(pwd).toString('base64').substring(0, 2);  // CRITICAL
    }
}
```

### AP-05: Sensitive Data Exposed in API Response / Logs
**Detection signals:**
- `to_dict()` or JSON serialization includes `password`, `senha`, `pass` field
- `/health` endpoint returning `secret_key`, `db_path`, `debug: True`
- `console.log` printing card numbers, gateway keys, or tokens
- Any field with `key`, `token`, `secret`, `password` in a response payload

```python
# health_check returning secret_key — CRITICAL
return jsonify({
    "secret_key": "minha-chave-super-secreta-123",
    "db_path": "loja.db",
    "debug": True
})
```
```python
# to_dict() exposing password hash — CRITICAL
def to_dict(self):
    return { 'password': self.password, ... }  # CRITICAL
```

---

## HIGH

### AP-06: God Class / God Method
**Detection signals:**
- Single class managing: DB initialization + route registration + business logic + payment processing
- `setupRoutes(app)` method inside the same class that owns `this.db`
- `AppManager` or similar class with 100+ lines and 4+ distinct responsibilities

```javascript
class AppManager {
    constructor() { this.db = new sqlite3.Database(...) }  // DB management
    initDb() { ... }                                        // Schema
    setupRoutes(app) { app.post('/checkout', ...) }        // Routes + business logic
}
```

### AP-07: Business Logic in Routes/Controllers
**Detection signals:**
- Discount calculation inside a route handler or model
- Payment gateway card validation (`cc.startsWith("4")`) inside a route
- Email/SMS notification triggered directly from a controller function

```python
# Discount calculation in models.py (not in a dedicated service)
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
```

### AP-08: Plaintext Password Storage
**Detection signals:**
- `INSERT INTO users ... VALUES (?, ?, ?)` with raw password as third param
- Password compared directly: `WHERE email = ? AND senha = ?`
- `check_password` comparing raw string to stored value without bcrypt

```python
cursor.execute("INSERT INTO usuarios (nome, email, senha) VALUES ('" + nome + "', '" + email + "', '" + senha + "')")
```

### AP-09: Orphaned Records / Missing Cascading Delete
**Detection signals:**
- `DELETE FROM users WHERE id = ?` with no follow-up deletion of related records
- Response text explicitly acknowledging the problem (as in the original code)

```javascript
app.delete('/api/users/:id', (req, res) => {
    this.db.run("DELETE FROM users WHERE id = ?", [id], (err) => {
        res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco.");
    });
});
```

### AP-10: Debug / Fake Notifications in Production Code
**Detection signals:**
- `print("ENVIANDO EMAIL: ...")` or `console.log("Processando cartão...")` as notification implementation
- Notification service sending real emails with hardcoded SMTP credentials
- Critical operations (payment, enrollment) with no real notification or with plaintext credit card logging

---

## MEDIUM

### AP-11: N+1 Query Problem
**Detection signals:**
- SQL query inside a `for` loop or `forEach` callback
- Nested cursors: `cursor2 = db.cursor(); cursor2.execute(...)` inside a `for row in rows` loop
- Callback pyramid: DB query inside DB query callback inside DB query callback

```python
for row in rows:
    cursor2 = db.cursor()
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = " + str(row["id"]))
    for item in cursor2.fetchall():
        cursor3 = db.cursor()
        cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))
```

### AP-12: Global Mutable State
**Detection signals:**
- Module-level mutable object used as cache: `let globalCache = {}`
- Module-level counter: `let totalRevenue = 0`
- Instance-level list used as persistent store: `self.notifications = []`

### AP-13: Missing Pagination on List Endpoints
**Detection signals:**
- `SELECT * FROM tabela` with no `LIMIT` in routes that list resources
- No `page`/`limit`/`offset` parameters on GET list endpoints

### AP-14: No Centralized Error Handler
**Detection signals:**
- Every route has its own `except Exception as e: return jsonify({"erro": str(e)})`
- No `@app.errorhandler(500)` (Flask) or `app.use((err, req, res, next) => ...)` (Express)

### AP-15: Callback Hell / Pyramid of Doom (Node.js)
**Detection signals:**
- 4+ levels of nested callbacks in a single route handler
- Deeply indented `this.db.get(...)` calls inside `this.db.all(...)` callbacks

### AP-16: In-Memory Database
**Detection signals:**
- `new sqlite3.Database(':memory:')` — all data lost on restart
- No persistent storage configured

---

## LOW

### AP-17: Debug-Only Print / Console.log in Production
**Detection signals:**
- `print("Listando " + str(len(produtos)) + " produtos")` in request handlers
- `console.log(...)` logging card numbers, gateway keys, or user data

### AP-18: Magic Numbers / Strings Without Named Constants
**Detection signals:**
- Discount thresholds inline: `if faturamento > 10000`, `faturamento * 0.1`
- Hardcoded category list: `["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]`
- Port number as literal: `port: 3000`

### AP-19: Single-Letter / Meaningless Variable Names
**Detection signals:**
- `let u`, `let e`, `let p`, `let cid`, `let cc` as parameter names in request handlers

### AP-20: Dead Code / Unused Variables
**Detection signals:**
- `totalRevenue = 0` exported but never mutated or used
- Functions defined but never called

---

## Deprecated APIs Quick Reference

| Technology | Deprecated Pattern | Modern Replacement |
|---|---|---|
| Python hashlib | `hashlib.md5()` for passwords | `bcrypt.hashpw()` |
| Flask | `app.config["DEBUG"] = True` always on | Env-var-controlled |
| Node.js | `new Buffer(...)` | `Buffer.from(...)` |
| sqlite3 (Node) | Callback-style `db.run(sql, cb)` | `better-sqlite3` (sync) or promises |
| smtplib (Python) | Hardcoded credentials in constructor | Load from `os.environ` |
| jsonwebtoken | `jwt.sign` without `algorithm` option | Always specify `{ algorithm: 'HS256' }` |
