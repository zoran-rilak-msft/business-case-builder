# Research: Business Case Builder Agent

**Branch**: `001-business-case-builder` | **Date**: 2026-03-10

## R1: Agent Architecture — Copilot-Native vs Standalone

**Decision**: GitHub Copilot agent (`.github/agents/bcb.agent.md`) with Python helper scripts

**Rationale**: The agent runs inside GitHub Copilot Chat, which provides LLM reasoning, conversational UI, tool orchestration (bash, file I/O, MCP tools), and user authentication — all out of the box. This eliminates the need for a standalone framework (Semantic Kernel, LangChain), custom authentication (MSAL), or a terminal UI (Rich). Python is used only for tasks requiring libraries: Word document generation, chart rendering, PPTX parsing, and ADO API calls.

**Architecture**:
- **Orchestration**: Copilot's agent system — instructions in `.agent.md` define the workflow
- **LLM**: Copilot's built-in model — no Azure OpenAI setup
- **M365 data**: WorkIQ MCP tool (already available in Copilot) — SharePoint, Outlook, Teams
- **Web search**: Copilot's built-in `web_search` tool
- **Document generation**: Python scripts invoked via Copilot's bash tool
- **Interactive mode**: Copilot Chat conversation (native)
- **Autonomous mode**: Agent instructions tell Copilot to skip confirmations and document assumptions

**Alternatives Considered**:
- **Standalone Python CLI with Semantic Kernel**: Full control but requires building auth, UI, LLM integration, and tool orchestration from scratch — duplicates what Copilot already provides.
- **M365 Copilot declarative agent**: Tighter M365 integration but more restrictive platform; harder to call arbitrary scripts for document generation.
- **Teams bot**: Good for M365 context but requires Azure Bot Service deployment; heavier infrastructure.

## R2: M365 Data Access via WorkIQ MCP

**Decision**: Use WorkIQ MCP tool for all M365 data access (SharePoint, Outlook, Teams)

**Rationale**: WorkIQ is already available as an MCP tool in Copilot. It provides natural-language querying of M365 data — emails, meetings, documents, Teams messages, and people information — without requiring direct Graph API calls, app registrations, or permission management. The agent's instructions simply tell Copilot to use WorkIQ for M365 research, and Copilot handles authentication through the user's existing session.

**Capabilities**:
- SharePoint document search ("find documents about [topic] on SharePoint")
- Outlook email search ("find emails about [feature] from the last 6 months")
- Teams message search ("what was discussed about [topic] in Teams")
- People information ("who is working on [project]")

**Limitations**:
- Results are natural-language summaries, not structured API responses
- Cannot perform complex Graph API queries (e.g., pagination, field filtering)
- Subject to the user's M365 permissions

**Alternatives Considered**:
- **Direct Microsoft Graph SDK calls from Python scripts**: More control and structured data, but requires app registration, MSAL authentication, and permission grants — significant setup friction for users.
- **Graph API via Copilot's bash tool + curl**: Possible but requires manual token management.

## R3: Azure DevOps Work Item Access

**Decision**: Python helper script (`scripts/fetch_ado_item.py`) using `azure-devops` SDK v7.1.0b4 with PAT authentication

**Rationale**: ADO work item fetching requires structured field access (title, description, acceptance criteria, linked items) that is better served by the official SDK than natural-language queries. The script accepts a work item ID and ADO org URL, authenticates via PAT (from environment variable), and outputs structured JSON that the Copilot agent can parse. This is a simple, focused script with one job.

**Authentication**: PAT stored in `ADO_PAT` environment variable. Entra ID via MSAL is an upgrade path for enterprise deployment.

**Alternatives Considered**:
- **WorkIQ for ADO**: WorkIQ focuses on M365 data; ADO access may not be available or may return less structured results.
- **Direct REST API with curl**: Viable but the SDK handles pagination, typed responses, and error handling more robustly.

## R4: Word Document Generation

**Decision**: Python script (`scripts/generate_report.py`) using python-docx v1.2.0+ with a `.dotx` template, charts embedded as 300 DPI PNGs from matplotlib

**Rationale**: python-docx is the de facto standard for Word generation in Python. Using a `.dotx` template pre-loaded with professional styles ensures consistent, polished output. The Copilot agent collects all analysis results, structures them as JSON, and passes the JSON to the script which assembles the document. This separation means the agent focuses on reasoning while the script handles formatting.

**Workflow**:
1. Copilot agent performs analysis, structures findings as JSON
2. Agent writes JSON to a temp file
3. Agent calls `python scripts/generate_report.py --input findings.json --output report.docx`
4. Script reads JSON, generates charts (matplotlib → PNG), assembles Word document
5. Agent reports the output file path to the user

**Report Sections** (from business case best practices):
1. Cover page (feature name, date, author)
2. Executive summary
3. Feature overview
4. Business value analysis by category (with charts)
5. Leading indicators and outcome linkage
6. Strategic value assessment
7. Assumptions and methodology
8. Source citations and references

**Chart Types**:
- Horizontal stacked bar: value breakdown by category
- Grouped bar: cost/revenue comparisons
- Waterfall: cumulative value build-up
- Error bar: confidence ranges per category

**Alternatives Considered**:
- **Plotly static export**: Better aesthetics for some charts, but requires kaleido dependency; matplotlib is sufficient.
- **Jinja2 + docxtpl**: Template-based Word generation; less control over programmatic chart insertion.
- **Markdown → Word conversion (pandoc)**: Loses fine-grained formatting control needed for professional reports.

## R5: PowerPoint Input Parsing

**Decision**: Python script (`scripts/parse_pptx.py`) using python-pptx v1.0.2+

**Rationale**: python-pptx reliably extracts text from slide shapes, text boxes, tables, and speaker notes. The script accepts a PPTX file path and outputs extracted text as JSON, which the Copilot agent can then analyze. Read-only operation is the most stable part of the library.

**Known Limitations**: SmartArt and OLE objects may not yield text; image-heavy presentations have minimal extractable content. The agent should warn the user if extracted content is sparse.

**Alternatives Considered**:
- **Apache Tika**: More comprehensive but requires Java runtime.
- **LibreOffice headless conversion**: Heavy dependency; overkill for text extraction.

## R6: Web Search for Public Internet Evidence

**Decision**: Copilot's built-in `web_search` tool

**Rationale**: Copilot already provides a web search tool that returns AI-generated responses with citations. The agent's instructions tell Copilot to search for industry benchmarks, market data, analyst reports, and case studies relevant to the feature being analyzed. No additional API keys or dependencies needed.

**Usage Pattern**: The agent issues targeted searches like:
- "What is the average ROI for implementing [feature type] in [industry]?"
- "Industry benchmarks for [metric] improvement from [capability]"
- "Case studies of [similar feature] business impact"

**Alternatives Considered**:
- **Bing Web Search API from Python script**: More control over result parsing, but requires Azure subscription and API key; Copilot's built-in search is sufficient.
- **DuckDuckGo search library**: Free but unreliable; adds a dependency for something Copilot already handles.

## R7: Agent Definition Pattern

**Decision**: Single `.github/agents/bcb.agent.md` file with comprehensive instructions + `.github/prompts/bcb.prompt.md` stub

**Rationale**: Following the established pattern in this repository (speckit agents). The agent file contains YAML frontmatter (description, handoffs) and markdown instructions that define the full workflow: input handling, feature comprehension, multi-source research, business value estimation, interactive Q&A, and report generation. The agent uses `$ARGUMENTS` for user input and invokes helper scripts via Copilot's bash tool.

**Handoffs**: After report generation, the agent can suggest follow-up actions (e.g., "Refine estimates", "Add more sources", "Generate executive summary only").

**Agent Capabilities** (via Copilot's tools):
- `bash` — invoke Python helper scripts
- `web_search` — search public Internet
- `workiq` — query M365 data (SharePoint, Outlook, Teams)
- `view/edit/create` — read and write files
- `ask_user` — interactive clarification questions

## R8: LLM Strategy for Business Value Estimation

**Decision**: Copilot's built-in LLM with structured prompting in agent instructions

**Rationale**: The agent instructions include detailed guidance for how Copilot should reason about business value: category definitions, estimation methodology, confidence scoring criteria, and anti-hallucination rules. All dollar estimates must be grounded in source data (from WorkIQ or web search) or explicitly stated assumptions. The agent instructions enforce the pattern: research first, estimate second, cite always.

**Anti-hallucination rules** (embedded in agent instructions):
- Every dollar estimate must reference at least one source or explicit assumption
- Use ranges ("$X–$Y") rather than point estimates
- Flag low-confidence estimates explicitly
- Omit categories with no supporting evidence rather than speculate
- Clearly separate "data-backed" from "assumption-based" estimates

**Prompting approach**: The agent instructions define a step-by-step reasoning chain:
1. Comprehend feature → identify applicable categories
2. Research each category via WorkIQ + web search
3. For each category with evidence: estimate value, assign confidence, cite sources
4. For each category without evidence: omit with explanation
5. Structure all findings as JSON → pass to report generation script
