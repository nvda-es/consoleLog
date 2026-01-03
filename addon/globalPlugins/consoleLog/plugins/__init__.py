# -*- coding: utf-8 -*-
# consoleLog - Directorio de Plugins
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Directorio de plugins del complemento.

Los plugins disponibles se cargan dinámicamente desde este directorio.
Cada plugin debe heredar de PluginBase y definir sus metadatos.

Plugins incluidos:
- base64_decoder: Decodificador de cadenas Base64.
- calculadora_express: Realiza cálculos matemáticos rápidos.
- clic_derecho: Simula clic derecho para pegar en consolas.
- copiar_salida: Copia el contenido de la consola al portapapeles.
- extractor_datos: Extrae URLs, IPs y rutas de archivos.
- filtro_log: Filtra líneas de log por palabras clave.
- google_ai: Asistente inteligente basado en Gemini.
- historial_comandos: Muestra el historial de comandos detectados.
- json_beauty: Formatea bloques JSON para mejor lectura.
- resumen_actividad: Genera un resumen de la actividad de la consola.
- timestamp_converter: Convierte marcas de tiempo a fechas legibles.
"""
