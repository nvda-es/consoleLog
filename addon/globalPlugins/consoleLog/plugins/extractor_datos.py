# -*- coding: utf-8 -*-
# consoleLog - Plugin de Extracción de Datos
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Plugin para extraer datos útiles como URLs, rutas de archivos y direcciones IP.
"""

import re
from typing import Any, List, Dict
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin


class PluginExtractorDatos(PluginBase):
	"""Plugin para extraer información estructurada del contenido.
	
	Busca y lista:
	- URLs (http, https)
	- Rutas de Windows y Linux
	- Direcciones IPv4
	"""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Extractor de Datos (URLs, Rutas, IPs)"),
		version="1.0.0",
		descripcion=_("Busca y extrae URLs, rutas de archivos y direcciones IP del terminal"),
		autor="Héctor J. Benítez Corredera",
		categoria="analisis"
	)
	
	# Patrones de búsqueda
	PATRONES = {
		'urls': r'https?://[^\s<>"]+|www\.[^\s<>"]+',
		'rutas': r'(?:[a-zA-Z]:\\(?:[^\\\/:*?"<>|\r\n]+\\)*[^\\\/:*?"<>|\r\n]*)|(?:/(?:[^/ ]+/)+[^/ ]*)',
		'ips': r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
	}
	
	def __init__(self):
		"""Inicializa el plugin extractor."""
		super().__init__()
		self._patrones_compilados = {k: re.compile(v) for k, v in self.PATRONES.items()}
	
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa.
		"""
		log.debug("consoleLog: Plugin ExtractorDatos inicializado")
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> Dict[str, List[str]]:
		"""Extrae datos del contenido de la consola.
		
		Args:
			texto: Contenido de la consola a analizar.
		
		Returns:
			Diccionario con listas de datos encontrados por categoría.
		"""
		texto = kwargs.get('texto', '')
		
		if not texto:
			return {'urls': [], 'rutas': [], 'ips': []}
		
		resultados = {}
		for categoria, patron in self._patrones_compilados.items():
			encontrados = patron.findall(texto)
			# Eliminar duplicados manteniendo orden
			vistos = set()
			unicos = []
			for item in encontrados:
				if item not in vistos:
					vistos.add(item)
					unicos.append(item)
			resultados[categoria] = unicos
		
		log.debug(f"consoleLog: Extracción completada. URLs: {len(resultados['urls'])}, Rutas: {len(resultados['rutas'])}, IPs: {len(resultados['ips'])}")
		return resultados
	
	def terminar(self):
		"""Libera recursos del plugin."""
		log.debug("consoleLog: Plugin ExtractorDatos terminado")
