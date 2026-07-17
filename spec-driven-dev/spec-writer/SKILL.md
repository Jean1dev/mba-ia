---
name: spec-writer
description: Generates technical implementation spec and plan for one or more features based on PRD, codebase analysis, and iterative clarification. Supports batch mode for generating multiple features from the same wave in parallel.
---

# Feature Specs Writer

Generate implementation-ready technical specifications based on the project's PRD and existing codebase patterns. The skill has two modes:

- **Single-feature mode (default):** operates on one feature at a time, identified by its PRD feature ID (F01, F02...), with an interactive interview (Steps 1–6 below).
- **Batch mode:** operates on multiple features from the same wave in parallel, auto-accepting all interview recommendations. Activated automatically when the input contains multiple IDs, a wave reference, or a mix. See the **Batch Mode** section near the end of this file.

**Output:** TWO files are required:
1. `spec.md` - Technical specification (7 sections)
2. `plan.md` - Implementation plan (phases and steps)

**Output location:** `docs/<feature-id>-<kebab-name>/spec.md` and `docs/<feature-id>-<kebab-name>/plan.md`
- The `<kebab-name>` is derived from the feature's name in the PRD Section 6 (lowercase, spaces → hyphens, special characters removed). Example: `F03. Video Upload` → `docs/F03-video-upload/`.

---

## Execution Steps (6 Steps)

Note: These are internal agent execution steps. The OUTPUT plan document will have 1-5 phases based on feature complexity.

### Step 1: Resolve Input and Pre-Analysis

**1.1: Identify the PRD and the target feature**

Accept free-form input from the user. The user may reference the feature by ID (`F03`), by name (`Video Upload`), by path (`docs/PRD.md F03`), or any combination. Resolve the reference:

- Locate the PRD file from the user's reference or look for `docs/PRD.md`, `PRD.md`, or similar conventional locations. If multiple plausible PRDs exist, ask the user which one.
- Identify the target feature within the PRD by ID or name.
- If the input is ambiguous (e.g., "upload" matches multiple features), confirm with the user before proceeding.
- If the referenced feature does not exist in the PRD, list available features from Section 8 and ask the user to clarify.

**PRD is mandatory.** If no PRD is found in the project, stop and instruct the user to generate one first with the `prd-writer` skill. Do not fall back to an unstructured interview.

**1.2: Check dependency readiness and Foundation features (greenfield)**

Read the PRD's Section 8 (Dependency Graph). For every feature in the target feature's `Dependencies` column, check whether it appears to be implemented in the codebase (source files exist matching the feature's scope). If any dependency is not yet implemented, warn the user: "F<X> depends on F<Y> (not yet implemented). Continue anyway?" Proceed only if confirmed.

If the PRD contains a **Foundation Features** subsection in Section 8, apply these additional checks based on the implementation state of each Foundation feature:

- **Foundation state detection (the correct greenfield signal):** for each feature listed in Foundation Features, check whether it appears implemented in the codebase by looking for one or more characteristic output files that the feature is supposed to create — for example, an ORM schema or migration file for a database Foundation, a session/middleware module for an auth Foundation, a root layout/template file for a layout Foundation, or any equivalent artifact in the stack being used (web framework, backend service, mobile app, etc.). Do NOT rely on the mere presence of generic project markers such as a source folder or a package/manifest file — any scaffolding tool (`create-next-app`, `rails new`, `django-admin startproject`, etc.) already creates those, yet the PRD's Foundation features may still be unimplemented.
  - **Greenfield** = zero Foundation features are implemented yet.
  - **Partial Foundation** = some Foundation features are implemented, others are still pending.
  - **Foundation complete** = every Foundation feature is implemented.
- **Scenario 1 — greenfield + target feature IS a Foundation feature:** proceed without extra warning. This is the expected path for a greenfield project.
- **Scenario 2 — greenfield + target feature is NOT in Foundation Features:** warn the user: "This appears to be a greenfield project (no Foundation feature is implemented yet). F<target> is not a Foundation feature. Foundation features (F<ID>, ...) set up the shared infrastructure and should be implemented first. Recommend starting with F<first-foundation>. Continue with F<target> anyway?" Proceed only if confirmed.
- **Scenario 3 — Partial Foundation (some Foundation features implemented, others pending) and target is not one of the remaining Foundations:** list the pending Foundation features and warn: "Foundation features F<ID1>, F<ID2>... are not yet implemented. Implementing F<target> before these may create file conflicts in the scaffolding. Continue anyway?" Proceed only if confirmed.
- **Foundation complete (mature codebase for Foundation purposes):** skip all Foundation-specific checks. The normal dependency readiness check above is enough.

**Batch Mode note:** In Batch Mode, the orchestrator performs these dependency and Foundation checks once across the whole batch (B.2 and B.3) and filters features before dispatch. Sub-agents skip every "warn the user / Continue anyway?" prompt in this step — assume the check was already resolved by the orchestrator and proceed.

**1.3: Codebase Pattern Discovery (two layers)**

Explore the codebase before writing the spec (before the interview in single-feature mode; before applying the Auto-Accept Policy in Batch Mode) to extract patterns. This is mandatory whenever the codebase is non-empty — do not wait for the user to provide paths.

**Layer 1 — Baseline (floor, not ceiling):** at minimum, extract observable patterns in these categories. Examples are illustrative across multiple stacks — the categories are the stack-agnostic intent.
- Runtime and language (any — Node, Python, Ruby, Go, Java, .NET, Rust, PHP, etc.)
- Framework and project layout (any — Next.js/Remix, Django/Flask/FastAPI, Rails, Spring, Phoenix, etc.)
- Database and data access (any — Postgres/MySQL/Mongo/SQLite; Prisma/SQLAlchemy/ActiveRecord/GORM/Entity Framework; raw SQL)
- Authentication strategy and library
- API or entry-point style (REST, GraphQL, RPC, CLI, job queue, event handler — whatever the project uses) and response/error format
- Validation approach (typed schemas, runtime validators, manual checks — whatever the codebase prefers)
- Testing framework and style (unit and integration)
- Error handling (exceptions, Result types, error codes, panic/recover, etc.)
- Folder structure and naming conventions

**Layer 2 — Broad exploration (also mandatory):** beyond the baseline, capture any additional pattern you observe that could inform implementation — architectural decisions, codebase idioms, recurring abstractions, logging/observability, config management, deploy conventions, internationalization, accessibility, anything. Do not restrict yourself to the baseline list. A thorough report in a medium project typically has 8-15 patterns.

**1.4: Empty codebase handling**

If the codebase is empty or only has scaffolding (e.g., only `package.json` with defaults, no `src/` implementation yet), skip Layer 1/Layer 2 discovery and instead plan to ask transversal stack questions inline during Step 2 (these questions will only be asked once — on the first feature. Subsequent features will find the answers in the codebase).

**Batch Mode note:** In Batch Mode there is no Step 2 interview. Apply the "Empty codebase bootstrap" row of the Auto-Accept Policy: fall back to industry best practices for the detected stack (or for the scaffolding that exists, if any), and document every bootstrap choice explicitly under the spec's Assumptions/Decisions section.

**1.5: Read the PRD feature data**

Extract the target feature's full definition from the PRD and load it as context for the spec (used by the interview in single-feature mode, and by the Auto-Accept Policy in Batch Mode):
- Feature name and ID
- Consumes block (if present)
- Provides block (if present)
- Core Scope block (if present)
- Full Scope additions block (if present)
- Capabilities
- Experience
- Error Handling (if present)
- Section 9 per-feature acceptance criteria
- Section 9 Cross-Feature Integration criteria that reference this feature (either as the consumer or the provider)

**1.6: Present understanding to the user**

```
Based on my analysis, I understand you want to implement:

**Feature:** F<ID>. <Name>
**Technical Summary:** [1-2 sentences derived from PRD Capabilities + Experience]
**Observed codebase patterns:** [summary of Layer 1 + Layer 2 findings, or "empty codebase — will bootstrap"]
**PRD context loaded:** Consumes, Provides, Core Scope, Full Scope, Capabilities, Experience, Error Handling, acceptance criteria

I need to clarify some technical decisions that the PRD and codebase don't already answer.
```

**Batch Mode note:** Sub-agents skip this step — there is no interactive user to present to. The orchestrator's consolidated plan (B.4) covers shared understanding for the batch.

### Step 2: Interview

**Batch Mode override:** In Batch Mode, this entire step is replaced by the Auto-Accept Policy (see Batch Mode section). Sub-agents skip Step 2 and proceed directly to Step 3 with the Auto-Accept defaults applied. Every "ask the user" instruction below becomes "apply the Auto-Accept default and document the choice in the spec's assumptions".

Interview the user relentlessly about every aspect of this plan until we reach a shared understanding. Walk down each branch of the design tree, resolving dependencies between decisions one-by-one. For each question, provide your recommended answer.

Ask the questions one at a time.

If a question can be answered by exploring the codebase or reading the PRD, explore or read instead of asking.

**Scope question (ask first, when applicable):** If the feature has both `Core Scope` and `Full Scope additions` blocks in the PRD, ask: "Should the spec cover Core Scope only, or Core + Full Scope additions?". If only one of the blocks is present, or neither is present, skip this question and assume the full feature scope.

**Anti-redundancy rule:** Do NOT ask about anything already observable in:
- The PRD's feature definition (Consumes, Provides, Core Scope, Capabilities, Experience, Error Handling)
- The PRD's acceptance criteria for this feature
- The codebase patterns discovered in Step 1.3
- A previously generated `spec.md` or `plan.md` for another feature in the same project (when those exist and are relevant)

Focus the interview on decisions the PRD and codebase **do not** already answer: internal architecture, database schema details (columns, indexes, constraints), endpoint signatures, validation rules not specified in Capabilities, naming of new files, choice between libraries when patterns aren't established, edge cases not covered by Error Handling.

**Partial PRD specifications:** When the PRD mentions a capability but omits a specific detail (e.g., "chunked upload" without chunk size), ask for the missing detail rather than assuming a default.

**Empty codebase bootstrap:** If Step 1.4 flagged empty codebase, ask transversal stack questions inline during this step (framework, ORM, auth, API style, validation, testing, error handling, folder structure). Once the first feature is implemented, the codebase becomes the reference for subsequent features.

### Step 3: Summary and Assumptions

After receiving answers:
- Summarize technical decisions made
- List assumptions derived from PRD, codebase patterns, and interview answers
- Explicitly note which PRD blocks informed which parts of the spec (traceability)

**Batch Mode note:** In Batch Mode there are no interview answers. Treat each Auto-Accept default that was applied as if it were an interview answer — list it under assumptions, name the policy row that produced it, and flag it so the user can review and override later. Traceability to PRD blocks works the same way as in single-feature mode.

### Step 4: Generate Documents

**Announce:** "Generating TWO documents: SPEC and PLAN..."

**Scaling guidance by complexity:**
- trivial: 1-2 phases, 2-4 steps
- simple: 2-3 phases, 5-8 steps
- medium: 3-4 phases, 10-15 steps
- complex: 4-5 phases, 15-25 steps

Note: SPEC document depth (schemas, indexes, migrations) scales with complexity. PLAN steps are always high-level regardless of complexity.

**4.1: Generate SPEC**:
- Scale sections based on COMPLEXITY_LEVEL:
  - trivial/simple: Skip API Contracts and Data Model if not applicable
  - medium/complex: All 7 sections required
- Scale depth within sections based on complexity
- Include JSON examples, SQL migrations, test specifications
- **If FEATURE_CROSS_CUTTING exists:** Include integrated cross-cutting concerns in the Scope section:
  ```
  **Included:**
  - Core feature functionality
  - Integrated from cross-cutting concerns:
  ```

**PRD → SPEC mapping (apply consistently across all specs):**

| PRD block | Spec.md destination |
|-----------|---------------------|
| Consumes | Scope (input contracts) + API Contracts (when the input arrives via API) |
| Provides | Scope (output contracts) + API Contracts (when the output is exposed via API) |
| Core Scope | Scope → "Included" |
| Full Scope additions | Scope → "Deferred" (when user picked Core only) or "Included" (when user picked Core + Full) |
| Capabilities | Requirements / Business Rules |
| Experience | Requirements / UX Flows |
| Error Handling | Error Handling section |
| Section 9 per-feature acceptance criteria | Testing Strategy → acceptance tests |
| Section 9 Cross-Feature Integration criteria (referencing this feature) | Testing Strategy → integration tests |

**4.2: Generate PLAN**:
- Prerequisites section
- Phases with numbered steps (1-3 sentences each, high-level)
- Describe WHAT to do, reference spec for HOW

Use the following template to generate the files: `references/feature-template.md`

**Announce:** "Both documents ready. Proceeding to save..."

### Step 5: Validate and Save

**Validate before saving:**

SPEC document:
- [ ] Required sections present (all 7 for medium/complex, skip API/DB if N/A for trivial/simple)
- [ ] Component overview has complete file paths
- [ ] API contracts have JSON examples (if included)
- [ ] Data model has column types, indexes, constraints (if included)
- [ ] Testing strategy has specific test functions
- [ ] PRD blocks mapped correctly per the PRD → SPEC table
- [ ] Consumes/Provides from PRD are reflected in Scope or API Contracts
- [ ] Cross-Feature Integration criteria from PRD Section 9 that reference this feature appear as integration tests

PLAN document:
- [ ] Numbered steps across phases
- [ ] Format: **N. Component** - High-level paragraph (1-3 sentences)
- [ ] Steps describe WHAT, not HOW (spec has details)

**Save both files to `docs/<feature-id>-<kebab-name>/spec.md` and `docs/<feature-id>-<kebab-name>/plan.md`.** Create the folder if it doesn't exist. Verify both files with the Read tool.

### Step 6: Output Result

Inform the path of the spec and plan files, the complexity level of the feature, and how many phases are in the plan.

---

## Batch Mode

Generate specs for multiple features of the same wave in parallel, auto-accepting all interview recommendations. This mode is a thin orchestration wrapper on top of Steps 1–6: sub-agents run the full single-feature flow; the orchestrator only resolves input, validates, dispatches, and reports.

### Activation

The skill enters Batch Mode automatically when the input matches any of these shapes:
- Multiple feature IDs: `F01 F02 F03`
- Wave reference: `wave 3`
- Mix within the same wave: `wave 3 F04`
- Multiple feature names, or names mixed with IDs, as long as all resolve to the same wave

Single-feature input (e.g., `F03`, `Video Upload`) continues to use the interactive flow (Steps 1–6).

### Same-wave rule

All features in a single batch must belong to the same wave (per PRD Section 8).

- Cross-wave input (e.g., `wave 3 wave 4`, or `F04 F05` where F04 is wave 3 and F05 is wave 4) is rejected. Message: "Features from different waves cannot be generated in the same batch. Later-wave specs are richer when generated after earlier waves are implemented, so the codebase has more patterns to observe. Run wave N first."
- Mixing `wave N` with extra feature names/IDs is allowed only if every listed feature belongs to wave N. Any outlier triggers the same rejection.
- Unknown wave number → reject, listing available waves from Section 8.
- Unknown feature ID/name → reject, listing available features.

### Orchestration flow

Step 1 (Resolve Input and Pre-Analysis) is adapted for the batch context as described below. Steps 2–6 are NOT executed by the orchestrator — they run inside each sub-agent, one per feature, per the Auto-Accept Policy.

**B.1: Resolve the batch**

- **Locate the PRD** using Step 1.1 rules (user-provided path, `docs/PRD.md`, `PRD.md`, or similar). If no PRD is found, stop and direct the user to `prd-writer`. If multiple plausible PRDs exist, ask the user which one BEFORE continuing — this is the first possible interactive pause in the orchestrator.
- Parse input into a list of target features (expand waves, merge lists, deduplicate).
- If the PRD has no `Execution Waves` subsection in Section 8 and the input references a wave (e.g., `wave 3`), reject with: "Wave references require a 'Execution Waves' subsection in Section 8 of the PRD, which this PRD does not have. Use feature IDs directly or update the PRD." Do not attempt to synthesize waves.
- If any feature name in the input is ambiguous (matches multiple features in the PRD, e.g., "upload" matches F03 and F11), list the candidates to the user and ask for disambiguation BEFORE proceeding to the rest of B.1. This is the second possible interactive pause before the consolidated plan.
- If any feature ID or name does not exist in the PRD, reject with the list of available features.
- Validate the same-wave rule.
- For each target, check whether `docs/<feature-id>-<kebab-name>/spec.md` already exists. Mark such features as "already has spec".

**B.2: Greenfield and Foundation classification**

Apply the Foundation state detection from Step 1.2 once for the whole batch. Classify each target feature as:
- **Foundation, not implemented** → must run sequentially (shared scaffolding prevents parallelism).
- **Non-Foundation, or Foundation already implemented** → eligible for the parallel pool.

**B.3: Dependency readiness**

For each target feature, check its PRD dependencies (Section 8). If a dependency is not implemented AND is not itself in the current batch, mark the feature as "dependency missing — will abort". Dependencies satisfied by other features in the same batch are acceptable (they'll be spec'd together; implementation order is the user's decision).

**B.4: Present consolidated plan and await confirmation**

Show the plan and await explicit confirmation. Default template:

```
Batch plan for <input>:
- F04 Video Library (Core only) — new
- F07 Background Processing Pipeline (full scope) — already has spec (skip / regenerate?)
- F12 Administration Panel (full scope — no Core/Full split) — new

Mode: parallel (N sub-agents)   # or "sequential (Foundation detected)" when applicable
Codebase state: Foundation complete   # or greenfield / Partial Foundation
Auto-accept: all spec-writer recommendations will be applied
Destination: docs/F04-video-library/, docs/F07-background-processing-pipeline/, docs/F12-administration-panel/

OK to proceed? (yes/no)
```

Per-feature scope tag (choose the right one per PRD shape):
- `(Core only)` — feature PRD has both `Core Scope` and `Full Scope additions` blocks (Auto-Accept picks Core).
- `(full scope)` — feature PRD has only one of the scope blocks, so Core and Full are the same.
- `(full scope — no Core/Full split)` — feature PRD has neither block; entire feature is in scope.

Per-feature status tags: `new`, `already has spec (skip / regenerate?)`, `dependency missing — will abort`, `Foundation, will run sequentially`, `already implemented (Foundation), skipping`.

Proceed only on explicit "yes". On "no" or any negative/ambiguous response, abort cleanly without dispatching sub-agents and without creating any files. If the user wants to change the plan, they re-invoke the skill with updated input. Features marked "already has spec" are skipped by default; the user can request regeneration in the confirmation response (e.g., "yes, regenerate F07").

**B.5: Dispatch sub-agents**

- **Sequential phase (Foundations only, when greenfield or Partial Foundation):** dispatch Foundation sub-agents one at a time, waiting for each to complete before starting the next, in the order they appear in PRD Section 8.
- **Parallel phase:** dispatch all remaining sub-agents in a single message with multiple Agent tool calls, no concurrency cap.
- Each sub-agent prompt includes:
  - The target feature ID and the PRD path
  - Instruction to execute Steps 1–6 of this SKILL.md for that feature
  - The Auto-Accept Policy below, replacing the interactive interview (Step 2)
  - Reminder to save `spec.md` and `plan.md` per Step 5

Each sub-agent performs its own Pattern Discovery (Step 1.3) independently — no sharing between sub-agents.

**B.6: Collect and report**

Wait for all sub-agents. Report consolidated result:

```
Batch complete: 3/4 features generated successfully
✓ F04 → docs/F04-video-library/
✓ F07 → docs/F07-background-processing-pipeline/
✓ F12 → docs/F12-administration-panel/
✗ F05 → failed: <reason>
```

Sub-agent failures are isolated — other sub-agents continue. Failed features can be re-run individually.

### Auto-Accept Policy

Each sub-agent skips the interactive interview (Step 2) and applies these defaults for the decisions the interview would have surfaced:

| Decision | Default |
|---|---|
| Scope (Core vs Core+Full, when both blocks exist) | Core only |
| Technical decisions with a clear recommendation from spec-writer | Apply the recommendation |
| Dependency not yet implemented (Step 1.2 warning) | Orchestrator handles in B.3 — sub-agent never receives a feature with an unmet external dependency; skip the Step 1.2 warning entirely |
| Greenfield Foundation warnings (Step 1.2 Scenarios 2/3) | Orchestrator handles in B.2 — sub-agent skips these scenarios |
| Feature requires new technology not present in the codebase | Auto-confirm; document the new dependency in the spec's decisions/assumptions |
| Multiple conflicting patterns in the codebase | Pick the most frequent (or most recent when tied); document the choice |
| Ambiguous feature reference | Cannot occur — orchestrator asks the user to disambiguate in B.1 before dispatch |
| Empty codebase bootstrap (Step 1.4) | Fall back to industry best practices for the detected stack; document assumptions explicitly |
| Partial PRD specifications (Step 2 — capability mentioned but a technical detail omitted, e.g., "chunked upload" without chunk size) | Apply an industry-standard default for the missing detail; document it as an explicit assumption in the spec. Do NOT block. |
| Description too vague (feature definition leaves many decisions open) | Apply best-practice defaults for each open decision and document them as explicit assumptions in the spec; never silently infer |
| No codebase patterns found (codebase non-empty but Pattern Discovery returned nothing) | Fall back to industry best practices for the detected stack; document as an explicit assumption |

All other spec-writer rules (PRD-driven content, codebase pattern adherence, SPEC/PLAN validation, kebab-case naming, file structure) apply unchanged.

**Documentation requirement:** every time a sub-agent applies an Auto-Accept default for a decision the PRD did not answer, it MUST record that decision under an "Assumptions" or "Decisions" subsection of the spec, so the user can review and correct later.

---

## Rules

**Precedence:** When a feature is running in Batch Mode, the `(Batch Mode)` rule groups below override any conflicting rule in the general `Always`/`Never` lists — notably, Batch Mode overrides the interview-related rules ("Preserve the iterative interview style", "Skip interview questions...", etc.). All non-conflicting rules still apply.

**Always:**
- Generate TWO files (spec and plan) in `docs/<feature-id>-<kebab-name>/`
- Validate both documents before saving
- Run Codebase Pattern Discovery in two layers (baseline + broad) before the interview
- Read the target feature from the PRD and use Consumes/Provides/Core Scope/Full Scope/Capabilities/Experience/Error Handling/acceptance criteria as primary context
- Skip interview questions whose answers are already in the PRD, the codebase, or previous specs
- Apply the PRD → SPEC mapping consistently across all features
- Preserve the iterative interview style: one question at a time, walk down the decision tree, provide a recommended answer

**Never:**
- Put actual code in spec (describe structure only)
- Put architecture decisions in plan
- Include time estimates
- Create testing phases in plan document
- Include Feature ID/Date/Version metadata
- Include implementation details in plan steps (data types, columns, methods)
- Proceed without a PRD — always require one and direct the user to `prd-writer` if absent
- Re-ask questions whose answers are observable in the codebase or already stated in the PRD
- Restrict codebase exploration to the baseline checklist — the baseline is a floor, not a ceiling

**Always (Batch Mode):**
- Validate the same-wave rule before dispatch; reject cross-wave batches
- Present a consolidated plan and await explicit confirmation before dispatching sub-agents
- Skip features whose `spec.md` already exists unless the user explicitly requests regeneration
- Run Foundation features sequentially when the codebase is greenfield or Partial Foundation
- Apply the Auto-Accept Policy inside each sub-agent instead of running the interactive interview

**Never (Batch Mode):**
- Mix features from different waves in the same batch
- Dispatch Foundation features in parallel when any Foundation is still unimplemented
- Cancel running sub-agents because another sub-agent failed
- Share a single Pattern Discovery across sub-agents — each runs its own

---

## Edge Cases

**Batch Mode precedence:** In Batch Mode, any edge case below that instructs the sub-agent to "ask the user", "confirm with the user", or "go deeper in the interview" is overridden by the corresponding row of the Auto-Accept Policy (Batch Mode section). Sub-agents never pause to ask; orchestrator-level edge cases ("Multiple PRD files", "Ambiguous feature reference", dependency warnings) are resolved once in B.1–B.3 before dispatch.

**No PRD found:** Stop and instruct the user to generate one first with `prd-writer`. Do not run the skill without a PRD.

**Feature not found in PRD:** List the available features from PRD Section 8 and ask the user which one was intended.

**Ambiguous feature reference:** If the user's input matches multiple features (e.g., "upload" matches F03 and F11), list the candidates and ask the user to disambiguate.

**Multiple PRD files in the project:** Ask the user which PRD to use.

**Dependency not yet implemented:** Warn the user (e.g., "F08 depends on F07, which is not yet implemented. Continue anyway?") and proceed only if confirmed. The spec can still be generated — implementation order is the user's decision.

**Empty/scaffolded-only codebase (first feature):** Skip Pattern Discovery and ask transversal stack questions inline in Step 2. Subsequent features will read the codebase instead.

**PRD has no Core Scope / Full Scope blocks for the feature:** Skip the scope question; assume full feature scope.

**PRD only has Core Scope (no Full Scope additions):** Assume scope = Core; do not ask.

**Description too vague:** If the PRD's feature definition is unusually thin and leaves many decisions open, go deeper in the interview — do not assume defaults silently.

**No codebase patterns found (but codebase non-empty):** Ask the user to confirm using industry best practices or provide a reference.

**Feature requires new technologies not present in the codebase:** List the new dependencies, ask the user to confirm, document in decisions.

**Multiple conflicting patterns in the codebase:** Present both, ask which to follow, document the choice.

**Sanitizing feature name to kebab-case:** lowercase the name, replace spaces with hyphens, strip characters outside `[a-z0-9-]`. Example: `F07. Background Video Processing Pipeline` → `F07-background-video-processing-pipeline`.

**Cross-wave batch input:** Reject with a message pointing to Section 8 of the PRD and explaining that waves run sequentially so the codebase accumulates patterns between waves. Do not auto-split into two batches — the user should run the earlier wave first, implement it, then run the next.

**Unknown wave reference:** List available waves from PRD Section 8 and ask the user to clarify.

**Batch contains a feature already spec'd:** The consolidated plan flags it as "already has spec"; default is skip. User can request regeneration explicitly in the confirmation response.

**Batch contains a feature whose external dependency is not implemented:** Mark the feature as "dependency missing — will abort" in the plan; generate specs for the remaining features and report the aborted one in the final result. Dependencies satisfied by another feature in the same batch do not count as missing.

**Batch with multiple Foundation features in a greenfield project:** Foundations run sequentially in the order they appear in PRD Section 8. The plan states this explicitly ("Mode: sequential (Foundation detected)"). Non-Foundation features in the same batch still run in parallel after the Foundations finish.

**Sub-agent failure in batch:** Other sub-agents continue to completion. Final report lists successes and failures with reasons. Failed features can be re-run individually or as a smaller batch.

**PRD without "Execution Waves" subsection in batch mode:** Wave references (`wave N`) require this subsection to expand into features. Reject with: "Wave references require a 'Execution Waves' subsection in Section 8 of the PRD. This PRD does not have one. Use feature IDs directly or update the PRD." Do not attempt to synthesize waves.

**User declines the consolidated plan (responds "no" at B.4):** Abort cleanly. No sub-agents dispatched, no files created, no partial state left behind. User re-invokes the skill with adjusted input.
