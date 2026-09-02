# ESPER — Explicador Pedagógico y Formateador de Diagnósticos GCC/Clang

**ESPER** envuelve la invocación del compilador GCC/Clang e intercepta errores, advertencias (`-Wall -Wextra -pedantic`) y notas del linker, traduciéndolas en paneles interactivos con diagnósticos pedagógicos en español rioplatense, causas raíz típicas y acciones correctivas sugeridas.

---

## 🎯 Alcance

### Qué cubre
- Base de conocimiento pedagógica referenciada formalmente a la norma ISO/IEC 9899 (estándares C11 y C23).
- Interceptor y wrapper para invocaciones de compilación (`make`, `gcc`), deduplicando cascadas masivas de advertencias.
- Sugerencia automática de flags de biblioteca requeridas (`-lm`, `-pthread`, `-lrt`).
- Explicación didáctica contextualizada de conceptos de C subyacentes a errores de compilación frecuentes.

### Qué no cubre (Límites y Delegación)
- Invocación primaria y gestión de políticas de compilación (delegado a `daedalus`).
- Formateo y estilo de código (delegado a `gaff`).
- Comprobación de tipos de datos abstractos (delegado a `motoko`).

---

## 📋 Requisitos

### Requisitos de Sistema y Entorno
- Multiplataforma. Python >= 3.10.

### Dependencias Externas y Binarios
- Ninguno obligatorio.

### Integración en el Ecosistema
- CLI `esper`. Plugin registrado en `ripley.plugins` (`gcc_explainer`).

---

## 🚀 Uso Rápido

```bash
# Compilar archivo traduciendo advertencias y errores automáticamente
esper compile main.c -o app -Wall -Wextra

# Explicar un mensaje de error puntual copiado de la terminal
esper explain "main.c:12:5: warning: format '%d' expects argument of type 'int *' [-Wformat=]"

# Piping directo desde GCC
gcc -Wall main.c -o app 2>&1 | esper pipe

# Salida estructurada JSON
esper compile main.c -o app --json
```
