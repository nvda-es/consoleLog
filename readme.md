# consoleLog - Manual de Usuario Completo
**Versión:** 2026..01.03
**Autor y Desarrollador:** Héctor J. Benítez Corredera

---

## Índice
1. [Introducción](#introducción)
2. [Instalación y Primeros Pasos](#instalación-y-primeros-pasos)
3. [El Visor de Consola](#el-visor-de-consola)
    - [Atajos de Teclado](#atajos-de-teclado)
    - [Gestión de Archivos y Búsqueda](#gestión-de-archivos-y-búsqueda)
4. [El Lanzador de Consolas](#el-lanzador-de-consolas)
5. [Sistema de Plugins (Herramientas Inteligentes)](#sistema-de-plugins)
    - [Google AI (Gemini/Gemma)](#google-ai)
    - [Herramientas de Análisis de Datos](#herramientas-de-análisis-de-datos)
    - [Herramientas de Utilidad](#herramientas-de-utilidad)
6. [Configuración y Personalización](#configuración-y-personalización)
7. [Solución de Problemas](#solución-de-problemas)
8. [Créditos y Licencia](#créditos)

---

<a name="introducción"></a>
## 1. Introducción
**consoleLog** (anteriormente conocido como VisorConsolasXD) es un complemento para el lector de pantalla NVDA diseñado para mostrar en un diálogo el contenido de las consolas de Windows. Permite a los usuarios interactuar con entornos de línea de comandos (como CMD, PowerShell, Terminal, Bash o Visual Studio developer) mediante una interfaz de texto enriquecido, accesible y altamente personalizable.

<a name="instalación-y-primeros-pasos"></a>
## 2. Instalación y Primeros Pasos
Una vez instalado el complemento, la primera acción recomendada es asignar un comando de teclado para abrir el visor:
1. Abra el menú de NVDA (Insert+N).
2. Vaya a **Preferencias** -> **Gestos de entrada**.
3. Busque la categoría **Visor de consola**.
4. Asigne una tecla a **Muestra el visor de consola** (por ejemplo: `NVDA+Control+V`).

<a name="el-visor-de-consola"></a>
## 3. El Visor de Consola
Cuando presiona el comando asignado estando sobre una ventana de consola, consoleLog captura todo el texto actual y lo presenta en una ventana dedicada. Esta ventana ignora las limitaciones de lectura de la consola estándar y permite navegar línea a línea con total libertad.

<a name="atajos-de-teclado"></a>
### Atajos de Teclado (Dentro del Visor)
El visor está optimizado para la velocidad:
- **Control + F**: Abre el diálogo de búsqueda.
- **F3**: Salta a la siguiente coincidencia de búsqueda.
- **Shift + F3**: Salta a la coincidencia anterior.
- **Control + G**: Diálogo para saltar a una línea específica.
- **Control + S**: Guarda todo el historial actual en un archivo `.txt`.
- **F1**: Indica la posición del cursor (línea y columna).
- **F2**: Muestra la ayuda de atajos de teclado.

<a name="gestión-de-archivos-y-búsqueda"></a>
### Gestión de Archivos y Búsqueda
El visor no es solo lectura. Puede guardar sesiones completas de depuración o logs extensos para su análisis posterior. La búsqueda es de "ciclo completo", lo que significa que si llega al final del texto y no encuentra más resultados, volverá a empezar por el principio automáticamente.

<a name="el-lanzador-de-consolas"></a>
## 4. El Lanzador de Consolas
Esta función permite abrir rápidamente diferentes consolas en el directorio actual del Explorador de Windows o el Escritorio.
1. Presione el comando del lanzador (debe asignarlo en Gestos de Entrada).
2. Aparecerá una lista con las consolas instaladas en su sistema:
   - **CMD** (Símbolo del sistema).
   - **PowerShell**.
   - **Terminal**.
   - **Bash**.
   - **Visual Studio developer**.
3. Seleccione una y se abrirá instantáneamente en esa ubicación exacta.

<a name="sistema-de-plugins"></a>
## 5. Sistema de Plugins (Herramientas Inteligentes)
consoleLog cuenta con una arquitectura modular que permite extender sus funcionalidades mediante plugins.

<a name="google-ai"></a>
### Google AI (Gemini/Gemma)
Permite mantener una conversación con la inteligencia artificial sobre lo que está ocurriendo en su consola.
- **Configuración multi-clave**: Puede añadir varias claves API para evitar límites de uso.
- **Archivos adjuntos**: Puede cargar archivos `.txt` externos.
- **Detección de errores**: Analiza errores y sugiere soluciones.
- **Instrucciones de Sistema**: Personaliza el comportamiento de la IA.

<a name="herramientas-de-análisis-de-datos"></a>
### Herramientas de Análisis de Datos
- **Extractor de Datos**: Busca direcciones IP, URLs y rutas de archivos en el texto.
- **JSON Beauty**: Formatea bloques JSON para mejorar su legibilidad.
- **Filtro de Log**: Aísla información relevante de registros extensos.

<a name="herramientas-de-utilidad"></a>
### Herramientas de Utilidad
- **Calculadora Express**: Resuelve operaciones matemáticas.
- **Convertidor de Tiempos**: Traduce marcas de tiempo (timestamps) a fechas legibles.
- **Base64**: Decodifica cadenas en formato Base64.
- **Copiado rápido**: Permite copiar el contenido de la consola enfocada de manera fácil.

<a name="configuración-y-personalización"></a>
## 6. Configuración y Personalización
A través del menú **Archivo -> Opciones**, puede ajustar el comportamiento del visor:
- **Talla de Fuente**: Ajuste el tamaño para su comodidad visual.
- **Fuente Monoespaciada**: Actívela para que las tablas y el código se alineen correctamente.
- **Recordar Posición**: El visor puede recordar el tamaño y posición de la ventana.
- **Gestión de Plugins**: Active o desactive plugins.

<a name="solución-de-problemas"></a>
## 7. Solución de Problemas
- **El visor aparece vacío**: Asegúrese de que la consola tiene texto visible y tiene el foco antes de activar el comando.
- **Google AI no responde**: Revise sus API Keys y la conexión a internet.
- **Alt no abre el menú**: Si el foco se queda atrapado, intente presionar Escape y luego Alt.

<a name="créditos"></a>
## 8. Créditos y Licencia
Este complemento es software libre bajo la licencia GPL v2.
**Desarrollador Principal:** Héctor J. Benítez Corredera.
**Contacto:** xebolax@gmail.com
**Repositorio:** [GitHub consoleLog](https://github.com/nvda-es/consoleLog)

---
*Gracias por usar consoleLog. Esperamos que esta herramienta mejore significativamente su productividad día a día.*
