---
description: Generate formal ADRs from potential ADRs
tags: [project, adr]
---

Launches the `adr-generator` agent to generate formal ADRs from potential ADRs.

When multiple modules or files are specified, launches agents in parallel for faster generation.

**What it does**:
- Generates formal ADRs using placeholder XXX for numbering
- Executes multiple targets in parallel when 2+ targets are specified
- Detects relationships with existing ADRs
- Organizes by module: `generated/{MODULE}/` or `generated/{MODULE}/needs-input/`
- Manual renumbering required after generation

**Usage**:
```
/adr-generate [modules] [--context-dir=PATH] [--language=LOCALE] [--include-consider] [--output-dir=PATH]
```

**Examples**:
```
/adr-generate --all
# Generate ALL potential ADRs to docs/adrs/generated/{MODULE}/
# Excluding the "consider" priority if --include-consider is not specified

/adr-generate BILLING
# Generate to docs/adrs/generated/BILLING/

/adr-generate BILLING API DATA
# Generate multiple modules in parallel

/adr-generate --include-consider BILLING
# Include both must-document AND consider priorities

/adr-generate --language=pt-BR --include-consider BILLING API
# Generate in Portuguese with all priorities

/adr-generate --context-dir=docs/context/ BILLING
# Generate with strategic context

/adr-generate --output-dir=output/adrs BILLING
# Generate to custom output directory: output/adrs/generated/BILLING/
```

---

## Implementation Instructions

When the user invokes `/adr-generate`:

### Step 1: Discover Potential ADR Files

Parse arguments to get:
- Module IDs (e.g., BILLING, API, DATA)
- Options (--context-dir, --language, --include-consider, --output-dir)
- Set output base directory (default: `docs/adrs`, or use `--output-dir` value)

**Default behavior (without --include-consider):**
Scan only must-document:
```
docs/adrs/potential-adrs/must-document/{MODULE}/*.md
```

**With --include-consider flag:**
Scan both priorities:
```
docs/adrs/potential-adrs/must-document/{MODULE}/*.md
docs/adrs/potential-adrs/consider/{MODULE}/*.md
```

Build list of ALL potential ADR files across ALL specified modules.

### Step 2: Launch Agents in Parallel

Launch MULTIPLE `adr-generator` agents **in parallel** using a SINGLE message with MULTIPLE Task tool calls - ONE agent per potential ADR file.

**Example: `/adr-generate BILLING API`**

If BILLING has 3 files and API has 2 files, launch 5 agents:

```
Single message with 5 Task tool calls:

Task 1:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/must-document/BILLING/payment-gateway.md"

Task 2:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/must-document/BILLING/dual-paypal.md"

Task 3:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/consider/BILLING/cache-strategy.md"

Task 4:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/must-document/API/rest-choice.md"

Task 5:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/must-document/API/grpc-internal.md"
```

### With Options

Include options in each agent's prompt:

```
Task 1:
- subagent_type: adr-generator
- prompt: "Generate formal ADR from docs/adrs/potential-adrs/must-document/BILLING/payment-gateway.md with --language=pt-BR and --context-dir=docs/context/"
```

**CRITICAL**:
- MUST send a SINGLE message with MULTIPLE Task tool calls
- ONE agent per potential ADR file (NOT one agent per module)
- ALL agents run in parallel
- Each agent uses placeholder XXX for numbering
- Do NOT run sequentially

### No Modules Specified (e.g., `/adr-generate`)
1. Scan `docs/adrs/potential-adrs/` to discover all modules
2. Ask user which modules to process
3. Follow Step 1 and Step 2 above
