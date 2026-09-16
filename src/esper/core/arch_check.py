"""Auditoría de incompatibilidades 32 vs 64 bits — Delegado a DAEDALUS."""

from __future__ import annotations
import sys
from pathlib import Path

try:
    from daedalus.core.arch_check import check_arch_incompatibilities
except ImportError:
    sibling = Path(__file__).resolve().parents[4] / "daedalus" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    from daedalus.core.arch_check import check_arch_incompatibilities

__all__ = ["check_arch_incompatibilities"]
