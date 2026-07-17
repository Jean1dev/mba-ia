---
name: implement-feature
description: Implements a feature autonomously based on its spec and plan, committing one commit per phase and reporting results against the feature's acceptance criteria.
---

# Implement Feature

Autonomously implement a feature from its existing `spec.md` + `plan.md`. The skill reads the feature's technical specification and implementation plan, writes the code phase by phase, validates each phase, commits, and reports results against the acceptance criteria declared in the PRD.

## INPUT

Free-form. The skill figures out what was passed. Any combination works:

- A feature identifier: `F09`, `Video Upload`, or similar.
- A feature folder: `docs/F09-in-video-transcription-search/`, `./F09/`, etc.
- A file inside the feature folder: `docs/F09-in-video-transcription-search/spec.md`.
- A PRD path: `@docs/PRD.md`, `docs/PRD.md`, `@PRD.md`.
- Extra natural-language instructions appended anywhere (see **Overrides**).

The skill only needs to locate two files and one reference source:

1. **`spec.md` and `plan.md`** for the target feature. If the input points to a folder, look inside. If it points to a file, look in its parent folder. If it points to an ID or name, search under `docs/` for a folder matching `<ID>-*` or whose name kebab-cases to the given name.
2. **The PRD**. If explicitly passed, use it. Otherwise, auto-discover: `docs/PRD.md` → `PRD.md` → any top-level `*.md` whose content reads like a product spec. If none found, abort. If multiple are plausible, abort and list them.

## OUTPUT

- **Commits**: one per phase of `plan.md`, on the current branch (no branch creation, no branch switching).
- **Chat report** at the end: the feature's acceptance-criteria checklist marked ✓ / ✗ / — against actual test results, plus sections for Deviations, Soft-fails, Pre-existing failures, Overrides applied, Overrides ignored, and Phase status.

No files are written besides code changes and commit objects. The chat report is ephemeral.

---

## EXECUTION STEPS

### Step 1: Resolve Input

Parse the entire input as free-form. Extract:

- **Feature reference**: the first token that resolves to a folder containing `spec.md` + `plan.md`. Matches: ID patterns like `F\d+`, folder paths, file paths (parent folder = target), feature names (kebab-case + fuzzy match to folder names under `docs/`).
- **PRD reference**: an explicit `*.md` path prefixed with `@` or written literally; if it looks like a PRD (product spec content at the top), accept it. Otherwise auto-discover.
- **Extra instructions**: any remaining text that isn't a path/ID/name — treat as natural-language overrides (Step 3).

If resolution fails:

- No `spec.md` or `plan.md` in the resolved folder → abort: "spec.md/plan.md missing in `<folder>`."
- No PRD found → abort: "No PRD found. Pass the path explicitly."
- Multiple plausible PRDs → abort and list candidates.
- Ambiguous feature reference (multiple folders match) → abort and list candidates.

### Step 2: Load Context

Read in full:

- `spec.md` of the target feature — Component Overview, Data Model, API Contracts, Business Rules, UX Flows, Error Handling, Testing Strategy, Assumptions/Decisions.
- `plan.md` — phases and steps in order.
- **The PRD's acceptance-criteria content for this feature** — locate it semantically, not by section number. Typical headings: "Acceptance Criteria", "Critérios de Aceitação", "AC". Typical shape: a checkbox list `- [ ]` scoped to the feature (by ID or name). Also locate any cross-feature/integration checklist that references this feature. Do NOT assume a fixed section number — find content by its shape.

If the PRD has no acceptance-criteria content for this feature, proceed with an empty AC checklist and note it under soft-fails.

Do NOT explore the codebase eagerly. Open files lazily as each phase requires them.

### Step 3: Apply Overrides

Interpret extra instructions as natural-language overrides on the defaults:

| Default | Example overrides |
|---|---|
| Hard-fail retry limit = 3 | "no retry limit", "max 5 tries" |
| Fully autonomous | "pause between phases" — skill waits in chat for a reply containing `ok`, `continue`, `segue`, `yes`, or similar |
| 1 commit per phase | "single commit at the end", "no commits, just implement" |
| Run lint + typecheck + tests | "skip tests", "skip lint", "skip typecheck" |
| Implement all phases | "only phases 1 and 2", "skip phase 3" — phase positions are ordinal; labels like `A/B/C` map to `1/2/3` |
| Abort tests on external dep missing | "stub missing services", "assume empty response for missing APIs" — substitutes stubs **ONLY in test code**, never in production modules |

For each recognized override, record before/after for the final report's "Overrides applied" section.

**Immutable core (cannot be overridden):** the final AC checklist and its traceability to the PRD. Instructions that would disable the report are logged under "Overrides ignored" with the reason.

Ambiguous or contradictory instructions → default wins; logged under "Overrides ignored" with "ambiguous, kept default".

### Step 4: Pre-flight Dependency Check

Locate the dependency content in the PRD semantically (typical headings: "Dependency Graph", "Dependencies"; typical shape: a table or list pairing each feature with its prerequisites). For each listed dependency of the target feature, verify it appears implemented in the codebase (look for the characteristic files described in that dependency's own `spec.md` Component Overview, or obvious source-level markers).

- Any dependency missing → **abort before any implementation**. Report: "F<target> depends on F<N>, which is not implemented yet."
- All dependencies present → proceed to Step 5.

If the PRD has no dependency content, skip this step.

### Step 5: Execute Phases

For each phase of `plan.md`, in order:

**5.1 — Skip if already done**

Inspect the last ~20 commits on the current branch. If any commit message indicates this exact phase already ran (same feature ID + phase name or ordinal), skip the phase with status `— already committed` and move on. Detection is best-effort: match on feature ID plus normalized phase name or phase index.

**5.2 — Implement**

Read spec.md sections relevant to the phase. Edit/create files to fulfill the phase's steps.

**What counts as "done" for a phase** — all of the following, not just "I wrote the code":

- Every file listed for this phase in spec.md's Component Overview exists and contains the described content.
- Every contract (API, schema, function signature) described for this phase matches what was written.
- Validation in 5.3 passes (hard fails resolved).
- If the phase produces runtime behavior that isn't covered by unit tests (UI pages, server routes, migrations, CLI commands), actually exercise it before claiming done: run the dev server / build / migration / command against a local environment and confirm it behaves. If the environment can't be brought up in this run, log the runtime-check under `Soft-fails` — do NOT silently claim the phase is done.

Writing code without running it is not "done". Declaring completion without meeting the checklist above is a violation of the skill's contract.

Adapt when reality diverges from the spec (column named `pinned` in DB vs `isPinned` in spec, different component file name, slightly different path, structurally compatible types). Specs are never 100% faithful to reality — adaptation is expected. Record every adaptation in a `Deviations` list for the final report. Do NOT abort on minor divergences.

**Abort the entire run only on:**

- Dependency feature missing (usually caught in Step 4; if discovered mid-phase, abort here).
- Hard fail past the retry limit in Step 5.3 below.

Missing external dependencies needed only by *tests* (e.g., `OPENAI_API_KEY` unavailable) do NOT abort the run — they soft-fail the affected test. The implementation code that calls the service is still written.

**5.3 — Validate**

Discover validation commands at runtime: inspect `package.json` `scripts`, or for non-Node stacks inspect the equivalent (`Makefile`, `pyproject.toml`, `Cargo.toml`, `vitest.config.*`, `jest.config.*`). Run the available ones.

- **Hard fail** = non-zero exit from lint, typecheck, or unit tests, where the failure is attributable to code this run changed. Retry up to the configured limit (default 3). Each retry reads the error, adjusts the code, re-runs. After the limit, abort the whole run and go to Step 6.
- **Soft fail** = validation cannot execute in this environment (e2e requiring browser/server not present; integration test requiring an external credential not set; suite explicitly marked non-runnable; command not found). Skip, log under `Soft-fails`, proceed.
- **Pre-existing failure** = validation fails but the failure is not attributable to code this run changed (touched unrelated files, existed on the branch before this run). Log under `Pre-existing failures`, do NOT count against the retry budget, proceed.

Warnings without non-zero exit are never failures.

**5.4 — Commit**

If validation passed (all hard fails resolved; only soft fails and pre-existing failures remain), stage only the files this phase touched and commit with a message summarizing the phase. Match the project's commit style by inspecting the last ~10 commit messages. Fallback: `feat(F<ID>): <phase name>`.

Stage specific files only (no `git add -A` / `git add .`). Commit on the current branch. Do not skip hooks.

If an override disabled commits, skip this sub-step and keep working-tree changes.

**5.5 — Proceed**

Move to the next phase. A run-level abort (hard fail past retry limit, dependency missing mid-phase) stops execution and goes to Step 6 with whatever phases already committed.

### Step 6: Final Verification

After the last phase commits (or when the run aborted), run an independent verification pass over the whole feature before writing the report. This step exists because per-phase checks can miss regressions, and because AI commonly claims "done" when it isn't.

Perform all of the following — no step is optional:

**6.1 — Full-suite validation**

Run the full validation suite on the entire repo (not just touched files): lint, typecheck, and the complete test suite as defined by the project. Do NOT filter to files this run changed.

- If failures appear that weren't flagged per-phase → they count as **regressions**. Attempt to fix up to the retry limit (same as hard-fail policy). If still failing, do NOT declare success — status becomes `completed with regressions` and the failures are listed under `Regressions` in the report.
- Pre-existing failures already logged in Step 5.3 stay categorized as pre-existing; they do not become regressions.

**6.2 — Component Overview walk-through**

Read spec.md's Component Overview (or equivalent file-list section) and, for every file listed, verify: the file exists, its described role is visible in the content, and its contracts (exports, routes, schemas) match the spec within the adaptation rules of Step 5.2.

Any missing file, missing export, or missing contract → add to `Missing from spec` in the report. Do NOT claim success if this list is non-empty.

**6.3 — AC re-check**

For each acceptance criterion loaded in Step 2, locate the test(s) mapped to it via spec.md's Testing Strategy (or equivalent). Run those tests fresh right now (not just trusting that they passed in a prior phase). Mark the AC ✓ only if the test passes in this final re-check. If the test no longer passes → mark ✗, add to `Regressions`, and do not claim success.

ACs without mapped tests remain `—` (no test).

**6.4 — Environment smoke check (when applicable)**

If the feature produces runtime surfaces that per-phase validation couldn't exercise (UI page, HTTP endpoint, migration, CLI command), do one final exercise of each against a local environment (dev server, ephemeral DB, etc.). A quick load-and-interact is enough — the goal is to catch things unit tests don't.

If the environment cannot be brought up in this run, log each skipped smoke check under `Soft-fails` — do NOT upgrade status to `success` unless every smoke check either passed or was honestly soft-failed.

**6.5 — Status decision**

The run's final status is determined by this step, not by whether phases committed:

- `success` — full suite green, every Component Overview item present, every AC's test passes in 6.3, every smoke check passed or soft-failed.
- `completed with regressions` — phases committed but 6.1 or 6.3 uncovered failures that the skill couldn't resolve.
- `incomplete` — `Missing from spec` (6.2) is non-empty.
- `aborted at phase <N>` — run stopped during Step 5 before reaching here.

Never report `success` when any of the checks above has an unresolved failure, even if every phase individually committed clean.

### Step 7: Final Report

Output the report to chat. Status comes from Step 6.5, never from "I think I finished":

```
Feature F<ID> — <name>

Status: success | completed with regressions | incomplete | aborted at phase <N>
Phases: <N> committed / <M> total
Branch: <current-branch>

Acceptance Criteria (re-checked in Step 6.3):
✓ <AC text> (covered by <test name>)
✗ <AC text> (test failed after <K> retries: <error summary>)
— <AC text> (no test covers this AC)

Cross-feature integration (if any):
✓ <criterion> (covered by <test name>)
...

Missing from spec (from Step 6.2):
- <file/export/contract that the spec required and is missing>
...

Regressions (from Step 6.1 or 6.3):
- <test name> started failing during this run: <error>
...

Deviations:
- <what was adapted and why>
...

Soft-fails:
- <what was skipped and why, including runtime smoke checks not exercised>
...

Pre-existing failures:
- <test name>: failed on entry to this run; left as-is
...

Overrides applied:
- Retry limit: 3 → unlimited
...

Overrides ignored:
- "<text>" (reason)
...

Abort reason (if status is aborted): <error>
```

If aborted, the report still lists whatever committed phases achieved and clearly marks which phase failed and why. If `completed with regressions` or `incomplete`, the report makes clear which checks failed so the user knows what to fix.

---

## RULES

**Always:**
- Require `spec.md` + `plan.md` in the target folder; abort without them.
- Locate AC and dependency content in the PRD semantically, never by fixed section number.
- Commit 1 per phase (default), staging only the files that phase touched.
- Match the project's recent commit-message style.
- Adapt to minor spec/code divergences; log every adaptation under `Deviations`.
- Run validation after each phase; differentiate hard-fail (retry ≤ limit) from soft-fail (skip + log) from pre-existing failure (log, don't retry).
- Before claiming a phase is "done": confirm every file listed for that phase exists with the described content AND validation has passed. Writing code without running it is never "done".
- For phases that produce runtime surfaces (UI, HTTP route, migration, CLI), actually exercise them against a local environment before claiming done, or soft-fail the runtime check.
- Execute Step 6 (Final Verification) in full before reporting — full-suite re-run, Component Overview walk-through, AC re-check, environment smoke check.
- Derive the final status exclusively from Step 6.5. Report `success` only when every Step 6 check is green.

**Never:**
- Claim the run is `success` when Step 6 found regressions, missing-from-spec items, or unresolved failures — even if every phase individually committed clean.
- Skip the AC report or its traceability (immutable core).
- Skip Step 6 (Final Verification).
- Create or switch branches.
- Abort on name/path/type cosmetic divergences.
- Abort on external dependency missing for a test — soft-fail the test, keep implementing.
- Use `git add -A` or `git add .`.
- Skip git hooks.
- Count pre-existing test failures against the retry budget.
- Re-run phases already committed on the branch (detected by commit-message match).
- Insert service stubs in production modules — stubs are allowed only in test files.
- Explore the codebase upfront with a broad sweep — read files lazily as phases require.
- Declare a phase complete based only on "I wrote the files". The completion checklist in 5.2 must hold.

---

## Overrides

Free-form instructions at the end of the invocation override defaults. Examples:

- **Retry limit**: `no retry limit`, `max 5 tries`.
- **Autonomy**: `pause between phases` — waits for user reply (`ok`, `continue`, `segue`, `yes`, etc.) after each phase.
- **Commit strategy**: `no commits, just implement`; `single commit at the end`.
- **Validation**: `skip tests`, `skip lint`, `skip typecheck`.
- **Phase selection**: `only phases 1 and 2`, `skip phase 3` — phase positions are ordinal; labels `A/B/C` map to `1/2/3`.
- **External services**: `stub OpenAI`, `assume empty response for missing APIs` — stubs apply ONLY in test code; production modules keep the real call.

Unrecognized or contradictory overrides: default wins; logged under `Overrides ignored`.

**Immutable core**: the AC checklist and its traceability to the PRD cannot be overridden.

---

## Edge Cases

**No PRD found**: abort before starting.

**No spec.md or plan.md**: abort before starting.

**Dependency feature not implemented**: abort at Step 4 with a clear message.

**Ambiguous feature reference**: list candidates, abort asking which.

**Working tree has unrelated changes at start**: proceed anyway — the skill is designed to be invokable anywhere (typically from a worktree). Commits stage only the specific files each phase touched.

**Phase name contains special characters**: fall back to `feat(F<ID>): implement phase <N>`.

**Re-invocation after a partial run**: Step 5.1 detects already-committed phases by commit-message match and skips them. Uncommitted working-tree changes from a prior interrupted run stay as-is; the skill does not clean them up.

**Hard fail past the retry limit on a step that isn't part of any AC**: abort anyway — the skill cannot judge which failures are "acceptable". User can override with `skip tests` or similar.

**External tool emits warnings, not errors**: warnings are not failures. Only non-zero exit codes count.

**Override contradicts the core contract** (e.g., `simplify the spec, drop requirements`): ignore it, log under `Overrides ignored`, proceed with the full spec.

**Validation commands not discoverable**: if `package.json` / config files don't reveal lint/typecheck/test commands, log each missing command under `Soft-fails` and proceed.

**PRD has no AC content for this feature**: proceed with empty AC checklist and note under soft-fails.

**PRD has no dependency content**: skip Step 4 and proceed.

**Commit-message style is inconsistent in recent history**: fall back to `feat(F<ID>): <phase name>`.
