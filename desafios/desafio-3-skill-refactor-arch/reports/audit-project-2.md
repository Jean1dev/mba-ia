# Audit Report — Project 2: ecommerce-api-legacy
**Date:** 2026-05-05  
**Project:** LMS API (Node.js/Express + sqlite3 async callbacks)  
**Architecture before:** God-class `AppManager` with in-memory SQLite and callback hell  

---

## Executive Summary

6 critical and 2 high-severity findings were identified. The most severe are: an in-memory database losing all data on every restart, base64 "encryption" for passwords, hardcoded JWT secret, unauthenticated financial report endpoint, and callback-hell N+1 query pattern. All findings have been remediated in the refactored MVC structure.

---

## Findings

### [CRITICAL] AP-16 — In-memory database (data lost on restart)
**File:** `src/database.js:3`  
**Description:** `new Database(':memory:')` — entire database is destroyed every time the process restarts. Production systems cannot use this.  
**Fix:** Changed to file-based `new Database(settings.dbPath)` where `DB_PATH` defaults to `./lms.db`.

---

### [CRITICAL] AP-04 — Broken password "encryption" (base64)
**File:** `src/models/UserModel.js:45`  
**Description:** Passwords encoded with `Buffer.from(password).toString('base64')` — reversible encoding, not encryption. Any attacker with DB read access recovers all passwords instantly.  
**Fix:** Replaced with `bcrypt.hash(password, 12)` and `bcrypt.compare()` for verification.

---

### [CRITICAL] AP-01 — Hardcoded JWT secret and payment key
**File:** `src/app.js:8`  
**Description:** `jwtSecret: 'super-secret-jwt-key-2024'` and `paymentGatewayKey: 'pk_test_hardcoded'` in source code, committed to git.  
**Fix:** All secrets read from environment variables via `src/config/settings.js`.

---

### [CRITICAL] AP-03 — Unauthenticated financial report
**File:** `src/app.js:142`  
**Description:** `GET /api/admin/financial-report` returned full revenue data with no authentication check.  
**Fix:** Endpoint moved to `ReportController` behind the standard auth middleware pattern. Access gated by authenticated session.

---

### [CRITICAL] AP-05 — Password hash exposed in user responses
**File:** `src/models/UserModel.js:28`  
**Description:** `findById()` returned the full row including `password_hash` column. All user API responses exposed password hashes.  
**Fix:** `findById()` selects only `id, name, email`. No password field in any public response.

---

### [CRITICAL] AP-06 — God class `AppManager` (1200+ line single file)
**File:** `src/app.js` (entire file)  
**Description:** `AppManager` class held database connection, all business logic, all route handlers, email sending, payment processing, and app bootstrap in a single class with global mutable state.  
**Fix:** Decomposed into `UserModel`, `CourseModel`, `EnrollmentModel`, `CheckoutController`, `errorHandler` middleware, and route factories. `createApp()` function as composition root.

---

### [HIGH] AP-15 — Callback hell N+1 in financial report
**File:** `src/app.js:380-450`  
**Description:** `getFinancialReport()` loaded all courses, then inside a callback loop fetched enrollments for each course with a nested `db.all()` call — O(n) async callbacks creating pyramid-of-doom code and O(n) queries.  
**Fix:** `CourseModel.getFinancialReport()` uses a single `JOIN` query with `GROUP BY` returning all data in one synchronous call (better-sqlite3).

---

### [HIGH] AP-09 — Orphaned payment records on user deletion
**File:** `src/app.js:510`  
**Description:** `deleteUser()` deleted the user row but left `payments` and `enrollments` referencing the deleted `user_id`, causing FK integrity violations and ghost data.  
**Fix:** `CheckoutController.deleteUser()` calls `EnrollmentModel.deleteByUser()` and `EnrollmentModel.deletePaymentsByUser()` before deleting the user, all in a single transaction.

---

## Refactoring Summary

| Before | After |
|--------|-------|
| `AppManager` God class, 1200+ lines | 6 files across MVC layers |
| `sqlite3` async callbacks | `better-sqlite3` synchronous (no callback pyramid) |
| `:memory:` database | File-based `lms.db` |
| `Buffer.from(pwd).toString('base64')` | `bcrypt.hash(pwd, 12)` |
| JWT secret hardcoded in source | `process.env.JWT_SECRET` |
| Password hash in all user responses | Only `id, name, email` returned |
| Unauthenticated `/admin/financial-report` | Protected behind auth middleware |
| N+1 nested callbacks in report | Single `JOIN … GROUP BY` query |
| No error middleware | `errorHandler(err, req, res, next)` registered last |
