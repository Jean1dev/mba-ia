# Project Analysis Guide

## Phase 1: Stack Detection

### Language Detection
Scan the project root for these indicators:

| Indicator | Language |
|---|---|
| `*.py` files + `requirements.txt` or `pyproject.toml` | Python |
| `*.js`/`*.ts` + `package.json` | Node.js |
| `*.java` + `pom.xml` or `build.gradle` | Java |
| `*.go` + `go.mod` | Go |
| `*.rb` + `Gemfile` | Ruby |

### Framework Detection

**Python:**
- `flask` in requirements.txt → Flask
- `django` in requirements.txt → Django
- `fastapi` in requirements.txt → FastAPI

**Node.js:**
- `express` in package.json dependencies → Express
- `fastify` → Fastify
- `nestjs` → NestJS

### Database Detection
Search for these patterns in source files:

| Pattern | DB |
|---|---|
| `sqlite3`, `better-sqlite3`, `sqlite` | SQLite |
| `psycopg`, `pg`, `postgresql` | PostgreSQL |
| `pymysql`, `mysql2`, `mysql` | MySQL |
| `mongoose`, `mongodb` | MongoDB |

Look for CREATE TABLE statements to identify domain tables.

### Architecture Detection Heuristics

**Flat/Monolithic (no separation):**
- All source files in root directory
- Single file with 200+ lines containing routes + DB + logic
- No `models/`, `controllers/`, `routes/`, `services/` directories

**Partial MVC (some separation):**
- Has `models/` or `routes/` directory but mixes concerns within files
- Services calling DB directly alongside business logic
- Controllers with complex business rules

**Full MVC:**
- Separate `models/`, `views/` or `routes/`, `controllers/` directories
- Controllers only orchestrate; models only access data
- No business logic in routes

## Phase 1 Output Format

Print this summary block:

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected language>
Framework:     <detected framework + version from requirements>
Dependencies:  <comma-separated list of key dependencies>
Domain:        <inferred from table names / routes / file names>
Architecture:  <Monolítica | Parcialmente organizada | MVC>
Source files:  <count> files analyzed
DB tables:     <comma-separated table names if found>
================================
```

## Domain Inference Rules

Infer the domain from table names and route patterns:
- Tables `produtos`, `pedidos`, `usuarios` → E-commerce API
- Tables `tasks`, `projects`, `users` → Task Manager
- Tables `cursos`, `alunos`, `matriculas` → LMS/Education
- Routes `/auth`, `/login` → Authentication system
- Routes `/checkout`, `/pagamento` → Payment/Checkout flow

## File Counting

Count all source files (`.py`, `.js`, `.ts`, `.rb`, `.java`, `.go`) excluding:
- `node_modules/`, `__pycache__/`, `.git/`, `venv/`, `.venv/`
- Test files (`test_*.py`, `*.test.js`, `*.spec.ts`)
