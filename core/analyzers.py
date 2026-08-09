"""
core/analyzers.py

The analysis orchestration layer. Each `run_*_analysis` function:

  1. resolves the configured paths,
  2. ensures the output subdirectories exist,
  3. lazily loads the matching tool script from `tools/` (a submodule),
  4. runs it, and
  5. returns the tool's JSON report (loaded back from disk).

The UI only ever talks to these functions through the callables injected
by `core.launcher.launch_app` - it never imports the tools itself.
"""

from pathlib import Path
from typing import Any, Callable, Dict, Optional

from .paths import ensure_output_dirs
from .tool_loader import ensure_tool_entry, load_json_report, load_tool_module

StatusCallback = Callable[[str, float], None]


def run_manifest_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    """Run the APKTool analyzer and return its manifest/structure report."""
    module = load_tool_module("apktool")
    ensure_tool_entry(module, "apktool", "run_analysis_pipeline")

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", ""))

    module.run_analysis_pipeline(
        apk_path_str=apk_path_str,
        output_dir_str=str(subdirs["apktool_output"]),
        apktool_path_str=paths.get("apktool_path"),
        status_callback=status_callback,
    )

    return load_json_report(subdirs["apktool_output"] / "apktool_analysis.json")


def run_java_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    """Not yet wired up.

    Reserved for the JADX + LLM pipeline (Java/Kotlin scan mode). Once the
    JADX-Analyzer submodule and the LLM analysis step are integrated, this
    function loads the `jadx` tool via `core.tool_loader` and returns the
    structured LLM report expected by the "Java / Kotlin" results tab.
    """
    raise NotImplementedError(
        "Java/Kotlin analysis is not implemented yet. The JADX-Analyzer tool "
        "and the LLM analysis step are not wired into the main app."
    )


def run_native_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    """Not yet wired up.

    Reserved for the Native-Analyzer (Ghidra/Radare2) pipeline used by the
    "Native Libraries" scan mode.
    """
    raise NotImplementedError(
        "Native analysis is not implemented yet. The Native-Analyzer tool is "
        "not wired into the main app."
    )
