# Manual del Complemento de Visor para Consolas de Windows
## Introducción

Este complemento facilita la visualización del contenido de las consolas de Windows a través de un diálogo interactivo. Es una herramienta válida para cualquier ventana de consola de Windows, permitiendo una navegación sencilla y opciones de búsqueda integradas.

## Configuración Inicial
### Asignación de Teclas

Para utilizar este complemento, es necesario asignar una combinación de teclas que invocará el diálogo del visor de consola. Puedes hacer esto desde la siguiente ruta:

```
NVDA > Preferencias > Gestos de Entrada > Visor de Consola > Muestra el Visor de Consola
```

### Restricciones

* Solo se permite tener un diálogo abierto a la vez.
* El diálogo solo puede ser invocado cuando una ventana de consola de Windows está enfocada.

## Funcionalidades del Diálogo

### Navegación

* Utiliza las teclas de cursor para navegar por el contenido.
* Pulsa `F1` para obtener la línea y posición actuales del cursor.

### Búsqueda

* `Ctrl + F`: Abre un diálogo de búsqueda.
* `F3`: Muestra un diálogo para buscar. Si ya se ha realizado una búsqueda anteriormente, buscará el siguiente resultado.
* `Shift + F3`: Busca el resultado anterior en la búsqueda.
* Las búsquedas no distinguen entre mayúsculas y minúsculas, y pueden realizarse con palabras exactas o fragmentos de palabras.
* Cada búsqueda exitosa emitirá un sonido "beep" indicando que el cursor está ahora en la siguiente palabra encontrada.

### Menú Rápido

Acceso rápido al menú con `Alt + R`, donde encontrarás las siguientes opciones:

* Buscar
* Guardar el contenido de la consola en un archivo
* Salir de la consola

### Salir del Diálogo

* `Alt + F4` o `Escape`: Cierra el diálogo.

## Actualización de Contenido

Si abres un diálogo y luego la consola se actualiza, tendrás que cerrar el diálogo y volver a invocarlo para ver las actualizaciones.

## Consolas Comunes de Windows

En Windows, existen varias consolas o terminales que puedes utilizar para ejecutar comandos y scripts. Aquí te presentamos una lista de las consolas más comunes:

1. **CMD** (Símbolo del sistema): Es una consola basada en texto para ejecutar comandos y batch scripts.
   
2. **PowerShell**: Es una consola avanzada que permite la automatización de tareas mediante scripts. Ofrece más características que el CMD tradicional.
   
3. **Windows Terminal**: Es una aplicación moderna que permite el acceso a múltiples consolas, como PowerShell, CMD y la consola de Linux (a través del Subsistema de Windows para Linux).
   
4. **Bash** (A través del Subsistema de Windows para Linux): Permite ejecutar un entorno de Linux dentro de Windows, permitiendo el uso de comandos y aplicaciones de Linux.

> **Nota**: Puedes acceder a estas consolas a través del menú inicio de Windows o mediante la búsqueda de Windows, escribiendo el nombre de la consola que deseas utilizar.

## Registro de cambios.
### Versión 1.4.

**Novedades**:

Asignar las teclas en la correspondiente categoría en gestos de entrada.

1. **Clic derecho en consolas**:
   - Ahora puedes realizar un clic derecho en consolas clásicas o modernas para pegar automáticamente el contenido del portapapeles en la consola.
   - Esta función es especialmente útil para transferir texto al entorno de la consola rápidamente sin necesidad de combinaciones adicionales.

2. **Lanzador de Consolas**:
   - Agregada una nueva funcionalidad que permite abrir diferentes consolas instaladas en el sistema desde cualquier directorio.
   - Detecta automáticamente las consolas disponibles: CMD, PowerShell, Windows Terminal, git-bash y consolas de Visual Studio.
   - Incluye opciones para abrir consolas en modo normal o con privilegios de administrador.
   - Permite seleccionar fácilmente la consola deseada con las teclas de flecha y abrirla con **`Intro`**.

### Versión 1.3.

* Agregada compatibilidad con Windows Terminal.

Esta función esta de prueba.

De momento en las pruebas realizadas extrae correctamente el texto y lo muestra para poder ser visualizado cómodamente en un dialogo y poder trabajar con él.

Esta nueva función se agrega al visor de consolas cmd, powershell y bash usando su misma combinación de teclas que tengamos agregado al complemento.

Al pulsar dicha combinación detectara que clase de consola tenemos enfocada y actuara en consecuencia.

### Versión 1.2.

* Solucionado error critico en Windows 10 de denegación de permisos (código 5).

* Agregado idioma turco y documentación (Umut KORKMAZ).

* Agregado detección de consola sin texto.

### Versión 1.1.

* Corrección de errores en cadenas traducibles.

* Agregado idioma inglés con traducción automática.

### Versión 1.0.

* Versión inicial.