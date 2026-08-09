"""
core/launcher.py

The application composition root. `launch_app` is the single place that
glues the pieces together:

    - loads/validates config (core.config),
    - shows the first-run setup wizard when required paths are missing,
    - constructs the main window (ui.AndroidAnalyzerApp) with the analyzer
      callables (core.analyzers) injected.

`main.py` only calls `launch_app()` and nothing else.
"""

from typing import Any, Dict

from .analyzers import run_manifest_analysis
from .config import is_setup_complete, load_config, save_config


def launch_app() -> None:
    """Bootstrap APKTrace: wizard (if needed) -> main window."""
    from ui import AndroidAnalyzerApp, SetupWizard

    config: Dict[str, Any] = load_config()

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
