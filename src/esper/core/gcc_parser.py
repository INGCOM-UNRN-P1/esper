"""Parser de diagnósticos de GCC/Clang y ejecutor de compilación con explicaciones."""

import re
import subprocess
from pathlib import Path
from typing import List, Optional
from esper.core.models import GccDiagnostic, DiagnosticSeverity, CompilationReport
from esper.core.diagnostic_catalog import lookup_explanation

# Patrón para líneas de diagnóstico GCC:
# archivo.c:linea:columna: severity: mensaje [-Wflag]
GCC_LINE_PATTERN = re.compile(
    r'^([^:\n]+):(\d+):(?:(\d+):)?\s*(error|warning|note|fatal error):\s*(.*?)(?:\s*\[(-W[a-zA-Z0-9_-]+)\])?$',
    re.MULTILINE
)


def parse_gcc_output(raw_stderr: str) -> List[GccDiagnostic]:
    """Parsea el texto de stderr emitido por GCC/Clang."""
    diagnostics: List[GccDiagnostic] = []

    for match in GCC_LINE_PATTERN.finditer(raw_stderr):
        file_path = match.group(1).strip()
        line_no = int(match.group(2))
        col_no = int(match.group(3)) if match.group(3) else None
        sev_str = match.group(4).strip().lower()
        msg = match.group(5).strip()
        flag = match.group(6).strip() if match.group(6) else None

        severity_map = {
            "error": DiagnosticSeverity.ERROR,
            "warning": DiagnosticSeverity.WARNING,
            "note": DiagnosticSeverity.NOTE,
            "fatal error": DiagnosticSeverity.FATAL_ERROR,
        }
        severity = severity_map.get(sev_str, DiagnosticSeverity.ERROR)

        title, explanation, root_cause, suggestion = lookup_explanation(msg)

        # Intentar leer snippet del archivo si existe
        snippet = None
        p = Path(file_path)
        if p.exists() and p.is_file():
            try:
                lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
                if 1 <= line_no <= len(lines):
                    snippet = lines[line_no - 1].strip()
            except Exception:
                pass

        diagnostics.append(GccDiagnostic(
            file_path=file_path,
            line_number=line_no,
            column_number=col_no,
            severity=severity,
            raw_message=msg,
            flag=flag,
            title_es=title,
            explanation_es=explanation,
            root_cause_es=root_cause,
            suggestion_es=suggestion,
            code_snippet=snippet
        ))

    # Linker errors: "undefined reference to `foo'"
    for line in raw_stderr.splitlines():
        if "undefined reference to" in line and not any("undefined reference to" in d.raw_message for d in diagnostics):
            parts = line.split(":")
            f_path = parts[0].strip() if len(parts) > 1 else "ld"
            msg = parts[-1].strip() if len(parts) > 1 else line
            title, explanation, root_cause, suggestion = lookup_explanation("undefined reference to")
            diagnostics.append(GccDiagnostic(
                file_path=f_path,
                line_number=1,
                severity=DiagnosticSeverity.ERROR,
                raw_message=msg,
                title_es=title,
                explanation_es=explanation,
                root_cause_es=root_cause,
                suggestion_es=suggestion
            ))

    return diagnostics


def run_gcc_and_explain(command_args: List[str]) -> CompilationReport:
    """Ejecuta una compilación con GCC y traduce los errores producidos."""
    cmd = ["gcc"] + command_args if not command_args[0].startswith("gcc") else command_args

    res = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=False
    )

    raw_err = res.stderr
    diagnostics = parse_gcc_output(raw_err)
    has_errors = any(d.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL_ERROR) for d in diagnostics)
    passed = (res.returncode == 0 and not has_errors)

    return CompilationReport(
        command=cmd,
        exit_code=res.returncode,
        passed=passed,
        diagnostics=diagnostics,
        raw_stderr=raw_err
    )
