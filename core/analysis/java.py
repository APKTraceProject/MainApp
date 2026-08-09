from typing import Any, Dict, Optional

from .base import StatusCallback


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
