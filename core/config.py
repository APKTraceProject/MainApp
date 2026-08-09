"""
core/config.py

Responsible for everything related to the application's config.json:
existence checks, defaults, loading, validation, merging, saving, and the
"is setup complete?" check used to decide whether the setup wizard must be
shown at startup.

Startup flow (driven by `core.launcher.launch_app`, logic lives here):

    1. config.json is missing      -> `ensure_config_exists()` creates a
       default one, then the wizard is shown.
    2. config.json exists          -> `load_config()` parses it and
       `validate_config()` checks required keys, missing fields and values.
    3. invalid / incomplete        -> the wizard is shown so the user can
       fix or populate the config.
    4. valid                       -> config is used and the wizard is
       skipped.

The UI never touches config.json directly - it only calls the functions
injected by `core.launcher.launch_app`.
"""

import copy
import json
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

# Decompiler/analyzer engines selectable for native library analysis.
NATIVE_ENGINE_OPTIONS = ["ghidra", "radare2"]

# The paths collected by the setup wizard. `native_engine_path` points at
# whichever engine was selected via `native_engine` (Ghidra headless script
# or the Radare2 executable). jadx_path/native_engine_path are kept here so
# the wizard/settings screen still ask for them up front, even though they
# aren't used by the main UI code yet.
REQUIRED_PATH_KEYS = ["output_dir", "apktool_path", "jadx_path", "native_engine_path"]

# Optional AI API fields stored alongside the tool paths. They may stay
# empty; they are validated for correct *type* but never required.
API_KEYS = ["provider", "api_key", "model"]

DEFAULT_CONFIG: Dict[str, Any] = {
    "paths": {
        "output_dir": "",
        "apktool_path": "",
        "jadx_path": "",
        "native_engine": "ghidra",
        "native_engine_path": "",
    },
    "api": {
        "provider": "",
        "api_key": "",
        "model": "",
    },
}


def merge_config(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge `updates` on top of a deep copy of `config`, section by section."""
    merged = copy.deepcopy(config)
    merged["paths"].update(updates.get("paths", {}) or {})
    merged["api"].update(updates.get("api", {}) or {})
    return merged


def ensure_config_exists() -> None:
    """Create config.json with the default structure if it does not exist yet.

    A freshly created file is incomplete (all paths empty) on purpose: the
    startup flow then routes the user to the setup wizard to fill it in.
    """
    if not CONFIG_PATH.exists():
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        save_config({})
        print(f"[*] No config.json found - created a fresh one at {CONFIG_PATH}.")


def load_config() -> Dict[str, Any]:
    """Read config.json into memory, filling any missing keys with defaults.

    A missing, corrupt, unreadable, or structurally wrong file never raises:
    valid keys are kept and the defaults are used for the rest, so callers
    can always treat the result as a dict shaped like DEFAULT_CONFIG. Whether
    the loaded values are actually *usable* is answered by `validate_config`.
    """
    config = copy.deepcopy(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                data = json.load(file) or {}
            if isinstance(data, dict):
                paths = data.get("paths") or {}
                api = data.get("api") or {}
                if isinstance(paths, dict):
                    migrated_paths = dict(paths)
                    # Backwards compat: configs written with the old
                    # `ghidra_path` key are migrated to `native_engine_path`.
                    if not migrated_paths.get("native_engine_path") and migrated_paths.get("ghidra_path"):
                        migrated_paths["native_engine_path"] = migrated_paths["ghidra_path"]
                    engine = str(migrated_paths.get("native_engine", "") or "").strip().lower()
                    if engine not in NATIVE_ENGINE_OPTIONS:
                        migrated_paths["native_engine"] = "ghidra"
                    config["paths"].update(migrated_paths)
                if isinstance(api, dict):
                    config["api"].update(api)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Could not read config.json ({exc}); falling back to defaults.")
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Persist `config` to config.json, always writing every known key."""
    merged = merge_config(DEFAULT_CONFIG, config)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(merged, file, indent=4, ensure_ascii=False)


def validate_config(config: Dict[str, Any]) -> List[str]:
    """Return a list of human-readable problems, or [] when config is usable.

    Checks structure (root/sections must be objects), required fields (the
    4 tool paths must be non-empty strings), and values (non-output paths
    must exist on disk; API fields, when present, must be strings). API
    fields are never *required* - they may be left empty.
    """
    if not isinstance(config, dict):
        return ["config root is not an object"]

    problems: List[str] = []

    paths = config.get("paths")
    if not isinstance(paths, dict):
        return ["'paths' section is missing or not an object"]

    for key in REQUIRED_PATH_KEYS:
        value = paths.get(key)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"paths.{key} is missing or empty")
        elif key != "output_dir" and not Path(value).expanduser().exists():
            problems.append(f"paths.{key} does not point to an existing file: {value!r}")

    engine = paths.get("native_engine")
    if not isinstance(engine, str) or engine.strip().lower() not in NATIVE_ENGINE_OPTIONS:
        problems.append(
            f"paths.native_engine must be one of: {', '.join(NATIVE_ENGINE_OPTIONS)}"
        )

    api = config.get("api")
    if api is not None and not isinstance(api, dict):
        problems.append("'api' section must be an object")
    elif isinstance(api, dict):
        for key in API_KEYS:
            value = api.get(key)
            if value is not None and not isinstance(value, str):
                problems.append(f"api.{key} must be a string")

    return problems


def is_valid_config(config: Dict[str, Any]) -> bool:
    """Return True when `validate_config` finds no problems."""
    return not validate_config(config)


def is_setup_complete(config: Dict[str, Any]) -> bool:
    """Return True only when the config is valid and fully populated.

    Equivalent to `is_valid_config`; kept as a public alias for clarity at
    the startup gate. `output_dir` may point at a directory that does not
    exist yet (it is created on demand); every other path must point to an
    existing file.
    """
    return is_valid_config(config)
