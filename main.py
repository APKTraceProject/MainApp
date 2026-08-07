"""
APKTrace - mainapp/main.py

Connects the UI (mainapp/ui) to the analyzer tools. All business logic lives
here: config.json I/O, path validation, output folder creation, and running
each analyzer tool. The UI never touches config.json or the tools directly -
it only calls the functions passed into AndroidAnalyzerApp.

Only apktool is wired up right now. Jadx and native/Ghidra analysis are not
implemented yet and are intentionally left out until those tools are ready.
"""

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Optional

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

# Location of the apktool wrapper script. Adjust this if your real folder
# layout differs (e.g. if apktool-analyzer lives under a "tools" subfolder).
APK_ANALYZER_SCRIPT = BASE_DIR / "tools" / "apktool-analyzer" / "apk_analyzer.py"

# The 4 paths collected by the setup wizard. jadx_path/ghidra_path are kept
# here so the wizard/settings screen still ask for them up front, even
# though they aren't used by any code yet.
REQUIRED_PATH_KEYS = ["output_dir", "apktool_path", "jadx_path", "ghidra_path"]

DEFAULT_CONFIG: Dict[str, Any] = {
    "paths": {
        "output_dir": "",
        "apktool_path": "",
        "jadx_path": "",
        "ghidra_path": "",
    },
    "api": {
        "provider": "",
        "api_key": "",
        "model": "",
    },
}


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
def load_config() -> Dict[str, Any]:
    config = copy.deepcopy(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                data = json.load(file) or {}
            config["paths"].update(data.get("paths", {}) or {})
            config["api"].update(data.get("api", {}) or {})
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Could not read config.json ({exc}); falling back to defaults.")
    return config


def save_config(config: Dict[str, Any]) -> None:
    merged = copy.deepcopy(DEFAULT_CONFIG)
    merged["paths"].update(config.get("paths", {}) or {})
    merged["api"].update(config.get("api", {}) or {})
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(merged, file, indent=4, ensure_ascii=False)


def is_setup_complete(config: Dict[str, Any]) -> bool:
    paths = config.get("paths", {})
    for key in REQUIRED_PATH_KEYS:
        value = (paths.get(key) or "").strip()
        if not value:
            return False
        if key != "output_dir" and not Path(value).expanduser().exists():
            return False
    return True


def ensure_output_dirs(output_dir_str: str) -> Dict[str, Path]:
    """Create <output_dir>/{apktool_output,jadx_output,ghidra_output} and return them."""
    output_dir = Path(output_dir_str).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    subdirs = {
        "apktool_output": output_dir / "apktool_output",
        "jadx_output": output_dir / "jadx_output",
        "ghidra_output": output_dir / "ghidra_output",
    }
    for path in subdirs.values():
        path.mkdir(parents=True, exist_ok=True)
    return subdirs


# --------------------------------------------------------------------------- #
# apktool analyzer - loaded lazily, only the first time it's actually run
# --------------------------------------------------------------------------- #
_apktool_module: Optional[ModuleType] = None


def _get_apktool_module() -> ModuleType:
    global _apktool_module
    if _apktool_module is not None:
        return _apktool_module

    if not APK_ANALYZER_SCRIPT.exists():
        raise RuntimeError(f"apk_analyzer.py not found at: {APK_ANALYZER_SCRIPT}")

    spec = importlib.util.spec_from_file_location("apktrace_apktool_analyzer", APK_ANALYZER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not create an import spec for: {APK_ANALYZER_SCRIPT}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        spec.loader.exec_module(module)
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"Failed to import {APK_ANALYZER_SCRIPT}: {exc}") from exc

    if not hasattr(module, "run_analysis_pipeline"):
        raise RuntimeError(f"{APK_ANALYZER_SCRIPT} does not define run_analysis_pipeline(...)")

    _apktool_module = module
    return _apktool_module


def _load_json_report(json_path: Path) -> Dict[str, Any]:
    """Read a tool's saved JSON report back from disk - the source of truth
    for its results, regardless of what run_analysis_pipeline returns."""
    if not json_path.exists():
        raise RuntimeError(f"Analysis finished but the expected report file was not found: {json_path}")
    try:
        with json_path.open("r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Could not read analysis report at {json_path}: {exc}") from exc


StatusCallback = Callable[[str, float], None]


def run_manifest_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    module = _get_apktool_module()

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", ""))

    module.run_analysis_pipeline(
        apk_path_str=apk_path_str,
        output_dir_str=str(subdirs["apktool_output"]),
        apktool_path_str=paths.get("apktool_path"),
        status_callback=status_callback,
    )

    return _load_json_report(subdirs["apktool_output"] / "apktool_analysis.json")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def launch_app() -> None:
    from ui import AndroidAnalyzerApp, SetupWizard

    config = load_config()

    if not is_setup_complete(config):
        print("[*] Required paths are missing - opening the first-run setup window...")
        wizard = SetupWizard(config=config, on_complete=save_config)
        wizard.mainloop()
        config = load_config()

        if not is_setup_complete(config):
            print("[!] Setup was not completed, so APKTrace cannot start. Exiting.")
            return

    app = AndroidAnalyzerApp(
        config=config,
        run_manifest_analysis=run_manifest_analysis,
        save_config=save_config,
    )
    app.mainloop()


def main() -> None:
    launch_app()


if __name__ == "__main__":
    main()