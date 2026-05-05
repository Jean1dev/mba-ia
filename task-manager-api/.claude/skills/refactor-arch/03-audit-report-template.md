# Audit Report Template

Use this exact format when generating the Phase 2 audit report.

---

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <project-directory-name>
Stack:   <Language> + <Framework>
Files:   <N> analyzed | ~<LOC> lines of code

## Summary
CRITICAL: <N> | HIGH: <N> | MEDIUM: <N> | LOW: <N>

## Findings

### [CRITICAL] <Finding Title>
File: <relative-path>:<start-line>-<end-line>
Description: <What exactly is the problem, specific to this codebase>
Impact: <Why this is dangerous or blocking>
Recommendation: <Specific fix — what to create or change>

### [CRITICAL] <Next Critical Finding>
...

### [HIGH] <Finding Title>
File: <relative-path>:<start-line>-<end-line>
Description: <Description>
Impact: <Impact>
Recommendation: <Recommendation>

...continue for all severities in order: CRITICAL → HIGH → MEDIUM → LOW...

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Rules for Generating Reports

1. **Order findings by severity**: CRITICAL first, then HIGH, MEDIUM, LOW
2. **Be specific**: Always include the actual file path and exact line numbers
3. **Quantify**: "14 findings" not "several issues"
4. **Name the anti-pattern**: Reference AP-01 through AP-20 from the catalog
5. **Adapt to the project**: Describe the actual code, not a generic description
6. **Minimum 5 findings**: The report must identify at least 5 distinct problems
7. **At least 1 CRITICAL or HIGH**: Every codebase will have at least one serious issue
8. **Include deprecated APIs**: If the project uses any deprecated APIs from the catalog, flag them

## Finding Title Conventions

Use these standard titles (adapt as needed):

- `Hardcoded Credentials / Secret Key`
- `SQL Injection Vulnerability`
- `God Class — Mixed Responsibilities`
- `Plaintext Password Storage`
- `Sensitive Data Exposed in API Response`
- `Business Logic in Controller/Route Handler`
- `Missing Authentication on Protected Routes`
- `Inline Auth Code Duplication (DRY Violation)`
- `Global Mutable State`
- `No Dependency Injection`
- `N+1 Query Problem`
- `Race Condition — Missing Transaction`
- `Missing Input Validation`
- `No API Versioning`
- `Missing Pagination on List Endpoints`
- `Deprecated API Usage`
- `No Centralized Error Handler`
- `Magic Numbers / Strings`
- `Debug Code in Production`
- `Poor Naming / Dead Code`

## LOC Estimation

Count lines by adding up file sizes. For estimation:
- Small project (< 5 files): count exactly
- Medium (5-20 files): approximate to nearest 50
- Large (20+ files): approximate to nearest 100
