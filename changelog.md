# Changelog - consoleLog

## [2026.01.04]
### Correcciones de Estabilidad y UIA
* **Optimización de Recursos UIA**: Corrección crítica de fugas de recursos en UI Automation que causaban inestabilidad en NVDA y fallos al detectar componentes en otras aplicaciones (como el Bloc de notas o el Explorador).
* **Solución de duplicación de voz**: Se eliminó un conflicto con el motor de NVDA que provocaba que el lector repitiera nombres de objetos y botones en el Explorador de Windows.
* **Mejora en detección de Terminal**: Refinamiento de la lógica de búsqueda para Windows Terminal, asegurando capturas más precisas.

### Interfaz y Funcionalidad
* **Aviso de Refresco en Terminal**: Al pulsar F5 en un visor de Windows Terminal, ahora se muestra un mensaje informativo indicando que la actualización en tiempo real para este tipo de consolas estará disponible próximamente.
* **Auto-scroll en Visor**: El visor ahora se desplaza automáticamente al final del texto tras un refresco (F5) si el usuario ya se encontraba al final del documento, facilitando la lectura de nuevos comandos en CMD y PowerShell.
- SHA256: 
