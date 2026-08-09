"""
core/config.py

Responsible for everything related to the application's config.json:
defaults, the location of the file, loading, merging, saving, and the
"is setup complete?" check used to decide whether the first-run wizard
must be shown.

The UI never touches config.json directly - it only calls the functions
injected by `core.launcher.launch_app`.
"""

import copy
import json
from pathlib import Path
from typing import Any, Dict

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config.json"

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


def merge_config(config: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """Merge `updates` on top of a deep copy of `config`, section by section."""
    merged = copy.deepcopy(config)
    merged["paths"].update(updates.get("paths", {}) or {})
    merged["api"].update(updates.get("api", {}) or {})
    return merged


def load_config() -> Dict[str, Any]:
    """Read config.json into memory, filling any missing keys with defaults.

    A missing, corrupt, or unreadable file never raises: the defaults are
    returned instead, so callers can always treat the result as valid.
    """
    config = copy.deepcopy(DEFAULT_CONFIG)
    if CONFIG_PATH.exists():
        try:
            with CONFIG_PATH.open("r", encoding="utf-8") as file:
                data = json.load(file) or {}
            config = merge_config(config, data)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[WARN] Could not read config.json ({exc}); falling back to defaults.")
    return config


def save_config(config: Dict[str, Any]) -> None:
    """Persist `config` to config.json, always writing every known key."""
    merged = merge_config(DEFAULT_CONFIG, config)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CONFIG_PATH.open("w", encoding="utf-8") as file:
        json.dump(merged, file, indent=4, ensure_ascii=False)


def is_setup_complete(config: Dict[str, Any]) -> bool:
    """Return True only when all 4 required paths are present and valid.

    `output_dir` may point at a directory that does not exist yet (it is
    created on demand); every other path must point to an existing file.
    """
    paths = config.get("paths", {})
    for key in REQUIRED_PATH_KEYS:
        value = (paths.get(key) or "").strip()
        if not value:
            return False
        if key != "output_dir" and not Path(value).expanduser().exists():
            return False
    return True
