# -*- coding: utf-8 -*-
# consoleLog - Plugin de Copiar Salida
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Plugin para copiar la salida de la consola al portapapeles.

Este plugin permite copiar todo el contenido visible de la consola
directamente al portapapeles sin necesidad de abrir el visor.
"""

import winsound
from typing import Any
from logHandler import log
import api

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin


class PluginCopiarSalida(PluginBase):
	"""Plugin para copiar la salida de la consola al portapapeles.
	
	Copia todo el contenido de la consola al portapapeles sin
	necesidad de abrir el visor de consola.
	"""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Copiar Salida al Portapapeles"),
		version="2.0.0",
		descripcion=_("Copia el contenido completo de la consola al portapapeles"),
		autor="Héctor J. Benítez Corredera",
		categoria="portapapeles"
	)
	
	def __init__(self):
		"""Inicializa el plugin de copiar salida."""
		super().__init__()
	
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa.
		"""
		log.debug("consoleLog: Plugin CopiarSalida inicializado")
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> bool:
		"""Copia el contenido de la consola al portapapeles.
		
		Args:
			texto: Texto a copiar al portapapeles.
		
		Returns:
			True si se copió correctamente.
		"""
		texto = kwargs.get('texto', '')
		
		if not texto:
			log.warning("consoleLog: No hay texto para copiar")
			return False
		
		try:
			# Copiar al portapapeles usando la API de NVDA
			if api.copyToClip(texto):
				# Beep de confirmación
				winsound.Beep(1200, 100)
				log.info("consoleLog: Contenido copiado al portapapeles")
				return True
			else:
				log.error("consoleLog: Error al copiar al portapapeles")
				return False
			
		except Exception as e:
			log.error(f"consoleLog: Error en plugin copiar: {e}")
			return False
	
	def terminar(self):
		"""Libera recursos del plugin."""
		log.debug("consoleLog: Plugin CopiarSalida terminado")
