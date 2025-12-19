---
description: Generate Mermaid diagrams from a Feature Design Document (FDD). Usage: /generate-mermaid <path-to-fdd.md> [output-folder]
---

You MUST invoke the mermaid-diagram-generator agent using the Task tool with subagent_type="mermaid-diagram-generator".

Extract the FDD file path and optional output folder from the command arguments:
- FDD file path (required)
- Output folder (optional, default: "docs/mermaid")

Pass the following detailed prompt to the agent:

"Generate Mermaid diagrams from the Feature Design Document located at [FDD_FILE_PATH].

Output folder: [OUTPUT_FOLDER]

The agent will execute its complete workflow (Phases 1-9). Your task is to ensure the agent receives the correct FDD path and output folder.

Key requirements the agent will follow:

ANALYSIS & SELECTION:
- Read FDD completely and detect language (Portuguese, English, Spanish, etc.)
- Extract explicit elements and identify what is central to system success
- Evaluate significance rigorously using 5 criteria (main flow, difficult parts, architectural decisions, public contracts, relationships)
- Select appropriate diagram types (Sequence, Flowchart TD/LR, Class, ER)
- Prune to most valuable diagrams (typical: 6-8, up to 10 maximum if truly justified)

GENERATION:
- Create ONE markdown file: [OUTPUT_FOLDER]/[feature-name]-diagrams.md
- Translate ALL section headers to FDD language with proper accents
- Keep technical terms in English (Service, Gateway, Redis, etc.)
- Write concise paragraphs (3-5 sentences) for each diagram
- Use concise labels (3 words max per node)
- Use proper accents EVERYWHERE (markdown text AND diagram node labels)
- Apply Mermaid syntax validation and guardrails automatically

QUALITY ASSURANCE:
- Mandatory internal review: re-read FDD and document, identify and correct ALL inconsistencies
- Validate: language matches FDD, 1-10 diagrams (typical: 6-8), significance criteria met, no redundancy/fabrication/excluded items
- Create self-contained complete file
- Report: detected language, file path, number of diagrams, rationale, validation results

CRITICAL RULES:
- Never invent information not in the FDD
- Generate diagrams in FDD language with proper accents EVERYWHERE
- Better 6 excellent diagrams than 10 mediocre ones
- Mandatory internal review before completion
- Keep technical terms in English
- No emojis anywhere
- Use proper accents in node labels (Mermaid supports UTF-8)
- Keep node labels simple; avoid complex expressions
- Put technical details in notes section below diagram, not in labels
- The agent handles all syntax validation and guardrails automatically"

Replace [FDD_FILE_PATH] with the actual file path from command arguments.
Replace [OUTPUT_FOLDER] with the specified output folder or "docs/mermaid" if not provided.
Replace [feature-name] with the appropriate feature name extracted from the FDD filename (e.g., "ratelimiter" from "ratelimiter-fdd.md").
