# Agent Contract: Business Case Builder

**Branch**: `001-business-case-builder` | **Date**: 2026-03-10

## Agent: `@bcb`

The Business Case Builder is a GitHub Copilot agent defined in `.github/agents/bcb.agent.md`. Users invoke it in Copilot Chat to analyze a feature and generate a business case report.

### Invocation

```
@bcb [OPTIONS] <FEATURE_DESCRIPTION>
```

### Input Formats

| Format | Syntax | Description |
|--------|--------|-------------|
| Freeform text | `@bcb Add SSO to our SaaS platform` | Direct feature description |
| Text file | `@bcb --file path/to/description.txt` | Read description from file |
| ADO work item | `@bcb --ado-item 12345` | Fetch feature from Azure DevOps |
| PowerPoint | `@bcb --pptx path/to/deck.pptx` | Extract feature from presentation |

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `--autonomous` | false | Run without interactive prompts; document all assumptions |
| `--output <path>` | auto-generated | Output path for the Word document |
| `--source <url>` | — | Additional source URL to search (repeatable) |

### Input Precedence

When multiple inputs are provided: `--ado-item` > `--pptx` > `--file` > positional text. Only one source is used per invocation.

### Agent Workflow

```
1. Parse Input
   ├── Freeform text: use directly
   ├── --file: read file contents
   ├── --pptx: call `python scripts/parse_pptx.py`
   └── --ado-item: call `python scripts/fetch_ado_item.py`

2. Feature Comprehension
   └── LLM analyzes description → identifies actors, impact, applicable categories

3. Research (parallel where possible)
   ├── WorkIQ: search SharePoint, Outlook, Teams for internal evidence
   ├── web_search: find industry benchmarks, case studies, market data
   └── Additional --source URLs if provided

4. Business Value Estimation
   └── For each applicable category: estimate value, assign confidence, cite sources

5. Interactive Review (unless --autonomous)
   ├── Present findings summary to user
   ├── Ask clarifying questions (max 10 turns)
   └── Request confirmation before report generation

6. Report Generation
   ├── Structure findings as JSON
   ├── Call `python scripts/generate_charts.py` for visualizations
   ├── Call `python scripts/generate_report.py` for Word document
   └── Report output file path to user
```

### Tools Used

| Tool | Purpose |
|------|---------|
| `bash` | Invoke Python helper scripts (report generation, chart creation, PPTX parsing, ADO fetching) |
| `web_search` | Search public Internet for industry benchmarks, case studies, market data |
| `workiq` | Query M365 data — SharePoint documents, Outlook emails, Teams messages |
| `view` / `create` | Read input files; write intermediate JSON |
| `ask_user` | Interactive clarification questions |

### Helper Scripts

| Script | Input | Output | Purpose |
|--------|-------|--------|---------|
| `scripts/generate_report.py` | `--input <json>` `--output <docx>` `--charts-dir <dir>` | `.docx` file | Assemble Word document from JSON findings |
| `scripts/generate_charts.py` | `--input <json>` `--output-dir <dir>` | PNG files | Generate matplotlib charts for embedding |
| `scripts/parse_pptx.py` | `--input <pptx>` | JSON to stdout | Extract text from PowerPoint slides |
| `scripts/fetch_ado_item.py` | `--item-id <id>` `--org <url>` | JSON to stdout | Fetch ADO work item details |
| `scripts/check_setup.py` | (none) | Status to stdout | Verify Python dependencies |

### Output

Reports are saved to the working directory with auto-generated names:

```
business-case-<sanitized-title>-<YYYY-MM-DD>.docx
```

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ADO_ORG_URL` | Only for `--ado-item` | Azure DevOps organization URL |
| `ADO_PAT` | Only for `--ado-item` | Azure DevOps Personal Access Token |

All other services (LLM, M365 data, web search) are provided by Copilot's built-in tools.

### Handoffs

After report generation, the agent offers follow-up actions:

| Label | Description |
|-------|-------------|
| Refine Estimates | Re-run analysis with user corrections or additional sources |
| Executive Summary Only | Generate a 1-page summary version of the report |
