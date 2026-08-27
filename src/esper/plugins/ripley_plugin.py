"""Plugin de ESPER para el microkernel RIPLEY."""

from pathlib import Path
from typing import Dict, Any
from esper.core.gcc_parser import run_gcc_and_explain


class EsperPlugin:
    """Plugin de explicación de diagnósticos GCC para Ripley."""

    name = "gcc_explainer"
    description = "Explicador pedagógico interactivo de salidas, errores y warnings de GCC/Clang"

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        source_dir = Path(context.get("source_dir", "."))
        main_c = source_dir / "main.c"

        if not main_c.exists():
            return {"passed": True, "diagnostics_count": 0}

        report = run_gcc_and_explain(["-Wall", "-Wextra", str(main_c), "-o", "/dev/null"])

        return {
            "passed": report.passed,
            "diagnostics_count": len(report.diagnostics),
            "diagnostics": [
                {
                    "severity": d.severity,
                    "title": d.title_es,
                    "location": f"{d.file_path}:{d.line_number}",
                    "explanation": d.explanation_es,
                    "suggestion": d.suggestion_es
                }
                for d in report.diagnostics
            ]
        }
