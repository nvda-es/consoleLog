# -*- coding: utf-8 -*-
# consoleLog - Plugin de Filtro de Registro (Logs)
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Plugin para filtrar y resaltar errores, advertencias e información crítica en logs.
"""

import re
from typing import Any, List
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin


class PluginFiltroLog(PluginBase):
	"""Plugin para filtrar y resaltar líneas importantes.
	
	Identifica líneas que contienen:
	- Error, Fault, Failed, Exception
	- Warning, Alert
	- Critical, Fatal
	"""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Filtro de Errores y Advertencias"),
		version="1.0.0",
		descripcion=_("Filtra el contenido para mostrar solo líneas con errores o advertencias"),
		autor="Héctor J. Benítez Corredera",
		categoria="analisis"
	)
	
	# Palabras clave para filtrado
	KEYWORDS_ERROR = [r'error', r'fault', r'fail', r'exception', r'critical', r'fatal']
	KEYWORDS_WARNING = [r'warning', r'warn', r'alert']
	
	def __init__(self):
		"""Inicializa el plugin de filtro."""
		super().__init__()
		self._patron_error = re.compile('|'.join(self.KEYWORDS_ERROR), re.IGNORECASE)
		self._patron_warning = re.compile('|'.join(self.KEYWORDS_WARNING), re.IGNORECASE)
	
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa.
		"""
		log.debug("consoleLog: Plugin FiltroLog inicializado")
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		"""Filtra el contenido de la consola.
		
		Args:
			texto: Contenido de la consola a filtrar.
		
		Returns:
			Lista de líneas que coinciden con los criterios de importancia.
		"""
		texto = kwargs.get('texto', '')
		
		if not texto:
			return []
		
		lineas_interesantes = []
		for linea in texto.splitlines():
			if self._patron_error.search(linea) or self._patron_warning.search(linea):
				lineas_interesantes.append(linea.strip())
		
		return lineas_interesantes
	
	def terminar(self):
		"""Libera recursos del plugin."""
		log.debug("consoleLog: Plugin FiltroLog terminado")
