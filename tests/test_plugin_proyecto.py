"""Regresión de ESPER-D0902: el plugin compilaba solo `main.c` con -Wall -Wextra.

Sin `main.c` daba el proyecto por aprobado sin mirar nada, ignoraba el resto de los
archivos y la configuración del manifiesto, y no usaba el perfil de cátedra.
"""

import shutil

import pytest

from esper.plugins.ripley_plugin import FLAGS_CATEDRA, EsperPlugin

necesita_gcc = pytest.mark.skipif(not shutil.which("gcc"), reason="requiere gcc")

CON_ADVERTENCIA = "#include <stdio.h>\nint f(void) { int sin_usar = 0; return 1; }\n"
LIMPIO = "int g(int a) { return a + 1; }\n"


@necesita_gcc
def test_se_analizan_todos_los_archivos_y_no_solo_main_c(tmp_path):
    (tmp_path / "lista.c").write_text(CON_ADVERTENCIA, encoding="utf-8")
    res = EsperPlugin().run({"source_dir": str(tmp_path)})
    assert res["diagnostics_count"] >= 1
    assert any(o["archivo"].endswith("lista.c") for o in res["observaciones"])


@necesita_gcc
def test_un_modulo_sin_main_no_falla_al_enlazar(tmp_path):
    (tmp_path / "util.c").write_text(LIMPIO, encoding="utf-8")
    res = EsperPlugin().run({"source_dir": str(tmp_path)})
    assert res["passed"] is True and res["observaciones"] == []


@necesita_gcc
def test_las_observaciones_llevan_ubicacion_y_severidad_de_ripley(tmp_path):
    (tmp_path / "a.c").write_text(CON_ADVERTENCIA, encoding="utf-8")
    obs = EsperPlugin().run({"source_dir": str(tmp_path)})["observaciones"]
    aviso = next(o for o in obs if o["severidad"] == "ADVERTENCIA")
    assert aviso["linea"] == 2 and aviso["archivo"].endswith("a.c")
    assert aviso["mensaje"] and aviso["sugerencia"]


@necesita_gcc
def test_un_error_de_compilacion_reprueba(tmp_path):
    (tmp_path / "roto.c").write_text("int f(void) { return ; ; x }\n", encoding="utf-8")
    res = EsperPlugin().run({"source_dir": str(tmp_path)})
    assert res["passed"] is False
    assert any(o["severidad"] == "ERROR" for o in res["observaciones"])


@necesita_gcc
def test_el_manifiesto_puede_elegir_archivos_y_flags(tmp_path):
    (tmp_path / "a.c").write_text(CON_ADVERTENCIA, encoding="utf-8")
    (tmp_path / "b.c").write_text(LIMPIO, encoding="utf-8")
    res = EsperPlugin().run({"source_dir": str(tmp_path), "c_files": [str(tmp_path / "b.c")]})
    assert res["observaciones"] == []


def test_el_perfil_por_defecto_es_el_de_catedra():
    assert "-std=c11" in FLAGS_CATEDRA and "-pedantic" in FLAGS_CATEDRA


def test_un_proyecto_sin_archivos_c_no_se_da_por_analizado_con_diagnosticos(tmp_path):
    res = EsperPlugin().run({"source_dir": str(tmp_path)})
    assert res["diagnostics_count"] == 0 and res["passed"] is True
