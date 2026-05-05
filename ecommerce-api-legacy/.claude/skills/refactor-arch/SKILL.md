# Skill: refactor-arch
## Automated Architectural Refactoring to MVC

You are an expert software architect and code auditor. Your mission is to analyze the current project, identify architectural problems and code smells, generate a structured audit report, and refactor the project to the MVC pattern.

This skill operates in **3 sequential phases**. Execute them in order. Never skip a phase.

---

## Reference Files

Load and internalize these reference files before starting:

- `01-project-analysis.md` — Heuristics for stack and architecture detection
- `02-antipatterns-catalog.md` — Anti-patterns with detection signals and severity
- `03-audit-report-template.md` — Standardized audit report format
- `04-mvc-architecture-guidelines.md` — Target MVC structure and layer rules
- `05-refactoring-playbook.md` — Concrete transformation patterns with before/after examples

---

## PHASE 1: PROJECT ANALYSIS

**Goal:** Understand the project's current state.

**Steps:**

1. List all source files in the current directory (exclude `node_modules`, `__pycache__`, `.git`, `venv`, `.venv`)
2. Read all source files and configuration files (`package.json`, `requirements.txt`, `pyproject.toml`)
3. Detect the language, framework, and version using `01-project-analysis.md`
4. Identify the database technology by searching for connection imports and CREATE TABLE statements
5. Infer the application domain from table names, route paths, and file names
6. Classify the current architecture (Monolítica / Parcialmente organizada / MVC)
7. Count source files (exclude test files, configs, node_modules)

**Print this summary block exactly:**

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <detected language>
Framework:     <framework + version from dependency file>
Dependencies:  <comma-separated key dependencies>
Domain:        <inferred domain description>
Architecture:  <Monolítica | Parcialmente organizada | MVC>
Source files:  <N> files analyzed
DB tables:     <comma-separated table names, or "none detected">
================================
```

Then say: "Phase 1 complete. Starting Phase 2 — Architecture Audit."

---

## PHASE 2: ARCHITECTURE AUDIT

**Goal:** Identify all anti-patterns and generate a structured report.

**Steps:**

1. Read `02-antipatterns-catalog.md` to load all detection patterns (AP-01 through AP-20)
2. Read `03-audit-report-template.md` for the exact report format
3. For each anti-pattern in the catalog, scan ALL source files for signals
4. For each finding:
   - Record the exact file path and line numbers
   - Classify severity (CRITICAL, HIGH, MEDIUM, LOW)
   - Write the specific description based on the actual code (not generic)
5. Also check for deprecated APIs using the table in `02-antipatterns-catalog.md`
6. Order findings by severity: CRITICAL → HIGH → MEDIUM → LOW
7. Generate the full report following `03-audit-report-template.md` format exactly

**Minimum requirements:**
- At least 5 findings total
- At least 1 CRITICAL or HIGH finding
- Every finding must have exact file path and line numbers

**After printing the complete report, STOP and ask:**

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

**Wait for user confirmation. Do NOT modify any files before receiving "y".**

---

## PHASE 3: REFACTORING

**Only execute this phase after user confirms with "y".**

**Goal:** Transform the project to MVC architecture, eliminating all identified problems.

**Steps:**

1. Read `04-mvc-architecture-guidelines.md` to load the target MVC structure
2. Read `05-refactoring-playbook.md` to load transformation patterns
3. Plan the new directory structure based on the detected stack and domain
4. Execute the refactoring in this order:
   a. Create new directory structure (`src/config/`, `src/models/`, `src/controllers/`, `src/views/` or `src/routes/`, `src/middlewares/`)
   b. Create `config/settings.py` or `config/settings.js` — extract all hardcoded values
   c. Create model files — one per domain, using parameterized queries, with dependency injection
   d. Create controller files — move business logic here, no HTTP concerns
   e. Create route/view files — thin HTTP layer only
   f. Create middleware files — auth decorator/middleware + global error handler
   g. Rewrite the app entry point as composition root
   h. Remove old files that have been replaced
5. After writing all files, validate the refactoring:
   - Install/verify dependencies
   - Start the application
   - Test that at least 2 endpoints respond correctly
   - Confirm no errors on startup

**Print final summary:**

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<print the actual directory tree with new files>

## Issues Resolved
<list the CRITICAL and HIGH issues that were fixed>

## Validation
  ✓ or ✗ Application boots without errors
  ✓ or ✗ All endpoints respond correctly
  ✓ or ✗ Zero CRITICAL/HIGH anti-patterns remaining
================================
```

---

## Technology-Agnostic Rules

This skill works with any backend language/framework. Adapt as follows:

| Aspect | Python/Flask | Node.js/Express | Java/Spring |
|---|---|---|---|
| Config | `os.environ.get()` | `process.env` | `@Value` + `application.properties` |
| Auth | `@decorator` | `middleware function` | `@Aspect` or filter |
| Error handler | `@app.errorhandler` | `app.use(errHandler)` | `@ControllerAdvice` |
| Routes | `Blueprint` | `express.Router()` | `@RestController` |
| DI | constructor params | constructor params | `@Autowired` |

When the stack is not Python or Node.js, apply the same MVC principles using the conventions of that language's ecosystem.

---

## Important Rules

1. **Never modify files** during Phase 2 — only analyze and report
2. **Always wait** for explicit "y" confirmation before Phase 3
3. **Preserve all original functionality** — every endpoint that existed before must still work
4. **Fix security issues first** — resolve AP-01, AP-02, AP-04 before structural changes
5. **Use parameterized queries** in all SQL — never string concatenation
6. **Inject dependencies** through constructors — no global module-level instances
7. **One model per domain** — do not create God models
8. **Report validation failures** honestly — if an endpoint fails, report ✗ and the error
