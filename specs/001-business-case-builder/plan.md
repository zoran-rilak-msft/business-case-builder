# Implementation Plan: Business Case Builder Agent

**Branch**: `001-business-case-builder` | **Date**: 2026-03-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-business-case-builder/spec.md`

## Summary

Build a GitHub Copilot agent (`@business-case-builder`) that accepts a feature description, researches business value across eight defined categories using Copilot's built-in tools (WorkIQ MCP for M365 data, web search for public Internet), and produces a Word document report with hard dollar value estimates, confidence ratings, source citations, and visual aids. The agent runs inside GitHub Copilot Chat, leveraging Copilot's own LLM for reasoning and orchestration, and calls Python helper scripts via bash for document generation and input parsing.

## Technical Context

**Language/Version**: Python 3.12+ (helper scripts only; agent orchestration is Copilot-native)
**Primary Dependencies**: python-docx (Word generation), matplotlib (charts), python-pptx (PPTX input parsing), azure-devops (ADO work item fetching), pydantic (data validation in scripts)
**Storage**: File-system based — generated reports saved as .docx files; no database; conversation state managed by Copilot Chat context
**Testing**: pytest for helper scripts
**Target Platform**: GitHub Copilot Chat (VS Code, CLI, GitHub.com); helper scripts cross-platform (macOS, Linux, Windows)
**Project Type**: Copilot agent — `.github/agents/` definition + Python helper scripts invoked via bash
**Performance Goals**: Report generation script completes within 30 seconds; interactive Q&A handled at conversational speed by Copilot
**Constraints**: Must operate within user's existing M365 permissions (via WorkIQ MCP); Copilot provides the LLM — no separate Azure OpenAI setup; helper scripts must be runnable from Copilot's bash tool
**Scale/Scope**: Single-user Copilot agent; processes one feature per conversation; report output typically 5–20 pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: N/A — Constitution has not been configured for this project (template only). No gates to enforce.

*Recommendation*: Run `/speckit.constitution` to define project principles before implementation begins.

## Project Structure

### Documentation (this feature)

```text
specs/001-business-case-builder/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
.github/
├── agents/
│   └── bcb.agent.md             # Agent definition (instructions, handoffs)
└── prompts/
    └── bcb.prompt.md            # Prompt stub referencing the agent

scripts/
├── generate_report.py           # Word document assembly from JSON input
├── generate_charts.py           # Chart/graph generation (matplotlib → PNG)
├── parse_pptx.py                # Extract text from PowerPoint files
├── fetch_ado_item.py            # Fetch ADO work item details
└── check_setup.py               # Verify Python deps and environment

templates/
└── business-case-template.dotx  # Word document template (styles, branding)

tests/
├── test_generate_report.py
├── test_generate_charts.py
├── test_parse_pptx.py
├── test_fetch_ado_item.py
├── fixtures/                    # Sample inputs for tests
│   ├── sample-feature.json
│   ├── sample-presentation.pptx
│   └── sample-ado-response.json
└── conftest.py

pyproject.toml                   # Python project config (deps, scripts)
```

**Structure Decision**: Copilot agent with helper scripts. The agent definition (`.github/agents/bcb.agent.md`) contains the full prompt and orchestration logic. Python scripts under `scripts/` handle tasks that require libraries (Word generation, chart creation, PPTX parsing, ADO access). Copilot invokes these scripts via its bash tool. This keeps the architecture minimal — Copilot IS the orchestrator, and Python is used only where libraries are needed.

## Complexity Tracking

> No constitution violations to justify — constitution not configured.
