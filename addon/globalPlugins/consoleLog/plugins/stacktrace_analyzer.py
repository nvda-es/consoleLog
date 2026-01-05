# -*- coding: utf-8 -*-
# consoleLog - Plugin Analizador de StackTrace
# Copyright (C) 2026 Héctor J. Benítez Corredera / Antigravity

import re
import os
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class PluginStackTrace(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Analizador de StackTrace"),
		version="1.0.0",
		descripcion=_("Analiza el log en busca de errores de Python y extrae rutas de archivos"),
		autor="Héctor J. Benítez / Antigravity",
		categoria="desarrollo"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		texto = kwargs.get('texto', '')
		# Patrón para Python: File "path", line X, in function
		patron_python = r'File "(.+?)", line (\d+)'
		
		coincidencias = re.findall(patron_python, texto)
		
		if not coincidencias:
			return [_("No se han encontrado trazas de error (Stack Traces) de Python en el texto.")]
		
		# Eliminar duplicados manteniendo el orden
		vistos = set()
		resultados = []
		for path, linea in coincidencias:
			# Formato amigable para el diálogo de selección
			nombre_fich = os.path.basename(path)
			item = f"{nombre_fich}:{linea} -> {path}"
			if item not in vistos:
				resultados.append(item)
				vistos.add(item)
		
		return resultados

	def terminar(self):
		pass
