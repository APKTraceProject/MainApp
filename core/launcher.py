"""
core/launcher.py

The application composition root. `launch_app` is the single place that
glues the pieces together, implementing the startup verification flow:

    1. config.json missing  -> `ensure_config_exists()` creates a default
       one, then the setup wizard is shown.
    2. config.json present  -> `load_config()` parses it and
       `validate_config()` checks required keys, missing fields, values.
    3. invalid / incomplete -> the setup wizard is shown so the user can
       fix or populate the config; it writes the result back to config.json.
    4. valid                -> config is used and the wizard is skipped.

`main.py` only calls `launch_app()` and nothing else.
"""

from typing import Any, Dict

from .analyzers import run_manifest_analysis, run_native_analysis
from .config import ensure_config_exists, load_config, save_config, validate_config


def _print_config_problems(problems: Any) -> None:
    for problem in problems:
        print(f"    - {problem}")


def launch_app() -> None:
    """Bootstrap APKTrace: verify config -> wizard (if needed) -> main window."""
    from ui import AndroidAnalyzerApp, SetupWizard

    ensure_config_exists()
    config: Dict[str, Any] = load_config()

    problems = validate_config(config)
    if problems:
        print("[*] Configuration is missing or incomplete:")
        _print_config_problems(problems)
        print("[*] Opening the setup window so you can fix it...")

        wizard = SetupWizard(config=config, on_complete=save_config)
        wizard.mainloop()

        config = load_config()
        problems = validate_config(config)
        if problems:
            print("[!] Setup was not completed, so APKTrace cannot start. Exiting.")
            _print_config_problems(problems)
            return

    app = AndroidAnalyzerApp(
        config=config,
        run_manifest_analysis=run_manifest_analysis,
        run_native_analysis=run_native_analysis,
        save_config=save_config,
    )
    app.mainloop()
