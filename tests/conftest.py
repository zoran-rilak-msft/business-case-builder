"""Shared pytest fixtures for the business-case-builder test suite."""

from datetime import datetime, timezone
from pathlib import Path

import pytest


@pytest.fixture
def tmp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    yield output_dir


@pytest.fixture
def sample_report_input() -> dict:
    """Return a minimal valid ReportInput dict matching the Pydantic schema."""
    return {
        "feature": {
            "title": "Test Feature",
            "description": "A test",
            "target_users": ["developers"],
            "source_format": "text",
        },
        "value_estimates": [
            {
                "category_id": "revenue_monetization",
                "category_name": "Revenue and Monetization",
                "dollar_value_low": 10000,
                "dollar_value_high": 50000,
                "dollar_unit": "per_year",
                "confidence": "medium",
                "reasoning": "Estimated based on projected user growth",
                "methodology": "Bottom-up estimation from usage data",
                "assumptions": ["Stable user growth rate"],
                "is_hard_dollar": True,
                "citations": [
                    {
                        "id": "cite-001",
                        "source_type": "user_provided",
                        "title": "Internal Revenue Report",
                        "excerpt": "Projected annual revenue impact",
                        "reliability": "primary",
                    }
                ],
            }
        ],
        "leading_indicators": [
            {
                "indicator": "MAU growth",
                "linked_outcome": "Revenue increase",
                "expected_impact": "15% increase in first 6 months",
            }
        ],
        "strategic_value": {
            "summary": "Strengthens platform competitive position",
            "dimensions": ["Platform optionality", "Competitive differentiation"],
        },
        "assumptions_made": ["Market conditions remain stable"],
        "mode": "interactive",
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@pytest.fixture
def sample_chart_request(tmp_path: Path) -> dict:
    """Return a minimal valid ChartRequest dict with one horizontal_bar chart."""
    return {
        "charts": [
            {
                "chart_id": "test-chart-001",
                "chart_type": "horizontal_bar",
                "title": "Test Chart",
                "data": {
                    "labels": ["Cat A", "Cat B"],
                    "values": [[100, 200]],
                },
            }
        ],
        "output_dir": str(tmp_path / "charts"),
    }
