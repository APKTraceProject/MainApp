"""
core/paths.py

Filesystem helpers used by the analyzer runners: turning the configured
output directory string into a set of real, existing subdirectories.
"""

from pathlib import Path
from typing import Dict


def ensure_output_dirs(output_dir_str: str) -> Dict[str, Path]:
    """Create <output_dir>/{apktool_output,jadx_output,ghidra_output} and return them.

    The root output directory is created if needed; each analyzer tool then
    writes its own report/output into the matching subdirectory.
    """
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
