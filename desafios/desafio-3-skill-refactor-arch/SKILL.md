# Skill: refactor-arch
## Automated Architectural Refactoring to MVC

You are an expert software architect and security auditor. Your mission is to analyze the current project, identify architectural problems and code smells, generate a structured audit report, and refactor the project to the MVC pattern.

This skill executes in **3 sequential phases**. Always follow the order. Never skip a phase.

---

## Reference Files

Read and internalize these files before starting:

- `01-project-analysis.md` — Stack and architecture detection heuristics
- `02-antipatterns-catalog.md` — 20+ anti-patterns with detection signals and severity
- `03-audit-report-template.md` — Standardized audit report format
- `04-mvc-architecture-guidelines.md` — Target MVC structure and layer rules
- `05-refactoring-playbook.md` — Concrete transformation patterns with before/after examples

---

## PHASE 1: PROJECT ANALYSIS

**Goal:** Understand the project's current state without modifying anything.

**Steps:**

1. List all source files (exclude `node_modules`, `__pycache__`, `.git`, `venv`, `.venv`, `*.db`)
2. Read all source and configuration files (`package.json`, `requirements.txt`)
3. Detect language, framework and version using `01-project-analysis.md`
4. Detect database technology by searching imports and schema definitions
5. Infer the application domain from table names, route paths and file names
6. Classify the current architecture (Monolithic / Partially organized / MVC)
7. Count source files (exclude test files, configs, node_modules)

**Print this exact summary block:**

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected language>
Framework:     <framework + version from dependency file>
Dependencies:  <comma-separated key dependencies>
Domain:        <inferred domain description>
Architecture:  <Monolithic | Partially organized | MVC>
Source files:  <N> files analyzed
DB tables:     <comma-separated table names, or "none detected">
================================
```

Then say: "Phase 1 complete. Starting Phase 2 — Architecture Audit."

---

## PHASE 2: ARCHITECTURE AUDIT

**Goal:** Identify all anti-patterns and generate a structured report.

**Steps:**

1. Read `02-antipatterns-catalog.md` to load all detection patterns
2. Read `03-audit-report-template.md` for the exact report format
3. Scan ALL source files for each anti-pattern in the catalog
4. For each finding record: exact file path, exact line numbers, severity, description specific to the actual code, impact, and recommendation
5. Check for deprecated APIs using the reference table in `02-antipatterns-catalog.md`
6. Order all findings: CRITICAL → HIGH → MEDIUM → LOW
7. Generate the full report following `03-audit-report-template.md` exactly

**Minimum requirements:**
- At least 5 findings
- At least 1 CRITICAL or HIGH finding
- Every finding must have exact file path and line numbers

**After printing the complete report, STOP and ask:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Wait for user confirmation. Do NOT modify any file before receiving "y".**

---

## PHASE 3: REFACTORING

**Only execute after the user confirms with "y".**

**Goal:** Transform the project to MVC architecture, eliminating all identified problems.

**Steps:**

1. Read `04-mvc-architecture-guidelines.md` to load the target MVC structure
2. Read `05-refactoring-playbook.md` to load transformation patterns
3. Plan the new directory structure based on detected stack and domain
4. Execute refactoring in this order:
   a. Create `src/config/` — extract ALL hardcoded values to env-var-based config
   b. Create `src/models/` — one file per domain, parameterized queries only, dependency injection
   c. Create `src/controllers/` — business logic here, no HTTP concerns
   d. Create `src/views/` or `src/routes/` — thin HTTP layer only
   e. Create `src/middlewares/` — auth decorator + global error handler
   f. Rewrite app entry point as composition root
   g. Remove old flat files replaced by the new structure
5. Validate:
   - Install dependencies
   - Start the application
   - Test that at least 2 original endpoints respond correctly

**Print final summary:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<actual directory tree>

## Issues Resolved
<list CRITICAL and HIGH issues fixed>

## Validation
  ✓ or ✗ Application boots without errors
  ✓ or ✗ All endpoints respond correctly
  ✓ or ✗ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

---

## Technology-Agnostic Adaptation

| Aspect | Python/Flask | Node.js/Express |
|---|---|---|
| Config | `os.environ.get()` | `process.env` |
| Auth middleware | `@decorator` | `middleware function` |
| Error handler | `@app.errorhandler` | `app.use(errHandler)` |
| Routes | `Blueprint` | `express.Router()` |
| Dependency injection | constructor params | constructor params |

---

## Non-Negotiable Rules

1. **Never modify files** during Phase 2
2. **Always wait** for explicit "y" before Phase 3
3. **Preserve all original functionality** — every endpoint must still work
4. **Fix security issues first**: hardcoded secrets, SQL injection, plaintext passwords
5. **Use parameterized queries** — never string concatenation or f-string interpolation in SQL
6. **No hardcoded credentials** anywhere in the codebase
7. **Remove dangerous admin endpoints** (arbitrary SQL execution, unauthenticated resets)
8. **One model per domain** — no God classes
