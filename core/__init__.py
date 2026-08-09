"""
APKTrace core package.

Contains all non-UI business logic:

  - core.config     - config.json I/O, defaults and setup validation
  - core.paths      - output directory management
  - core.tool_loader- lazy loading of the analyzer tool scripts (submodules)
  - core.analyzers  - the run_*_analysis orchestration functions
  - core.launcher   - the application composition root (launch_app)

The UI package (ui/) consumes these through the callables injected by
`core.launcher.launch_app`; it never imports the tools directly.
"""

from .analyzers import run_java_analysis, run_manifest_analysis, run_native_analysis
from .config import (
    API_KEYS,
    DEFAULT_CONFIG,
    REQUIRED_PATH_KEYS,
    ensure_config_exists,
    is_setup_complete,
    is_valid_config,
    load_config,
    save_config,
    validate_config,
)
from .launcher import launch_app
from .paths import ensure_output_dirs

__all__ = [
    "API_KEYS",
    "DEFAULT_CONFIG",
    "REQUIRED_PATH_KEYS",
    "ensure_config_exists",
    "load_config",
    "save_config",
    "validate_config",
    "is_valid_config",
    "is_setup_complete",
    "ensure_output_dirs",
    "run_manifest_analysis",
    "run_java_analysis",
    "run_native_analysis",
    "launch_app",
]
