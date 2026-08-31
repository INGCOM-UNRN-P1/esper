"""Generador de guías de resolución paso a paso en Markdown para consultas estudiantiles."""

from __future__ import annotations
from pathlib import Path
from typing import List
from esper.core.models import CompilationReport, GccDiagnostic


def generate_resolution_guide(report: CompilationReport) -> str:
    """Genera una guía interactiva en Markdown con pasos claros de resolución para el alumno."""
    lines = [
        "# Guía Didáctica de Resolución de Errores de Compilación",
        "",
        "> [!NOTE]",
        "> Esta guía fue sintetizada automáticamente por **ESPER** para ayudarte a comprender y resolver cada advertencia y error detectado por el compilador.",
        ""
    ]

    if report.passed and not report.diagnostics:
        lines.append("## ✓ Estado del Código")
        lines.append("El programa compila limpiamente sin advertencias ni errores pendientes.")
        return "\n".join(lines)

    lines.append(f"## Resumen de Diagnósticos ({len(report.diagnostics)} ítems)")
    lines.append("")

    for idx, d in enumerate(report.diagnostics, 1):
        sev_icon = "❌" if "error" in str(d.severity).lower() else "⚠️"
        loc = f"`{Path(d.file_path).name}:{d.line_number}`"
        lines.append(f"### {idx}. {sev_icon} {d.title_es} ({loc})")
        lines.append("")
        lines.append(f"- **Mensaje original:** `{d.raw_message}`")
        if d.flag:
            lines.append(f"- **Flag de control:** `{d.flag}`")
        if d.iso_c_citation:
            lines.append(f"- **Norma estándar:** *{d.iso_c_citation}*")
        lines.append("")
        if d.code_snippet:
            lines.append("```c")
            lines.append(f"// Línea {d.line_number}")
            lines.append(d.code_snippet)
            lines.append("```")
            lines.append("")
        lines.append(f"**¿Qué significa?**\n{d.explanation_es}")
        lines.append("")
        lines.append(f"**Causa raíz habitual:**\n{d.root_cause_es}")
        lines.append("")
        lines.append("**Pasos para resolverlo:**")
        lines.append(f"1. {d.suggestion_es}")
        if d.suggested_flags:
            flags_str = " ".join(d.suggested_flags)
            lines.append(f"2. Asegurate de incluir los flags de enlazado necesarios en el comando: `{flags_str}`")
        lines.append("")

    return "\n".join(lines)
