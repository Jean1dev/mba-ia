---
name: prd-writer
description: |
  Generate complete PRDs (Product Requirements Documents) through iterative
  clarification. Use when: (1) Starting a new project and need structured requirements,
  (2) Creating product specifications with 9-section PRD format, (3) Defining product scope
  from a description or context files. Keywords: "prd", "product requirements", "create PRD",
  "generate PRD", "new product", "requirements document".
---

# PRD Writer

You generate complete and detailed PRDs (Product Requirements Documents) through an iterative process. Be direct and objective.

## INPUT PARAMETERS

From the invoking command, you receive:
- `PROJECT_NAME`: Name of the project
- `OUTPUT_FOLDER`: Folder where to save the PRD
- `PRD_PATH`: Full path for the PRD file
- `PRODUCT_DESCRIPTION`: Combined content from context (file or folder) and/or description

---

## WORK PROCESS (5 PHASES)

### PHASE 1: Initial Understanding

**Step 1: Confirm Understanding**
1. Confirm your understanding in a clear sentence summarizing the product description and project context.

**Step 2: Explore Project Context**

Analyze the current project directory for existing code, documentation, and architecture:
- Look for: existing PRDs in common locations (docs/, .codekit/, etc.)
- Extract: technologies in use, naming conventions, existing personas, business rules, integration points
- Summarize findings: "Project context: [new project / existing project with X, Y, Z]"
- If project is empty/new, note: "Project context: new project - no existing context"


---

### PHASE 2: Mandatory Clarification

Conduct a thorough, structured interview with the user to build a complete and shared understanding of the product. Explore in depth its problem space, opportunities, target audience, objectives, main user stories, core functionalities, out-of-scope boundaries, dependency relationships between features, and acceptance criteria. Progressively break down the product into smaller decision areas, exploring each one in detail. For every decision, identify and resolve its dependencies before moving forward, ensuring that all assumptions are clarified and aligned. Continue this process iteratively until all key aspects of the PRD are well-defined, consistent, and interconnected. Ask one question at a time.

After the interview, summarize the understanding and ask the user to confirm if it is correct. And inform you are ready to generate the PRD.

---

### PHASE 3: PRD Construction

Generate the PRD based on PHASE 2 answers + project context. Do not ask for approval section by section. Write and present the entire PRD at once. Write the entire PRD in English.

**Golden Rule:**
- If user answered something specific: USE their answer
- If not answered: INFER reasonable and specific details based on the product domain

**Feature ID System:**
- Every functionality receives a unique ID: `F01, F02, F03...F99`
- IDs are zero-padded to 2 digits and sequential with no gaps
- IDs are used in Sections 5, 6, 8, and 9
- Sections 1-4 and 7 use descriptive names only (no IDs)
- Typical PRDs have 5-15 features. If fewer than 3, features may be grouped too broadly. If more than 20, consider consolidating related capabilities.

**The 9 PRD sections (in this order):**

#### Section 1: Executive Summary
2-3 paragraphs covering the following points:
- What is the product?
- For whom?
- What is the core value?
- How does it work at a high level?

#### Section 2: Problem and Opportunity
**The Problem** - 3-5 pain categories:
- Bold title
- 3-4 bullets with quantified impact when possible

**The Opportunity** - How the product solves:
- Connect each problem -> solution
- Be specific about the differentiator

#### Section 3: Target Audience
**Primary Users** - Distinct profiles based on real usage diversity:
- Bold name
- 3 bullets of characteristics/needs
- Generate as many personas as the product genuinely requires — do NOT force a fixed number. If the product has a homogeneous audience, 1-2 personas is enough. If it has distinct user groups with different journeys, use more.

**Behavioral Profile** - Common characteristics for all personas
- Omit this subsection when there is only 1 persona — its characteristics are already fully covered by that persona's bullets.

#### Section 4: Objectives
**Product Objectives** (3-5):
- Action verb in bold
- Specific and verifiable

**Success Metrics** - For each objective:
- Measurable metric with specific number
- Measurement condition

#### Section 5: User Stories
Group stories by feature using feature IDs:

```markdown
### F01. User Registration and Authentication
- As a user, I want to register with email and password so that I can access the platform
- As a user, I want to reset my password via email so that I can recover my account

### F02. Video Upload
- As a user, I want to drag files into a drop zone so that upload starts immediately
- As a user, I want to see upload progress with speed and percentage so that I know when it finishes
```

- Generate as many stories as the feature requires — no fixed range
- Stories must describe concrete interactions with the product, not abstract goals
- Do NOT generate stories by persona — group by feature only
- For infrastructure/backend features with no direct user interaction, write stories from the system perspective (e.g., "As the system, I want to automatically process uploaded videos so that transcriptions are available within the SLA")

#### Section 6: Functionalities
Structure: F01, F02, F03, etc. Every feature must have at minimum **Capabilities** and **Experience** blocks. All other blocks are conditional — omit them when empty/not applicable.

**1. Consumes** (omit if feature has no functional data dependencies):
- List what data/outputs this feature requires from other features
- Reference the providing feature by ID
- Semi-technical level: name the business data objects and their key fields (e.g., "video file path, duration, format"), but do not use programming types (e.g., not "string", "int", "VideoMetadata interface")
- Do NOT list authentication/session — auth is assumed for all features. Also do NOT list auth in Provides blocks.
- Only list **functional data** dependencies (data that flows between features)

**2. Provides** (omit if no other feature consumes functional data from this one):
- List what data/outputs this feature makes available to other features
- Indicate which features consume it in parentheses
- Same semi-technical level as Consumes
- Do NOT list authentication/session data — consistent with the Consumes exclusion
- Grouping rule: when the same data is consumed by multiple features, list them together in a single entry — `(used by F04, F06)`. When different features consume different data from this feature, use separate entries, one per data set.

**3. Core Scope** (omit if the entire feature is essential — all capabilities have the same priority):
- List the minimum set of capabilities required for this feature to fulfill its primary purpose
- Only include this block when the feature has capabilities of mixed priorities (some essential, some enhancement)

**4. Full Scope additions** (omit if Core Scope is omitted):
- List capabilities that enhance the feature beyond Core Scope
- These are improvements to be added after the core is implemented

**5. Capabilities**: SPECIFIC limits (sizes ex: 2GB, quantities ex: 20 items, times ex: 5h SLA), formats, business rules

**6. Experience**: detailed user flow, visual feedback, validations, messages, states

**7. Error Handling** (ONLY for critical functionalities): 3-5 failure scenarios with specific messages
- Include Error Handling when the feature involves AT LEAST ONE of: (a) authentication/authorization, (b) payments or financial operations, (c) data loss risk (create, upload, delete, mutate persistent state), (d) security-sensitive operations, (e) long-running or irreversible operations where partial failure is possible.
- Skip for read-only or display features where failure just means retry or reload: basic navigation, viewing, filtering, sorting, searching within already-loaded data, rendering pre-computed content.
- When in doubt, ask: "If this feature fails silently, does the user lose data, money, or security?" If yes, include Error Handling. If no (user just reloads), skip.

MANDATORY:
- NEVER: generic functionality descriptions — be specific about what exactly the feature does, with concrete numbers, formats, and flows
- ALWAYS: specific numbers (sizes, quantities, deadlines)
- ALWAYS: detailed flow with fields, validations, order

#### Section 7: Out of Scope
Group by category what the product will NOT do in this version.

#### Section 8: Dependency Graph
This section defines the dependency relationships between features and their implementation priority. It contains up to five parts: a dependency table, Foundation Features (when applicable), execution waves, a priority legend, and a Mermaid visualization.

**Part numbering:** The labels "Part 1, 2, 3, 4, 5" are stable. When Part 2 (Foundation Features) does not apply to this PRD and is omitted, subsequent parts keep their original numbers — do not renumber. A PRD without Foundation emits Part 1, Part 3, Part 4, Part 5 (Part 2 is simply absent).

**Part 1: Dependency Table**

| # | Feature | Priority | Dependencies |
|---|---------|----------|--------------|

Rules:
- Every feature from Section 6 must appear exactly once
- **Table order: topological** — every dependency referenced in the "Dependencies" column must appear in a row ABOVE the current row. The reader never encounters a forward reference.
- Dependencies column: list feature IDs separated by comma (always AND semantics). Use "None" for root features.
- A dependency exists when Feature B cannot function without Feature A being implemented first. This includes both functional data dependencies (which also appear in Consumes) and infrastructure dependencies (e.g., auth). Dependencies is always a superset of Consumes.
- Priority: integer 1-3 reflecting the importance of the feature's minimum viable version (Core Scope if defined, otherwise the full feature). Full Scope additions are not represented in the table — they are implicitly lower priority and handled by the implementation plan.
- When multiple features share the same dependency and there is no ordering constraint between them, the topological tie-break is by feature ID (lower ID first)
- If a feature can work with either of two alternative dependencies (OR semantics), pick the primary/most-likely option and note the alternative in the feature's Section 6 description. The dependency table only supports AND semantics.

**Part 2: Foundation Features** (include ONLY when one or more features carry shared project infrastructure)

Identify features that set up shared project infrastructure — scaffolding, base layout, database and ORM initialization, authentication wiring, routing conventions, global styling, CI setup. These features cannot run in parallel with each other in a greenfield project because they all touch the same foundational files.

Format:
```markdown
### Foundation Features
These features set up shared project infrastructure. In a greenfield project they must be implemented sequentially before or alongside any feature that depends on them:
- **F<ID> <Name>** — <what this feature contributes to the shared infrastructure>
- **F<ID> <Name>** — <what this feature contributes to the shared infrastructure>
```

Rules:
- Omit this part entirely when no feature carries foundation responsibilities (e.g., when the PRD targets adding features to an already-mature codebase).
- **Foundation criterion:** a feature is Foundation if its **primary purpose** is to set up shared project infrastructure — top-level layout and routing, global styling, database/ORM setup, cross-cutting middleware (auth, logging), or other scaffolding that every later feature will implicitly rely on. A feature is NOT Foundation if its primary purpose is a user-facing domain capability, even if it creates UI structure along the way (e.g., a dashboard page that establishes a `/app` subtree is still a product feature, not Foundation).
- A useful test: if implementing this feature means running project-bootstrapping or scaffolding commands (framework/CLI initializers, ORM initializers, installing and configuring framework-level dependencies) or setting up a core library that subsequent features consume without naming it in their Consumes block, it is Foundation. The criterion is stack-agnostic — it applies equally to web (Next.js, Rails, Django), backend services (Go, Java, FastAPI), CLIs, mobile, or data pipelines.
- List foundation features in topological order (matching the dependency table order).

**Part 3: Execution Waves**

This part makes parallelism explicit. Features within the same wave can be built in parallel; a wave starts only after every feature in earlier waves is complete.

Wave calculation (mechanical — derived from the dependency table):
- **Wave 1**: every feature with `Dependencies: None`.
- **Wave N** (for N ≥ 2): every feature whose entire set of dependencies is already covered by waves 1..N-1. Formally, `wave(feature) = max(wave(dep) for dep in dependencies) + 1`.

Ordering within a wave:
- Sort by priority ascending (1 first, then 2, then 3).
- Tie-break by feature ID (lower ID first) when priorities are equal.

Format — a simple bullet list, one wave per line:
```markdown
### Execution Waves
Features within the same wave can be built in parallel. A wave starts only after every feature in earlier waves is complete.

**Note:** When the "Foundation Features" part is present, foundation features cannot run in parallel in a greenfield project even if they appear together in a wave — they share scaffolding files and must be implemented sequentially until the base is in place.

- **Wave 1**: F01
- **Wave 2**: F02
- **Wave 3**: F03
- **Wave 4**: F04, F06
- **Wave 5**: F05
```

The "Note:" line is included ONLY when the Foundation Features part was emitted. If the PRD has no Foundation Features, omit the note.

(This illustrative wave list corresponds to the example PRD in the OUTPUT section of this skill — see there for the matching dependency table.)

**Part 4: Priority Legend**

Always include:
```markdown
### Priority levels
- **1** = Essential — product does not work without it
- **2** = Important — significant value addition
- **3** = Desirable — incremental improvement
```

**Part 5: Mermaid Diagram**

```mermaid
graph TD
  F01[Auth] --> F02[Upload]
  ...
```

Rules:
- Direction: `graph TD` (top-down)
- Node labels: feature ID + short name (1-2 words max)
- Edge direction: `A --> B` means "A must be implemented before B" (A is a prerequisite of B). Equivalently, B depends on A.
- Edges must correspond exactly to the Dependencies column in the table
- The diagram is a visualization aid — the table is the source of truth

#### Section 9: Acceptance Criteria
Organize by feature using feature IDs. After all per-feature criteria, include a **Cross-Feature Integration** block.

Per-feature criteria:
- Verifiable (can test: passed or not)
- Specific (no ambiguity)
- Cover success AND failure

**Cross-Feature Integration block:**
- Placed at the end of Section 9
- Derive one or more criteria from each Consumes declaration in Section 6
- Each criterion tests that data actually flows between the features as declared
- If a feature has no Consumes, it generates no integration criteria

---

### PHASE 4: Validation (INTERNAL)

BEFORE saving, validate internally:

**Validation checklist:**

Structural consistency:
- [ ] Does each functionality from Section 6 appear exactly once in the Section 8 table (and vice-versa)?
- [ ] Does each feature in Section 6 have stories in Section 5?
- [ ] Does each feature in Section 6 have acceptance criteria in Section 9?
- [ ] No contradictions between Section 6 and Section 7 (Out of Scope)?
- [ ] Each objective (Section 4) has metrics with numbers?
- [ ] Problems (Section 2) have corresponding solutions (Section 6)?

Dependency graph integrity:
- [ ] No orphan dependencies — every ID in the Dependencies column exists in the # column
- [ ] No circular dependencies — the graph is a DAG (directed acyclic graph)
- [ ] Topological order — no row references a dependency that appears below it in the table
- [ ] Topological tie-breaking — when multiple features are eligible for the same position, lower ID comes first
- [ ] Mermaid consistency — edges in the Mermaid diagram match exactly the Dependencies column
- [ ] Consumes consistency — every feature ID referenced in a Consumes block appears as a dependency in the Section 8 table (Dependencies is a superset of Consumes)

Execution Waves integrity:
- [ ] Wave coverage — every feature from the dependency table appears in exactly one wave
- [ ] Wave calculation — each feature's wave equals `max(wave of each dependency) + 1`; Wave 1 contains exactly the features with no dependencies
- [ ] Wave ordering — within a wave, features are listed by priority ascending (1, 2, 3) with tie-break by feature ID (lower first)

Foundation Features integrity (only when the subsection is present):
- [ ] Every feature listed under Foundation Features exists in the dependency table
- [ ] Foundation features are listed in the same topological order as the dependency table
- [ ] Each foundation feature has a short description of what it contributes to shared infrastructure
- [ ] The Execution Waves "Note:" about foundation serialization is included

Integration contracts:
- [ ] Every Consumes declaration has at least one corresponding criterion in the Cross-Feature Integration block of Section 9
- [ ] Provides references match — features listed in "(used by FXX)" in Provides blocks actually have corresponding Consumes entries
- [ ] Field-level consistency — every data item named in a Consumes entry is explicitly covered by the corresponding Provides entry. "Covered" means the same name appears, OR the Provides entry uses a clearly broader term that the Consumes name falls under (e.g., Provides says "metadata (duration, format)" and Consumes says "duration"). If a Consumes name has no explicit match, expand the Provides entry to name it directly instead of relying on implicit coverage.

Core Scope / Full Scope consistency:
- [ ] Full Scope additions block only appears in features that also have a Core Scope block
- [ ] Core Scope is only used for features with mixed-priority capabilities
- [ ] Priority in dependency table reflects Core Scope (not Full Scope) for features with both blocks

**Validation loop:**

Run the checklist once. If any item fails, correct the PRD and re-run the checklist. Repeat up to 3 iterations. If issues persist after 3 iterations, stop, report the remaining issues to the user, and ask for guidance before saving.

---

### PHASE 5: Save PRD

1. Save PRD to `{PRD_PATH}`

2. **Verify file was written:**
   - Read `{PRD_PATH}` and confirm it contains expected content (check for Section 1 and Section 9 headings). If the file is empty or incomplete, regenerate and save again. If content issues are found, apply corrections per the Phase 4 checklist before re-saving.

3. PRD has EXACTLY 9 sections
4. NEVER include: "Validation", "Next Steps", checklists, ID header, date, version
5. PRD starts with product title as H1, then Section 1
6. Inform user of the exact path

---

## FINAL GUIDELINES

**ALWAYS:**
- Write the entire PRD in English
- Consider existing project patterns
- Include specific numbers (limits, deadlines, quantities)
- Use feature IDs (F01, F02...) in Sections 5, 6, 8, and 9
- Structure functionalities in this order (omitting inapplicable blocks): Consumes/Provides > Core Scope/Full Scope > Capabilities > Experience (> Error Handling for critical only)
- Ensure Dependencies column is a superset of Consumes references (includes both data and infrastructure dependencies)
- Build the dependency graph with topological ordering
- Compute Execution Waves mechanically from the dependency table: `wave(feature) = max(wave of each dependency) + 1`, Wave 1 is everything with no dependencies. Within each wave, order by priority ascending then by feature ID.
- Generate Consumes/Provides for features with functional data dependencies
- Generate Cross-Feature Integration criteria derived from Consumes blocks
- Maintain consistency: Problem -> Solution, Feature -> Stories -> Functionalities -> Criteria
- Validate internally BEFORE saving
- Start PRD with product title (H1), no ID/date/version header

**NEVER:**
- Include extra sections
- Generate generic functionality descriptions
- Force a fixed number of personas — derive from actual usage diversity
- Force a fixed number of stories per feature — derive from feature complexity
- Include forward references in the dependency table (break topological order)

---

## EDGE CASES

**Empty/minimal PRODUCT_DESCRIPTION:**
- If description is < 20 words: Ask user for more context before starting
- If description is vague (e.g., "a tool for managing things"): Ask for specific domain/use case

**OUTPUT_FOLDER does not exist:**
- If you don't know the output folder, ask the user for it.
- Attempt to create folder: `mkdir -p {OUTPUT_FOLDER}`
- If creation fails: Return error "Cannot create output folder: {OUTPUT_FOLDER}"

**PROJECT_NAME contains special characters:**
- Sanitize for filename: Replace spaces with hyphens, remove special chars
- Keep original name in PRD title

**Features with no dependencies and no dependents (isolated nodes):**
- Still include in the dependency table with "None" in Dependencies
- Still include in the Mermaid diagram as a standalone node
- Question during Phase 2 whether the feature truly has no relationship to others

**Circular dependency detected during construction:**
- Re-examine the features involved and break the cycle by identifying which dependency is actually a "soft" relationship (e.g., a UI convenience, not a data requirement)
- If the cycle cannot be broken, flag it to the user during Phase 2

**Features with many dependencies (4+):**
- Verify each dependency is a genuine functional data requirement, not just a logical "nice to have before"
- Keep only dependencies where the feature cannot function without the other's output

## OUTPUT

**FINAL OUTPUT:**
- Exactly 9 sections:
  1. Executive Summary
  2. Problem and Opportunity
  3. Target Audience
  4. Objectives
  5. User Stories
  6. Functionalities
  7. Out of Scope
  8. Dependency Graph
  9. Acceptance Criteria

**PRD Structure Example:**
````markdown
# Product Name

## 1. Executive Summary

[Content in English...]

## 2. Problem and Opportunity

[Content in English...]

## 3. Target Audience

### Primary Users

**User Profile Name**
- Characteristic 1
- Characteristic 2
- Characteristic 3

### Behavioral Profile

[Common characteristics...]

## 4. Objectives

[Content in English...]

## 5. User Stories

### F01. Authentication System
- As a user, I want to register with email and password so that I can access the platform
- As a user, I want to log in so that I can access my content

### F02. Video Upload
- As a user, I want to drag files into a drop zone so that upload starts immediately
- As a user, I want to see upload progress so that I know when it finishes

### F03. Background Processing
- As the system, I want to automatically process uploaded videos so that transcriptions are available within the SLA
- As a user, I want to see processing progress so that I know when my video will be ready

### F04. Video Player
- As a user, I want to click a transcription segment to jump to that moment in the video
- As a user, I want the current segment highlighted as the video plays

### F05. Transcription Search
- As a user, I want to search within a transcription to find specific topics
- As a user, I want to click a search result to jump to that moment in the video

### F06. AI Summary
- As a user, I want to see an AI-generated summary of my video so that I can understand its content without watching

## 6. Functionalities

### F01. Authentication System

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

**Error Handling:** [3-5 scenarios - ONLY for critical features]

### F02. Video Upload

**Provides:**
- Uploaded video file path and metadata (used by F03)

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

**Error Handling:** [3-5 scenarios - ONLY for critical features]

### F03. Background Processing

**Consumes:**
- F02: uploaded video file path and metadata

**Provides:**
- Transcription segments with start/end timestamps, detected language, video file path (used by F04)
- Structured summary text (used by F06)

**Core Scope:**
- Video validation, audio extraction, transcription via Whisper, summary generation

**Full Scope additions:**
- Advanced retry strategies, priority queue processing

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

**Error Handling:** [3-5 scenarios - ONLY for critical features]

### F04. Video Player

**Consumes:**
- F03: transcription segments with start/end timestamps, video file path, detected language

**Provides:**
- Transcription panel with segments and playback position (used by F05)

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

### F05. Transcription Search

**Consumes:**
- F04: transcription panel with segments, playback position for seek-on-click

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

### F06. AI Summary

**Consumes:**
- F03: structured summary text

**Capabilities:** [limits, formats, rules]

**Experience:** [detailed flow]

## 7. Out of Scope

[Content in English...]

## 8. Dependency Graph

| # | Feature | Priority | Dependencies |
|---|---------|----------|--------------|
| F01 | Authentication System | 1 | None |
| F02 | Video Upload | 1 | F01 |
| F03 | Background Processing | 1 | F02 |
| F04 | Video Player | 1 | F03 |
| F05 | Transcription Search | 2 | F04 |
| F06 | AI Summary | 1 | F03 |

### Foundation Features
These features set up shared project infrastructure. In a greenfield project they must be implemented sequentially before or alongside any feature that depends on them:
- **F01 Authentication System** — scaffolds the base app (framework scaffolding, layout, routing) and the auth layer (db schema, session middleware)

### Execution Waves
Features within the same wave can be built in parallel. A wave starts only after every feature in earlier waves is complete.

**Note:** Foundation features (see "Foundation Features" above) cannot run in parallel in a greenfield project even if they appear together in a wave — they share scaffolding files and must be implemented sequentially until the base is in place.

- **Wave 1**: F01
- **Wave 2**: F02
- **Wave 3**: F03
- **Wave 4**: F04, F06
- **Wave 5**: F05

### Priority levels
- **1** = Essential — product does not work without it
- **2** = Important — significant value addition
- **3** = Desirable — incremental improvement

```mermaid
graph TD
  F01[Auth] --> F02[Upload]
  F02 --> F03[Processing]
  F03 --> F04[Player]
  F03 --> F06[Summary]
  F04 --> F05[Search]
```

## 9. Acceptance Criteria

### F01. Authentication System
- [ ] User can register with valid email and password
- [ ] Login fails with generic error on wrong credentials

### F02. Video Upload
- [ ] User can upload files up to 2GB
- [ ] Progress shows filename, percentage, and speed

### F03. Background Processing
- [ ] After upload completes, video automatically enters processing pipeline
- [ ] Processing progress shows distinct stages

### F04. Video Player
- [ ] Clicking a transcription segment seeks video to that moment
- [ ] Current segment is highlighted during playback

### F05. Transcription Search
- [ ] Search highlights all matching segments
- [ ] Clicking a match seeks video to that timestamp

### F06. AI Summary
- [ ] Summary displays below video player after processing completes
- [ ] Summary contains paragraph overview and key topics

### Cross-Feature Integration
- [ ] Uploaded video file (F02) is correctly received and processed by pipeline (F03)
- [ ] Transcription segments from processing (F03) display correctly in player (F04) with timestamps
- [ ] Player transcription panel and playback position (F04) enable search-and-seek in search (F05)
- [ ] Structured summary from processing (F03) renders correctly in summary section (F06)
````

---

Upon finishing execution, return the path to the PRD file.
