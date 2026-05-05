# Anti-Patterns Catalog

## Severity Scale
- **CRITICAL:** Security vulnerabilities or architecture failures that break correct operation
- **HIGH:** MVC/SOLID violations that severely impede maintainability and testing
- **MEDIUM:** Code quality issues, duplication, moderate performance problems
- **LOW:** Readability, naming, magic values

---

## CRITICAL Severity

### AP-01: Hardcoded Credentials / Secrets
**Detection signals:**
- `SECRET_KEY = "..."` with literal string value in source file
- `JWT_SECRET = "..."` in source code (not env var)
- `password = "hardcoded"` or `senha = "hardcoded"` in config
- Any credential not loaded from `os.environ`, `process.env`, or `.env` file

**Python example:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"  # CRITICAL
```
**Node.js example:**
```javascript
const JWT_SECRET = 'lms-secret-key-nao-mude-isso';  // CRITICAL
```

### AP-02: SQL Injection
**Detection signals:**
- String concatenation in SQL queries: `"SELECT ... WHERE id = " + str(id)`
- f-string interpolation: `f"SELECT * FROM users WHERE email = '{email}'"`
- Template literals: `` `SELECT * FROM users WHERE id = ${id}` ``
- Any SQL string built with user-controlled input without parameterized queries

**Example:**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(produto_id))  # CRITICAL
conn.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")  # CRITICAL
```

### AP-03: God Class / God Method
**Detection signals:**
- Single file/class with 200+ lines handling multiple domains
- Class with methods for: DB access + business logic + validation + formatting
- File containing routes + models + database initialization + middleware

**Detection:** File has methods/functions from 3+ different architectural layers

### AP-04: Plaintext Password Storage
**Detection signals:**
- Passwords stored directly in DB without hashing: `INSERT INTO users ... VALUES (password)`
- MD5-only hashing: `hashlib.md5(password.encode()).hexdigest()` (insufficient)
- Password returned/logged as plaintext

**Example:**
```python
conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))  # CRITICAL
```

### AP-05: Exposed Sensitive Data in API Response
**Detection signals:**
- Routes returning `password`, `senha`, or `hash` fields in JSON response
- `SELECT *` from users table returned directly to API caller
- `console.log` / `print` statements logging credentials or tokens

---

## HIGH Severity

### AP-06: Business Logic in Controllers/Routes
**Detection signals:**
- Route handler functions with 20+ lines of business logic
- If/else chains computing prices, discounts, or status transitions inside route functions
- Validation logic duplicated across multiple route handlers

**Example:**
```python
def criar_pedido():
    # 50 lines of inventory checking, pricing, checkout logic here
```

### AP-07: No Authentication/Authorization on Protected Routes
**Detection signals:**
- Routes that modify data (`POST`, `PUT`, `DELETE`) with no token/session check
- Missing middleware for auth on routes that should be protected
- Any admin route accessible without role check

### AP-08: Inline Auth Logic Duplication (DRY Violation)
**Detection signals:**
- Same auth token extraction/verification code copied into 3+ route handlers
- Pattern: `token = req.headers.authorization?.replace('Bearer ', '')` repeated

### AP-09: Global Mutable State
**Detection signals:**
- Module-level mutable dicts/lists used as shared cache or session store
- `let activeUsers = {}` at module level in Node.js
- Python class attributes or module globals mutated across requests

### AP-10: No Dependency Injection / Hard Coupling
**Detection signals:**
- Model/service instances created at module level: `produto_model = ProdutoModel()`
- Direct imports of concrete implementations instead of interfaces
- No way to swap implementations without changing source code

---

## MEDIUM Severity

### AP-11: N+1 Query Problem
**Detection signals:**
- SQL query inside a `for` loop or `.map()` callback
- Fetching related data one-by-one instead of using JOINs or bulk queries

**Example:**
```python
for produto in produtos:
    conn2 = get_connection()
    vendas = conn2.execute("SELECT COUNT(*) FROM itens_pedido WHERE produto_id = ?", (p["id"],))
```

### AP-12: Race Condition / Missing Transaction
**Detection signals:**
- Check-then-act pattern on shared resource without transaction: read stock, then update stock in separate queries
- `UPDATE` and `INSERT` pairs without `BEGIN TRANSACTION`

### AP-13: Missing Input Validation
**Detection signals:**
- Route accepts POST/PUT with `request.json` but no schema validation
- No check that required fields are present before DB insert
- No type checking on numeric fields (price, quantity, priority)

### AP-14: No API Versioning
**Detection signals:**
- Routes registered as `/resource` with no `/v1/` or `/api/v1/` prefix
- No version in URL pattern or header

### AP-15: Unbounded Queries / Missing Pagination
**Detection signals:**
- `SELECT * FROM table` with no `LIMIT` clause in list endpoints
- No `page`/`limit` parameters in GET endpoints that return lists

### AP-16: Deprecated API Usage
**Detection signals:**
- Python 2 style: `print "text"` (not function)
- Flask deprecated: `flask.ext.*` imports, `app.run()` without `if __name__ == "__main__"`
- bcrypt deprecated: `bcrypt.checkpw` vs `compareSync` (JS) — check package version compatibility
- SQLite3 deprecated: using `.fetchall()` on closed connection
- Node.js deprecated: `new Buffer()` instead of `Buffer.from()`
- Express deprecated: `res.sendfile()` instead of `res.sendFile()`
- jsonwebtoken: `jwt.sign` without explicit algorithm (defaults may change)

### AP-17: No Centralized Error Handler
**Detection signals:**
- Each route has its own `try/except` or `try/catch`
- No `@app.errorhandler` (Flask) or `app.use((err, req, res, next) => ...)` (Express)
- Error details (stack traces, DB errors) returned directly to client

---

## LOW Severity

### AP-18: Magic Numbers / Magic Strings
**Detection signals:**
- Numeric literals inline: `if len(name) < 3`, `expiresIn: '7d'`, port `3000` hardcoded
- Status strings hardcoded inline: `if status == "todo"` without named constant

### AP-19: Debug Code in Production
**Detection signals:**
- `app.run(debug=True)` in production entry point
- `console.log` / `print` statements logging request data or passwords
- `[DEBUG]` print statements

### AP-20: Poor Naming / Unused Code
**Detection signals:**
- Single-letter variables: `x`, `y`, `z` used for business data
- Functions defined but never called
- Variables assigned but never used
- Comments like `# TODO: implement` for critical functionality

---

## Deprecated APIs Quick Reference

| Technology | Deprecated | Modern Replacement |
|---|---|---|
| Flask <2.0 | `flask.ext.*` | Direct package imports |
| Flask | `app.run()` outside `__name__ == "__main__"` | Guard with `if __name__ == "__main__"` |
| Node.js | `new Buffer()` | `Buffer.from()` |
| Express | `res.sendfile()` | `res.sendFile()` |
| Express | `app.use(express.bodyParser())` | `app.use(express.json())` |
| JWT | No algorithm specified | `{ algorithm: 'HS256' }` |
| bcrypt | `bcrypt.compareSync` in async context | `await bcrypt.compare()` |
| SQLite (Python) | Using connection after `conn.close()` | Always close after last use |
