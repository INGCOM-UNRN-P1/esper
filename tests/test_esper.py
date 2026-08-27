"""Tests unitarios y de integración para ESPER."""

from pathlib import Path
from typer.testing import CliRunner
from esper.cli import app
from esper.core.gcc_parser import parse_gcc_output, run_gcc_and_explain
from esper.plugins.ripley_plugin import EsperPlugin

runner = CliRunner()


def test_parse_gcc_warning_format():
    raw = "main.c:12:5: warning: format ‘%d’ expects argument of type ‘int *’, but argument 2 has type ‘int’ [-Wformat=]"
    diags = parse_gcc_output(raw)
    assert len(diags) == 1
    d = diags[0]
    assert d.file_path == "main.c"
    assert d.line_number == 12
    assert "Incompatibilidad de Formato" in d.title_es
    assert "&" in d.suggestion_es


def test_parse_gcc_implicit_function():
    raw = "app.c:5:10: error: implicit declaration of function ‘printf’ [-Wimplicit-function-declaration]"
    diags = parse_gcc_output(raw)
    assert len(diags) == 1
    assert "Invocación de Función sin Declaración" in diags[0].title_es


def test_run_gcc_and_explain_success(tmp_path):
    c = tmp_path / "main.c"
    c.write_text("int main(void) { return 0; }")
    report = run_gcc_and_explain([str(c), "-o", str(tmp_path / "out")])
    assert report.passed is True
    assert len(report.diagnostics) == 0


def test_cli_explain():
    res = runner.invoke(app, ["explain", "main.c:10: warning: unused variable ‘x’ [-Wunused-variable]"])
    assert res.exit_code == 0
    assert "Variable Declarada sin Uso" in res.output


def test_cli_version():
    res = runner.invoke(app, ["version"])
    assert res.exit_code == 0
    assert "ESPER" in res.output


def test_ripley_plugin(tmp_path):
    c = tmp_path / "main.c"
    c.write_text("int main(void) { return 0; }")
    plugin = EsperPlugin()
    res = plugin.run({"source_dir": str(tmp_path)})
    assert res["passed"] is True
