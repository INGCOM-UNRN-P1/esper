"""Tests de las funcionalidades QoL y subcomandos de ESPER."""

from pathlib import Path
from typer.testing import CliRunner
from esper.cli import app
from esper.core.models import CompilationReport, GccDiagnostic, DiagnosticSeverity
from esper.core.diagnostic_catalog import lookup_explanation, list_catalog_entries
from esper.core.standards_db import get_standard_citation
from esper.core.filter import filter_and_deduplicate
from esper.core.suggest_flags import analyze_missing_flags
from esper.core.arch_check import check_arch_incompatibilities
from esper.core.guide_generator import generate_resolution_guide
from esper.core.formatter import format_diagnostic_panel
from esper.core.doctor import ejecutar_diagnostico_doctor

runner = CliRunner()


def test_doctor_execution():
    rep = ejecutar_diagnostico_doctor()
    assert rep.all_ok is True
    assert any(c.name == "gcc" for c in rep.checks)

    res = runner.invoke(app, ["doctor", "--json"])
    assert res.exit_code == 0
    assert '"all_ok": true' in res.output


def test_standards_citations():
    cit = get_standard_citation("implicit-function-declaration")
    assert cit is not None
    assert "ISO/IEC 9899" in cit

    cit_fmt = get_standard_citation("format")
    assert cit_fmt is not None
    assert "§7.21.6" in cit_fmt


def test_filter_and_deduplicate():
    diags = [
        GccDiagnostic(
            file_path="main.c",
            line_number=10,
            severity=DiagnosticSeverity.WARNING,
            raw_message="unused variable 'a'",
            flag="-Wunused-variable",
            title_es="Variable Declarada sin Uso",
            explanation_es="Exp",
            root_cause_es="Cause",
            suggestion_es="Sugg"
        ),
        GccDiagnostic(
            file_path="main.c",
            line_number=15,
            severity=DiagnosticSeverity.WARNING,
            raw_message="unused variable 'b'",
            flag="-Wunused-variable",
            title_es="Variable Declarada sin Uso",
            explanation_es="Exp",
            root_cause_es="Cause",
            suggestion_es="Sugg"
        ),
        GccDiagnostic(
            file_path="main.c",
            line_number=20,
            severity=DiagnosticSeverity.WARNING,
            raw_message="unused variable 'c'",
            flag="-Wunused-variable",
            title_es="Variable Declarada sin Uso",
            explanation_es="Exp",
            root_cause_es="Cause",
            suggestion_es="Sugg"
        ),
    ]

    filtered, supp = filter_and_deduplicate(diags, max_per_type=2)
    assert len(filtered) == 2
    assert supp == 1


def test_suggest_flags():
    stderr_math = "main.c:(.text+0x15): undefined reference to `sin'\nmain.c:(.text+0x20): undefined reference to `sqrt'"
    suggs = analyze_missing_flags(stderr_math, [])
    assert any(s["flag"] == "-lm" for s in suggs)

    stderr_posix = "main.c:5:10: warning: implicit declaration of function ‘strdup’"
    suggs_posix = analyze_missing_flags(stderr_posix, [])
    assert any(s["flag"] == "-D_POSIX_C_SOURCE=200809L" for s in suggs_posix)


def test_arch_check():
    raw_cast = "main.c:12:15: warning: cast from pointer to integer of different size [-Wpointer-to-int-cast]"
    findings = check_arch_incompatibilities(raw_cast)
    assert len(findings) == 1
    assert "32 vs 64 bits" in findings[0]["title"]
    assert "uintptr_t" in findings[0]["suggestion"]


def test_guide_generator():
    diag = GccDiagnostic(
        file_path="main.c",
        line_number=42,
        severity=DiagnosticSeverity.WARNING,
        raw_message="comparison of integer expressions of different signedness [-Wsign-compare]",
        flag="-Wsign-compare",
        title_es="Comparación entre Enteros con y sin Signo",
        explanation_es="Explicación detallada.",
        root_cause_es="Causa raíz.",
        suggestion_es="Alineá los tipos a unsigned.",
        code_snippet="if (i < strlen(s))",
        iso_c_citation="ISO/IEC 9899:2011 §6.3.1"
    )
    rep = CompilationReport(
        passed=False,
        diagnostics=[diag]
    )
    guide = generate_resolution_guide(rep)
    assert "# Guía Didáctica" in guide
    assert "ISO/IEC 9899:2011" in guide
    assert "strlen(s)" in guide


def test_catalog_command():
    res = runner.invoke(app, ["catalog", "--json"])
    assert res.exit_code == 0
    assert "implicit declaration of function" in res.output


def test_explain_by_warning_flag():
    res = runner.invoke(app, ["explain", "-Wunused-variable"])
    assert res.exit_code == 0
    assert "Variable Declarada sin Uso" in res.output or "-Wunused-variable" in res.output


def test_suggest_flags_command(tmp_path):
    log = tmp_path / "build.log"
    log.write_text("undefined reference to `sin'\n")
    res = runner.invoke(app, ["suggest-flags", str(log), "--json"])
    assert res.exit_code == 0
    assert "-lm" in res.output


def test_check_arch_command(tmp_path):
    log = tmp_path / "arch.log"
    log.write_text("warning: format ‘%d’ expects argument of type ‘int’, but argument 2 has type ‘size_t’ [-Wformat=]\n")
    res = runner.invoke(app, ["check-arch", str(log), "--json"])
    assert res.exit_code == 0
    assert "%zu" in res.output[0:] or "size_t" in res.output


def test_formatter_panel():
    diag = GccDiagnostic(
        file_path="test.c",
        line_number=10,
        column_number=5,
        severity=DiagnosticSeverity.ERROR,
        raw_message="expected ';' before '}' token",
        title_es="Falta Punto y Coma",
        explanation_es="Falta cerrar la sentencia con ';'.",
        root_cause_es="Olvido de sintaxis.",
        suggestion_es="Agregá ';' al final de la línea.",
        code_snippet="int x = 42"
    )
    panel = format_diagnostic_panel(diag)
    assert panel is not None
