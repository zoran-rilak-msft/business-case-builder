# Business Case Builder (`@bcb`)

A GitHub Copilot agent that analyzes feature descriptions, researches business value across multiple sources, and generates comprehensive Word document reports with hard dollar estimates, charts, and source citations.

## Prerequisites

- **Python 3.12+**
- **GitHub Copilot** with agent support enabled
- **WorkIQ** (Microsoft 365 Copilot) enabled for M365 data access
- **Azure DevOps PAT** (optional, only for `--ado-item` input)

## Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .

# Verify setup
python scripts/check_setup.py
```

## Usage

Invoke the agent in GitHub Copilot Chat:

### Basic — from text description
```
@bcb Add single sign-on authentication to our SaaS platform
```

### From a file
```
@bcb --file docs/feature-proposal.md
```

### From a PowerPoint deck
```
@bcb --pptx presentations/product-roadmap.pptx
```

### From an Azure DevOps work item
```
@bcb --ado-item 12345
```

### Autonomous mode (no interactive prompts)
```
@bcb --autonomous Implement real-time collaboration features
```

### Custom output path
```
@bcb --output reports/sso-business-case.docx Add SSO to our platform
```

## What the Agent Does

1. **Parses input** — accepts text, files, PPTX decks, or ADO work items
2. **Comprehends the feature** — extracts title, purpose, target users, impact areas
3. **Researches evidence** — searches M365 (SharePoint, Outlook, Teams) via WorkIQ and the public internet
4. **Estimates business value** across 8 categories:
   - Revenue and Monetization
   - Cost Reduction and Avoidance
   - User and Adoption Value
   - Risk Reduction and Mitigation
   - Productivity and Time Value
   - Strategic and Competitive Value
   - Customer Experience and Brand Value
   - Organizational and Capability Value
5. **Interactive review** — presents findings, asks clarifying questions, allows revisions
6. **Generates report** — Word document with executive summary, value analysis, charts, and citations

## Output

The agent produces a `.docx` Word document containing:
- Cover page with feature title and date
- Executive summary with total value range
- Detailed business value analysis per category
- Charts (horizontal bar, waterfall, error bar)
- Leading indicators table
- Strategic value narrative
- Source citations with reliability ratings

## Development

```bash
# Activate venv
source .venv/bin/activate

# Run tests
python -m pytest tests/ -v

# Run linter
python -m ruff check scripts/ tests/

# Check dependencies
python scripts/check_setup.py
```

## Project Structure

```
.github/
  agents/
    bcb.agent.md          # Copilot agent definition
  prompts/
    bcb.prompt.md         # Prompt stub
scripts/
  models.py               # Pydantic data models
  generate_charts.py      # Chart generation (matplotlib)
  generate_report.py      # Report assembly (python-docx)
  parse_pptx.py           # PowerPoint text extraction
  fetch_ado_item.py       # Azure DevOps work item fetcher
  check_setup.py          # Dependency verification
templates/
  business-case-template.dotx  # Word document template
tests/
  conftest.py             # Shared fixtures
  fixtures/               # Test data files
  test_generate_charts.py
  test_generate_report.py
  test_parse_pptx.py
  test_fetch_ado_item.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ADO_ORG_URL` | For `--ado-item` only | Azure DevOps organization URL |
| `ADO_PAT` | For `--ado-item` only | Azure DevOps Personal Access Token |

## License

Internal use only.
