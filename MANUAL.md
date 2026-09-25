# Manual de Uso y Referencia Técnica: esper

> **ESPER** — Explicador pedagógico y formateador interactivo de salidas y errores de GCC/Clang
> **Versión:** `0.1.0` · **CLI principal:** `esper` · **Plugin Ripley:** `gcc_explainer`

---

## 1. Arquitectura y Propósito Pedagógico

`esper` forma parte del ecosistema de herramientas de la cátedra de Programación 1 (UNRN). Su objetivo central es resolver de forma modular, determinista y automatizada las tareas asociadas a su dominio específico dentro del ciclo de desarrollo, evaluación y aprendizaje de software en C.

### Alcance Funcional (Qué cubre)
- Base de conocimiento pedagógica referenciada formalmente a la norma ISO/IEC 9899 (estándares C11 y C23).
- Interceptor y wrapper para invocaciones de compilación (`make`, `gcc`), deduplicando cascadas masivas de advertencias.
- Sugerencia automática de flags de biblioteca requeridas (`-lm`, `-pthread`, `-lrt`).
- Explicación didáctica contextualizada de conceptos de C subyacentes a errores de compilación frecuentes.

### Límites de Responsabilidad y Delegación (Qué no cubre)
- Invocación primaria y gestión de políticas de compilación (delegado a `daedalus`).
- Formateo y estilo de código (delegado a `gaff`).
- Comprobación de tipos de datos abstractos (delegado a `motoko`).

### Principios de Diseño
- **Enfoque Pedagógico:** Diagnósticos y mensajes en español rioplatense orientados a facilitar la comprensión de errores conceptuales.
- **Salida Estructurada Dual:** Soporte nativo para visualización enriquecida en terminal (Rich) y salida parseable para orquestadores (`--json`).
- **Integración Contractual:** Capacidad de emitir secciones de reporte para `dredd` (`dredd-section`) y actuar como satélite orquestado por `ripley`.
- **Idempotencia y Robustez:** Validación de precondiciones y comandos de autodiagnóstico (`doctor`) para verificación del entorno.

---

## 2. Instalación y Requisitos

### Requisitos del Sistema
- **Python:** `>= 3.10` (recomendado Python 3.11 o 3.12).
- **Gestor de paquetes:** [`uv`](https://github.com/astral-sh/uv) (entorno estándar de cátedra).
- **Toolchain C (si aplica):** GCC / Clang, Make, GDB y bibliotecas estándar de desarrollo.

### Instalación en el Entorno de Usuario
Para instalar la herramienta de forma global y aislada en el sistema mediante `uv tool`:
```bash
uv tool install --editable /home/mrtin/dev/tools/esper
```

### Verificación de Instalación
Ejecutá el comando `doctor` para constatar que todas las dependencias y binarios requeridos estén presentes y operativos:
```bash
esper doctor
```

---

## 3. Guía Integral de Comandos (CLI)

| Comando | Descripción Breve |
| :--- | :--- |
| [`esper compile`](#compile) | Envuelve la ejecución de GCC y traduce todos los errores y advertencias. |
| [`esper wrapper`](#wrapper) | Modo Wrapper transparente para Makefiles: ejecuta el comando interceptando errores. |
| [`esper explain`](#explain) | Explica un mensaje de error puntual o consulta teórica de cualquier advertencia de GCC. |
| [`esper list-warnings`](#listwarnings) | Lista todas las advertencias y reglas pedagógicas documentadas en el catálogo de ESPER. |
| [`esper catalog`](#catalog) | Lista todas las advertencias y reglas pedagógicas documentadas en el catálogo de ESPER. |
| [`esper suggest-flags`](#suggestflags) | Analiza un archivo o error y sugiere flags de compilación/enlazado faltantes. |
| [`esper check-arch`](#checkarch) | Audita advertencias relacionadas con incompatibilidades de tamaño en 32 vs 64 bits. |
| [`esper guide`](#guide) | Genera una guía de resolución paso a paso en Markdown para el archivo C indicado. |
| [`esper pipe`](#pipe) | Lee mensajes de GCC desde stdin (tubería: `gcc ... 2>&1 | esper pipe`). |
| [`esper doctor`](#doctor) | Audita el entorno y verifica la disponibilidad de compiladores y dependencias. |
| [`esper report`](#report) | Genera directamente la sección de reporte Markdown de ESPER para Dredd. |
| [`esper version`](#version) | Muestra la versión de ESPER. |

### `esper compile`

Envuelve la ejecución de GCC y traduce todos los errores y advertencias.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--ctx` | `typer.Context` | `None` | - |
| `--dedup` | `bool` | `False` | Suprimir advertencias repetitivas o en cascada. |
| `--json` | `bool` | `False` | Emitir salida en formato JSON estructurado |
| `--md`, `--output-md` | `Optional[Path]` | `None` | Generar sección de reporte en formato Markdown para fusión en Dredd. |
| `--guide` | `bool` | `False` | Generar guía detallada paso a paso en Markdown. |

#### Ejemplo de Invocación
```bash
esper compile
```

### `esper wrapper`

Modo Wrapper transparente para Makefiles: ejecuta el comando interceptando errores.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--ctx` | `typer.Context` | `None` | - |

#### Ejemplo de Invocación
```bash
esper wrapper
```

### `esper explain`

Explica un mensaje de error puntual o consulta teórica de cualquier advertencia de GCC.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--ctx` | `typer.Context` | `None` | - |
| `--query` | `Optional[str]` | `None` | Mensaje de error, texto de GCC o nombre de flag (ej: -Wunused-variable) |
| `--json` | `bool` | `False` | Emitir salida en formato JSON estructurado |
| `--guide` | `bool` | `False` | Generar guía paso a paso en Markdown. |

#### Ejemplo de Invocación
```bash
esper explain
```

### `esper list-warnings`

Lista todas las advertencias y reglas pedagógicas documentadas en el catálogo de ESPER.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir salida en formato JSON. |

#### Ejemplo de Invocación
```bash
esper list-warnings
```

### `esper catalog`

Lista todas las advertencias y reglas pedagógicas documentadas en el catálogo de ESPER.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir salida en formato JSON. |

#### Ejemplo de Invocación
```bash
esper catalog
```

### `esper suggest-flags`

Analiza un archivo o error y sugiere flags de compilación/enlazado faltantes.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `fuente` | `Path` | Archivo fuente C o log de compilación. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir salida en formato JSON. |

#### Ejemplo de Invocación
```bash
esper suggest-flags <fuente>
```

### `esper check-arch`

Audita advertencias relacionadas con incompatibilidades de tamaño en 32 vs 64 bits.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `log_file` | `Path` | Archivo con la salida de compilador a auditar. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir salida en formato JSON. |

#### Ejemplo de Invocación
```bash
esper check-arch <log_file>
```

### `esper guide`

Genera una guía de resolución paso a paso en Markdown para el archivo C indicado.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `fuente` | `Path` | Archivo C a compilar y generar guía. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--output`, `-o` | `Optional[Path]` | `None` | Guardar la guía en un archivo Markdown. |

#### Ejemplo de Invocación
```bash
esper guide <fuente>
```

### `esper pipe`

Lee mensajes de GCC desde stdin (tubería: `gcc ... 2>&1 | esper pipe`).

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--dedup` | `bool` | `False` | Suprimir advertencias repetitivas o en cascada. |
| `--json` | `bool` | `False` | Emitir salida en formato JSON estructurado |

#### Ejemplo de Invocación
```bash
esper pipe
```

### `esper doctor`

Audita el entorno y verifica la disponibilidad de compiladores y dependencias.

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--json` | `bool` | `False` | Emitir diagnóstico en formato JSON. |
| `-v`, `--verbose` | `bool` | `False` | Mostrar detalle completo. |

#### Ejemplo de Invocación
```bash
esper doctor
```

### `esper report`

Genera directamente la sección de reporte Markdown de ESPER para Dredd.

#### Argumentos
| Argumento | Tipo | Descripción |
| :--- | :--- | :--- |
| `fuente` | `Path` | Archivo C a compilar y explicar. |

#### Opciones y Banderas
| Opción / Banderas | Tipo | Por Defecto | Descripción |
| :--- | :--- | :--- | :--- |
| `--output`, `-o` | `Optional[Path]` | `None` | Ruta de destino del archivo Markdown. |

#### Ejemplo de Invocación
```bash
esper report <fuente>
```

### `esper version`

Muestra la versión de ESPER.

#### Ejemplo de Invocación
```bash
esper version
```

---

## 4. Formatos de Salida e Integración con el Ecosistema

### Modo Interactivo / Terminal (Rich)
Por defecto, la herramienta renderiza paneles, árboles y tablas estilizadas para facilitar la lectura del estudiante y docente en terminales modernas con soporte ANSI.

### Modo Estructurado JSON (`--json`)
Para integración con pipelines de CI/CD, scripts de automatización u orquestadores externos, la opción `--json` emite un documento JSON estricto por la salida estándar (`stdout`), dirigiendo cualquier mensaje de logging a `stderr`:
```bash
esper compile --json
```

### Integración con Dredd (`dredd-section`)
Cuando la herramienta genera reportes de evaluación para entregas de alumnos, produce una sección Markdown estandarizada conforme al contrato de integración de Dredd (v1.0.0):
```markdown
<!-- dredd-section: esper, tool=esper, version=0.1.0, status=ok -->
```
Este encabezado garantiza la agregación determinista de los hallazgos en la rúbrica docente.

### Integración con Ripley
`esper` está registrada en el catálogo de plugins satélites de Ripley (`SATELLITE_CATALOG`). Puede invocarse directamente a través del motor de evaluación de Ripley configurando el análisis en `ripley.toml`.

---

## 5. Diagnóstico y Códigos de Salida

### Códigos de Retorno (`exit code`)
| Código | Significado |
| :---: | :--- |
| `0` | Ejecución exitosa sin hallazgos críticos ni errores de sintaxis. |
| `1` | Hallazgos pedagógicos detectados, infracción de reglas o advertencias activas. |
| `2` | Error de sintaxis en argumentos CLI o archivo fuente no encontrado. |
| `>2` | Error no recuperable del sistema, fallo de memoria o excepción interna. |

### Diagnóstico del Entorno (`doctor`)
Ante comportamientos inesperados, verificá el estado operativo con:
```bash
esper doctor
```
Comprueba la presencia de las dependencias requeridas y la integridad de los componentes del paquete.