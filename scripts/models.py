"""Pydantic v2 models for all JSON contracts used by the Business Case Builder agent."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SourceType(str, Enum):
    internet = "internet"
    sharepoint = "sharepoint"
    ado = "ado"
    communications = "communications"
    user_provided = "user_provided"


class Reliability(str, Enum):
    primary = "primary"
    secondary = "secondary"
    tertiary = "tertiary"


class DollarUnit(str, Enum):
    one_time = "one_time"
    per_year = "per_year"
    per_month = "per_month"


class Confidence(str, Enum):
    weak = "weak"
    medium = "medium"
    strong = "strong"


class SourceFormat(str, Enum):
    text = "text"
    file = "file"
    ado_work_item = "ado_work_item"
    pptx = "pptx"


class Mode(str, Enum):
    interactive = "interactive"
    autonomous = "autonomous"


class ChartType(str, Enum):
    horizontal_bar = "horizontal_bar"
    grouped_bar = "grouped_bar"
    waterfall = "waterfall"
    error_bar = "error_bar"


# ---------------------------------------------------------------------------
# Source / citation models
# ---------------------------------------------------------------------------

class SourceCitation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    source_type: SourceType
    title: str
    url: Optional[str] = None
    excerpt: str
    reliability: Reliability


# ---------------------------------------------------------------------------
# Value-estimation models
# ---------------------------------------------------------------------------

class ValueEstimate(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    category_id: str
    category_name: str
    subcategory: Optional[str] = None
    dollar_value_low: Optional[float] = None
    dollar_value_high: Optional[float] = None
    dollar_unit: DollarUnit
    confidence: Confidence
    reasoning: str
    methodology: str
    assumptions: list[str]
    is_hard_dollar: bool
    citations: list[SourceCitation]


class LeadingIndicator(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    indicator: str
    linked_outcome: str
    expected_impact: str


class StrategicValue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    summary: str
    dimensions: list[str]


# ---------------------------------------------------------------------------
# Feature / report input models
# ---------------------------------------------------------------------------

class FeatureInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    description: str
    target_users: list[str]
    source_format: SourceFormat
    source_reference: Optional[str] = None


class ReportInput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    feature: FeatureInput
    value_estimates: list[ValueEstimate]
    leading_indicators: list[LeadingIndicator]
    strategic_value: StrategicValue
    assumptions_made: list[str]
    sources_unavailable: list[str]
    mode: Mode
    generated_at: str


# ---------------------------------------------------------------------------
# Chart models
# ---------------------------------------------------------------------------

class ChartData(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    labels: list[str]
    values: list[list[float]]
    series_names: Optional[list[str]] = None
    error_low: Optional[list[float]] = None
    error_high: Optional[list[float]] = None


class ChartStyle(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    colors: Optional[list[str]] = None
    figsize: tuple[int, int] = (6, 4)
    dpi: int = 300


class ChartItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chart_id: str
    chart_type: ChartType
    title: str
    data: ChartData
    style: ChartStyle = Field(default_factory=ChartStyle)


class ChartRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    charts: list[ChartItem]
    output_dir: str


# ---------------------------------------------------------------------------
# PPTX / slide models
# ---------------------------------------------------------------------------

class SlideContent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    slide_number: int
    title: Optional[str] = None
    body_text: str
    speaker_notes: str
    table_data: Optional[list[list[str]]] = None


class PptxOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file_path: str
    slide_count: int
    slides: list[SlideContent]
    extracted_text: str


# ---------------------------------------------------------------------------
# Azure DevOps models
# ---------------------------------------------------------------------------

class LinkedItem(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    relation_type: str


class AdoItemOutput(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    title: str
    description: str
    acceptance_criteria: Optional[str] = None
    work_item_type: str
    state: str
    assigned_to: Optional[str] = None
    tags: list[str]
    linked_items: list[LinkedItem]
