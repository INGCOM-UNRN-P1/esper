"""Generador de guías de resolución paso a paso — Delegado a DAEDALUS."""

from __future__ import annotations
import sys
from pathlib import Path

try:
    from daedalus.core.guide_generator import generate_resolution_guide
except ImportError:
    sibling = Path(__file__).resolve().parents[4] / "daedalus" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    from daedalus.core.guide_generator import generate_resolution_guide

__all__ = ["generate_resolution_guide"]
