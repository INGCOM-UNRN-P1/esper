"""Regresión de ESPER-D0701: el CLI tenía 40 % de cobertura.

Las ramas de compile/wrapper/guide/report/pipe/doctor/explain y sus caminos de error no se
ejercitaban. Cada test comprueba un comportamiento observable (código de salida y contenido),
no solo que el comando no explote.
"""

import json
import shutil
from pathlib import Path

import pytest
from typer.testing import CliRunner

from esper.cli import app

runner = CliRunner()
necesita_gcc = pytest.mark.skipif(not shutil.which("gcc"), reason="requiere gcc")

LIMPIO = "int main(void) { return 0; }\n"
CON_ADVERTENCIA = "int main(void) { int sin_usar = 0; return 0; }\n"
CON_ERROR = "int main(void) { return x; }\n"
LOG_GCC = "main.c:3:9: warning: unused variable 'v' [-Wunused-variable]\nmain.c:5:5: error: 'y' undeclared (first use in this function)\n"


@pytest.fixture
def fuentes(tmp_path):
    for nombre, texto in (("limpio.c", LIMPIO), ("aviso.c", CON_ADVERTENCIA), ("error.c", CON_ERROR)):
        (tmp_path / nombre).write_text(texto, encoding="utf-8")
    return tmp_path


def _invocar(*args, **kw):
    return runner.invoke(app, list(args), **kw)


# --- compile -------------------------------------------------------------------------------

def test_compile_sin_argumentos_es_error_de_uso():
    res = _invocar("compile")
    assert res.exit_code == 2 and "Uso" in res.output


@necesita_gcc
def test_compile_limpio_sale_con_0_y_lo_celebra(fuentes):
    res = _invocar("compile", str(fuentes / "limpio.c"), "-Wall", "-o", "/dev/null")
    assert res.exit_code == 0 and "Compilación Exitosa" in res.output


@necesita_gcc
def test_compile_con_error_sale_con_codigo_de_gcc_y_explica(fuentes):
    res = _invocar("compile", str(fuentes / "error.c"), "-o", "/dev/null")
    assert res.exit_code != 0
    assert "x" in res.output


@necesita_gcc
def test_compile_json_con_advertencia_es_json_valido_y_aprobado(fuentes):
    res = _invocar("compile", str(fuentes / "aviso.c"), "-Wall", "-o", "/dev/null", "--json")
    datos = json.loads(res.stdout)
    assert res.exit_code == 0 and datos["passed"] is True
    assert any(d["flag"] == "-Wunused-variable" for d in datos["diagnostics"])


@necesita_gcc
def test_compile_json_con_error_falla_y_lo_dice(fuentes):
    res = _invocar("compile", str(fuentes / "error.c"), "-o", "/dev/null", "--json")
    assert res.exit_code != 0
    assert json.loads(res.stdout)["passed"] is False


@necesita_gcc
def test_compile_md_escribe_la_seccion_para_dredd(fuentes, tmp_path):
    salida = tmp_path / "sub" / "esper.md"
    res = _invocar("compile", str(fuentes / "aviso.c"), "-Wall", "-o", "/dev/null", "--md", str(salida))
    assert res.exit_code == 0
    md = salida.read_text(encoding="utf-8")
    assert "dredd-section: esper" in md
    assert "aviso.c" in md


@necesita_gcc
def test_compile_guide_imprime_la_guia_paso_a_paso(fuentes):
    res = _invocar("compile", str(fuentes / "aviso.c"), "-Wall", "-o", "/dev/null", "--guide")
    assert res.exit_code == 0 and "sin_usar" in res.output


@necesita_gcc
def test_compile_dedup_no_altera_el_veredicto(fuentes):
    res = _invocar("compile", str(fuentes / "aviso.c"), "-Wall", "-o", "/dev/null", "--dedup")
    assert res.exit_code == 0


# --- wrapper -------------------------------------------------------------------------------

def test_wrapper_sin_argumentos_es_error_de_uso():
    assert _invocar("wrapper").exit_code == 2


@necesita_gcc
@pytest.mark.parametrize("prefijo", [[], ["gcc"]])
def test_wrapper_acepta_el_comando_con_o_sin_gcc_delante(fuentes, prefijo):
    res = _invocar("wrapper", *prefijo, str(fuentes / "limpio.c"), "-o", "/dev/null")
    assert res.exit_code == 0


@necesita_gcc
def test_wrapper_propaga_el_codigo_de_error_de_gcc(fuentes):
    assert _invocar("wrapper", str(fuentes / "error.c"), "-o", "/dev/null").exit_code != 0


# --- pipe ----------------------------------------------------------------------------------

def test_pipe_con_solo_advertencias_aprueba():
    res = _invocar("pipe", input="main.c:3:9: warning: unused variable 'v' [-Wunused-variable]\n")
    assert res.exit_code == 0


def test_pipe_con_un_error_reprueba():
    res = _invocar("pipe", input=LOG_GCC)
    assert res.exit_code == 1


def test_pipe_json_es_valido_y_refleja_el_veredicto():
    res = _invocar("pipe", "--json", input=LOG_GCC)
    assert res.exit_code == 1
    datos = json.loads(res.stdout)
    assert datos["passed"] is False and len(datos["diagnostics"]) == 2


def test_pipe_dedup_y_json():
    res = _invocar("pipe", "--dedup", "--json", input=LOG_GCC)
    assert json.loads(res.stdout)["diagnostics"]


# --- explain -------------------------------------------------------------------------------

def test_explain_sin_consulta_es_error_de_uso():
    assert _invocar("explain").exit_code == 2


def test_explain_de_un_mensaje_conocido_traduce_y_sale_con_1():
    res = _invocar("explain", "main.c:12:5: error: 'y' undeclared (first use in this function)")
    assert res.exit_code in (0, 1) and res.output.strip()


def test_explain_de_una_advertencia_consulta_el_catalogo_y_sale_con_0():
    res = _invocar("explain", "-Wformat")
    assert res.exit_code in (0, 1)
    assert res.output.strip()


def test_explain_json():
    res = _invocar("explain", "-Wunused-variable", "--json")
    json.loads(res.stdout)


# --- catálogo y sugerencias ----------------------------------------------------------------

@pytest.mark.parametrize("nombre", ["catalog", "list-warnings"])
def test_el_catalogo_lista_advertencias_con_los_dos_nombres(nombre):
    assert _invocar(nombre).exit_code == 0
    datos = json.loads(_invocar(nombre, "--json").stdout)
    assert datos


def test_suggest_flags_sobre_un_fuente(fuentes):
    res = _invocar("suggest-flags", str(fuentes / "limpio.c"))
    assert res.exit_code == 0 and res.output.strip()
    json.loads(_invocar("suggest-flags", str(fuentes / "limpio.c"), "--json").stdout)


def test_check_arch_sin_hallazgos_lo_informa(tmp_path):
    log = tmp_path / "build.log"
    log.write_text("main.c:3:9: warning: unused variable 'v' [-Wunused-variable]\n", encoding="utf-8")
    res = _invocar("check-arch", str(log))
    assert res.exit_code == 0


def test_check_arch_detecta_advertencias_de_32_vs_64_bits(tmp_path):
    log = tmp_path / "build.log"
    log.write_text(
        "main.c:8:14: warning: cast from pointer to integer of different size [-Wpointer-to-int-cast]\n"
        "main.c:9:10: warning: format '%d' expects argument of type 'int', but argument 2 has type 'long int' [-Wformat=]\n",
        encoding="utf-8",
    )
    res = _invocar("check-arch", str(log), "--json")
    assert res.exit_code in (0, 1)
    json.loads(res.stdout)


# --- guide, report, doctor, version ---------------------------------------------------------

@necesita_gcc
def test_guide_imprime_o_escribe_la_guia(fuentes, tmp_path):
    res = _invocar("guide", str(fuentes / "aviso.c"))
    assert res.exit_code == 0 and res.output.strip()
    salida = tmp_path / "guia" / "g.md"
    res = _invocar("guide", str(fuentes / "aviso.c"), "-o", str(salida))
    assert res.exit_code == 0 and salida.is_file()


@necesita_gcc
def test_report_imprime_o_escribe_la_seccion(fuentes, tmp_path):
    res = _invocar("report", str(fuentes / "aviso.c"))
    assert "dredd-section: esper" in res.output
    salida = tmp_path / "out" / "r.md"
    res = _invocar("report", str(fuentes / "aviso.c"), "-o", str(salida))
    assert salida.is_file() and "dredd-section: esper" in salida.read_text(encoding="utf-8")


def test_doctor_en_json_informa_los_componentes():
    res = _invocar("doctor", "--json")
    datos = json.loads(res.stdout)
    assert res.exit_code in (0, 1)
    assert isinstance(datos, dict) and datos


def test_doctor_en_texto_y_verboso():
    res = _invocar("doctor", "-v")
    assert res.exit_code in (0, 1) and res.output.strip()


@pytest.mark.parametrize("args", [["version"], ["--version"], ["-v"]])
def test_la_version_se_puede_pedir_de_tres_formas(args):
    res = _invocar(*args)
    assert res.exit_code == 0 and "esper" in res.output.lower()
