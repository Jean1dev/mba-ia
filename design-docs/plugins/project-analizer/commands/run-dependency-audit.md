---
allowed-tools: Task, Read, Write, TodoWrite
description: Run a dependency audit on the project and generate a full report with the findings and the documentation for each dependency.
---
# Dependency Audit Process Command

You MUST invoke the dependency-auditor agent using the Task tool with subagent_type="dependency-auditor".

Extract the following parameters from command arguments:
- project-folder (optional, default: entire project root)
- output-folder (optional, default: "/docs/agents/dependency-auditor")
- ignore-folders (optional, comma-separated list)

Pass the following prompt to the agent:

"Execute dependency audit with the following parameters:

Project scope: [PROJECT_SCOPE]
Output location: [OUTPUT_FOLDER]
Folders to ignore: [IGNORE_FOLDERS]

Execute your complete workflow following all internal guidelines.

CRITICAL REMINDERS:
- Do not modify any project files
- Use MCP servers (Context7, Firecrawl) for validation when available
- Always verify dependency versions externally
- Exclude folders specified in ignore-folders parameter from audit
- Save report to: [OUTPUT_FOLDER]/dependencies-report-{YYYY-MM-DD HH:MM:SS}.md

REPORT must include:
- All sections specified in agent guidelines (Summary, Critical Issues, Dependencies table, Risk Analysis, etc.)
- Analysis of the 10 most critical files
- Explicit confirmation of saved file path
- List of unverified dependencies (if any)"

Replace [PROJECT_SCOPE] with the specified project-folder or "entire project root" if not provided.
Replace [OUTPUT_FOLDER] with the specified output-folder or "/docs/agents/dependency-auditor" if not provided.
Replace [IGNORE_FOLDERS] with the comma-separated list or "none" if not provided.

## Usage Examples

```bash
# Audit the entire project (default: root folder)
/run-dependency-audit

# Audit a specific folder
/run-dependency-audit --project-folder=project-folder

# Audit and save report to custom location (default: /docs/agents/dependency-auditor/)
# File pattern: dependencies-report-{YYYY-MM-DD HH:MM:SS}.md
/run-dependency-audit --output-folder=output-folder

# Exclude specific folders from audit
/run-dependency-audit --ignore-folders=adk_repo,venv,.env,node_modules,.git

# Combined usage
/run-dependency-audit --project-folder=src --output-folder=reports --ignore-folders=node_modules,dist
```
