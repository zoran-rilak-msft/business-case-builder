"""Tests for scripts/search_sharepoint.py."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.models import SharePointDocumentContent, SharePointSearchItem, SharePointSearchResult
from scripts.search_sharepoint import (
    _build_search_payload,
    _extract_text_docx,
    _extract_text_pdf,
    _extract_text_pptx,
    _extract_text_xlsx,
    _parse_args,
    _parse_search_response,
)

FIXTURES_DIR = Path(__file__).parent / "fixtures"


# ---------------------------------------------------------------------------
# Pydantic model validation
# ---------------------------------------------------------------------------


class TestModelValidation:
    """Verify SharePoint Pydantic models accept valid data."""

    def test_search_item_construction(self) -> None:
        item = SharePointSearchItem(
            drive_item_id="driveABC!item123",
            title="Roadmap.docx",
            url="https://contoso.sharepoint.com/sites/eng/Roadmap.docx",
            site_name="contoso.sharepoint.com",
            last_modified="2025-01-15T10:30:00Z",
            file_type="docx",
            snippet="Q3 roadmap priorities…",
            size_bytes=204800,
        )
        assert item.drive_item_id == "driveABC!item123"
        assert item.title == "Roadmap.docx"
        assert item.size_bytes == 204800

    def test_search_result_empty(self) -> None:
        result = SharePointSearchResult(
            query="nonexistent",
            site_scope=None,
            result_count=0,
            results=[],
        )
        assert result.result_count == 0
        assert result.results == []

    def test_document_content_construction(self) -> None:
        doc = SharePointDocumentContent(
            drive_item_id="driveABC!item456",
            title="Report.pdf",
            url="https://contoso.sharepoint.com/sites/eng/Report.pdf",
            file_type="pdf",
            extracted_text="Sample extracted text content.",
            page_count=5,
            extraction_method="PyPDF2",
        )
        assert doc.file_type == "pdf"
        assert doc.page_count == 5
        assert doc.extraction_method == "PyPDF2"

    def test_document_content_optional_page_count(self) -> None:
        doc = SharePointDocumentContent(
            drive_item_id="d!i",
            title="Notes.docx",
            url="",
            file_type="docx",
            extracted_text="hello",
            extraction_method="python-docx",
        )
        assert doc.page_count is None


# ---------------------------------------------------------------------------
# Text extraction (using real fixture files)
# ---------------------------------------------------------------------------


class TestTextExtraction:
    """Verify text extraction helpers against the sample fixture files."""

    def test_extract_text_docx(self) -> None:
        content = (FIXTURES_DIR / "sample-sharepoint.docx").read_bytes()
        text, page_count = _extract_text_docx(content)

        assert "Cloud Migration Business Case" in text
        assert "annual cost savings" in text
        assert page_count is None  # docx extractor does not report pages

    def test_extract_text_pptx(self) -> None:
        content = (FIXTURES_DIR / "sample-sharepoint.pptx").read_bytes()
        text, page_count = _extract_text_pptx(content)

        assert "Feature ROI Analysis" in text
        assert "Projected annual savings" in text
        assert page_count is not None and page_count > 0

    def test_extract_text_pdf(self) -> None:
        content = (FIXTURES_DIR / "sample-sharepoint.pdf").read_bytes()
        text, page_count = _extract_text_pdf(content)

        assert "Enterprise Security Assessment" in text
        assert page_count is not None and page_count > 0

    def test_extract_text_xlsx(self) -> None:
        content = (FIXTURES_DIR / "sample-sharepoint.xlsx").read_bytes()
        text, page_count = _extract_text_xlsx(content)

        assert "Infrastructure" in text
        assert "500000" in text
        assert page_count is not None and page_count > 0


# ---------------------------------------------------------------------------
# Search response parsing
# ---------------------------------------------------------------------------


def _make_graph_hit(*, name: str, web_url: str, drive_id: str, item_id: str) -> dict:
    """Build a single hit dict matching Graph /search/query shape."""
    return {
        "resource": {
            "name": name,
            "webUrl": web_url,
            "lastModifiedDateTime": "2025-06-01T12:00:00Z",
            "size": 102400,
            "id": item_id,
            "parentReference": {
                "driveId": drive_id,
                "siteId": "contoso.sharepoint.com,abc,def",
            },
        },
        "summary": f"Snippet for {name}",
    }


class TestParseSearchResponse:
    """Verify _parse_search_response extracts items correctly."""

    def test_two_hits(self) -> None:
        raw = {
            "value": [
                {
                    "hitsContainers": [
                        {
                            "hits": [
                                _make_graph_hit(
                                    name="Design.docx",
                                    web_url="https://sp/Design.docx",
                                    drive_id="driveA",
                                    item_id="item1",
                                ),
                                _make_graph_hit(
                                    name="Budget.xlsx",
                                    web_url="https://sp/Budget.xlsx",
                                    drive_id="driveB",
                                    item_id="item2",
                                ),
                            ]
                        }
                    ]
                }
            ]
        }

        result = _parse_search_response(raw, query="design budget", site_scope=None)

        assert result.result_count == 2
        assert result.query == "design budget"
        assert result.results[0].title == "Design.docx"
        assert result.results[0].drive_item_id == "driveA!item1"
        assert result.results[0].file_type == "docx"
        assert result.results[1].title == "Budget.xlsx"
        assert result.results[1].drive_item_id == "driveB!item2"

    def test_empty_response(self) -> None:
        result = _parse_search_response({}, query="nope", site_scope=None)

        assert result.result_count == 0
        assert result.results == []

    def test_empty_hits_containers(self) -> None:
        raw = {"value": [{"hitsContainers": [{"hits": []}]}]}
        result = _parse_search_response(raw, query="empty", site_scope="https://site")

        assert result.result_count == 0
        assert result.site_scope == "https://site"


# ---------------------------------------------------------------------------
# Build search payload
# ---------------------------------------------------------------------------


class TestBuildSearchPayload:
    """Verify _build_search_payload structures the Graph request correctly."""

    def test_basic_query(self) -> None:
        payload = _build_search_payload("migration plan", site_scope=None)

        assert len(payload["requests"]) == 1
        req = payload["requests"][0]
        assert req["query"]["queryString"] == "migration plan"
        assert "driveItem" in req["entityTypes"]

    def test_site_scoped_query(self) -> None:
        site = "https://contoso.sharepoint.com/sites/eng"
        payload = _build_search_payload("roadmap", site_scope=site)

        qs = payload["requests"][0]["query"]["queryString"]
        assert "roadmap" in qs
        assert site in qs
        assert "path:" in qs


# ---------------------------------------------------------------------------
# CLI argument parsing
# ---------------------------------------------------------------------------


class TestParseArgs:
    """Verify argparse configuration via _parse_args."""

    def test_query_only(self) -> None:
        args = _parse_args(["--query", "test"])
        assert args.query == "test"
        assert args.site is None
        assert args.download is None

    def test_query_with_site(self) -> None:
        args = _parse_args(["--query", "test", "--site", "https://contoso.sharepoint.com/sites/eng"])
        assert args.query == "test"
        assert args.site == "https://contoso.sharepoint.com/sites/eng"

    def test_download(self) -> None:
        args = _parse_args(["--download", "driveId!itemId"])
        assert args.download == "driveId!itemId"
        assert args.query is None

    def test_login(self) -> None:
        args = _parse_args(["--login"])
        assert args.login is True
        assert args.query is None
        assert args.download is None

    def test_query_and_download_mutually_exclusive(self) -> None:
        with pytest.raises(SystemExit):
            _parse_args(["--query", "test", "--download", "driveId!itemId"])

    def test_no_args_exits(self) -> None:
        with pytest.raises(SystemExit):
            _parse_args([])


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------


class TestErrorHandling:
    """Verify graceful behaviour on unsupported inputs."""

    def test_unsupported_file_type_not_in_extractors(self) -> None:
        from scripts.search_sharepoint import _EXTRACTORS

        assert "txt" not in _EXTRACTORS
        assert "csv" not in _EXTRACTORS
        assert set(_EXTRACTORS.keys()) == {"docx", "pptx", "pdf", "xlsx"}
