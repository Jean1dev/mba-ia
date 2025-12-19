# ADRs Management Plugin

## Objective

The ADRs Management plugin provides a comprehensive 3-phase workflow for creating, managing, and linking Architecture Decision Records (ADRs). It helps teams systematically document architectural decisions with evidence-based analysis, formal ADR generation, and relationship mapping.

## Installation

### Prerequisites

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add devfullcycle/claude-mkt-place
```

### Install Plugin

Then install the ADRs Management plugin:

```bash
/plugin install adrs-management@devfullcycle
```

## Available Commands

### `/adr-map`

**Description**: Creates a modular codebase mapping to prepare for ADR identification (Phase 1). Analyzes the entire project structure, identifies technologies and architectural patterns, and divides the codebase into logical modules.

**Syntax**:
```bash
/adr-map [--project-dir=PATH] [--context-dir=PATH] [--output-dir=PATH]
```

**Parameters**:
- `--project-dir=PATH`: Optional - Directory to map (default: current directory)
- `--context-dir=PATH`: Optional - Directory with context files (docs, diagrams, images, PDFs) to inform mapping
- `--output-dir=PATH`: Optional - Base output directory (default: `docs/adrs`)

**Examples**:
```bash
# Map current directory
/adr-map

# Map specific project directory
/adr-map --project-dir=/path/to/project

# Map with architecture documentation context
/adr-map --context-dir=docs/architecture

# Full control with custom paths
/adr-map --project-dir=/legacy --context-dir=/legacy/docs --output-dir=analysis/adrs
```

**Output**: Creates `{OUTPUT_DIR}/mapping.md` with:
- Project overview and technology stack
- System modules with IDs and descriptions
- Cross-cutting concerns
- Guidelines for Phase 2 analysis

---

### `/adr-identify`

**Description**: Identifies potential ADRs for specific modules based on the codebase mapping (Phase 2). Analyzes code with strict architectural filtering, uses git history for temporal context, and creates individual potential ADR files in priority-based folders.

**Prerequisites**: Run `/adr-map` first if `mapping.md` doesn't exist.

**Syntax**:
```bash
/adr-identify [module-ids] [--output-dir=PATH] [--adrs-dir=PATH]
```

**Parameters**:
- `module-ids`: Optional - One or more module identifiers (e.g., AUTH, DATA, API). If omitted, prompts for selection.
- `--output-dir=PATH`: Optional - Base output directory (default: `docs/adrs`)
- `--adrs-dir=PATH`: Optional - Directory with existing ADRs for context (default: `{OUTPUT_DIR}/generated/`)

**Examples**:
```bash
# Prompt for module selection
/adr-identify

# Analyze single module
/adr-identify AUTH

# Analyze multiple modules in parallel
/adr-identify AUTH DATA API

# Custom output directory
/adr-identify --output-dir=output/adrs AUTH

# Use existing ADRs for context
/adr-identify --adrs-dir=docs/adrs/generated AUTH
```

**Output Structure**:
```
{OUTPUT_DIR}/potential-adrs/
├── must-document/    # High priority (score ≥100)
│   └── MODULE-ID/
│       └── decision-title-kebab-case.md
└── consider/         # Medium priority (score 75-99)
    └── MODULE-ID/
        └── decision-title-kebab-case.md
```

**How It Works**:
- Scoring: 3 dimensions (Scope+Impact, Cost to Change, Team Knowledge) - 150 points total
- Thresholds: ≥100 pts (high priority), 75-99 pts (medium priority), <75 pts (discarded)
- Only ~5% of findings become ADRs (strict filtering)
- Automatically avoids duplicates and detects relationships with existing ADRs

---

### `/adr-generate`

**Description**: Generates formal ADRs from potential ADRs (Phase 3). Transforms potential ADRs into formal MADR-formatted documents with sequential numbering, strategic context integration, and relationship detection.

**Prerequisites**: Run `/adr-identify` first to create potential ADRs.

**Syntax**:
```bash
/adr-generate [modules] [--context-dir=PATH] [--language=LOCALE] [--include-consider] [--output-dir=PATH]
```

**Parameters**:
- `modules`: Optional - Module IDs or `--all` for all modules. If omitted, prompts for selection.
- `--context-dir=PATH`: Optional - Directory with strategic context documents
- `--language=LOCALE`: Optional - Target language (en, pt-BR, es, fr, de). Default: en
- `--include-consider`: Optional - Include medium priority ADRs (default: only high priority)
- `--output-dir=PATH`: Optional - Base output directory (default: `docs/adrs`)

**Examples**:
```bash
# Generate all high-priority ADRs
/adr-generate --all

# Generate for specific module
/adr-generate BILLING

# Generate multiple modules in parallel
/adr-generate BILLING API DATA

# Include medium priority ADRs
/adr-generate --include-consider BILLING

# Generate in Portuguese
/adr-generate --language=pt-BR --include-consider BILLING API

# With strategic context
/adr-generate --context-dir=docs/context/ BILLING

# Custom output directory
/adr-generate --output-dir=output/adrs BILLING
```

**Output Structure**:
```
{OUTPUT_DIR}/generated/
└── {MODULE}/
    ├── ADR-XXX-title.md          # Complete ADRs
    └── needs-input/
        └── ADR-XXX-title.md      # ADRs with gaps requiring input
```

**Note**: Generated ADRs use placeholder `XXX` for numbering. Manual renumbering required after generation.

---

### `/adr-link`

**Description**: Detects and creates bidirectional relationships between existing ADRs with clickable Markdown links. Analyzes temporal evolution, technical dependencies, semantic similarity, and explicit hints to build a comprehensive ADR relationship graph.

**Prerequisites**: Run `/adr-generate` first to create formal ADRs.

**Syntax**:
```bash
/adr-link [modules] [--validate] [--report-only] [--adrs-path=PATH] [--output-dir=PATH]
```

**Parameters**:
- `modules`: Optional - Module IDs to process. If omitted, processes all modules.
- `--validate`: Optional - Validate existing links without modifying files
- `--report-only`: Optional - Generate relationship report without updating files
- `--adrs-path=PATH`: Optional - Path to ADRs directory (default: `docs/adrs/generated/`)
- `--output-dir=PATH`: Optional - Directory for reports (default: `docs/adrs/reports/`)

**Examples**:
```bash
# Process all ADRs
/adr-link

# Process specific modules
/adr-link BILLING API

# Validate existing links
/adr-link --validate

# Generate report only
/adr-link --report-only

# Custom ADRs path
/adr-link --adrs-path=output/adrs/generated

# Generate report in specific directory
/adr-link --report-only --output-dir=docs/reports/
```

**Relationship Types Detected**:
- **Supersedes/Superseded by**: ADR replaces an older one
- **Depends on**: ADR requires a previous decision to function
- **Related to**: Technical relationship without direct dependency
- **Amends**: Partially modifies previous decision without replacement

**Output**: Updates ADR files with relationship headers and generates validation/report files in `{OUTPUT_DIR}/`.

---

## Workflow

The ADRs Management plugin follows a 3-phase workflow:

### Phase 1: Codebase Mapping (`/adr-map`)
1. Analyze project structure
2. Identify technologies and frameworks
3. Divide codebase into logical modules
4. Create `mapping.md` with modular structure

### Phase 2: ADR Identification (`/adr-identify`)
1. Analyze specified modules
2. Apply architectural filtering (Step 0 + Red Flags + Scoring)
3. Create potential ADR files in priority folders
4. Enrich with git history context
5. Update index file

### Phase 3: ADR Generation (`/adr-generate`)
1. Transform potential ADRs into formal MADR documents
2. Detect relationships with existing ADRs
3. Organize by module and priority
4. Mark gaps requiring human input

### Post-Processing: Relationship Linking (`/adr-link`)
1. Analyze all generated ADRs
2. Detect relationships (Supersedes, Depends on, Related to, Amends)
3. Create bidirectional clickable links
4. Validate link integrity

## Usage Examples

### Complete Workflow Example

```bash
# Step 1: Map the codebase
/adr-map --context-dir=docs/architecture

# Step 2: Identify potential ADRs for key modules
/adr-identify AUTH DATA API BILLING

# Step 3: Generate formal ADRs
/adr-generate --include-consider AUTH DATA API BILLING

# Step 4: Link relationships
/adr-link
```

### Incremental Analysis Example

```bash
# Start with one module
/adr-map
/adr-identify AUTH
/adr-generate AUTH

# Add more modules later
/adr-identify DATA API
/adr-generate DATA API

# Link all ADRs together
/adr-link
```

### Custom Output Location Example

```bash
/adr-map --output-dir=custom/adrs
/adr-identify --output-dir=custom/adrs AUTH
/adr-generate --output-dir=custom/adrs AUTH
/adr-link --adrs-path=custom/adrs/generated
```

## Output Structure

```
docs/adrs/                          # Default output directory
├── mapping.md                      # Phase 1 output
├── potential-adrs-index.md         # Phase 2 index
├── potential-adrs/
│   ├── must-document/              # High priority (score ≥100)
│   │   └── {MODULE}/
│   │       └── decision-title.md
│   └── consider/                   # Medium priority (score 75-99)
│       └── {MODULE}/
│           └── decision-title.md
├── generated/                      # Phase 3 output
│   └── {MODULE}/
│       ├── ADR-XXX-title.md        # Complete ADRs
│       └── needs-input/
│           └── ADR-XXX-title.md    # ADRs with gaps
└── reports/                        # Phase 4 output
    ├── adr-link-report-{timestamp}.md
    └── adr-link-validation-{timestamp}.md
```

## Important Notes

- **Phase Order**: Always run phases in order (map → identify → generate → link)
- **Module IDs**: Use module IDs from `mapping.md` when identifying ADRs
- **Parallel Processing**: Multiple modules can be processed in parallel for faster analysis
- **Git History**: The plugin automatically uses git history to enrich ADRs with temporal context
- **Language Support**: ADRs can be generated in multiple languages (en, pt-BR, es, fr, de)
- **Renumbering**: Generated ADRs use placeholder `XXX` - manual renumbering required
- **Strict Filtering**: Only ~5% of findings become ADRs to maintain quality
- **Relationship Detection**: Automatic relationship detection helps build decision graphs

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `mapping.md` not found | Run `/adr-map` first |
| No potential ADRs found | Check module IDs in `mapping.md`, ensure codebase has architectural decisions |
| ADR generation fails | Verify potential ADR files exist in `potential-adrs/` folder |
| Links not created | Run `/adr-link` after generating ADRs |
| Module not found | Check spelling or run `/adr-map` to see available modules |

