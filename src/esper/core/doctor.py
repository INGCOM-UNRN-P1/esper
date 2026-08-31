"""Diagnóstico desacoplado del entorno y dependencias para ESPER."""

from __future__ import annotations
import shutil
import subprocess
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class DependencyCheck(BaseModel):
    name: str
    category: str
    required: bool
    status: str
    version: str = ""
    detail: str = ""


class DoctorReport(BaseModel):
    all_ok: bool
    checks: List[DependencyCheck] = Field(default_factory=list)
    system_summary: Dict[str, Any] = Field(default_factory=dict)


def ejecutar_diagnostico_doctor() -> DoctorReport:
    """Ejecuta una auditoría completa de los binarios y dependencias requeridas por ESPER."""
    checks: List[DependencyCheck] = []
    all_ok = True

    # 1. GCC
    gcc_path = shutil.which("gcc")
    if gcc_path:
        try:
            res = subprocess.run(["gcc", "--version"], capture_output=True, text=True, check=False)
            ver = res.stdout.splitlines()[0] if res.stdout else "Detectado"
            checks.append(DependencyCheck(
                name="gcc",
                category="Compilador",
                required=True,
                status="OK",
                version=ver,
                detail=f"Ubicación: {gcc_path}"
            ))
        except Exception as e:
            checks.append(DependencyCheck(
                name="gcc",
                category="Compilador",
                required=True,
                status="ERROR",
                detail=f"Falla al ejecutar: {e}"
            ))
            all_ok = False
    else:
        checks.append(DependencyCheck(
            name="gcc",
            category="Compilador",
            required=True,
            status="FALTA",
            detail="GCC no se encuentra en el PATH del sistema."
        ))
        all_ok = False

    # 2. Clang (Opcional)
    clang_path = shutil.which("clang")
    if clang_path:
        try:
            res = subprocess.run(["clang", "--version"], capture_output=True, text=True, check=False)
            ver = res.stdout.splitlines()[0] if res.stdout else "Detectado"
            checks.append(DependencyCheck(
                name="clang",
                category="Compilador Alternativo",
                required=False,
                status="OK",
                version=ver,
                detail=f"Ubicación: {clang_path}"
            ))
        except Exception:
            checks.append(DependencyCheck(
                name="clang",
                category="Compilador Alternativo",
                required=False,
                status="WARNING",
                detail="Presente pero no responde a --version."
            ))
    else:
        checks.append(DependencyCheck(
            name="clang",
            category="Compilador Alternativo",
            required=False,
            status="INFO",
            detail="Clang no instalado (opcional)."
        ))

    # 3. Make / mingw32-make
    make_bin = shutil.which("make") or shutil.which("mingw32-make")
    if make_bin:
        checks.append(DependencyCheck(
            name="make",
            category="Automatizador de Build",
            required=False,
            status="OK",
            detail=f"Ubicación: {make_bin}"
        ))
    else:
        checks.append(DependencyCheck(
            name="make",
            category="Automatizador de Build",
            required=False,
            status="INFO",
            detail="Make no encontrado en PATH."
        ))

    return DoctorReport(
        all_ok=all_ok,
        checks=checks,
        system_summary={
            "herramienta": "esper",
            "modo": "diagnostico_doctor"
        }
    )
