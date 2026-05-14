# Audit Report — Project 1: code-smells-project
**Date:** 2026-05-05  
**Project:** E-commerce API (Python/Flask + raw SQLite)  
**Architecture before:** Monolithic single-file (`app.py`, 800+ lines)  

---

## Executive Summary

5 critical and 3 high-severity findings were identified. The most severe issues are SQL injection via f-string query building, unauthenticated admin shell (`/admin/query`), plaintext passwords stored as MD5, and hardcoded secret keys. All findings have been remediated in the refactored `src/` MVC structure.

---

## Findings

### [CRITICAL] AP-02 — SQL Injection via f-string concatenation
**File:** `app.py:87, 102, 145`  
**Description:** User-supplied values injected directly into SQL strings via Python f-strings.  
```python
# BEFORE
cursor.execute(f"SELECT * FROM produtos WHERE categoria = '{categoria}'")
cursor.execute(f"SELECT * FROM usuarios WHERE email = '{email}'")
```
**Fix:** All queries replaced with parameterized SQL using `?` placeholders and tuple arguments.

---

### [CRITICAL] AP-03 — Unauthenticated admin shell endpoint
**File:** `app.py:312`  
**Description:** `/admin/query` accepted arbitrary SQL from POST body with no authentication, allowing full database read/write/delete by any client.  
**Fix:** Endpoint removed entirely. No equivalent exists in the refactored API.

---

### [CRITICAL] AP-01 — Hardcoded credentials and secret key
**File:** `app.py:12, 18`  
**Description:** `SECRET_KEY = 'minha-chave-secreta-123'` and SMTP password hardcoded in source.  
**Fix:** All secrets moved to environment variables via `src/config/settings.py` with safe defaults only for development.

---

### [CRITICAL] AP-04 — Broken password hashing (MD5)
**File:** `app.py:198`  
**Description:** User passwords hashed with MD5, a cryptographically broken algorithm with no salt, trivially reversed via rainbow tables.  
```python
# BEFORE
senha_hash = hashlib.md5(senha.encode()).hexdigest()
```
**Fix:** Replaced with `bcrypt.hashpw` (cost factor 12, random salt per hash).

---

### [CRITICAL] AP-05 — Sensitive data exposed in API responses
**File:** `app.py:210, 267`  
**Description:** `/usuarios` and `/login` responses included the `senha` (password hash) field. `/admin/info` exposed DB path and internal config.  
**Fix:** `to_dict()` on `UsuarioModel` never includes `senha`. `/admin/info` removed.

---

### [HIGH] AP-06 — God Class / no separation of concerns
**File:** `app.py` (entire file, ~800 lines)  
**Description:** Single file contained Flask app setup, database connection, all business logic, all HTTP routes, and validation. Impossible to test or maintain independently.  
**Fix:** Refactored into MVC layers: `src/models/`, `src/controllers/`, `src/views/`, `src/middlewares/`, `src/config/`.

---

### [HIGH] AP-09 — Orphaned records on user deletion
**File:** `app.py:445`  
**Description:** Deleting a user left all their `pedidos` (orders) in the DB with dangling `usuario_id` FK references.  
**Fix:** `PedidoController.delete_user_cascade()` deletes all orders before deleting the user within a single transaction.

---

### [HIGH] AP-02b — N+1 queries in order listing
**File:** `app.py:178`  
**Description:** `GET /pedidos` loaded all orders, then executed a separate `SELECT` per order to fetch the associated user name — O(n) queries for n orders.  
**Fix:** `PedidoModel.find_all()` uses a single `JOIN` query to fetch user data in one round-trip.

---

### [LOW] AP-10 — Debug mode hardcoded to True in production path
**File:** `app.py:799`  
**Description:** `app.run(debug=True)` unconditionally enabled Flask debug mode, exposing the interactive debugger to the network.  
**Fix:** `DEBUG` read from `os.environ.get("DEBUG", "false")`.

---

## Refactoring Summary

| Before | After |
|--------|-------|
| 1 file, ~800 lines | 12 files across MVC layers |
| Raw `sqlite3` with f-string SQL | Parameterized queries with tuple params |
| MD5 password hashing | bcrypt (cost 12, random salt) |
| `SECRET_KEY` hardcoded | `os.environ.get("SECRET_KEY", ...)` |
| `/admin/query` open shell | Endpoint removed |
| Password hash in API responses | `to_dict()` omits `senha` |
| No error handling | Centralized `register_error_handlers()` |
| N+1 on order listing | Single JOIN query |
