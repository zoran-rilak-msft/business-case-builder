"""Tests for scripts/fetch_ado_item.py."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.models import AdoItemOutput

PROJECT_ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = PROJECT_ROOT / "tests" / "fixtures" / "sample-ado-response.json"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "fetch_ado_item.py"


class TestSchemaValidation:
    """Verify the sample fixture validates against the Pydantic model."""

    def test_schema_validation(self) -> None:
        data = json.loads(FIXTURE_PATH.read_text())
        item = AdoItemOutput(**data)

        assert item.id == 12345
        assert item.title == "Implement SSO for Enterprise Customers"
        assert item.work_item_type == "Feature"
        assert item.state == "Active"
        assert item.assigned_to == "Jane Smith"
        assert item.tags == ["enterprise", "security", "authentication", "P1"]
        assert len(item.linked_items) == 2
        assert item.linked_items[0].relation_type == "Child"


class TestCLI:
    """Integration tests that exercise the script via subprocess."""

    @staticmethod
    def _run(args: list[str], env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        run_env = dict(env) if env is not None else dict(os.environ)
        # Ensure the project root is on PYTHONPATH so `scripts.models` resolves.
        run_env["PYTHONPATH"] = str(PROJECT_ROOT)
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=run_env,
        )

    def test_missing_ado_pat_error(self) -> None:
        # Build a minimal env WITHOUT ADO_PAT
        env = {k: v for k, v in os.environ.items() if k != "ADO_PAT"}
        env.pop("ADO_PAT", None)

        result = self._run(
            ["--item-id", "12345", "--org", "https://dev.azure.com/test"],
            env=env,
        )

        assert result.returncode == 1
        assert "ADO_PAT" in result.stderr

    def test_help_flag(self) -> None:
        result = self._run(["--help"])

        assert result.returncode == 0
        assert "--item-id" in result.stdout
