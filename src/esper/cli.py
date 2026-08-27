"""CLI principal de ESPER."""

import sys
import json
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from esper.core.models import CompilationReport, DiagnosticSeverity
from esper.core.gcc_parser import parse_gcc_output, run_gcc_and_explain
from esper.core.diagnostic_catalog import lookup_explanation

app = typer.Typer(
    name="esper",
    help="Explicador pedagógico y formateador interactivo de salidas y errores de GCC/Clang",
    add_completion=True
)
console = Console()


def render_diagnostics(report: CompilationReport):
    """Muestra diagnósticos de compilación en paneles estructurados Rich."""
    if report.passed and not report.diagnostics:
        console.print(Panel(
            "[bold green]✓ Compilación Exitosa sin Errores ni Advertencias[/bold green]\n"
            "El código compila limpiamente bajo los estándares de la cátedra.",
            title="[bold green]ESPER GCC Explainer[/bold green]"
        ))
        return

    for diag in report.diagnostics:
        if diag.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL_ERROR):
            color = "red"
            badge = "ERROR"
        elif diag.severity == DiagnosticSeverity.WARNING:
            color = "yellow"
            badge = "WARNING"
        else:
            color = "blue"
            badge = "NOTE"

        loc = f"{diag.file_path}:{diag.line_number}"
        if diag.column_number:
            loc += f":{diag.column_number}"

        flag_str = f" [{diag.flag}]" if diag.flag else ""
        content = (
            f"[bold {color}]🚨 {diag.title_es}[/bold {color}]\n\n"
            f"• [bold]Ubicación:[/bold] {loc}{flag_str}\n"
            f"• [bold]Mensaje de GCC:[/bold] [dim]{diag.raw_message}[/dim]\n"
        )
        if diag.code_snippet:
            content += f"• [bold]Código:[/bold] [cyan]{diag.code_snippet}[/cyan]\n"

        content += (
            f"\n[bold]¿Qué significa?[/bold]\n{diag.explanation_es}\n\n"
            f"[bold yellow]Causa Raíz Típica:[/bold yellow]\n{diag.root_cause_es}\n\n"
            f"[bold green]↳ Acción Sugerida:[/bold green]\n{diag.suggestion_es}"
        )

        console.print(Panel(content, title=f"[bold {color}]{badge}[/bold {color}]"))


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def compile(
    ctx: typer.Context,
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado")
):
    """Envuelve la ejecución de GCC y traduce todos los errores y advertencias."""
    args = ctx.args
    if not args:
        console.print("[yellow]Uso: esper compile <archivos.c> -o <binario> [flags GCC][/yellow]")
        raise typer.Exit(code=2)

    report = run_gcc_and_explain(args)

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        if not report.passed:
            raise typer.Exit(code=report.exit_code or 1)
        return

    render_diagnostics(report)
    if not report.passed:
        raise typer.Exit(code=report.exit_code or 1)


@app.command()
def explain(
    error_message: str = typer.Argument(..., help="Mensaje o texto de error de GCC a explicar"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado")
):
    """Explica un mensaje de error puntual o texto copiado de GCC."""
    diagnostics = parse_gcc_output(error_message)

    if not diagnostics:
        title, explanation, root_cause, suggestion = lookup_explanation(error_message)
        from esper.core.models import GccDiagnostic
        diagnostics = [GccDiagnostic(
            file_path="input",
            line_number=1,
            severity=DiagnosticSeverity.ERROR,
            raw_message=error_message,
            title_es=title,
            explanation_es=explanation,
            root_cause_es=root_cause,
            suggestion_es=suggestion
        )]

    report = CompilationReport(
        command=["explain"],
        exit_code=1,
        passed=False,
        diagnostics=diagnostics,
        raw_stderr=error_message
    )

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        return

    render_diagnostics(report)


@app.command()
def pipe(
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado")
):
    """Lee mensajes de GCC desde stdin (tubería: `gcc ... 2>&1 | esper pipe`)."""
    raw_input = sys.stdin.read()
    diagnostics = parse_gcc_output(raw_input)
    has_errors = any(d.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL_ERROR) for d in diagnostics)

    report = CompilationReport(
        command=["pipe"],
        exit_code=1 if has_errors else 0,
        passed=not has_errors,
        diagnostics=diagnostics,
        raw_stderr=raw_input
    )

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        if not report.passed:
            raise typer.Exit(code=1)
        return

    render_diagnostics(report)
    if not report.passed:
        raise typer.Exit(code=1)


@app.command()
def version():
    """Muestra la versión de ESPER."""
    from esper import __version__
    console.print(f"[bold cyan]ESPER[/bold cyan] versión [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
