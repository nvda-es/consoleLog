# -*- coding: utf-8 -*-
# consoleLog - Plugin de Historial de Comandos
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Plugin para extraer el historial de comandos de la consola.

Este plugin permite identificar y extraer los comandos ejecutados
del contenido de la consola.
"""

import re
from typing import Any, List
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin


class PluginHistorialComandos(PluginBase):
	"""Plugin para extraer el historial de comandos.
	
	Analiza el contenido de la consola para identificar los comandos
	ejecutados basándose en patrones comunes de prompts.
	"""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Historial de Comandos"),
		version="2.0.0",
		descripcion=_("Extrae y lista los comandos ejecutados en la consola"),
		autor="Héctor J. Benítez Corredera",
		categoria="analisis"
	)
	
	# Patrones de prompts comunes
	PATRONES_PROMPT = [
		r'^[A-Za-z]:\\[^>]*>(.+)$',  # CMD: C:\Users\User>comando
		r'^PS [A-Za-z]:\\[^>]*>(.+)$',  # PowerShell: PS C:\Users>comando
		r'^\$ (.+)$',  # Bash: $ comando
		r'^> (.+)$',  # Prompt genérico: > comando
		r'^>>> (.+)$',  # Python REPL: >>> comando
	]
	
	def __init__(self):
		"""Inicializa el plugin de historial."""
		super().__init__()
		self._patrones_compilados = [re.compile(p) for p in self.PATRONES_PROMPT]
	
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa.
		"""
		log.debug("consoleLog: Plugin HistorialComandos inicializado")
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		"""Extrae los comandos del contenido de la consola.
		
		Args:
			texto: Contenido de la consola a analizar.
		
		Returns:
			Lista de comandos encontrados.
		"""
		texto = kwargs.get('texto', '')
		
		if not texto:
			log.debug("consoleLog: No hay texto para analizar")
			return []
		
		comandos = []
		
		for linea in texto.splitlines():
			linea = linea.strip()
			if not linea:
				continue
			
			for patron in self._patrones_compilados:
				match = patron.match(linea)
				if match:
					comando = match.group(1).strip()
					if comando:
						comandos.append(comando)
					break
		
		log.debug(f"consoleLog: Encontrados {len(comandos)} comandos")
		return comandos
	
	def obtener_ultimo_comando(self, texto: str) -> str:
		"""Obtiene el último comando ejecutado.
		
		Args:
			texto: Contenido de la consola.
		
		Returns:
			Último comando encontrado o cadena vacía.
		"""
		comandos = self.ejecutar(texto=texto)
		return comandos[-1] if comandos else ""
	
	def obtener_comandos_unicos(self, texto: str) -> List[str]:
		"""Obtiene los comandos únicos ejecutados.
		
		Args:
			texto: Contenido de la consola.
		
		Returns:
			Lista de comandos únicos.
		"""
		comandos = self.ejecutar(texto=texto)
		# Mantener orden de aparición
		vistos = set()
		unicos = []
		for cmd in comandos:
			if cmd not in vistos:
				vistos.add(cmd)
				unicos.append(cmd)
		return unicos
	
	def terminar(self):
		"""Libera recursos del plugin."""
		log.debug("consoleLog: Plugin HistorialComandos terminado")
