---
description: Detect and create bidirectional relationships between existing ADRs with clickable links
tags: [project, adr]
---

Launches the `adr-linker` agent to analyze existing ADRs and create bidirectional relationship links.

Post-processes generated ADRs to detect relationships (Supersedes, Depends on, Related to, Amends) and update files with clickable Markdown links following MADR standard.

**What it does**:
- Scans existing ADRs in `docs/adrs/generated/`
- Detects 4 relationship types using temporal, semantic, and technical analysis
- Creates bidirectional clickable links (A→B and B→A)
- Updates ADR files automatically with relationship headers
- Validates link integrity and generates comprehensive report
- Uses git history + potential ADR hints for accurate detection

**Usage**:
```
/adr-link [modules] [--validate] [--report-only] [--adrs-path=PATH] [--output-dir=PATH]
```

**Examples**:
```
/adr-link
# Process all ADRs across all modules

/adr-link BILLING API
# Process only BILLING and API modules

/adr-link --validate
# Validate existing links without modifying files

/adr-link --report-only
# Generate relationship report without updating files

/adr-link --adrs-path=output/adrs/generated
# Process ADRs in custom path

/adr-link --report-only --output-dir=docs/reports/
# Generate report in specific directory

/adr-link BILLING --adrs-path=custom/adrs --output-dir=reports/
# Process BILLING module with custom paths
```

---

## Implementation Instructions

When the user invokes `/adr-link`:

### Step 1: Parse Arguments and Determine Scope

**Extract options**:
- Module IDs (e.g., BILLING, API, DATA) - if provided
- Flags: `--validate`, `--report-only`
- Paths: `--adrs-path=<path>`, `--output-dir=<path>`

**Determine paths**:
- ADRs path: `--adrs-path` value or default `docs/adrs/generated/`
- Output directory: `--output-dir` value or default `docs/adrs/reports/`

**Determine scope**:
- No modules specified: Process ALL modules in `{adrs-path}/`
- Modules specified: Process only those modules in `{adrs-path}/{MODULE}/`
- Flag behavior:
  - `--validate`: Read-only mode, check link integrity, save report to `{output-dir}/`
  - `--report-only`: Detect relationships, save report to `{output-dir}/`, don't update files

### Step 2: Discover ADR Files

**Scan strategy**:
```
adrs_path = --adrs-path value OR "docs/adrs/generated/"

If modules specified:
  Scan: {adrs_path}/{MODULE}/**/*.md

If no modules:
  Scan: {adrs_path}/**/*.md
```

**Include**:
- Main directory: `{adrs_path}/{MODULE}/ADR-*.md`
- Subdirectories: `{adrs_path}/{MODULE}/needs-input/ADR-*.md`

**Exclude**:
- Non-ADR files (README.md, index files)
- Archived/deleted ADRs

**Build file list**:
```
Example output:
Found 47 ADR files:
- BILLING: 18 ADRs
- API: 12 ADRs
- AUTH: 7 ADRs
- DATA: 6 ADRs
- AUDIT: 4 ADRs
```

### Step 3: Launch adr-linker Agent

**CRITICAL**: Launch SINGLE agent instance (NOT multiple in parallel)

The adr-linker agent processes ALL ADRs in a single execution to:
- Build complete relationship graph
- Ensure bidirectional consistency
- Avoid file write conflicts

**Agent prompt construction**:

**Basic invocation** (no modules):
```
Analyze and link all ADRs in {adrs_path}. Detect all relationship types (Supersedes, Depends on, Related to, Amends), create bidirectional clickable links, and update ADR files.
```

**With modules**:
```
Analyze and link ADRs in modules: BILLING, API at {adrs_path}. Detect all relationship types, create bidirectional clickable links, and update ADR files.
```

**With --validate flag**:
```
Validate existing ADR relationships in {adrs_path}. Check link integrity, bidirectionality, and target existence. DO NOT modify files. Save validation report to {output_dir}/adr-link-validation-{timestamp}.md.
```

**With --report-only flag**:
```
Analyze and detect relationships between ADRs in {adrs_path} but DO NOT update files. Generate comprehensive relationship report showing all detected relationships, grouped by type and module. Save report to {output_dir}/adr-link-report-{timestamp}.md.
```

**Example Task calls**:

**1. Process all ADRs** (default paths):
```
Task:
  subagent_type: adr-linker
  description: Link all ADRs
  prompt: "Analyze and link all ADRs in docs/adrs/generated/. Detect all relationship types (Supersedes, Depends on, Related to, Amends), create bidirectional clickable links, and update ADR files. Use git history from repository root for temporal analysis."
```


### Step 4: Handle Agent Response

Agent returns summary report containing:
- **Success**: Number of relationships detected and ADRs updated, grouped by type (Supersedes, Depends on, Related to, Amends)
- **Validation**: Link integrity check results, broken links if any
- **Errors**: Git repository not found, invalid paths, permission issues

### Step 5: Integration Notes

**When to use**:
- After parallel ADR generation (resolves race conditions)
- After manual ADR creation
- After ADR renumbering
- Periodic maintenance

**When NOT to use**:
- During ADR generation (let adr-generator handle initial relationships)
- On potential ADRs (only works on generated ADRs)

## Error Reference

| Error | Solution |
|-------|----------|
| No ADR files found | Run `/adr-generate` first |
| Permission denied | Check file permissions: `chmod 644 docs/adrs/generated/**/*.md` |
| Circular dependency | Agent breaks lowest-confidence link automatically |
| Module not found | Check spelling or run `/adr-generate MODULE` |
| Custom path not found | Verify path exists or omit `--adrs-path` |
| Cannot create output dir | Use writable directory with `--output-dir` |

## Summary

The `/adr-link` command is a powerful post-processing tool that:
1. Solves race condition problem in parallel ADR generation
2. Creates bidirectional navigation between related decisions
3. Maintains MADR compliance with clickable Markdown links
4. Validates relationship integrity
5. Provides comprehensive analysis of ADR evolution

Use after ADR generation to build a complete, navigable architecture decision graph.
