# -*- coding: utf-8 -*-
# consoleLog - Plugin Resumen de Actividad
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import re
from typing import Any, List, Dict
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginResumenActividad(PluginBase):
	"""Plugin para analizar y resumir las herramientas detectadas en la consola."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Resumen de Actividad"),
		version="1.0.0",
		descripcion=_("Analiza el texto para identificar herramientas de desarrollo y dar estadísticas"),
		autor="Héctor J. Benítez Corredera",
		categoria="analisis"
	)
	
	HERRAMIENTAS = {
		'Git': r'\bgit\s+\w+',
		'Docker': r'\bdocker\s+\w+',
		'NPM/Node': r'\bnpm\s+\w+|\bnode\s+',
		'Python': r'\bpython\d*\s+|\bpip\s+',
		'Cursos de Red': r'\bping\s+|\bipconfig\b|\bifconfig\b|\bnetstat\b',
		'Compiladores': r'\bgcc\b|\bg\+\+\b|\bjavac\b|\bdotnet\b',
		'Cloud': r'\baws\s+|\baz\s+|\bgcloud\s+'
	}
	
	def inicializar(self) -> bool:
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		texto = kwargs.get('texto', '')
		if not texto: return []
		
		resumen = []
		lineas = texto.splitlines()
		resumen.append(_("Estadísticas Generales:"))
		resumen.append(_("- Total de líneas: {}").format(len(lineas)))
		resumen.append(_("- Total de palabras: {}").format(len(texto.split())))
		
		resumen.append("")
		resumen.append(_("Herramientas Detectadas:"))
		
		encontrado = False
		for nombre, patron in self.HERRAMIENTAS.items():
			matches = re.findall(patron, texto, re.IGNORECASE)
			if matches:
				encontrado = True
				resumen.append(f"- {nombre}: {len(matches)} menciones")
				
		if not encontrado:
			resumen.append(_("- No se detectaron herramientas específicas."))
			
		return resumen

	def terminar(self):
		pass
