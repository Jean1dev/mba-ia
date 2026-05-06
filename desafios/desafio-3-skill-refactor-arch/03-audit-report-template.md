# Audit Report Template

Use this exact format when generating the Phase 2 report.

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
Description: <Specific description based on the ACTUAL code, not generic>
Impact: <Why this is dangerous or blocking — specific to this project>
Recommendation: <Concrete fix — what to create or change>

### [CRITICAL] <Next Finding>
...

### [HIGH] <Finding>
...

[continue for all severities: CRITICAL → HIGH → MEDIUM → LOW]

================================
Total: <N> findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

---

## Rules

1. **Order by severity**: CRITICAL first, then HIGH, MEDIUM, LOW
2. **Be specific**: Use actual variable names, actual string values, actual file paths from the codebase
3. **Exact line numbers**: `models.py:28` not `models.py`
4. **Minimum 5 findings** — every codebase will have at least 5
5. **Minimum 1 CRITICAL or HIGH** — always present
6. **Reference actual code**: quote the problematic line if it helps clarity
7. **Include deprecated API findings** when applicable

## Standard Finding Titles

- `Hardcoded Secret Key / Credentials`
- `SQL Injection — String Concatenation`
- `SQL Injection — f-string Interpolation`
- `Unauthenticated Arbitrary SQL Execution Endpoint`
- `Unauthenticated Database Reset Endpoint`
- `Broken Cryptography — MD5 Password Hashing`
- `Home-Rolled Cryptography (badCrypto)`
- `Sensitive Data Exposed in API Response`
- `Secret Key Leaked via /health Endpoint`
- `God Class — Mixed Responsibilities`
- `Business Logic in Model Layer`
- `Plaintext Password Storage and Comparison`
- `Orphaned Records on User Delete`
- `Fake Notifications via print() Statements`
- `N+1 Query Problem`
- `Callback Hell / Pyramid of Doom`
- `Global Mutable State`
- `Missing Pagination on List Endpoints`
- `No Centralized Error Handler`
- `In-Memory Database (Data Lost on Restart)`
- `Debug print() Statements in Request Handlers`
- `Magic Numbers / Strings Without Named Constants`
- `Single-Letter Variable Names`
- `Dead Code / Unused Variable`
