"""Catálogo de explicaciones pedagógicas de GCC/Clang — Delegado a DAEDALUS."""

from __future__ import annotations
import sys
from pathlib import Path

try:
    from daedalus.core.diagnostic_catalog import (
        CATALOGO_GCC,
        lookup_explanation,
        list_catalog_entries,
    )
except ImportError:
    sibling = Path(__file__).resolve().parents[4] / "daedalus" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    from daedalus.core.diagnostic_catalog import (
        CATALOGO_GCC,
        lookup_explanation,
        list_catalog_entries,
    )

__all__ = ["CATALOGO_GCC", "lookup_explanation", "list_catalog_entries"]
