import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from ..paths import ensure_output_dirs
from .base import StatusCallback


def run_native_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    """Run native analysis using the Native-Analyzer submodule, saving raw_data/report.json and ai_native_analysis.json."""
    if status_callback:
        status_callback("Initializing Native Analysis environment...", 0.2)

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", "output"))

    native_out_dir = subdirs["native_analysis_output"]
    raw_data_dir = subdirs["native_raw_data"]

    base_dir = Path(__file__).resolve().parent.parent.parent
    example_path = base_dir / "Native-analysis.example.json"

    ai_analysis_file = native_out_dir / "ai_native_analysis.json"
    raw_report_file = raw_data_dir / "report.json"

    # 1. AI Analysis file: Copy from root Native-analysis.example.json
    ai_data = {}
    if example_path.exists():
        try:
            with open(example_path, "r", encoding="utf-8") as f:
                ai_data = json.load(f)
            with open(ai_analysis_file, "w", encoding="utf-8") as f:
                json.dump(ai_data, f, indent=2)
        except Exception as e:
            print(f"[WARN] Failed to copy AI analysis file: {e}")

    # 2. Execute Native Analysis submodule directly
    if status_callback:
        status_callback("Executing Native Analysis submodule scanner...", 0.5)

    native_dir = base_dir / "tools" / "Native-Analyzer"
    if str(native_dir) not in sys.path:
        sys.path.insert(0, str(native_dir))

    # Extract configuration parameters from application config object and CLI YAML defaults
    paths = config.get("paths", {}) if isinstance(config, dict) else {}
    native_cfg = (
        config.get("native_analysis") or config.get("native") or {}
        if isinstance(config, dict)
        else {}
    )

    try:
        from native_analysis.core.config_loader import ConfigLoader
        cli_config = ConfigLoader.load_cli_config(str(native_dir / "config" / "cli_config.yaml"))
    except Exception:
        cli_config = {}

    target_path_raw = (
        apk_path_str
        or native_cfg.get("target_path")
        or paths.get("target_path")
        or cli_config.get("target_path")
    )
    engine_type = (
        native_cfg.get("engine")
        or paths.get("native_engine")
        or cli_config.get("engine")
        or "ghidra"
    )
    decompiler_path = (
        native_cfg.get("decompiler_path")
        or native_cfg.get("ghidra_headless_path")
        or paths.get("native_engine_path")
        or paths.get("decompiler_path")
        or cli_config.get("decompiler_path")
    )
    rules_path = (
        native_cfg.get("rules_path")
        or paths.get("rules_path")
        or cli_config.get("rules_path")
        or str(native_dir / "config" / "rules.yaml")
    )
    # Output path strictly set to native_analysis_output/raw_data/report.json
    output_json_path = raw_report_file

    raw_data: Dict[str, Any] = {}
    target_path = Path(target_path_raw) if target_path_raw else None

    if target_path and target_path.exists() and target_path.suffix.lower() in (".so", ".apk"):
        try:
            from native_analysis.core.engine import ScanEngine
            from native_analysis.reporters.json_reporter import JSONReporter

            engine = ScanEngine(
                rules_path=str(rules_path),
                decompiler_path=str(decompiler_path) if decompiler_path else None,
                engine=str(engine_type).lower(),
                ghidra_headless_path=str(decompiler_path) if decompiler_path else None,
            )
            scanned_targets = engine.scan(str(target_path))
            raw_data = JSONReporter.generate_report(
                scanned_targets=scanned_targets,
                output_file_path=str(output_json_path),
                analysis_engine=str(engine_type).lower(),
            )
        except Exception as e:
            print(f"[ERROR] Native Analysis execution failed: {e}")

    # Fallback to reading existing raw_report_file if available
    if not raw_data and raw_report_file.exists():
        try:
            with open(raw_report_file, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to read existing raw report: {e}")

    if status_callback:
        status_callback("Native analysis completed successfully!", 1.0)

    return {
        "ai_report": ai_data,
        "raw_report": raw_data,
        "ai_report_path": str(ai_analysis_file),
        "raw_report_path": str(raw_report_file),
    }
