# Business Case Builder (`@business-case-builder`)

A GitHub Copilot agent that analyzes feature descriptions, researches business value across multiple sources, and generates comprehensive Word document reports with hard dollar estimates, charts, and source citations.

## Prerequisites

- **Python 3.12+**
- **GitHub Copilot** with agent support enabled
- **WorkIQ** (Microsoft 365 Copilot) enabled for M365 data access
- **Azure DevOps PAT** (optional, only for `--ado-item` input)
- **Azure AD app registration** (optional, for direct SharePoint document search — see [SharePoint Setup](#sharepoint-direct-search-setup))

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
@business-case-builder Add single sign-on authentication to our SaaS platform
```

### From a file
```
@business-case-builder --file docs/feature-proposal.md
```

### From a PowerPoint deck
```
@business-case-builder --pptx presentations/product-roadmap.pptx
```

### From an Azure DevOps work item
```
@business-case-builder --ado-item 12345
```

### Autonomous mode (no interactive prompts)
```
@business-case-builder --autonomous Implement real-time collaboration features
```

### Custom output path
```
@business-case-builder --output reports/sso-business-case.docx Add SSO to our platform
```

### Scoped SharePoint search
```
@business-case-builder --sharepoint-site https://contoso.sharepoint.com/sites/engineering Add TLS certificate management
```

## What the Agent Does

1. **Parses input** — accepts text, files, PPTX decks, or ADO work items
2. **Comprehends the feature** — extracts title, purpose, target users, impact areas
3. **Researches evidence** — searches M365 (SharePoint, Outlook, Teams) via WorkIQ, downloads and analyzes full SharePoint documents via Microsoft Graph, and searches the public internet
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
  search_sharepoint.py    # SharePoint search & document text extraction (Graph API)
  sharepoint_auth.py      # MSAL device-code authentication for Graph
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
  test_search_sharepoint.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ADO_ORG_URL` | For `--ado-item` only | Azure DevOps organization URL |
| `ADO_PAT` | For `--ado-item` only | Azure DevOps Personal Access Token |
| `BCB_GRAPH_CLIENT_ID` | For SharePoint search only | Azure AD application (client) ID |

## SharePoint Direct Search Setup

The agent can search SharePoint via WorkIQ (no setup needed) for quick natural-language queries. For **full document download and analysis**, configure direct Graph API access:

### 1. Register an Azure AD application

1. Go to [Azure Portal → App registrations](https://portal.azure.com/#view/Microsoft_AAD_RegisteredApps/ApplicationsListBlade)
2. Click **New registration**
3. Name: `Business Case Builder` (or any name)
4. Supported account types: **Accounts in this organizational directory only**
5. Redirect URI: **Public client/native (mobile & desktop)** → `http://localhost`
6. Click **Register**

### 2. Configure API permissions

1. Go to **API permissions** → **Add a permission** → **Microsoft Graph** → **Delegated permissions**
2. Add: `Sites.Read.All`, `Files.Read.All`
3. Click **Grant admin consent** (or ask your IT admin)

### 3. Set the environment variable

```bash
export BCB_GRAPH_CLIENT_ID="your-app-client-id-here"
```

### 4. Authenticate (first use)

```bash
python scripts/search_sharepoint.py --login
```

This opens a device-code flow — follow the on-screen instructions to sign in. Tokens are cached at `~/.bcb/graph_token_cache.bin` for subsequent runs.

## License

Internal use only.
