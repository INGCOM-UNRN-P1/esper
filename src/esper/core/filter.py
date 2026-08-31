"""Filtro de supresión de advertencias repetitivas y derivadas para ESPER."""

from __future__ import annotations
from typing import List, Tuple
from esper.core.models import GccDiagnostic, DiagnosticSeverity


def filter_and_deduplicate(
    diagnostics: List[GccDiagnostic],
    max_per_type: int = 2,
    suppress_header_cascades: bool = True
) -> Tuple[List[GccDiagnostic], int]:
    """Filtra y deduplica advertencias repetitivas o en cascada para no abrumar al estudiante.
    
    Retorna: (diagnosticos_filtrados, cantidad_suprimidos)
    """
    seen_counts: dict[str, int] = {}
    filtered: List[GccDiagnostic] = []
    suppressed_count = 0

    first_error_file = None
    for d in diagnostics:
        if d.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL_ERROR):
            first_error_file = d.file_path
            break

    for d in diagnostics:
        # Clave para deduplicación: archivo + flag/title
        key = f"{d.file_path}:{d.flag or d.title_es}"

        # 1. Supresión de cascadas: Si hubo un error grave en un .h o cabecera previa, y este es un warning derivado en otro archivo
        if suppress_header_cascades and first_error_file and first_error_file.endswith(".h") and not d.file_path.endswith(".h"):
            if d.severity == DiagnosticSeverity.NOTE or "previous declaration" in d.raw_message.lower():
                d.is_suppressed = True
                suppressed_count += 1
                continue

        # 2. Control de repeticiones máximas del mismo tipo
        count = seen_counts.get(key, 0)
        if count >= max_per_type:
            d.is_suppressed = True
            suppressed_count += 1
            continue

        seen_counts[key] = count + 1
        filtered.append(d)

    return filtered, suppressed_count
