# Project Analysis Guide

## Language Detection

| Indicator | Language |
|---|---|
| `*.py` + `requirements.txt` or `pyproject.toml` | Python |
| `*.js`/`*.ts` + `package.json` | Node.js |
| `*.java` + `pom.xml` or `build.gradle` | Java |
| `*.go` + `go.mod` | Go |
| `*.rb` + `Gemfile` | Ruby |

## Framework Detection

**Python:**
- `flask` in requirements.txt → Flask
- `django` → Django
- `fastapi` → FastAPI
- `flask-sqlalchemy` or `sqlalchemy` → SQLAlchemy ORM in use

**Node.js:**
- `express` in package.json → Express
- `fastify` → Fastify
- `@nestjs/core` → NestJS

## Database Detection

Search for these import patterns and schema definitions:

| Pattern | DB |
|---|---|
| `sqlite3`, `better-sqlite3`, `:memory:`, `sqlite:///` | SQLite |
| `psycopg`, `pg`, `postgresql` | PostgreSQL |
| `pymysql`, `mysql2` | MySQL |
| `mongoose`, `mongodb` | MongoDB |
| `db.Model` (SQLAlchemy), `CREATE TABLE` | Relational ORM/Raw SQL |

## Architecture Classification

**Monolithic (flat):**
- All files in root directory
- Single file with 200+ lines mixing routes + DB + business logic
- No `models/`, `controllers/`, `routes/` directories
- Routes defined inside the same class that manages the DB

**Partially organized:**
- Has `models/`, `routes/`, `services/` directories but mixes concerns within files
- Routes calling DB directly
- Business logic in model methods

**Full MVC:**
- Clear separation: Models (data), Controllers (logic), Views/Routes (HTTP)
- No business logic in routes
- No SQL in controllers

## Domain Inference

| Table/route patterns | Domain |
|---|---|
| `produtos`, `pedidos`, `usuarios` | E-commerce API |
| `tasks`, `projects`, `categories` | Task Manager |
| `courses`, `enrollments`, `payments` | LMS/Education |
| `users` + `/login` + `/checkout` | Auth + payment flow |

## File Count

Count `.py`, `.js`, `.ts`, `.rb`, `.java`, `.go` source files excluding:
- `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `.venv/`
- Test files (`test_*.py`, `*.test.js`, `*.spec.ts`)
- Migration files, seed files

## Phase 1 Output Format

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <language>
Framework:     <framework + version>
Dependencies:  <key deps comma-separated>
Domain:        <description from table/route names>
Architecture:  <Monolithic | Partially organized | MVC>
Source files:  <N> files analyzed
DB tables:     <table names or "none detected">
================================
```
