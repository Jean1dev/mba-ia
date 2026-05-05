# Audit Report — Project 3: task-manager-api
**Date:** 2026-05-05  
**Project:** Task Manager API (Python/Flask + SQLAlchemy ORM)  
**Architecture before:** Partially organized (models separated, but fat routes with business logic)  

---

## Executive Summary

3 critical and 3 high-severity findings were identified. The most severe are: hardcoded `SECRET_KEY` and SMTP password, plaintext password visible in API responses, and N+1 ORM queries in task listing and report generation. All findings have been remediated in the refactored `src/` MVC structure.

---

## Findings

### [CRITICAL] AP-01 — Hardcoded SECRET_KEY and SMTP credentials
**File:** `app.py:13`, `services/notification_service.py:8-9`  
**Description:** Flask secret key hardcoded as `'super-secret-key-123'`. SMTP email password hardcoded as `'senha123'` in `NotificationService.__init__`. Both committed in plaintext to version control.  
```python
# BEFORE
app.config['SECRET_KEY'] = 'super-secret-key-123'
self.email_password = 'senha123'
```
**Fix:** `SECRET_KEY` moved to `os.environ.get("SECRET_KEY", "dev-only-change-in-production")`. `NotificationService` accepts a `config` parameter defaulting to `Config` class, reading `SMTP_PASSWORD` from env.

---

### [CRITICAL] AP-05 — N+1 ORM queries in task listing (implicit lazy loads)
**File:** `routes/task_routes.py:42-57`  
**Description:** `GET /tasks` loaded all tasks then, inside a Python loop, called `User.query.get(t.user_id)` and `Category.query.get(t.category_id)` per task — generating 2n+1 SQL queries for n tasks.  
```python
# BEFORE — inside a for loop over tasks:
user = User.query.get(t.user_id)   # 1 query per task
cat  = Category.query.get(t.category_id)  # 1 query per task
```
**Fix:** `Task.find_all_with_relations()` uses `joinedload(Task.user)` and `joinedload(Task.category)`, fetching all data in a single SQL JOIN.

---

### [CRITICAL] AP-05b — N+1 queries in summary report
**File:** `routes/report_routes.py:53-68`  
**Description:** `GET /reports/summary` loaded all users then issued `Task.query.filter_by(user_id=u.id).all()` inside a loop — O(n) queries for n users.  
**Fix:** `ReportController.summary()` uses a single `GROUP BY` aggregation query with `func.count`, `func.sum`, and `outerjoin`.

---

### [HIGH] AP-05c — Password hash potentially visible in user routes
**File:** `routes/user_routes.py:6` (import of `hashlib`)  
**Description:** Legacy `hashlib` import remained in `user_routes.py`. The original `models/user.py` stored MD5 hashes; `to_dict()` did not explicitly exclude the `password` field, risking accidental exposure if the dict construction changed.  
**Fix:** `src/models/user.py` `to_dict()` explicitly lists only safe fields (`id, name, email, role, active, created_at`). Password field is never included.

---

### [HIGH] AP-06 — Business logic in route handlers
**File:** `routes/task_routes.py`, `routes/user_routes.py`, `routes/report_routes.py`  
**Description:** Route handlers contained input validation, database access, business rules (overdue calculation, completion rate), and HTTP serialization in a single function — violating single-responsibility and making unit testing impossible without a running Flask server.  
**Fix:** Business logic extracted to `src/controllers/task_controller.py`, `user_controller.py`, and `report_controller.py`. Routes are thin HTTP adapters.

---

### [HIGH] AP-10 — No centralized error handling
**File:** `app.py`, all route files  
**Description:** Each route handler had its own `try/except` block returning inconsistent error formats. Some used bare `except:` catching all exceptions silently, swallowing stack traces.  
**Fix:** `src/middlewares/error_handler.py` registers `@app.errorhandler` for `ValueError→400`, `LookupError→404`, `PermissionError→401`, and a catch-all 500 handler with `logger.exception`.

---

### [LOW] AP-01b — `/health` endpoint exposing timestamp metadata
**File:** `app.py:23`  
**Description:** Health endpoint returned `{'status': 'ok', 'timestamp': str(datetime.datetime.now())}`. While low severity, exposing server time can assist in timing attacks and information gathering.  
**Fix:** Health endpoint returns only `{'status': 'ok', 'database': 'connected'}`.

---

## Refactoring Summary

| Before | After |
|--------|-------|
| `SECRET_KEY = 'super-secret-key-123'` | `os.environ.get("SECRET_KEY", ...)` |
| SMTP password `'senha123'` hardcoded | `Config.SMTP_PASSWORD` from env |
| 2n+1 queries in task listing | Single `joinedload` JOIN query |
| n+1 queries in report summary | Single `GROUP BY` aggregation |
| Business logic in route handlers | MVC: controllers + views separated |
| Bare `except:` silencing errors | Centralized `register_error_handlers()` |
| No `bcrypt` dependency | `bcrypt==4.1.2` added to `requirements.txt` |
| Fat routes (~300 lines each) | Thin blueprints via factory pattern |
