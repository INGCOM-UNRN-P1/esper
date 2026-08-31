"""Modelos de datos para el diagnóstico y explicación de errores de GCC en ESPER."""

from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class DiagnosticSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"
    FATAL_ERROR = "fatal error"


class GccDiagnostic(BaseModel):
    file_path: str
    line_number: int
    column_number: Optional[int] = None
    severity: DiagnosticSeverity
    raw_message: str
    flag: Optional[str] = None  # ej: "-Wimplicit-function-declaration", "-Wformat"
    title_es: str
    explanation_es: str
    root_cause_es: str
    suggestion_es: str
    code_snippet: Optional[str] = None
    iso_c_citation: Optional[str] = None
    suggested_flags: List[str] = Field(default_factory=list)
    is_suppressed: bool = False


class CompilationReport(BaseModel):
    command: List[str] = Field(default_factory=list)
    exit_code: int = 0
    passed: bool = True
    diagnostics: List[GccDiagnostic] = Field(default_factory=list)
    raw_stderr: str = ""
    suppressed_count: int = 0
