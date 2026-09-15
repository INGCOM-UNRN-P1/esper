"""CLI principal de ESPER."""

from __future__ import annotations
import sys
import json
from pathlib import Path
from typing import List, Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from esper import __version__
from esper.core.models import CompilationReport, DiagnosticSeverity, GccDiagnostic
from esper.core.gcc_parser import parse_gcc_output, run_gcc_and_explain
from esper.core.diagnostic_catalog import lookup_explanation, list_catalog_entries
from esper.core.formatter import format_diagnostic_panel
from esper.core.filter import filter_and_deduplicate
from esper.core.suggest_flags import analyze_missing_flags
from esper.core.arch_check import check_arch_incompatibilities
from esper.core.guide_generator import generate_resolution_guide
from esper.core.doctor import ejecutar_diagnostico_doctor

app = typer.Typer(
    name="esper",
    help="Explicador pedagógico y formateador interactivo de salidas y errores de GCC/Clang",
    add_completion=True
)
console = Console()


def version_callback(value: bool):
    if value:
        console.print(f"[bold cyan]esper[/bold cyan] versión [green]{__version__}[/green]")
        raise typer.Exit(code=0)


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "-v",
        "--version",
        help="Muestra la versión de ESPER y finaliza.",
        callback=version_callback,
        is_eager=True,
    )
):
    """Punto de entrada principal de ESPER."""
    pass


def render_diagnostics(report: CompilationReport, dedup: bool = False):
    """Muestra diagnósticos de compilación en paneles estructurados Rich de alto contraste."""
    if report.passed and not report.diagnostics:
        console.print(Panel(
            "[bold green]✓ Compilación Exitosa sin Errores ni Advertencias[/bold green]\n"
            "El código compila limpiamente bajo los estándares de la cátedra.",
            title="[bold green]ESPER GCC Explainer[/bold green]"
        ))
        return

    diags = report.diagnostics
    if dedup:
        diags, supp_count = filter_and_deduplicate(diags)
        report.suppressed_count = supp_count

    for diag in diags:
        panel = format_diagnostic_panel(diag)
        console.print(panel)

    if report.suppressed_count > 0:
        console.print(f"[dim]ℹ Se suprimieron {report.suppressed_count} advertencias repetitivas o en cascada para mayor claridad.[/dim]")


def generar_seccion_markdown(report: CompilationReport) -> str:
    """Genera sección de diagnóstico pedagógico GCC para Dredd."""
    lines = [
        "<!-- dredd-section: esper v1.0.0 -->\n",
        "## Explicador Pedagógico de Compilación (Esper)\n",
    ]
    estado = "✓ Compilación Exitosa" if report.passed else "❌ Falló Compilación"
    lines.append(f"- **Estado:** {estado}")
    lines.append(f"- **Diagnósticos procesados:** {len(report.diagnostics)}\n")
    if report.passed and not report.diagnostics:
        lines.append("> [!TIP]\n> **Sin Advertencias:** El código no produjo advertencias ni errores del compilador.\n")
    else:
        lines.append("| Archivo:Línea | Severidad | Diagnóstico | Norma ISO C | Causa Raíz | Sugerencia |")
        lines.append("| :--- | :---: | :--- | :--- | :--- | :--- |")
        for d in report.diagnostics:
            loc = f"`{Path(d.file_path).name}:{d.line_number}`"
            sev = d.severity.value if hasattr(d.severity, "value") else str(d.severity)
            norma_txt = f"*{d.iso_c_citation}*" if d.iso_c_citation else "N/A"
            tit_limpio = d.title_es.replace("|", "&#124;")
            norma_limpia = norma_txt.replace("|", "&#124;")
            causa_limpia = d.root_cause_es.replace("|", "&#124;")
            sug_limpia = d.suggestion_es.replace("|", "&#124;")
            lines.append(f"| {loc} | **{sev}** | {tit_limpio} | {norma_limpia} | {causa_limpia} | {sug_limpia} |")
        lines.append("")
    return "\n".join(lines)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def compile(
    ctx: typer.Context,
    dedup: bool = typer.Option(False, "--dedup", help="Suprimir advertencias repetitivas o en cascada."),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado"),
    output_md: Optional[Path] = typer.Option(None, "--md", "--output-md", help="Generar sección de reporte en formato Markdown para fusión en Dredd."),
    guide: bool = typer.Option(False, "--guide", help="Generar guía detallada paso a paso en Markdown."),
):
    """Envuelve la ejecución de GCC y traduce todos los errores y advertencias."""
    args = ctx.args
    if not args:
        console.print("[yellow]Uso: esper compile <archivos.c> -o <binario> [flags GCC][/yellow]")
        raise typer.Exit(code=2)

    report = run_gcc_and_explain(args)

    if dedup:
        report.diagnostics, report.suppressed_count = filter_and_deduplicate(report.diagnostics)

    if guide:
        guide_text = generate_resolution_guide(report)
        console.print(guide_text)
        raise typer.Exit(code=0 if report.passed else 1)

    if output_md:
        md_text = generar_seccion_markdown(report)
        output_md.parent.mkdir(parents=True, exist_ok=True)
        output_md.write_text(md_text, encoding="utf-8")
        console.print(f"[bold green]✓ Sección Markdown generada en:[/bold green] {output_md}")
        raise typer.Exit(code=0 if report.passed else 1)

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        if not report.passed:
            raise typer.Exit(code=report.exit_code or 1)
        return

    render_diagnostics(report, dedup=False)
    if not report.passed:
        raise typer.Exit(code=report.exit_code or 1)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def wrapper(
    ctx: typer.Context,
):
    """Modo Wrapper transparente para Makefiles: ejecuta el comando interceptando errores."""
    args = ctx.args
    if not args:
        console.print("[yellow]Uso: esper wrapper gcc main.c -o app[/yellow]")
        raise typer.Exit(code=2)

    cmd_args = args[1:] if args[0] in ("gcc", "clang") else args
    report = run_gcc_and_explain(cmd_args)
    render_diagnostics(report)
    raise typer.Exit(code=report.exit_code)


@app.command(context_settings={"allow_extra_args": True, "ignore_unknown_options": True})
def explain(
    ctx: typer.Context,
    query: Optional[str] = typer.Argument(None, help="Mensaje de error, texto de GCC o nombre de flag (ej: -Wunused-variable)"),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON estructurado"),
    guide: bool = typer.Option(False, "--guide", help="Generar guía paso a paso en Markdown.")
):
    """Explica un mensaje de error puntual o consulta teórica de cualquier advertencia de GCC."""
    actual_query = query or " ".join(ctx.args)
    if not actual_query:
        console.print("[yellow]Uso: esper explain <mensaje_error_o_flag>[/yellow]")
        raise typer.Exit(code=2)

    diagnostics = parse_gcc_output(actual_query)

    if not diagnostics:
        title, explanation, root_cause, suggestion, flag, citation, sugg_flags = lookup_explanation(actual_query)
        diagnostics = [GccDiagnostic(
            file_path="consulta",
            line_number=1,
            severity=DiagnosticSeverity.WARNING if "-w" in query.lower() else DiagnosticSeverity.ERROR,
            raw_message=query,
            flag=flag,
            title_es=title,
            explanation_es=explanation,
            root_cause_es=root_cause,
            suggestion_es=suggestion,
            iso_c_citation=citation,
            suggested_flags=sugg_flags
        )]

    report = CompilationReport(
        command=["explain"],
        exit_code=0 if "-w" in query.lower() else 1,
        passed=False,
        diagnostics=diagnostics,
        raw_stderr=query
    )

    if guide:
        guide_text = generate_resolution_guide(report)
        console.print(guide_text)
        return

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        return

    render_diagnostics(report)


@app.command("catalog")
@app.command("list-warnings")
def list_warnings(
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON.")
):
    """Lista todas las advertencias y reglas pedagógicas documentadas en el catálogo de ESPER."""
    entries = list_catalog_entries()
    if json_output:
        print(json.dumps(entries, indent=2, ensure_ascii=False))
        return

    table = Table(title="Catálogo de Advertencias y Diagnósticos de GCC/Clang (ESPER)", show_header=True, header_style="bold magenta")
    table.add_column("Flag / Concepto", style="cyan")
    table.add_column("Diagnóstico en Español", style="bold white")
    table.add_column("Norma ISO C", style="italic yellow")

    for e in entries:
        flag_s = e["flag"] or e["key"]
        norma_s = e["citation"] or "-"
        table.add_row(flag_s, e["title"], norma_s)

    console.print(table)


@app.command("suggest-flags")
def suggest_flags_cmd(
    fuente: Path = typer.Argument(..., help="Archivo fuente C o log de compilación.", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON.")
):
    """Analiza un archivo o error y sugiere flags de compilación/enlazado faltantes."""
    content = fuente.read_text(encoding="utf-8", errors="replace")
    diagnostics = parse_gcc_output(content)
    suggestions = analyze_missing_flags(content, diagnostics)

    if json_output:
        print(json.dumps(suggestions, indent=2, ensure_ascii=False))
        return

    if not suggestions:
        console.print("[bold green]✓ No se detectaron flags faltantes de enlazado o bibliotecas estándar.[/bold green]")
        return

    table = Table(title="Sugerencias de Flags de Compilación y Enlazado", show_header=True, header_style="bold cyan")
    table.add_column("Flag Sugerido", style="bold yellow")
    table.add_column("Motivo", style="white")
    table.add_column("Instrucción de Remediación", style="green")

    for s in suggestions:
        table.add_row(s["flag"], s["reason"], s["fix"])

    console.print(table)


@app.command("check-arch")
def check_arch_cmd(
    log_file: Path = typer.Argument(..., help="Archivo con la salida de compilador a auditar.", exists=True),
    json_output: bool = typer.Option(False, "--json", help="Emitir salida en formato JSON.")
):
    """Audita advertencias relacionadas con incompatibilidades de tamaño en 32 vs 64 bits."""
    raw_text = log_file.read_text(encoding="utf-8", errors="replace")
    findings = check_arch_incompatibilities(raw_text)

    if json_output:
        print(json.dumps(findings, indent=2, ensure_ascii=False))
        return

    if not findings:
        console.print("[bold green]✓ No se detectaron riesgos de portabilidad 32 vs 64 bits en el log analizado.[/bold green]")
        return

    for f in findings:
        console.print(Panel(
            f"[bold red]🚨 {f['title']}[/bold red]\n\n"
            f"[bold]Explicación:[/bold] {f['explanation']}\n\n"
            f"[bold yellow]Causa Raíz:[/bold yellow] {f['root_cause']}\n\n"
            f"[bold green]↳ Remediación:[/bold green] {f['suggestion']}",
            title="[bold red]Incompatibilidad 32/64 bits[/bold red]"
        ))


@app.command("guide")
def guide_cmd(
    fuente: Path = typer.Argument(..., help="Archivo C a compilar y generar guía.", exists=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Guardar la guía en un archivo Markdown.")
):
    """Genera una guía de resolución paso a paso en Markdown para el archivo C indicado."""
    report = run_gcc_and_explain([str(fuente)])
    guide_text = generate_resolution_guide(report)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(guide_text, encoding="utf-8")
        console.print(f"[bold green]✓ Guía Markdown generada en:[/bold green] {output}")
    else:
        console.print(guide_text)


@app.command()
def pipe(
    dedup: bool = typer.Option(False, "--dedup", help="Suprimir advertencias repetitivas o en cascada."),
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

    if dedup:
        report.diagnostics, report.suppressed_count = filter_and_deduplicate(report.diagnostics)

    if json_output:
        print(json.dumps(report.model_dump(), indent=2, ensure_ascii=False))
        if not report.passed:
            raise typer.Exit(code=1)
        return

    render_diagnostics(report, dedup=False)
    if not report.passed:
        raise typer.Exit(code=1)


@app.command("doctor")
def doctor_cmd(
    json_output: bool = typer.Option(False, "--json", help="Emitir diagnóstico en formato JSON."),
    verbose: bool = typer.Option(False, "-v", "--verbose", help="Mostrar detalle completo.")
):
    """Audita el entorno y verifica la disponibilidad de compiladores y dependencias."""
    rep = ejecutar_diagnostico_doctor()
    if json_output:
        print(json.dumps(rep.model_dump(), indent=2, ensure_ascii=False))
        raise typer.Exit(code=0 if rep.all_ok else 1)

    table = Table(title="Diagnóstico del Entorno (ESPER Doctor)", show_header=True, header_style="bold cyan")
    table.add_column("Componente", style="bold")
    table.add_column("Categoría", style="dim")
    table.add_column("Tipo", style="yellow")
    table.add_column("Estado", style="bold")
    table.add_column("Detalle", style="white")

    for c in rep.checks:
        st_color = "green" if c.status == "OK" else ("yellow" if c.status in ("INFO", "WARNING") else "red")
        req_s = "Requerido" if c.required else "Opcional"
        det = c.version if c.version else c.detail
        table.add_row(c.name, c.category, req_s, f"[{st_color}]{c.status}[/{st_color}]", det)

    console.print(table)
    if rep.all_ok:
        console.print("[bold green]✓ Todos los componentes requeridos por ESPER están disponibles.[/bold green]")
        raise typer.Exit(code=0)
    else:
        console.print("[bold red]❌ Faltan componentes críticos para el funcionamiento de ESPER.[/bold red]")
        raise typer.Exit(code=1)


@app.command("report")
def report_cmd(
    fuente: Path = typer.Argument(..., help="Archivo C a compilar y explicar."),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Ruta de destino del archivo Markdown."),
):
    """Genera directamente la sección de reporte Markdown de ESPER para Dredd."""
    report = run_gcc_and_explain([str(fuente)])
    md_content = generar_seccion_markdown(report)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(md_content, encoding="utf-8")
        console.print(f"[bold green]✓ Reporte Markdown generado en:[/bold green] {output}")
    else:
        print(md_content)


@app.command()
def version():
    """Muestra la versión de ESPER."""
    console.print(f"[bold cyan]ESPER[/bold cyan] versión [green]{__version__}[/green]")


if __name__ == "__main__":
    app()
