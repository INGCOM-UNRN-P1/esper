"""Base de datos de referencias normativas ISO C — Delegado a DAEDALUS."""

from __future__ import annotations
import sys
from pathlib import Path

try:
    from daedalus.core.standards_db import STANDARDS_ISO_C, get_standard_citation
except ImportError:
    sibling = Path(__file__).resolve().parents[4] / "daedalus" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    from daedalus.core.standards_db import STANDARDS_ISO_C, get_standard_citation

__all__ = ["STANDARDS_ISO_C", "get_standard_citation"]
