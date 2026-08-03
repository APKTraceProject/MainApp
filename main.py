"""
APKTrace - mainapp/main.py

This file is the connection center between the UI (mainapp/ui) and the
individual analyzer tools (apktool-analyzer, jadx-analyzer, native-analyzer).

Everything that is "business logic" lives here, NOT in the UI:
    - loading / saving the single shared config.json (paths + API settings)
    - validating that the 4 required paths are present before the main UI opens
    - creating the output folder structure (apktool_output, jadx_output, ghidra_output)
    - dynamically loading each analyzer tool's module (by file path, so a
      "main.py" inside jadx-analyzer/ can never collide with this file)
    - running each analysis pipeline and handing the report back to the UI

The UI never imports apk_analyzer / jadx / ghidra modules directly and never
reads or writes config.json directly - it only calls the functions exposed
below, which are handed to AndroidAnalyzerApp as plain callables.
"""

import copy
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Optional

# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config.json"

APKTOOL_ANALYZER_DIR = BASE_DIR / "apktool-analyzer"
JADX_ANALYZER_DIR = BASE_DIR / "jadx-analyzer"
NATIVE_ANALYZER_DIR = BASE_DIR / "native-analyzer"

# The 4 required addresses described by the project owner:
#   1) output_dir    -> parent folder; app creates apktool_output/jadx_output/ghidra_output inside it
#   2) apktool_path   -> apktool executable/jar
#   3) jadx_path      -> jadx executable/bat
#   4) ghidra_path    -> ghidra executable/script
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
# Config management (single shared config.json next to this file)
# --------------------------------------------------------------------------- #
def load_config() -> Dict[str, Any]:
    """Load the shared config, merging in defaults for any missing keys."""
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
    """Persist the shared config to mainapp/config.json (merged with defaults)."""
    merged = copy.deepcopy(DEFAULT_CONFIG)
    merged["paths"].update(config.get("paths", {}) or {})
    merged["api"].update(config.get("api", {}) or {})

    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(merged, file, indent=4, ensure_ascii=False)


def is_setup_complete(config: Dict[str, Any]) -> bool:
    """True once all 4 required paths are filled in (tool paths must exist on disk)."""
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
# Dynamic tool loading
#
# Each sub-tool lives in its own folder/submodule and may very well contain a
# file named "main.py" of its own (jadx-analyzer/main.py, for example). Doing
# a plain `sys.path.append(...); import main` would silently collide with
# THIS file's own module. Loading each tool by its exact file path with a
# unique module name avoids that entirely.
# --------------------------------------------------------------------------- #
def _load_module(module_name: str, file_path: Path) -> Optional[ModuleType]:
    if not file_path.exists():
        return None
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as exc:  # noqa: BLE001 - we want to degrade gracefully, not crash the app
        print(f"[WARN] Failed to load {file_path}: {exc}")
        return None


# NOTE: the apktool analyzer's actual file is apk_analyzer.py (not
# apktool_analyzer.py) - loading it explicitly by path fixes the previous
# `import apktool_analyzer` mismatch that silently made the UI fall back to
# a mock/no-op analysis.
_apktool_module = _load_module("apktrace_apktool_analyzer", APKTOOL_ANALYZER_DIR / "apk_analyzer.py")
_jadx_module = _load_module("apktrace_jadx_analyzer", JADX_ANALYZER_DIR / "main.py")
_native_module = _load_module("apktrace_native_analyzer", NATIVE_ANALYZER_DIR / "cli.py")


# --------------------------------------------------------------------------- #
# Analysis pipelines - the UI only ever calls these
# --------------------------------------------------------------------------- #
StatusCallback = Callable[[str, float], None]


def run_manifest_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    if _apktool_module is None or not hasattr(_apktool_module, "run_analysis_pipeline"):
        raise RuntimeError(
            "apktool-analyzer/apk_analyzer.py could not be loaded. Check that the file "
            "exists and that 'Apktool Path' in Settings points to a valid apktool jar/executable."
        )

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", ""))

    return _apktool_module.run_analysis_pipeline(
        apk_path_str=apk_path_str,
        output_dir_str=str(subdirs["apktool_output"]),
        apktool_path_str=paths.get("apktool_path"),
        status_callback=status_callback,
    )


def run_java_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    if _jadx_module is None or not hasattr(_jadx_module, "run_analysis_pipeline"):
        raise RuntimeError(
            "jadx-analyzer is not connected yet. Add a jadx-analyzer/main.py exposing "
            "run_analysis_pipeline(apk_path_str, output_dir_str, jadx_path_str, status_callback) "
            "to enable this scan mode."
        )

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", ""))

    return _jadx_module.run_analysis_pipeline(
        apk_path_str=apk_path_str,
        output_dir_str=str(subdirs["jadx_output"]),
        jadx_path_str=paths.get("jadx_path"),
        status_callback=status_callback,
    )


def run_native_analysis(
    apk_path_str: str,
    config: Dict[str, Any],
    status_callback: Optional[StatusCallback] = None,
) -> Dict[str, Any]:
    if _native_module is None or not hasattr(_native_module, "run_analysis_pipeline"):
        raise RuntimeError(
            "native-analyzer is not connected yet. Add a native-analyzer/cli.py exposing "
            "run_analysis_pipeline(apk_path_str, output_dir_str, ghidra_path_str, status_callback) "
            "to enable this scan mode."
        )

    paths = config.get("paths", {})
    subdirs = ensure_output_dirs(paths.get("output_dir", ""))

    return _native_module.run_analysis_pipeline(
        apk_path_str=apk_path_str,
        output_dir_str=str(subdirs["ghidra_output"]),
        ghidra_path_str=paths.get("ghidra_path"),
        status_callback=status_callback,
    )


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
        run_java_analysis=run_java_analysis,
        run_native_analysis=run_native_analysis,
        save_config=save_config,
    )
    app.mainloop()


def main() -> None:
    launch_app()


if __name__ == "__main__":
    main()