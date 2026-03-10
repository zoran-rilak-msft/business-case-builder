"""Tests for scripts/generate_charts.py."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _run_script(json_path: Path, output_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "scripts/generate_charts.py", "--input", str(json_path), "--output-dir", str(output_dir)],
        capture_output=True,
        text=True,
    )


def _write_request(tmp_path: Path, request: dict) -> Path:
    json_path = tmp_path / "request.json"
    with open(json_path, "w") as f:
        json.dump(request, f)
    return json_path


def test_horizontal_bar_generates_png(sample_chart_request, tmp_path):
    json_path = _write_request(tmp_path, sample_chart_request)
    output_dir = tmp_path / "charts"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    png = output_dir / "test-chart-001.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_grouped_bar_generates_png(tmp_path):
    request = {
        "charts": [
            {
                "chart_id": "grouped-bar-001",
                "chart_type": "grouped_bar",
                "title": "Low vs High Estimates",
                "data": {
                    "labels": ["Revenue", "Cost Savings"],
                    "values": [[100_000, 50_000], [200_000, 80_000]],
                    "series_names": ["Low", "High"],
                },
            }
        ],
        "output_dir": str(tmp_path / "charts"),
    }
    json_path = _write_request(tmp_path, request)
    output_dir = tmp_path / "charts"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    png = output_dir / "grouped-bar-001.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_waterfall_generates_png(tmp_path):
    request = {
        "charts": [
            {
                "chart_id": "waterfall-001",
                "chart_type": "waterfall",
                "title": "Value Build-up",
                "data": {
                    "labels": ["Revenue", "Savings", "Efficiency"],
                    "values": [[100_000, 50_000, 30_000]],
                },
            }
        ],
        "output_dir": str(tmp_path / "charts"),
    }
    json_path = _write_request(tmp_path, request)
    output_dir = tmp_path / "charts"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    png = output_dir / "waterfall-001.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_error_bar_generates_png(tmp_path):
    request = {
        "charts": [
            {
                "chart_id": "error-bar-001",
                "chart_type": "error_bar",
                "title": "Estimates with Confidence",
                "data": {
                    "labels": ["Cat A", "Cat B"],
                    "values": [[150_000, 75_000]],
                    "error_low": [100_000, 50_000],
                    "error_high": [200_000, 100_000],
                },
            }
        ],
        "output_dir": str(tmp_path / "charts"),
    }
    json_path = _write_request(tmp_path, request)
    output_dir = tmp_path / "charts"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    png = output_dir / "error-bar-001.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_invalid_json_exits_with_error(tmp_path):
    bad_json = tmp_path / "bad.json"
    bad_json.write_text("{not valid json!!}")
    output_dir = tmp_path / "charts"
    result = _run_script(bad_json, output_dir)

    assert result.returncode == 1
    assert result.stderr.strip() != ""


def test_output_dir_created_if_missing(tmp_path):
    request = {
        "charts": [
            {
                "chart_id": "auto-dir-001",
                "chart_type": "horizontal_bar",
                "title": "Auto Dir Test",
                "data": {
                    "labels": ["X"],
                    "values": [[42]],
                },
            }
        ],
        "output_dir": str(tmp_path / "deeply" / "nested" / "dir"),
    }
    json_path = _write_request(tmp_path, request)
    output_dir = tmp_path / "deeply" / "nested" / "dir"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    assert output_dir.exists()
    png = output_dir / "auto-dir-001.png"
    assert png.exists()
    assert png.stat().st_size > 0


def test_chart_dimensions(tmp_path):
    from PIL import Image

    request = {
        "charts": [
            {
                "chart_id": "dim-001",
                "chart_type": "horizontal_bar",
                "title": "Dimension Test",
                "data": {
                    "labels": ["A", "B"],
                    "values": [[10, 20]],
                },
                "style": {
                    "figsize": [10, 6],
                    "dpi": 300,
                },
            }
        ],
        "output_dir": str(tmp_path / "charts"),
    }
    json_path = _write_request(tmp_path, request)
    output_dir = tmp_path / "charts"
    result = _run_script(json_path, output_dir)

    assert result.returncode == 0, result.stderr
    png = output_dir / "dim-001.png"
    img = Image.open(png)
    width, height = img.size
    # At 300 DPI, 10x6 inches → ~3000x1800 pixels; bbox_inches='tight' may adjust
    assert 2500 < width < 3500, f"Unexpected width: {width}"
    assert 1400 < height < 2200, f"Unexpected height: {height}"
