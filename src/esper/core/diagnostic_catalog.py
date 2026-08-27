"""Catálogo de explicaciones pedagógicas y sugerencias de remediación para GCC/Clang."""

from typing import Tuple, Dict, Any

# Diccionario de patrones comunes en mensajes de GCC
# Clave: subcadena de error / flag -> (title_es, explanation_es, root_cause_es, suggestion_es)
CATALOGO_GCC: Dict[str, Tuple[str, str, str, str]] = {
    "implicit declaration of function": (
        "Invocación de Función sin Declaración Previa",
        "Estás usando una función que el compilador no conoce en este punto del archivo.",
        "Te olvidaste de incluir la cabecera correspondiente (ej: #include <stdio.h> para printf/scanf) o de declarar el prototipo antes del main.",
        "Agregá el '#include <...>' adecuado al inicio del archivo o declará el prototipo 'tipo nombre_funcion(...);' antes de invocarla."
    ),
    "format ‘%d’ expects argument of type": (
        "Incompatibilidad de Formato en scanf / printf",
        "El especificador de formato ('%d', '%s', '%f', etc.) no coincide con el tipo de la variable pasada.",
        "En 'scanf', probablemente olvidaste anteponer el operador '&' a la variable (ej: scanf('%d', &x)). En 'printf', pasaste un puntero o un tipo diferente.",
        "Verificá que en scanf pases la dirección de memoria (&variable) y que el especificador coincida exactamente con el tipo de dato."
    ),
    "assignment to ‘int’ from ‘int *’": (
        "Asignación Inválida de Puntero a Entero",
        "Intentaste guardar una dirección de memoria (puntero) directamente en una variable numérica entera sin desreferenciar.",
        "Falta el operador de desreferencia '*' o asignaste un puntero directamente a una variable de tipo 'int'.",
        "Si querés el valor apuntado, usá '*ptr'. Si querés guardar la dirección, declará la variable receptora como puntero 'int*'."
    ),
    "assignment to ‘int *’ from ‘int’": (
        "Asignación Inválida de Entero a Puntero",
        "Intentaste asignar un número entero directamente a una variable puntero.",
        "Un puntero sólo puede almacenar direcciones de memoria válidas (obtenidas con '&var' o 'malloc').",
        "Asigná la dirección de una variable existente ('ptr = &x;') o asignale memoria dinámica con 'malloc()'."
    ),
    "dereferencing pointer to incomplete type": (
        "Desreferencia de Tipo Incompleto / TDA Opaco",
        "Intentaste acceder a los campos internos de un struct ('ptr->campo') cuya estructura interna está oculta o no fue definida en la cabecera.",
        "El archivo .h sólo declaró 'typedef struct s_tda t_tda;' para mantenerlo opaco, o te olvidaste de incluir el .h con la definición completa.",
        "No accedas directamente a 'ptr->campo'. Utilizá las funciones primitivas públicas provistas en el .h para interactuar con el TDA."
    ),
    "undefined reference to": (
        "Símbolo no Encontrado en Enlazado (Linker Error)",
        "El compilador encontró la declaración de la función, pero el enlazador (ld) no encontró su código compilado (.c o librería).",
        "Te olvidaste de pasar el archivo .c correspondiente en el comando de compilación (ej: 'gcc main.c modulo.c') o falta enlazar una librería (ej: '-lm').",
        "Incluí todos los archivos fuentes en la compilación ('gcc main.c tda.c -o app') o agregá el flag de librería faltante ('-lm' para math.h)."
    ),
    "unused variable": (
        "Variable Declarada sin Uso",
        "Declaraste una variable pero nunca leés su valor en el código.",
        "Variable residual de pruebas o cálculo redundante.",
        "Eliminá la variable innecesaria o asegurate de usarla en tu algoritmo si era parte del cálculo."
    ),
    "control reaches end of non-void function": (
        "Función sin Retorno Garantizado",
        "La función promete devolver un valor pero puede terminar sin ejecutar una sentencia 'return'.",
        "En alguna rama de un if/else o al final del cuerpo de la función no hay un 'return' explícito.",
        "Asegurate de que todas las rutas de ejecución terminen con un 'return <valor>;' válido."
    ),
    "conflicting types for": (
        "Conflicto de Tipos en Firma de Función",
        "La firma de la función en su definición (.c) no coincide con el prototipo declarado en la cabecera (.h).",
        "Difieren el tipo de retorno o los tipos/cantidad de parámetros entre el .h y el .c.",
        "Hacé coincidir exactamente el tipo de retorno y los argumentos entre el prototipo en el .h y la definición en el .c."
    ),
}


def lookup_explanation(raw_msg: str) -> Tuple[str, str, str, str]:
    """Busca la explicación más adecuada para un mensaje de error o warning de GCC."""
    for key, val in CATALOGO_GCC.items():
        if key in raw_msg.lower():
            return val

    return (
        "Diagnóstico de Compilación GCC",
        f"El compilador reportó: {raw_msg}",
        "El código infringe las reglas sintácticas o semánticas del estándar C.",
        "Revisá la línea indicada y consultá la documentación de C sobre la sintaxis correspondiente."
    )
