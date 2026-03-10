# Quickstart: Business Case Builder Agent

**Branch**: `001-business-case-builder` | **Date**: 2026-03-10

## Prerequisites

- GitHub Copilot with agent support (VS Code, Copilot CLI, or GitHub.com)
- Python 3.12 or higher (for helper scripts)
- WorkIQ MCP tool enabled in Copilot (for M365 data access)
- Azure DevOps PAT (optional, only for `--ado-item` input)

## Installation

```bash
# Clone and enter project
git clone <repo-url>
cd business-case-builder

# Install Python helper script dependencies
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

pip install -e ".[dev]"
```

## Configuration

For ADO work item input support, set environment variable:

```bash
export ADO_ORG_URL=https://dev.azure.com/<your-org>
export ADO_PAT=<your-pat>
```

No other configuration is needed — Copilot handles LLM access and WorkIQ handles M365 authentication.

## Using the Agent

### In Copilot Chat (VS Code or CLI)

```
@bcb Add single sign-on authentication to our SaaS platform
```

The agent will:
1. Analyze your feature description
2. Search M365 sources (via WorkIQ) and public Internet for business value evidence
3. Ask clarifying questions (interactive mode, default)
4. Present findings and ask for confirmation
5. Generate a Word document business case report

### Autonomous Mode

```
@bcb --autonomous Add single sign-on authentication to our SaaS platform
```

The agent proceeds without interactive prompts and documents all assumptions.

### Input from Files

```
@bcb --file feature-description.txt
@bcb --pptx feature-deck.pptx
@bcb --ado-item 12345
```

### Output

Reports are saved to the working directory:

```
./business-case-<feature-title>-<date>.docx
```

## Development

```bash
# Run helper script tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html

# Lint
ruff check scripts/ tests/
```

## Verify Setup

```bash
# Check Python dependencies are installed
python scripts/check_setup.py

# Expected output:
# ✓ python-docx: installed (1.2.0)
# ✓ matplotlib: installed (3.9.0)
# ✓ python-pptx: installed (1.0.2)
# ✓ azure-devops: installed (7.1.0b4)
# ✓ All dependencies available
```
