# Data Model: Business Case Builder Agent

**Branch**: `001-business-case-builder` | **Date**: 2026-03-10

> **Note**: This agent runs inside GitHub Copilot Chat. Most state is managed by Copilot's conversation context. The data model below defines the **JSON structures** exchanged between the Copilot agent and its Python helper scripts, and the logical entities the agent reasons about.

## JSON Contracts (Agent ↔ Scripts)

### ReportInput (Agent → `generate_report.py`)

The Copilot agent structures its analysis findings as JSON and passes it to the report generation script.

```json
{
  "feature": {
    "title": "string — feature name",
    "description": "string — one-paragraph summary of the feature",
    "target_users": ["string — who benefits"],
    "source_format": "text | file | ado_work_item | pptx",
    "source_reference": "string (optional) — ADO URL, file path, etc."
  },
  "value_estimates": [
    {
      "category_id": "string — e.g., revenue_monetization",
      "category_name": "string — e.g., Revenue and Monetization",
      "subcategory": "string (optional) — e.g., Direct Revenue → New product revenue",
      "dollar_value_low": "number (optional)",
      "dollar_value_high": "number (optional)",
      "dollar_unit": "one_time | per_year | per_month",
      "confidence": "weak | medium | strong",
      "reasoning": "string — how the value was estimated",
      "methodology": "string — calculation or estimation method",
      "assumptions": ["string — assumptions made"],
      "is_hard_dollar": "boolean",
      "citations": [
        {
          "id": "string — e.g., cite-001",
          "source_type": "internet | sharepoint | ado | communications | user_provided",
          "title": "string — source document/page name",
          "url": "string (optional)",
          "excerpt": "string — relevant finding from source",
          "reliability": "primary | secondary | tertiary"
        }
      ]
    }
  ],
  "leading_indicators": [
    {
      "indicator": "string — e.g., MAU growth",
      "linked_outcome": "string — business outcome it drives",
      "expected_impact": "string — e.g., 15% increase in first 6 months"
    }
  ],
  "strategic_value": {
    "summary": "string — strategic value narrative",
    "dimensions": ["string — e.g., Platform optionality, Competitive differentiation"]
  },
  "assumptions_made": ["string — assumptions the agent made during analysis"],
  "sources_unavailable": ["string — sources that could not be accessed"],
  "mode": "interactive | autonomous",
  "generated_at": "ISO 8601 datetime"
}
```

**Validation Rules**:
- `feature.title` and `feature.description` are required
- At least one `value_estimates` entry must have `is_hard_dollar: true`
- Every `value_estimates` entry must have at least one citation
- `confidence` must be one of: `weak`, `medium`, `strong`
- Entries with no citations are omitted from the report (enforced by agent instructions)

---

### PptxOutput (`parse_pptx.py` → Agent)

```json
{
  "file_path": "string — path to the parsed PPTX",
  "slide_count": "integer",
  "slides": [
    {
      "slide_number": "integer",
      "title": "string (optional) — slide title if identifiable",
      "body_text": "string — concatenated text from all shapes",
      "speaker_notes": "string — notes text",
      "table_data": [["string — cell content"]]
    }
  ],
  "extracted_text": "string — all text concatenated for LLM consumption"
}
```

---

### AdoItemOutput (`fetch_ado_item.py` → Agent)

```json
{
  "id": "integer — work item ID",
  "title": "string",
  "description": "string — HTML content, agent should parse",
  "acceptance_criteria": "string (optional)",
  "work_item_type": "string — e.g., Feature, User Story, Epic",
  "state": "string — e.g., New, Active, Resolved",
  "assigned_to": "string (optional)",
  "tags": ["string"],
  "linked_items": [
    {
      "id": "integer",
      "title": "string",
      "relation_type": "string — e.g., Child, Parent, Related"
    }
  ]
}
```

---

### ChartRequest (Agent → `generate_charts.py`)

```json
{
  "charts": [
    {
      "chart_id": "string — unique ID for the chart file",
      "chart_type": "horizontal_bar | grouped_bar | waterfall | error_bar",
      "title": "string",
      "data": {
        "labels": ["string"],
        "values": [["number"]],
        "series_names": ["string (optional)"],
        "error_low": ["number (optional)"],
        "error_high": ["number (optional)"]
      },
      "style": {
        "colors": ["string — hex colors (optional)"],
        "figsize": [6, 4],
        "dpi": 300
      }
    }
  ],
  "output_dir": "string — directory for PNG files"
}
```

**Output**: One PNG file per chart, named `{chart_id}.png` in the output directory.

---

## Logical Entities (Agent Reasoning)

These entities are not persisted — they exist in Copilot's conversation context as the agent reasons about the business case.

### Business Value Categories (Fixed)

| ID | Name | Subcategories |
|----|------|---------------|
| `revenue_monetization` | Revenue and Monetization | Direct revenue, Revenue acceleration, Revenue retention, Price realization |
| `cost_reduction` | Cost Reduction and Avoidance | Operational cost reduction, Cost avoidance, Efficiency gains |
| `user_adoption` | User and Adoption Value | New users/customers, Active usage growth, Expansion within accounts, Behavioral change |
| `risk_reduction` | Risk Reduction and Mitigation | Security risk, Compliance/regulatory risk, Operational risk, Business continuity |
| `productivity` | Productivity and Time Value | Time saved, Throughput increase, Quality improvements, Focus shift |
| `strategic_competitive` | Strategic and Competitive Value | Speed to market, Platform optionality, Competitive differentiation, Ecosystem leverage |
| `customer_experience` | Customer Experience and Brand Value | CSAT/NPS, Reduced customer effort, Trust/brand credibility, Referenceability |
| `organizational_capability` | Organizational and Capability Value | Skill uplift, Process maturity, Data quality, Decision-making quality |

### Confidence Scoring Criteria

| Level | Criteria |
|-------|----------|
| **Strong** | Multiple corroborating sources; quantitative data available; directly measurable |
| **Medium** | At least one supporting source; reasonable extrapolation from benchmarks; partially measurable |
| **Weak** | Based primarily on assumptions or analogies; no direct data; qualitative assessment only |

### Source Reliability Classification

| Level | Definition | Examples |
|-------|-----------|----------|
| **Primary** | Direct data from the organization or authoritative research | Internal financial data, Gartner/Forrester reports, peer-reviewed studies |
| **Secondary** | Analysis or synthesis of primary data | Industry blog analyses, consulting firm white papers, case studies |
| **Tertiary** | Opinion, anecdotal, or aggregated content | Blog posts, forum discussions, vendor marketing materials |
