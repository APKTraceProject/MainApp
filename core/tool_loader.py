"""
core/tool_loader.py

Loads the analyzer tool scripts (which live in the `tools/` submodules)
as Python modules at runtime, lazily and on demand.

Each tool is a standalone script with its own module-level functions. We
import them through importlib so the UI never pays the import cost until
an analysis is actually run, and so a missing/untouched submodule fails
only when that specific tool is invoked - not at application startup.

It also owns `load_json_report`, the common way every runner reads a
tool's saved JSON report back from disk.
"""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent.parent

# Every tool is a git submodule under tools/<Name>. The keys below are the
# logical tool names used by core/analyzers.py; the values are the exact
# script paths on disk.
TOOL_SCRIPTS: Dict[str, Path] = {
    "apktool": BASE_DIR / "tools" / "APKTool-Analyzer" / "apk_analyzer.py",
    "jadx": BASE_DIR / "tools" / "JADX-Analyzer" / "main.py",
    "native": BASE_DIR / "tools" / "Native-Analyzer" / "cli.py",
}

# Keep already-loaded modules so repeated runs do not re-execute the script.
_module_cache: Dict[str, ModuleType] = {}


def tool_script_path(tool_name: str) -> Path:
    """Return the on-disk path of a tool's entry script, raising if unknown."""
    path = TOOL_SCRIPTS.get(tool_name)
    if path is None:
        raise KeyError(f"Unknown tool '{tool_name}'. Known tools: {sorted(TOOL_SCRIPTS)}")
    return path


def load_tool_module(tool_name: str) -> ModuleType:
    """Load (and cache) a tool script as a module.

    Raises RuntimeError if the script is missing, cannot be imported, or
    does not define the expected entry function.
    """
    cached = _module_cache.get(tool_name)
    if cached is not None:
        return cached

    script_path = tool_script_path(tool_name)
    if not script_path.exists():
        raise RuntimeError(f"Tool script not found at: {script_path}")

    spec = importlib.util.spec_from_file_location(f"apktrace_{tool_name}_tool", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not create an import spec for: {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to import {script_path}: {exc}") from exc

    _module_cache[tool_name] = module
    return module


def ensure_tool_entry(module: ModuleType, tool_name: str, entry_name: str) -> None:
    """Assert that a loaded tool module exposes `entry_name`."""
    if not hasattr(module, entry_name):
        raise RuntimeError(
            f"{tool_script_path(tool_name)} does not define {entry_name}(...)"
        )


def load_json_report(json_path: Path) -> Dict[str, Any]:
    """Read a tool's saved JSON report back from disk - the source of truth
    for its results, regardless of what the tool's pipeline function returns."""
    if not json_path.exists():
        raise RuntimeError(f"Analysis finished but the expected report file was not found: {json_path}")
    try:
        with json_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Could not read analysis report at {json_path}: {exc}") from exc
