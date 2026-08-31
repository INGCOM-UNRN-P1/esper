---
title: "Manual de Referencia: esper"
subtitle: "Esper — Compilación Asistida con Citas Canónicas a la Norma ISO C (C11 / C23)"
author: "Cátedra de Algoritmos y Programación"
date: "2026-08-31"
---

(manual-esper)=
# Esper — Compilación Asistida con Citas Canónicas a la Norma ISO C (C11 / C23)

````{abstract}
**Rol en el ecosistema:** Diagnóstico de compilación que vincula cada advertencia o error con la cláusula exacta del estándar ISO/IEC 9899 (C11/C23) para fundamentación teórica de cátedra.
````

---

(manual-esper-proposito)=
## 1. Propósito y Filosofía Pedagógica

La herramienta **`esper`** forma parte del ecosistema oficial de software de la cátedra. Su diseño sigue principios pedagógicos rigurosos:

1. **Evidencia Técnica Directa**: Todo diagnóstico se fundamenta en la norma ISO C (C11/C23), en el modelo de memoria del sistema o en convenciones arquitectónicas formales.
2. **Acción Correctiva Concreta**: Cada advertencia incluye la prescripción técnica inmediata para resolver el defecto sin recurrir a conjeturas.
3. **Autonomía del Estudiante**: Facilita la autoevaluación local antes de la entrega final del trabajo práctico.
4. **Objetividad Docente**: Estandariza la corrección automática eliminando discrepancias subjetivas en la evaluación.

---

(manual-esper-instalacion)=
## 2. Instalación y Verificación del Entorno

````{important}
Para garantizar la reproducibilidad técnica de la cátedra, asegurate de instalar las dependencias nativas del sistema operativo antes de instalar el paquete Python.
````

### 2.1 Requisitos Previos del Sistema

Instalá los paquetes del sistema requeridos según tu distribución o entorno:

````{tab-set}
```{tab-item} Ubuntu / Debian
sudo apt update && sudo apt install -y \
    build-essential \
    gcc \
    gdb \
    valgrind \
    clang-format \
    libclang-dev \
    bubblewrap \
    typst \
    graphviz \
    python3-pip \
    python3-venv
```

```{tab-item} Arch Linux / Manjaro
sudo pacman -S --needed \
    base-devel \
    gcc \
    gdb \
    valgrind \
    clang \
    bubblewrap \
    typst \
    graphviz \
    python-pip \
    uv
```

```{tab-item} Fedora / RHEL
sudo dnf install -y \
    gcc \
    gcc-c++ \
    gdb \
    valgrind \
    clang-tools-extra \
    bubblewrap \
    typst \
    graphviz \
    python3-pip
```

```{tab-item} macOS (Homebrew)
brew install gcc gdb clang-format typst graphviz uv
```

```{tab-item} Windows (MSYS2 / WSL2)
# En WSL2 (Ubuntu): utilizar los paquetes de Ubuntu/Debian arriba.
# En MSYS2 MINGW64:
pacman -S --needed \
    mingw-w64-x86_64-gcc \
    mingw-w64-x86_64-gdb \
    mingw-w64-x86_64-clang-tools-extra
```
````

---

### 2.2 Métodos de Instalación de `esper`

Podés instalar `esper` mediante cualquiera de los siguientes métodos estándar:

````{tab-set}
```{tab-item} uv tool (Recomendado)
# Instalación aislada de alta velocidad con uv
uv tool install . --editable

# O instalar todo el ecosistema de herramientas de la cátedra en lote:
source ./install_tools.sh
```

```{tab-item} pip / venv
# Crear y activar un entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# Instalar en modo editable para desarrollo
pip install -e .
```

```{tab-item} pipx
# Instalación global aislada en tu PATH
pipx install --editable .
```
````

---

### 2.3 Autocompletado en la Shell

La interfaz CLI de `esper` cuenta con autocompletado nativo para comandos, flags y archivos. Para configurarlo permanentemente en tu shell:

````{code-block} bash
# Configuración automática en Bash / Zsh / Fish
esper --install-completion

# Para cargar el autocompletado en la sesión actual de inmediato:
source ./install_tools.sh
````

---

### 2.4 Verificación del Entorno con `doctor`

Toda herramienta del ecosistema cuenta con el subcomando unificado `doctor`. Ejecutalo para auditar el estado del entorno:

````{code-block} bash
esper doctor
````

#### Comprobaciones Ejecutadas por el Diagnóstico:
- **Compilador C**: Verifica disponibilidad de `gcc` o `clang` con soporte de estándares C11 y C23.
- **Depurador y Core Dumps**: Comprueba que `gdb` esté instalado y que `ulimit -c` permita generación de core dumps.
- **Herramientas de Memoria**: Valida la presencia de `valgrind` y librerías `libasan`/`libubsan`.
- **Formateo y Estilo**: Verifica el binario `clang-format` (versión 16+).
- **Sandboxing de Kernel**: Audita permisos no privilegiados de `bwrap` (Bubblewrap namespaces).
- **Generador de Tipografía y Documentos**: Comprueba `typst` ($\ge 0.11$) y `dot` (Graphviz).

#### Matriz de Resolución de Problemas:

| Síntoma / Alerta de `doctor` | Causa Raíz | Acción Correctiva |
| :--- | :--- | :--- |
| `❌ gcc / clang no encontrado` | Toolchain C faltante | Instalá `build-essential` o `base-devel`. |
| `❌ bwrap permisos insuficientes` | User namespaces desactivados | Habilitá `sysctl kernel.unprivileged_userns_clone=1`. |
| `❌ typst no disponible` | Motor de PDF faltante | Descargá Typst vía `cargo install typst-cli` o gestor de paquetes. |
| `❌ gdb no responde` | GDB sin interfaz MI/Python | Reinstalá `gdb` completo desde el repositorio oficial. |

(manual-esper-comandos)=
## 3. Referencia Completa de Comandos CLI

A continuación se detallan los subcomandos principales disponibles en `esper`:

| Sintaxis del Comando | Descripción y Efecto |
| :--- | :--- |
| `esper compile src/*.c -o ./bin/programa` | Compila y anota errores con referencias a la norma ISO C. |
| `esper cite <codigo_error>` | Busca y muestra el texto normativo oficial de una regla de C. |
| `esper check --flags "<cflags>" src/` | Audita la compatibilidad de flags con el estándar fijado. |
| `esper doctor` | Verifica versiones de GCC, Clang y catálogos normativos. |

````{tip}
Podés agregar el flag `--json` a la mayoría de los comandos para exportar resultados en formato estructurado o `--md` para generar reportes Markdown para el informe de entrega.
````

---

(manual-esper-tutorial)=
## 4. Tutorial Paso a Paso con Ejemplos Reales

### Caso de Estudio

Considerá el siguiente fragmento de código representativo:

````{code-block} c
:linenos:
#include <stdio.h>

void f(void) {
    int arr[5];
    int *p = &arr[5]; // Válido en C11 (§6.5.6 p8: one past the end)
    int valor = *p;   // Comportamiento indefinido en C11 (§6.5.6 p8: desreferencia inválida)
}
````

### Ejecución de la Herramienta

Ejecutá el análisis desde tu terminal:

````{code-block} bash
esper compile src/*.c -o ./bin/programa
````

### Salida Obtenida en Consola

````{code-block} text
[!] ERROR NORMATIVO en f.c:6:17:
    Desreferenciación del elemento 'one-past-the-end' de un arreglo.

📜 CITA NORMATIVA ISO/IEC 9899:2011 (C11) §6.5.6 p8:
    "If the pointer operand and the result point to elements of the same array object,
    or one past the last element of the array object, the evaluation shall not produce
    an overflow; otherwise, the behavior is undefined. If the result points one past
    the last element of the array object, it shall not be used as the operand of a
    unary '*' operator that is evaluated." 
````

````{note}
Prestá atención a la explicación pedagógica generada: la herramienta no solo señala la línea del problema, sino que explica la causa raíz y el impacto en memoria o arquitectura.
````

---

(manual-esper-ejercicios)=
## 5. Ejercicios Prácticos y Desafíos

Practicá el uso avanzado de **`esper`** resolviendo los siguientes ejercicios:

````{exercise} Desafío 1: Compilación con Citas Normativas
Compilar un módulo con violaciones de punteros y analizar las cláusulas ISO citadas.

**Instrucción de ejecución:**
```bash
esper compile src/punteros.c -o bin/ptr_test
```
````

````{solution} Desafío 1
```bash
esper compile src/punteros.c -o bin/ptr_test
# Verificá que la operación concluya exitosamente con código de salida 0.
```
````

````{exercise} Desafío 2: Consulta de Cláusula de Comportamiento Indefinido
Consultar la especificación ISO C sobre modificación de variables entre puntos de secuencia.

**Instrucción de ejecución:**
```bash
esper cite "sequence-point-violation"
```
````

````{solution} Desafío 2
```bash
esper cite "sequence-point-violation"
# Revisá el archivo generado o el informe en terminal para confirmar la resolución del problema.
```
````

````{exercise} Desafío 3: Auditoría de Compatibilidad C11 vs C23
Verificar qué construcciones de tu código cambiarán en la nueva norma ISO C23.

**Instrucción de ejecución:**
```bash
esper check --std c23 src/
```
````

````{solution} Desafío 3
```bash
esper check --std c23 src/
# Comprobá que la salida confirme la ausencia de advertencias o errores pendientes.
```
````

---

(manual-esper-makefile)=
## 6. Integración en el Flujo de Trabajo y Makefile

Para incorporar `esper` de forma automática a tu flujo de desarrollo, agregá la siguiente regla en el `Makefile` de tu proyecto:

````{code-block} makefile
check-esper:
	@echo "=== Ejecutando verificación con esper ==="
	esper check src/ include/

.PHONY: check-esper
````

Ejecutá `make check-esper` antes de cada commit para asegurar que tu código conserve el estado de aprobación.

---

(manual-esper-arquitectura)=
## 7. Arquitectura Interna y Mecanismo Técnico

La herramienta **`esper`** implementa un motor de alta precisión basado en:

- **Tecnología Núcleo:** `ISO/IEC 9899:2011/2024 Corpus Matcher + Clang Diagnostic Consumer + Rich Renderer`.
- **Aislamiento y Determinismo:** Diseñada para operar sin efectos colaterales en entornos de integración continua (CI), terminales de estudiantes y servidores docentes headless.
- **Manejo de Errores Pedagógico:** Todo fallo de sintaxis, memoria o lógica se traduce en una acción prescriptiva concreta con su respectiva justificación técnica.

---

(manual-esper-ecosistema)=
## 8. Integración y Conexión con el Ecosistema

````{note}
Ninguna herramienta opera de forma aislada. **`esper`** forma parte del pipeline integral de evaluación, verificación y enseñanza de la cátedra.
````

### Diagrama de Flujo e Interoperabilidad

````{mermaid}
graph TD
    GCC[GCC / Clang Warnings] --> ESP[Esper: Explicador Normativo]
    ESP -->|Búsqueda de Cláusula| ISO[Corpus ISO C11 / C23]
    ESP -->|Cita Canónica Didáctica| DAE[Daedalus: Compilador Asistido]
    ESP -->|Fundamentación Teórica| RIP[Ripley: Linter de Cátedra]
````

### Matriz de Intercambio de Datos

| Canal | Herramientas Conectadas | Tipo de Datos Transferidos |
| :--- | :--- | :--- |
| **Entradas (Inputs)** | - `Salidas de error y advertencia de GCC/Clang` | Código fuente, AST, binarios, testcases, contratos |
| **Salidas (Outputs)** | - `daedalus (citas normativas)`
- `spunkmeyer (fundamento de antipatrones)` | Informes Markdown, diagnósticos Rich, JSON, actas |
| **Sincronización** | `daedalus`, `ripley`, `spunkmeyer` | Validación cruzada, flags compartidos y autofix |

### Pipeline de Integración Recomendado

Podés encadenar `esper` con otras herramientas del ecosistema en una única línea de comando:

````{code-block} bash
# Pipeline de integración típico
daedalus compile src/main.c 2>&1 | esper explain
````

---

(manual-esper-seccion-plugins)=
## 9. Extensión, Desarrollo de Plugins y API Python

Para crear tus propias reglas, conectores de evaluación o integrar `esper` programáticamente en pipelines de CI/CD:

- 👉 **Consultá la guía completa:** [Guía de Extensión y Creación de Plugins](plugins.md)

