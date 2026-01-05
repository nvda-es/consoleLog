# Changelog - consoleLog

## [2026.01.05]
### Modo de Seguimiento y Nuevos Plugins
* **Modo de Seguimiento Automático (Auto-Tail)**: Nueva funcionalidad que permite al visor actualizarse en tiempo real cada 2 segundos y desplazarse automáticamente al final si hay contenido nuevo. 
    * Activación mediante el menú **Ver** o el atajo **Control + Shift + F**.
* **Nuevos Plugins de Especialista**:
    * **Monitor de Recursos**: Permite visualizar rápidamente el uso de RAM, espacio en disco y la versión de NVDA.
    * **Analizador de StackTrace**: Herramienta de desarrollo que detecta trazas de error de Python y permite extraer las rutas de los archivos para una depuración ágil.

### Organización y Experiencia de Usuario
* **Submenús por Categorías**: El menú de plugins ahora se organiza inteligentemente por categorías (*IA, Desarrollo, Utilidades, Edición*), facilitando la navegación cuando hay muchas herramientas activas.
* **Nuevas Opciones en Ajustes (Control+P)**:
    * Casilla para conmutar la **Categorización de Plugins**.
    * Casilla para habilitar o silenciar los **Sonidos de Seguimiento** (pitidos de actualización).
* **Mejora en Windows Terminal**: Integración del aviso de "próximamente" en el modo seguimiento para evitar confusiones y errores repetitivos en esta consola.

### Correcciones y Estabilidad
* **Solución de Fallos en Plugins**: Corrección definitiva del error `NoneType` que impedía la carga de plugins debido a conflictos en la inicialización de la función de traducción de NVDA.
* **Documentación Actualizada**: El manual de usuario (`readme.md`) ahora incluye todos los nuevos atajos y descripciones de los últimos plugins.
* **Actualización de Versión**: Incremento de versión oficial a **2026.01.05** en todos los metadatos.

---


## [2026.01.04]
### Correcciones de Estabilidad y UIA
* **Optimización de Recursos UIA**: Corrección crítica de fugas de recursos en UI Automation que causaban inestabilidad en NVDA y fallos al detectar componentes en otras aplicaciones (como el Bloc de notas o el Explorador).
* **Solución de duplicación de voz**: Se eliminó un conflicto con el motor de NVDA que provocaba que el lector repitiera nombres de objetos y botones en el Explorador de Windows.
* **Mejora en detección de Terminal**: Refinamiento de la lógica de búsqueda para Windows Terminal, asegurando capturas más precisas.

### Interfaz y Funcionalidad
* **Aviso de Refresco en Terminal**: Al pulsar F5 en un visor de Windows Terminal, ahora se muestra un mensaje informativo indicando que la actualización en tiempo real para este tipo de consolas estará disponible próximamente.
* **Auto-scroll en Visor**: El visor ahora se desplaza automáticamente al final del texto tras un refresco (F5) si el usuario ya se encontraba al final del documento, facilitando la lectura de nuevos comandos en CMD y PowerShell.

---

## [2026.01.03]
### Cambios Principales
* **Rebranding Completo**: El Complemento ha sido renombrado de "VisorConsolasXD" a **consoleLog**, recuperando su identidad original con tecnología moderna.
* **Nueva Arquitectura Modular**: Se ha reescrito el núcleo del complemento para soportar un sistema de plugins extensible y una gestión de memoria más eficiente.
* **Sistema de Plugins (11 herramientas)**:
    * **Google AI (Gemini)**: Integración avanzada con modelos de IA para analizar y depurar contenido de consola. Soporte para múltiples API Keys y archivos adjuntos.
    * **Extractor de Datos**: Localización rápida de URLs, direcciones IP y rutas de archivos.
    * **JSON Beauty**: Formateador inteligente para bloques JSON detectados.
    * **Filtro de Log**: Aislamiento de líneas específicas para facilitar la depuración.
* **Lanzador de Consolas Pro**:
    * Soporte completo para **CMD**, **PowerShell**, **PowerShell 7 (Core)**, **Windows Terminal**, **Git Bash**, **WSL (Linux)** y **Visual Studio Developer Command Prompt**.
    * **Detección Inteligente**: El lanzador identifica automáticamente qué consolas están instaladas en su sistema.
    * **Memoria de selección**: Ahora el lanzador recuerda opcionalmente la última consola utilizada (configurable en opciones).

### Novedades en Configuración y UI
* **Diálogo de Opciones (Control+P)**: Nueva interfaz integrada para personalizar el complemento sin editar archivos `.ini`.
* **Personalización del Visor**:
    * Ajuste dinámico del **tamaño de fuente**.
    * Opción para activar/desactivar **fuente monoespaciada** (ideal para alinear tablas y código).
    * **Persistencia de Ventana**: El visor guarda y restaura automáticamente su última posición y tamaño.
* **Nuevos Atajos de Teclado**:
    * **F2**: Acceso directo a la ayuda y lista de comandos.
    * **F5**: Refresco instantáneo de contenido capturando de nuevo la consola.

### Correcciones y Mejoras
* **Estabilidad del teclado**: Se corrigió un error crítico (`wxAssertionError`) que ocurría al presionar la tecla Enter en el visor.
* **Manejo del Menú**: Optimización de la tecla **Alt** para evitar interferencias con el área de texto y garantizar acceso fluido a la barra de herramientas.
* **Documentación**: Actualización exhaustiva del manual en Markdown y HTML con todas las funciones nuevas.
* **Copyright**: Actualización legal de todos los archivos al año **2026**.

### Información Técnica
* **Versión**: 2026.01.03
* **Autor**: Héctor J. Benítez Corredera
* **Compatibilidad**: NVDA 2025.1 o superior.

---

## [Historial Anterior]
* Versiones 1.x: Transición y desarrollo de la arquitectura modular bajo el nombre VisorConsolasXD.
* Versiones originales de consoleLog: Complemento básico de captura de texto de consola.
