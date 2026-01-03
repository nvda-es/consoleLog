# Changelog - consoleLog

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
