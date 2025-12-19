---
description: Create a modular codebase mapping to prepare for ADR identification (Phase 1)
tags: [project, adr]
---

Launch the `adr-analyzer` agent to execute Phase 1: Codebase Mapping.

This will:
1. Analyze the entire project structure
2. Identify technologies, frameworks, and architectural patterns
3. Divide the codebase into logical, independent modules
4. Create mapping.md with modular structure

The mapping file will include:
- Project overview and technology stack
- System modules with IDs, scope estimates, and descriptions
- Cross-cutting concerns (infrastructure, authentication, data layer, etc.)
- Guidelines for Phase 2 analysis

**Usage**:
```
/adr-map [--project-dir=PATH] [--context-dir=PATH] [--output-dir=PATH]
```

**Examples**:
```
/adr-map
# Maps current directory, outputs to docs/adrs/mapping.md

/adr-map --project-dir=/path/to/project
# Maps specific project directory

/adr-map --context-dir=docs/architecture
# Maps current directory using architecture docs/diagrams to inform mapping

/adr-map --project-dir=/legacy --context-dir=/legacy/docs --output-dir=analysis/adrs
# Full control: custom project, context, and output directories
```

**Context Files**: All file types supported - architecture docs, design docs, README files,
diagrams (PNG, SVG), images, PDFs, tech stack documentation. These help the agent better
understand module boundaries and business domains.

**Output**: `{OUTPUT_DIR}/mapping.md` (default: `docs/adrs/mapping.md`)

After Phase 1 completes, you can use `/adr-identify` to identify potential ADRs for specific modules.

For large codebases (10,000+ files), this creates a foundation for incremental analysis without overwhelming the context window.

---

## Implementation Instructions

When the user invokes `/adr-map`:

Parse arguments to extract:
- `--project-dir=<path>`: Optional directory to map (default: `.` - current working directory)
- `--context-dir=<path>`: Optional context directory with docs/diagrams (default: none)
- `--output-dir=<path>`: Optional output directory (default: `docs/adrs`)

Launch the `adr-analyzer` agent with the Task tool:

**Without options:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Execute Phase 1: Create codebase mapping"
```

**With --project-dir:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Execute Phase 1: Create codebase mapping with --project-dir=/path/to/project"
```

**With --context-dir:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Execute Phase 1: Create codebase mapping with --context-dir=docs/architecture"
```

**With multiple options:**
```
Task tool:
- subagent_type: adr-analyzer
- prompt: "Execute Phase 1: Create codebase mapping with --project-dir=/legacy --context-dir=/legacy/docs --output-dir=analysis/adrs"
```

The agent will:
1. Analyze the project at --project-dir (or current directory)
2. Load context files from --context-dir if provided (all file types)
3. Create `{OUTPUT_DIR}/mapping.md` with complete codebase analysis and optional context notes
