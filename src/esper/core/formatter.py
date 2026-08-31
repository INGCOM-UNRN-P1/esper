"""Formateador visual de alto contraste y bloques delimitados con Rich para ESPER."""

from __future__ import annotations
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from esper.core.models import GccDiagnostic, DiagnosticSeverity, CompilationReport


def format_diagnostic_panel(diag: GccDiagnostic) -> Panel:
    """Genera un panel Rich con colores de alto contraste y código enmarcado."""
    if diag.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL_ERROR):
        color = "bright_red"
        badge = "ERROR"
        border_style = "bold red"
    elif diag.severity == DiagnosticSeverity.WARNING:
        color = "bright_yellow"
        badge = "ADVERTENCIA"
        border_style = "bold yellow"
    else:
        color = "bright_cyan"
        badge = "NOTA"
        border_style = "cyan"

    loc = f"{diag.file_path}:{diag.line_number}"
    if diag.column_number:
        loc += f":{diag.column_number}"

    flag_text = f" [{diag.flag}]" if diag.flag else ""
    
    body = [
        f"[bold {color}]🚨 {diag.title_es}[/bold {color}]",
        f"• [bold]Ubicación:[/bold] [underline]{loc}[/underline]{flag_text}",
        f"• [bold]Mensaje de GCC:[/bold] [dim]{diag.raw_message}[/dim]"
    ]

    if diag.iso_c_citation:
        body.append(f"• [bold magenta]Norma ISO C:[/bold magenta] [italic]{diag.iso_c_citation}[/italic]")

    if diag.code_snippet:
        snippet_lines = [
            "\n[bold]Fragmento de Código Afectado:[/bold]",
            f"[dim]┌─ Línea {diag.line_number}[/dim]",
            f"[bold white]│  {diag.code_snippet}[/bold white]"
        ]
        if diag.column_number and diag.column_number > 0:
            indent = " " * (diag.column_number - 1)
            snippet_lines.append(f"[bold {color}]│  {indent}^~~~[/bold {color}]")
        snippet_lines.append("[dim]└─────────────────────────────────[/dim]")
        body.extend(snippet_lines)

    body.append(f"\n[bold]¿Qué significa?[/bold]\n{diag.explanation_es}")
    body.append(f"\n[bold yellow]Causa Raíz Típica:[/bold yellow]\n{diag.root_cause_es}")
    body.append(f"\n[bold green]↳ Acción Sugerida:[/bold green]\n{diag.suggestion_es}")

    if diag.suggested_flags:
        body.append(f"\n[bold cyan]Flags sugeridos:[/bold cyan] `{' '.join(diag.suggested_flags)}`")

    return Panel("\n".join(body), title=f"[bold {color}]{badge}[/bold {color}]", border_style=border_style)
