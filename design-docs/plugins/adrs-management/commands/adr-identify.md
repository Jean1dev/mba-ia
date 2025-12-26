---
description: Identify potential ADRs for specific modules based on the codebase mapping (Phase 2)
tags: [project, adr]
---

Launches the `adr-analyzer` agent to identify potential ADRs in specified modules.

When multiple modules are specified, launches agents in parallel for faster analysis.

**Prerequisites**: Run `/adr-map` first if mapping.md doesn't exist in the output directory.

**What it does**:
- Analyzes specified module(s) with strict architectural filtering
- Executes multiple modules in parallel when 2+ modules are specified
- Uses git history internally to enrich potential ADRs with temporal context
- Creates individual ADR files in priority-based folders (NO numbers in filenames)
- Weaves git insights naturally into content (dates, keywords, evolution)
- Updates the index with findings

**Usage**:
```
/adr-identify [module-ids] [--output-dir=PATH] [--adrs-dir=PATH]
```

**Examples**:
```
/adr-identify
# Prompts which modules to analyze (uses docs/adrs by default)

/adr-identify AUTH
# Analyze only AUTH module

/adr-identify AUTH DATA API
# Analyze multiple modules

/adr-identify --output-dir=output/adrs AUTH
# Analyze AUTH module with custom output directory

/adr-identify --adrs-dir=docs/adrs/generated AUTH
# Uses existing ADRs from custom directory for context and duplicate detection
```

**Output Structure**:
```
{OUTPUT_DIR}/potential-adrs/          # Default: docs/adrs/potential-adrs
├── must-document/    # High priority (score ≥100 out of 150)
│   └── MODULE-ID/
│       ├── decision-title-kebab-case.md
│       └── another-architectural-decision.md
└── consider/         # Medium priority (score 75-99 out of 150)
    └── MODULE-ID/
        └── medium-priority-decision.md
```

**Important**: Filenames use descriptive kebab-case WITHOUT numbers. Numbering happens in Phase 3 when formal ADRs are generated.

**Existing ADR Integration**: Automatically scans {OUTPUT_DIR}/generated/ (or --adrs-dir path) for existing ADRs to:
- Avoid duplicate identification (>70% similarity warning)
- Detect relationships with existing decisions (40-70% similarity)
- Provide timeline context (decision evolution, supersession patterns)
- Suggest consolidation opportunities (implementation details of existing ADRs)

**How It Works**:
- **Scoring**: 3 dimensions (Scope+Impact, Cost to Change, Team Knowledge), 150 points total (75 base score from Step 0 + 75 from dimensions)
- **Thresholds**: ≥100 pts (67%, high priority), 75-99 pts (50-66%, medium priority), <75 pts (discard)
- **Filtering**: Step 0 (Positive Identification) + Red Flags 1-5
- **Git Integration**: Enriches content with temporal context (dates, evolution, intent keywords)

**Key Features**:
- **Step 0 (Positive Identification)**: Base technology decisions (infrastructure services, framework, ORM, API, auth, payment, AI/ML) automatically trigger ADR creation with base score
- **Red Flag 5**: Consolidates overly granular decisions into larger strategic ADRs (prevents ADR sprawl)
- **Operational Impact**: Captures observability, resilience, and production reliability decisions

**Expected Results**:
- Only ~5% of findings become ADRs (strict filtering)
- Potential ADRs enriched with git history (dates, evolution, intent keywords)
- No separate "Git History" section - insights woven naturally into content

**Note**: This identifies potential ADRs with evidence. You decide which to formally document in Phase 3.

---

## Implementation Instructions

When the user invokes `/adr-identify` with module IDs:

### Parse Arguments
Extract from command:
- Module IDs (e.g., AUTH, DATA, API)
- `--output-dir=<path>`: Optional output directory (default: `docs/adrs`)
- `--adrs-dir=<path>`: Optional existing ADRs directory (default: `{OUTPUT_DIR}/generated/`)

### Single Module (e.g., `/adr-identify AUTH`)
Launch a single `adr-analyzer` agent with the Task tool:

**Without --output-dir:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the AUTH module"
```

**With --output-dir:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the AUTH module with --output-dir=custom/path"
```

**With --adrs-dir:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the AUTH module with --adrs-dir=docs/adrs/generated"
```

### Multiple Modules (e.g., `/adr-identify AUTH DATA API` or `/adr-identify --output-dir=output/adrs AUTH DATA`)
Launch multiple `adr-analyzer` agents **in parallel** using a single message with multiple Task tool calls:

**Without --output-dir:**
```
Single message with multiple Task tool calls:

Task tool call 1:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the AUTH module"

Task tool call 2:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the DATA module"

Task tool call 3:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the API module"
```

**With --output-dir:**
```
Single message with multiple Task tool calls:

Task tool call 1:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the AUTH module with --output-dir=custom/path"

Task tool call 2:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the DATA module with --output-dir=custom/path"

Task tool call 3:
- subagent_type: adr-analyzer
- prompt: "Identify potential ADRs for the API module with --output-dir=custom/path"
```

**IMPORTANT**:
- When 2+ modules are specified, you MUST send a single message with multiple Task tool calls
- Each agent should analyze only ONE specific module
- Do NOT run agents sequentially - run them in parallel for better performance
- Each agent will create its own potential ADR files in the appropriate priority folders
- The index file will be updated by each agent independently
- All agents must use the same --output-dir if specified

### No Modules Specified (e.g., `/adr-identify` or `/adr-identify --output-dir=custom/path`)
1. Determine output directory (from --output-dir or default `docs/adrs`)
2. Read `{OUTPUT_DIR}/mapping.md` to get available modules
3. Present the module list to the user
4. Ask which module(s) they want to analyze
5. Once specified, follow the logic above (single or multiple)
