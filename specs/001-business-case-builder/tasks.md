# Tasks: Business Case Builder Agent

**Input**: Design documents from `/specs/001-business-case-builder/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and dependency management

- [x] T001 Create project directory structure: scripts/, templates/, tests/, tests/fixtures/
- [x] T002 Create pyproject.toml with dependencies: python-docx, matplotlib, python-pptx, azure-devops, pydantic, and dev dependencies: pytest, ruff
- [x] T003 [P] Create .github/prompts/bcb.prompt.md as a prompt stub with `agent: bcb` frontmatter
- [x] T004 [P] Configure ruff for linting in pyproject.toml with target Python 3.12+

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Shared data models, templates, and test infrastructure that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Create scripts/models.py with Pydantic models for all JSON contracts: ReportInput (feature, value_estimates, leading_indicators, strategic_value, assumptions_made), ChartRequest (charts list with chart_type, data, style), PptxOutput (slides with body_text, speaker_notes), and AdoItemOutput (id, title, description, acceptance_criteria, linked_items) — use schemas from data-model.md
- [x] T006 [P] Create templates/business-case-template.dotx — a Word document template with professional styles: Heading 1-3 hierarchy (Calibri, navy accent), styled tables (light header row), page headers/footers with page numbers, 1-inch margins, and a cover page layout placeholder
- [x] T007 [P] Create scripts/check_setup.py — verify all Python dependencies are importable, print version for each, exit 0 if all present or exit 1 with missing list
- [x] T008 [P] Create tests/conftest.py with shared pytest fixtures: tmp_output_dir (temporary directory for test outputs), sample_report_input (minimal valid ReportInput dict), and sample_chart_request (minimal valid ChartRequest dict)

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 — Generate Business Case from Feature Description (Priority: P1) 🎯 MVP

**Goal**: User provides a freeform text feature description via `@bcb`, the agent analyzes it for business value across 8 categories, and generates a Word document report with hard dollar estimates, confidence ratings, source citations, and charts.

**Independent Test**: Invoke `@bcb Add single sign-on to our SaaS platform` and verify a .docx file is produced containing: executive summary, at least one dollar estimate with reasoning, confidence levels, and at least one embedded chart.

### Implementation for User Story 1

- [x] T009 [US1] Create .github/agents/bcb.agent.md with YAML frontmatter (description: "Build a business case report for a feature", handoffs for "Refine Estimates" and "Executive Summary Only") and core agent instructions: $ARGUMENTS input parsing, feature comprehension workflow (extract title, purpose, target users, expected impact), business value category evaluation against all 8 categories from spec.md (Revenue/Monetization, Cost Reduction, User/Adoption, Risk Reduction, Productivity, Strategic/Competitive, Customer Experience, Organizational Capability), confidence scoring criteria (weak/medium/strong per data-model.md), JSON structuring of findings matching ReportInput schema from scripts/models.py, and bash invocations for generate_charts.py and generate_report.py with file path reporting to user
- [x] T010 [P] [US1] Create scripts/generate_charts.py — accept --input <json-path> (ChartRequest schema) and --output-dir <dir>, generate matplotlib charts as 300 DPI PNGs: horizontal_bar (value breakdown by category), grouped_bar (cost/revenue comparison), waterfall (cumulative value build-up), error_bar (confidence ranges per category); output one PNG per chart named {chart_id}.png; use professional styling (Calibri font, navy/gray palette, no gridlines, data labels)
- [x] T011 [P] [US1] Create tests/test_generate_charts.py — test each chart type generates a valid PNG file, test invalid JSON input raises clear error, test output directory is created if missing, test chart dimensions match requested figsize
- [x] T012 [US1] Create scripts/generate_report.py — accept --input <json-path> (ReportInput schema), --output <docx-path>, --template <dotx-path> (optional, defaults to templates/business-case-template.dotx), --charts-dir <dir> (optional); assemble Word document sections: cover page (feature title, date, mode), executive summary (from strategic_value.summary + top value estimates), feature overview (from feature.description, target_users, source_format), business value analysis (one subsection per value_estimate with dollar range, confidence badge, reasoning, methodology, assumptions, and citation references), leading indicators table (from leading_indicators array), strategic value narrative, assumptions and methodology section, source citations table (numbered references with source_type, title, url, excerpt, reliability); embed chart PNGs from charts-dir where referenced; auto-generate output filename if --output not provided: business-case-{sanitized-title}-{YYYY-MM-DD}.docx
- [x] T013 [US1] Create tests/test_generate_report.py — test report generation from sample-feature.json produces valid .docx, test all required sections are present (exec summary, value analysis, citations), test chart embedding works with sample PNGs, test missing template falls back to plain document, test output filename auto-generation
- [x] T014 [P] [US1] Create tests/fixtures/sample-feature.json — a complete ReportInput JSON with: feature (title: "SSO Integration", description, target_users, source_format: "text"), 3 value_estimates across different categories (one with is_hard_dollar: true, varying confidence levels, 2+ citations each), leading_indicators (2 entries), strategic_value, assumptions_made (3 items), mode: "interactive"

**Checkpoint**: User Story 1 is fully functional — `@bcb [text]` produces a complete Word document business case report

---

## Phase 4: User Story 2 — Interactive Feature Exploration (Priority: P2)

**Goal**: The agent engages in interactive dialogue, asking clarifying questions and presenting findings for user confirmation before generating the report. This is the default mode.

**Independent Test**: Invoke `@bcb Improve performance` (deliberately vague) and verify the agent asks at least one clarifying question, presents a summary of findings, and requests confirmation before generating the report.

### Implementation for User Story 2

- [x] T015 [US2] Update .github/agents/bcb.agent.md — insert interactive workflow section after feature comprehension: (1) identify aspects of the feature that are unclear or could significantly affect value estimation, (2) use ask_user tool to ask up to 3 targeted clarifying questions (scope boundaries, user types, expected scale), (3) incorporate answers into the analysis, (4) after value estimation, present a structured findings summary to the user (markdown table of categories, estimates, confidence), (5) use ask_user to request confirmation ("Proceed with report generation?" with choices: Yes / Revise estimates / Add more context), (6) handle revision loop (user provides corrections, agent updates estimates, re-presents), (7) only invoke report generation scripts after user confirms
- [x] T016 [US2] Update .github/agents/bcb.agent.md — add contradiction detection: if user provides information that conflicts with earlier answers or the original description, surface the contradiction with both interpretations and ask the user to resolve before proceeding

**Checkpoint**: Default invocation is now interactive — agent asks questions and confirms before generating the report

---

## Phase 5: User Story 3 — Multi-Source Evidence Gathering (Priority: P3)

**Goal**: The agent searches M365 data (via WorkIQ) and public Internet (via web_search) to find evidence supporting business value estimates. Every claim is backed by a citation.

**Independent Test**: Invoke `@bcb Implement automated CI/CD pipeline` and verify the report includes citations from at least two distinct source types (e.g., internet + sharepoint) and that each value estimate references at least one source.

### Implementation for User Story 3

- [x] T017 [P] [US3] Update .github/agents/bcb.agent.md — add WorkIQ research instructions: for each applicable business value category, formulate WorkIQ queries to search SharePoint ("find documents about [feature domain] business case on SharePoint"), Outlook ("find emails about [feature] priorities or budget from the last 6 months"), and Teams ("what was discussed about [feature domain] in Teams"); extract relevant findings; format as SourceCitation objects with source_type, title, excerpt, and reliability classification
- [x] T018 [P] [US3] Update .github/agents/bcb.agent.md — add web search research instructions: for each applicable category, issue targeted web_search queries for industry benchmarks ("average ROI for [feature type] in [industry]"), case studies ("business impact of [similar feature] case study"), and market data ("market size for [capability]"); extract findings with URLs; classify source reliability (primary/secondary/tertiary per data-model.md)
- [x] T019 [US3] Update .github/agents/bcb.agent.md — add citation management: every value estimate MUST include at least one citation; estimates with no supporting evidence from any source are omitted from the report; agent tracks which sources were searched and which were unavailable; sources_unavailable list is populated in the ReportInput JSON
- [x] T020 [US3] Update scripts/generate_report.py — enhance citations section: add numbered footnote-style references from value estimate text to citation table, add source reliability badges (Primary ★★★, Secondary ★★, Tertiary ★), add "Sources Searched" appendix listing all queries performed and their result counts

**Checkpoint**: Reports now contain sourced, verifiable citations from M365 and public Internet

---

## Phase 6: User Story 4 — Multi-Format Input Support (Priority: P4)

**Goal**: Users can provide feature descriptions as text files, Azure DevOps work items, or PowerPoint presentations in addition to freeform text.

**Independent Test**: Invoke `@bcb --ado-item 12345` and `@bcb --pptx deck.pptx` and verify both produce equivalent business case reports with extracted feature information.

### Implementation for User Story 4

- [x] T021 [P] [US4] Create scripts/parse_pptx.py — accept --input <pptx-path>, iterate all slides extracting text from shapes (.text property), speaker notes (.notes_slide.notes_text_frame.text), and table cells; output PptxOutput JSON (per data-model.md) to stdout; handle errors gracefully: warn on empty slides, skip unreadable shapes, report extraction summary (slides parsed, text length)
- [x] T022 [P] [US4] Create tests/test_parse_pptx.py — test text extraction from shapes and speaker notes, test handling of empty presentation, test table data extraction, test error handling for corrupt file
- [x] T023 [P] [US4] Create tests/fixtures/sample-presentation.pptx — a 3-slide PPTX with: slide 1 (title + body text), slide 2 (bullet points + speaker notes), slide 3 (table with sample data)
- [x] T024 [P] [US4] Create scripts/fetch_ado_item.py — accept --item-id <id> and --org <url>, authenticate with ADO_PAT env var via azure-devops SDK BasicAuthentication, fetch work item with expand=all, extract System.Title, System.Description, Microsoft.VSTS.Common.AcceptanceCriteria, work item type, state, tags, and linked items (relations); output AdoItemOutput JSON (per data-model.md) to stdout; exit 1 with clear error if ADO_PAT not set or work item not found
- [x] T025 [P] [US4] Create tests/test_fetch_ado_item.py — test JSON output structure matches AdoItemOutput schema, test missing ADO_PAT env var produces clear error, test work item not found produces clear error (mock SDK responses)
- [x] T026 [P] [US4] Create tests/fixtures/sample-ado-response.json — a mock ADO work item response with: id, title, description (HTML), acceptance criteria, type "Feature", 2 linked child items
- [x] T027 [US4] Update .github/agents/bcb.agent.md — add multi-format input handling: detect --file, --pptx, --ado-item flags from $ARGUMENTS; for --file: read file contents with view tool; for --pptx: invoke `python scripts/parse_pptx.py --input <path>` and parse PptxOutput JSON; for --ado-item: invoke `python scripts/fetch_ado_item.py --item-id <id> --org $ADO_ORG_URL` and parse AdoItemOutput JSON; apply input precedence (ado-item > pptx > file > text); warn if multiple formats provided; for unsupported formats: inform user of accepted formats

**Checkpoint**: Users can provide input as freeform text, text file, PPTX, or ADO work item link

---

## Phase 7: User Story 5 — Autonomous Operation Mode (Priority: P5)

**Goal**: Users can request fully autonomous operation where the agent completes the entire analysis without interactive prompts, documenting all assumptions.

**Independent Test**: Invoke `@bcb --autonomous Add real-time notifications` and verify the agent produces a complete report without any intermediate questions, with an assumptions section listing all decisions made.

### Implementation for User Story 5

- [x] T028 [US5] Update .github/agents/bcb.agent.md — add autonomous mode handling: detect --autonomous flag from $ARGUMENTS; when autonomous: skip all ask_user calls (clarifying questions and confirmation), make reasonable assumptions when encountering ambiguity (document each in assumptions_made array), proceed directly from research to report generation, include all assumptions prominently in the ReportInput JSON; ensure autonomous mode still performs WorkIQ and web search research (don't skip evidence gathering)
- [x] T029 [US5] Update scripts/generate_report.py — add dedicated "Assumptions and Agent Decisions" section in the report when assumptions_made is non-empty: list each assumption with context explaining why the assumption was necessary and what alternative interpretations exist; place this section prominently after the executive summary

**Checkpoint**: Users can run `@bcb --autonomous [description]` for unattended, fully automated business case generation

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, configuration, and final validation

- [x] T030 [P] Update .vscode/settings.json — add bcb prompt to chat.promptFilesRecommendations and auto-approve scripts/ directory in chat.tools.terminal.autoApprove
- [x] T031 [P] Create README.md at repository root — project overview, prerequisites (Python 3.12+, Copilot with agent support, WorkIQ enabled), installation instructions (pip install), usage examples (@bcb with all input formats), development guide (running tests, linting)
- [x] T032 Run python scripts/check_setup.py to validate all dependencies are installable
- [x] T033 Run pytest to validate all test suites pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Foundational — no dependencies on other stories
  - US2 (P2): Depends on US1 (adds interactive workflow to agent definition created in US1)
  - US3 (P3): Depends on US1 (adds research workflow to agent definition; enhances generate_report.py from US1)
  - US4 (P4): Depends on US1 (adds input handling to agent definition created in US1); scripts are independent
  - US5 (P5): Depends on US2 (autonomous mode skips interactive workflow from US2)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational
    ↓
Phase 3: US1 — Core Report Generation (P1) 🎯 MVP
    ↓
Phase 4: US2 — Interactive Exploration (P2)     Phase 6: US4 — Multi-Format Input (P4)
    ↓                                                ↑ (scripts are independent, agent update needs US1)
Phase 5: US3 — Multi-Source Evidence (P3)            |
    ↓                                                |
Phase 7: US5 — Autonomous Mode (P5)                  |
    ↓                                                ↓
Phase 8: Polish
```

### Within Each User Story

- Models/contracts before scripts
- Scripts before agent definition updates (agent invokes scripts)
- Tests alongside or after their corresponding scripts
- Agent definition updates are sequential (single file)

### Parallel Opportunities

- Phase 1: T003 and T004 can run in parallel
- Phase 2: T006, T007, T008 can run in parallel (after T005)
- Phase 3 (US1): T010 and T011 can run in parallel; T014 is independent
- Phase 6 (US4): T021–T026 can ALL run in parallel (different scripts/files); T027 is sequential after them
- US3 scripts and US4 scripts can run in parallel (different files, no dependency between them)

---

## Parallel Example: User Story 1

```
# After Foundational phase, launch in parallel:
Task T010: "Create scripts/generate_charts.py"
Task T011: "Create tests/test_generate_charts.py"
Task T014: "Create tests/fixtures/sample-feature.json"

# Then sequential:
Task T009: "Create .github/agents/bcb.agent.md" (core agent definition)
Task T012: "Create scripts/generate_report.py" (uses charts from T010)
Task T013: "Create tests/test_generate_report.py"
```

## Parallel Example: User Story 4

```
# ALL scripts and tests can run in parallel:
Task T021: "Create scripts/parse_pptx.py"
Task T022: "Create tests/test_parse_pptx.py"
Task T023: "Create tests/fixtures/sample-presentation.pptx"
Task T024: "Create scripts/fetch_ado_item.py"
Task T025: "Create tests/test_fetch_ado_item.py"
Task T026: "Create tests/fixtures/sample-ado-response.json"

# Then sequential:
Task T027: "Update .github/agents/bcb.agent.md with multi-format input handling"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Invoke `@bcb Add SSO to our platform` and verify Word report is generated
5. Deploy/demo if ready — user can already generate business cases from text

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP!** (text → report)
3. Add User Story 2 → Test independently → Interactive Q&A before report
4. Add User Story 3 → Test independently → Reports now have sourced citations
5. Add User Story 4 → Test independently → PPTX/ADO/file input supported
6. Add User Story 5 → Test independently → Autonomous mode available
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (core — must complete first)
3. Once US1 is done:
   - Developer A: User Story 2 (interactive mode)
   - Developer B: User Story 4 scripts (parse_pptx.py, fetch_ado_item.py — parallel, independent files)
4. Once US2 is done:
   - Developer A: User Story 5 (autonomous mode — depends on US2)
   - Developer B: User Story 3 (multi-source evidence)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- The agent definition (.github/agents/bcb.agent.md) is the central artifact — most stories update it sequentially
- Helper scripts (scripts/) are independent and can be developed/tested in parallel
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
