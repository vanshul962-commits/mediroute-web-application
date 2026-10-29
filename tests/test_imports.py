"""Test that all application pages and modules import cleanly without syntax or import errors."""

import importlib.util
import os
import glob
import pytest


def test_import_all_python_files():
    """Ensure every single .py file in the repository can be loaded cleanly."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    py_files = glob.glob(os.path.join(base_dir, "**", "*.py"), recursive=True)

    # Exclude virtual environments if any
    py_files = [f for f in py_files if ".venv" not in f and "site-packages" not in f]

    assert len(py_files) >= 15, f"Expected at least 15 Python files, found {len(py_files)}"

    for file_path in py_files:
        rel_path = os.path.relpath(file_path, base_dir)
        mod_name = os.path.splitext(rel_path)[0].replace(os.path.sep, ".")
        spec = importlib.util.spec_from_file_location(mod_name, file_path)
        assert spec is not None, f"Could not create spec for {file_path}"
        assert spec.loader is not None, f"Could not create loader for {file_path}"
        try:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
        except Exception as e:
            pytest.fail(f"Failed to import {rel_path}: {e}")
