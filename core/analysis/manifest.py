from typing import Any, Dict, Optional

from ..paths import ensure_output_dirs
from ..tool_loader import ensure_tool_entry, load_json_report, load_tool_module
from .base import StatusCallback


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
