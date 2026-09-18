"""Plugin de ESPER para el microkernel RIPLEY."""

from pathlib import Path
from typing import Dict, Any, List
from esper.core.gcc_parser import run_gcc_and_explain

# Perfil de cátedra: el mismo estándar y advertencias que usa daedalus, sin los
# -Werror ni -g/-O0 que solo tienen sentido al compilar el ejecutable final.
FLAGS_CATEDRA = ["-std=c11", "-Wall", "-Wextra", "-pedantic", "-Wconversion"]

_SEVERIDADES = {"error": "ERROR", "fatal error": "ERROR", "warning": "ADVERTENCIA", "note": "INFO"}


def _archivos_c(workspace: Path, manifest_config: Dict[str, Any]) -> List[Path]:
    if manifest_config.get("c_files"):
        return [Path(f) for f in manifest_config["c_files"]]
    if workspace.is_file():
        return [workspace]
    return sorted(workspace.glob("*.c")) + sorted(workspace.glob("src/*.c"))


class EsperPlugin:
    """Plugin de explicación de diagnósticos GCC para Ripley."""

    name = "gcc_explainer"
    description = "Explicador pedagógico interactivo de salidas, errores y warnings de GCC/Clang"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        source_dir = Path(context.get("source_dir", "."))
        # Antes se compilaba solo `main.c` (y si no existía se daba por aprobado el
        # proyecto), ignorando el resto de los archivos y la configuración.
        archivos = _archivos_c(source_dir, context)
        flags = list(context.get("flags") or FLAGS_CATEDRA)

        observaciones = []
        aprobado = True
        for archivo in archivos:
            # `-fsyntax-only`: se necesitan los diagnósticos, no un ejecutable, y así un
            # módulo sin `main` no falla al enlazar.
            report = run_gcc_and_explain([*flags, "-fsyntax-only", str(archivo)])
            aprobado = aprobado and report.passed
            for d in report.diagnostics:
                severidad = getattr(d.severity, "value", str(d.severity)).lower()
                observaciones.append({
                    "codigo": d.flag or "gcc",
                    "severidad": _SEVERIDADES.get(severidad, "ADVERTENCIA"),
                    "archivo": d.file_path or str(archivo),
                    "linea": d.line_number or 0,
                    "titulo": d.title_es,
                    "mensaje": d.explanation_es,
                    "sugerencia": d.suggestion_es,
                })

        return {
            "passed": aprobado,
            "ok": aprobado,
            "diagnostics_count": len(observaciones),
            "observaciones": observaciones,
        }
