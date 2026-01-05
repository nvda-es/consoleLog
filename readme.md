# consoleLog - Manual de Usuario Completo
**Versión:** 2026.01.06
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
El visor está optimizado para la velocidad y accesibilidad:
- **Alt**: Activa la barra de menús superior.
- **Control + F**: Abre el diálogo de búsqueda de texto.
- **F3 / Shift + F3**: Salta a la siguiente / anterior coincidencia de búsqueda (Ciclo completo).
- **Control + G**: Diálogo para saltar rápidamente a una línea específica.
- **Control + S**: Guarda todo el historial actual en un archivo `.txt`.
- **Control + P**: Abre directamente el diálogo de opciones/ajustes.
- **Control + Shift + F**: Conmuta el **Modo de Seguimiento Automático (Auto-Tail)**.
- **Control + C / Control + A**: Copiar selección / Seleccionar todo el contenido.
- **F1**: Anuncia la posición actual del cursor (línea y columna).
- **F2**: Ayuda de atajos de teclado (Accesible y navegable).
- **F5**: Actualiza el contenido (Nota: Aviso informativo en Windows Terminal).
- **Escape / Alt + F4**: Cierra el visor de consola.

<a name="gestión-de-archivos-y-búsqueda"></a>
### Gestión de Archivos y Búsqueda
El visor no es solo lectura. Puede guardar sesiones completas de depuración o logs extensos para su análisis posterior. La búsqueda es de "ciclo completo", lo que significa que si llega al final del texto y no encuentra más resultados, volverá a empezar por el principio automáticamente.

<a name="el-lanzador-de-consolas"></a>
## 4. El Lanzador de Consolas
Esta función permite abrir rápidamente diferentes consolas en el directorio actual del Explorador de Windows o el Escritorio.
1. Presione el comando del lanzador (debe asignarlo en Gestos de Entrada).
2. Aparecerá una lista con las consolas instaladas en su sistema:
   - **CMD** (Símbolo del sistema de Windows).
   - **PowerShell** (Instancia clásica v5.1).
   - **PowerShell 7** (Versión Core, si está instalada).
   - **Windows Terminal** (Soporta pestañas y perfiles modernos).
   - **Git Bash** (Entorno Git para Windows).
   - **WSL (Linux)** (Subsistema de Windows para Linux).
   - **Visual Studio developer** (Símbolo del sistema para desarrolladores de 32 y 64 bits).
   - **Msys2 / MinGW** (Entornos de desarrollo adicionales).
3. Seleccione una y se abrirá instantáneamente en esa ubicación exacta.

<a name="sistema-de-plugins"></a>
## 5. Sistema de Plugins (Herramientas Inteligentes)
consoleLog cuenta con una arquitectura modular que permite extender sus funcionalidades mediante plugins.

<a name="google-ai"></a>
### Google AI (Gemini/Gemma)
Permite mantener una conversación inteligente sobre el contenido de su consola.
- **Chat Interactivo**: Utilice **`j`** y **`k`** para moverse cíclicamente por el historial de mensajes (con audio-feedback).
- **Auto-reparar error**: Botón que analiza el fallo actual y propone parches de código exactos.
- **Generador de Informe**: Nuevo plugin que genera un reporte estructurado (Resumen, Errores, Soluciones) en Markdown.
- **Configuración multi-clave**: Soporte para múltiples API Keys con rotación automática en caso de límites (429).
- **Archivos adjuntos**: Cargue archivos `.txt` para dar más contexto a la IA.
- **Instrucciones de Sistema**: Personalice la personalidad de su asistente.

<a name="herramientas-de-análisis-de-datos"></a>
### Herramientas de Análisis de Datos
- **Extractor de Datos**: Localiza IPs, URLs y rutas de archivos.
- **JSON Beauty**: Formatea bloques JSON desordenados.
- **Decodificador JWT**: Busca y decodifica tokens de seguridad JWT en los logs.
- **Formateador SQL**: Organiza consultas SQL complejas para facilitar su lectura.
- **Filtro de Log**: Aísla líneas por niveles (Error, Info, etc.).

<a name="herramientas-de-utilidad"></a>
### Herramientas de Utilidad
- **Monitor de Recursos**: Muestra el uso de disco, RAM y versión de NVDA en un panel rápido.
- **Analizador de StackTrace**: Detecta errores de programación de Python y permite extraer las rutas de archivos involucrados para una depuración rápida.
- **Calculadora Express**: Resuelve operaciones matemáticas que aparezcan en el texto.
- **Convertidor de Tiempos**: Traduce marcas de tiempo (UNIX timestamps) a fechas legibles.
- **Base64**: Decodifica cadenas en formato Base64 comúnmente encontradas en logs.
- **Copiado rápido**: Permite copiar el contenido de la consola enfocada de manera directa sin abrir el visor.

<a name="configuración-y-personalización"></a>
## 6. Configuración y Personalización
A través del menú **Archivo -> Opciones**, puede ajustar el comportamiento del visor:
- **Talla de Fuente**: Ajuste el tamaño para su comodidad visual.
- **Fuente Monoespaciada**: Actívela para que las tablas y el código se alineen correctamente.
- **Recordar Posición**: El visor puede recordar el tamaño y posición de la ventana.
- **Recordar selección en Lanzador**: Vuelve a seleccionar la última consola usada automáticamente.
- **Sistema de Alertas y Marcadores**: Defina palabras clave (ej: ERROR) que disparen sonidos o anuncios de NVDA en tiempo real.
- **Categorizar Plugins**: Organización inteligente por submenús (IA, Desarrollo, Utiles).
- **Intervalo de Seguimiento**: Configure el tiempo de refresco del Modo Tail (1-60 seg).
- **Sonidos Personalizados**: Elija silenciar las actualizaciones automáticas manteniendo los sonidos de activación.
- **Gestión de Plugins**: Pestaña dedicada para habilitar/deshabilitar herramientas.

<a name="solución-de-problemas"></a>
## 7. Solución de Problemas
- **El visor aparece vacío**: Asegúrese de que la consola tiene texto visible y tiene el foco antes de activar el comando.
- **Google AI no responde**: Revise sus API Keys y la conexión a internet.
- **Alt no abre el menú**: Si el foco se queda atrapado en el texto, intente presionar Escape una vez y luego Alt.
- **F5 no funciona en Windows Terminal**: Debido a la arquitectura de aislamiento de Windows Terminal, el refresco en tiempo real está actualmente desactivado para esta consola. Se recomienda cerrar y volver a abrir el visor (NVDA+Control+V) para obtener el contenido actualizado.

<a name="créditos"></a>
## 8. Créditos y Licencia
Este complemento es software libre bajo la licencia GPL v2.
**Desarrollador Principal:** Héctor J. Benítez Corredera.
**Contacto:** xebolax@gmail.com
**Repositorio:** [GitHub consoleLog](https://github.com/nvda-es/consoleLog)

---
*Gracias por usar consoleLog. Esperamos que esta herramienta mejore significativamente su productividad día a día.*
