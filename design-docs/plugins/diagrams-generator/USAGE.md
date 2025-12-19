# Diagrams Generator Plugin

## Objective

The Diagrams Generator plugin creates visual architecture diagrams from Feature Design Documents (FDDs). It supports two diagram types: C4 diagrams (PlantUML format) for comprehensive architecture visualization, and Mermaid diagrams for technical flowcharts, sequence diagrams, and class diagrams.

## Installation

### Prerequisites

First, add the marketplace to Claude Code:

```bash
/plugin marketplace add devfullcycle/claude-mkt-place
```

### Install Plugin

Then install the Diagrams Generator plugin:

```bash
/plugin install diagrams-generator@devfullcycle
```

## Available Commands

### `/c4-generate`

**Description**: Generates C4 architecture diagrams (System Context, Container, Component, and Code levels) in PlantUML format from a Feature Design Document (FDD). Creates separate `.puml` files for each diagram level and an analysis markdown file.

**Syntax**:
```bash
/c4-generate <path-to-fdd.md> [output-folder] [--no-images]
```

**Parameters**:
- `path-to-fdd.md`: **Required** - Path to the Feature Design Document
- `output-folder`: Optional - Output directory for generated files (default: `docs/c4`)
- `--no-images`: Optional - Skip PNG image generation (default: PNG images are generated)

**Examples**:
```bash
# Generate C4 diagrams with default output location
/c4-generate docs/features/payment-fdd.md

# Generate to custom output folder
/c4-generate docs/features/auth-fdd.md docs/architecture/c4

# Generate without PNG images
/c4-generate docs/features/payment-fdd.md --no-images

# Generate with custom output and no images
/c4-generate docs/features/notification-fdd.md output/c4 --no-images
```

**Output Structure**:
```
{output-folder}/
├── {feature-name}-c1.puml    # System Context diagram
├── {feature-name}-c2.puml    # Container diagram
├── {feature-name}-c3.puml    # Component diagram
├── {feature-name}-c4.puml    # Code level diagram
├── {feature-name}-c1.png     # PNG image (if generated)
├── {feature-name}-c2.png     # PNG image (if generated)
├── {feature-name}-c3.png     # PNG image (if generated)
├── {feature-name}-c4.png     # PNG image (if generated)
└── {feature-name}-c4.md      # Analysis document (no PlantUML code)
```

**Diagram Levels**:
- **C1 - System Context**: Business context and system boundaries (stakeholders, external systems)
- **C2 - Container**: Technology stack and deployment units (services, databases, APIs)
- **C3 - Component**: Internal component structure and responsibilities
- **C4 - Code**: Maximum implementation detail using standard PlantUML class diagrams

**Features**:
- Automatically detects FDD language and generates diagrams in the same language
- Uses proper accents and special characters for non-English languages
- Keeps technical terms in English (Service, Gateway, Redis, etc.)
- Only generates diagrams with sufficient FDD information (never fabricates)
- Creates separate `.puml` files for each diagram level
- Optional PNG image generation (requires PlantUML installation)

---

### `/mermaid-generate`

**Description**: Generates technical Mermaid diagrams from Feature Design Documents (FDDs). Creates focused, meaningful diagrams (typically 6-8, up to 10 maximum) including sequence diagrams, flowcharts, class diagrams, and ER diagrams.

**Syntax**:
```bash
/mermaid-generate <path-to-fdd.md> [output-folder]
```

**Parameters**:
- `path-to-fdd.md`: **Required** - Path to the Feature Design Document
- `output-folder`: Optional - Output directory for generated file (default: `docs/mermaid`)

**Examples**:
```bash
# Generate Mermaid diagrams with default output location
/mermaid-generate docs/features/payment-fdd.md

# Generate to custom output folder
/mermaid-generate docs/features/auth-fdd.md docs/diagrams/mermaid

# Generate from FDD in subdirectory
/mermaid-generate docs/design/rate-limiter-fdd.md
```

**Output Structure**:
```
{output-folder}/
└── {feature-name}-diagrams.md    # Single markdown file with all diagrams
```

**Diagram Types Generated**:
- **Sequence Diagrams**: API calls, event flows, request-response patterns, temporal ordering
- **Flowchart TD (Top-Down)**: Internal process logic, algorithms, decision trees, state machines
- **Flowchart LR (Left-Right)**: Mode comparison, strategy selection, parallel alternatives
- **Class Diagrams**: Public APIs, data structures, type relationships, interface hierarchies
- **ER Diagrams**: Data models, entity relationships, message schemas

**Features**:
- Generates only significant diagrams that enhance comprehension
- Automatically detects FDD language and generates diagrams in the same language
- Uses proper accents and special characters everywhere (markdown text AND node labels)
- Keeps technical terms in English (Service, Gateway, Redis, etc.)
- Multiple diagrams of the same type allowed if they serve different purposes
- Single self-contained markdown file with all diagrams
- Concise labels (3 words max per node)
- Clean Mermaid syntax with automatic validation

---

## Workflow

### C4 Diagram Generation Workflow

1. **FDD Analysis**: Reads and analyzes the Feature Design Document
2. **Language Detection**: Identifies FDD language and matches diagram language
3. **Level Assessment**: Determines which C4 levels have sufficient information
4. **Diagram Generation**: Creates PlantUML code for each applicable level
5. **File Creation**: Writes separate `.puml` files for each diagram
6. **Analysis Document**: Creates markdown file with analysis (no PlantUML code)
7. **PNG Generation** (optional): Generates PNG images if PlantUML is installed

### Mermaid Diagram Generation Workflow

1. **FDD Deep Analysis**: Reads complete FDD and identifies explicit elements
2. **Significance Evaluation**: Filters diagrams using 5 criteria (main flow, difficult parts, architectural decisions, public contracts, relationships)
3. **Diagram Type Selection**: Chooses appropriate diagram types (Sequence, Flowchart, Class, ER)
4. **Pruning**: Selects most valuable diagrams (typically 6-8, up to 10 maximum)
5. **Label Preparation**: Creates concise labels with proper accents
6. **Document Generation**: Creates single markdown file with all diagrams
7. **Internal Review**: Re-reads FDD and document, corrects inconsistencies
8. **Validation**: Ensures language matches, no redundancy, no fabrication

---

## Usage Examples

### C4 Diagrams Example

```bash
# Generate C4 diagrams for payment processing feature
/c4-generate docs/features/payment-processing-fdd.md

# Output:
# - docs/c4/payment-processing-c1.puml (System Context)
# - docs/c4/payment-processing-c2.puml (Container)
# - docs/c4/payment-processing-c3.puml (Component)
# - docs/c4/payment-processing-c4.puml (Code)
# - docs/c4/payment-processing-c4.md (Analysis)
# - PNG images (if PlantUML installed)
```

### Mermaid Diagrams Example

```bash
# Generate Mermaid diagrams for authentication feature
/mermaid-generate docs/features/authentication-fdd.md

# Output:
# - docs/mermaid/authentication-diagrams.md
#   Contains: Main flow sequence, authentication algorithm flowchart,
#             mode comparison flowchart, token class diagram
```

### Custom Output Locations

```bash
# C4 diagrams to custom location
/c4-generate docs/features/payment-fdd.md architecture/c4

# Mermaid diagrams to custom location
/mermaid-generate docs/features/auth-fdd.md diagrams/mermaid
```

### Without PNG Generation

```bash
# Generate C4 diagrams without PNG images (faster)
/c4-generate docs/features/payment-fdd.md --no-images
```

---

## Output Structure

### C4 Diagrams Output

```
docs/c4/                          # Default output directory
├── {feature-name}-c1.puml        # System Context (PlantUML)
├── {feature-name}-c2.puml        # Container (PlantUML)
├── {feature-name}-c3.puml        # Component (PlantUML)
├── {feature-name}-c4.puml        # Code Level (PlantUML)
├── {feature-name}-c1.png         # PNG image (if generated)
├── {feature-name}-c2.png         # PNG image (if generated)
├── {feature-name}-c3.png         # PNG image (if generated)
├── {feature-name}-c4.png         # PNG image (if generated)
└── {feature-name}-c4.md          # Analysis document
```

### Mermaid Diagrams Output

```
docs/mermaid/                     # Default output directory
└── {feature-name}-diagrams.md    # Single file with all diagrams
```

---

## Important Notes

### C4 Diagrams

- **Language Matching**: Diagrams are generated in the same language as the FDD with proper accents
- **Technical Terms**: Technology names remain in English (Redis, Kafka, Docker, etc.)
- **No Fabrication**: Only generates diagrams with sufficient FDD information
- **Separate Files**: Each diagram level gets its own `.puml` file
- **PNG Generation**: Requires PlantUML installation (`brew install plantuml` on macOS)
- **UTF-8 Support**: All `.puml` files include UTF-8 charset declaration for proper accent rendering
- **Skipped Levels**: If a level lacks sufficient information, it's skipped and documented

### Mermaid Diagrams

- **Significance First**: Only generates diagrams that significantly enhance comprehension
- **Typical Count**: 6-8 diagrams per FDD (up to 10 maximum if truly justified)
- **Language Matching**: Document and diagrams match FDD language with proper accents
- **Single File**: All diagrams in one self-contained markdown file
- **Multiple Types Allowed**: Can generate multiple diagrams of the same type if they serve different purposes
- **Concise Labels**: Maximum 3 words per node label
- **Clean Syntax**: Automatic syntax validation and guardrails

### FDD Requirements

- **Format**: Markdown file describing the feature/system
- **Content**: Should include architecture, components, flows, and technical details
- **Language**: Can be in any language (English, Portuguese, Spanish, etc.)
- **Structure**: No specific structure required, but more detail enables better diagrams

## Troubleshooting

| Issue | Solution |
|-------|----------|
| FDD file not found | Verify the path to the FDD file is correct |
| No diagrams generated | Check if FDD has sufficient architectural information |
| PNG generation fails | Install PlantUML: `brew install plantuml` (macOS) or `apt-get install plantuml` (Linux) |
| Accents not rendering | Ensure `.puml` files include `!pragma charset UTF-8` (automatically added) |
| Too many diagrams | Mermaid generator limits to 10 maximum; adjust FDD detail level |
| Syntax errors | Check Mermaid syntax in generated file; agent validates automatically |

## Differences: C4 vs Mermaid

**C4 Diagrams**:
- Focus: Comprehensive architecture visualization (4 levels)
- Format: PlantUML (`.puml` files)
- Best for: Complete system architecture documentation
- Output: Multiple files (one per level) + analysis document
- Rendering: Requires PlantUML viewer or PNG generation

**Mermaid Diagrams**:
- Focus: Specific technical flows and relationships
- Format: Mermaid (embedded in markdown)
- Best for: Flowcharts, sequences, class diagrams, ER diagrams
- Output: Single markdown file with all diagrams
- Rendering: Renders directly in markdown viewers (GitHub, GitLab, etc.)

Choose C4 for comprehensive architecture documentation, Mermaid for specific technical flows and relationships.

