"""Sugerencia didáctica de flags de compilación y enlazado — Delegado a DAEDALUS."""

from __future__ import annotations
import sys
from pathlib import Path

try:
    from daedalus.core.suggest_flags import (
        MATH_SYMBOLS,
        PTHREAD_SYMBOLS,
        POSIX_FUNCTIONS,
        analyze_missing_flags,
    )
except ImportError:
    sibling = Path(__file__).resolve().parents[4] / "daedalus" / "src"
    if sibling.is_dir() and str(sibling) not in sys.path:
        sys.path.insert(0, str(sibling))
    from daedalus.core.suggest_flags import (
        MATH_SYMBOLS,
        PTHREAD_SYMBOLS,
        POSIX_FUNCTIONS,
        analyze_missing_flags,
    )

__all__ = [
    "MATH_SYMBOLS",
    "PTHREAD_SYMBOLS",
    "POSIX_FUNCTIONS",
    "analyze_missing_flags",
]
