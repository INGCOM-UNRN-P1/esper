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
## 2. Instalación y Diagnóstico del Entorno

````{important}
Asegurate de contar con el compilador GCC/Clang y las librerías del sistema instaladas antes de ejecutar `esper`.
````

Para comprobar el estado de salud de tu entorno de trabajo y las dependencias auxiliares:

````{code-block} bash
# Comprobación de dependencias del sistema
esper doctor
````

Si se detecta la falta de alguna utilidad (como `gdb`, `valgrind`, `clang-format` o `typst`), el comando indicará el paquete exacto a instalar según tu distribución GNU/Linux o entorno MSYS2.

---

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
