# ESPER — Explicador Pedagógico y Formateador de Diagnósticos GCC/Clang

**ESPER** envuelve la invocación del compilador GCC/Clang e intercepta errores, advertencias (`-Wall -Wextra -pedantic`) y notas del linker, traduciéndolas en paneles interactivos con diagnósticos pedagógicos en español rioplatense, causas raíz típicas y acciones correctivas sugeridas.

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
