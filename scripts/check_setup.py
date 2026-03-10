#!/usr/bin/env python3
"""Verify all required dependencies are importable."""

import importlib
import importlib.metadata
import sys

DEPENDENCIES = [
    ("docx", "python-docx"),
    ("matplotlib", "matplotlib"),
    ("pptx", "python-pptx"),
    ("azure.devops", "azure-devops"),
    ("pydantic", "pydantic"),
]


def get_version(import_name: str, package_name: str) -> str | None:
    """Get package version via __version__ or importlib.metadata."""
    try:
        mod = importlib.import_module(import_name)
        version = getattr(mod, "__version__", None)
        if version:
            return version
    except ImportError:
        pass

    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def check_dependencies() -> int:
    """Check all dependencies and return count of missing ones."""
    missing = 0

    for import_name, package_name in DEPENDENCIES:
        try:
            importlib.import_module(import_name)
            version = get_version(import_name, package_name)
            version_str = version if version else "unknown version"
            print(f"✓ {package_name}: installed ({version_str})")
        except ImportError:
            print(f"✗ {package_name}: NOT INSTALLED")
            missing += 1

    print()
    if missing == 0:
        print("✓ All dependencies available")
    else:
        print(f"✗ Missing {missing} dependencies")

    return missing


if __name__ == "__main__":
    sys.exit(1 if check_dependencies() > 0 else 0)
