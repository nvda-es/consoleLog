# -*- coding: utf-8 -*-
# consoleLog - Plugin Calculadora Express
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import re
import math
from typing import Any, List
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginCalculadoraExpress(PluginBase):
	"""Plugin para detectar y evaluar expresiones matemáticas simples."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Calculadora Express"),
		version="1.0.0",
		descripcion=_("Busca y resuelve operaciones matemáticas básicas en el texto"),
		autor="Héctor J. Benítez Corredera",
		categoria="utilidades"
	)
	
	def inicializar(self) -> bool:
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		texto = kwargs.get('texto', '')
		if not texto: return []
		
		# Patrón para operaciones matemáticas básicas: suma, resta, mult, div, potencias
		# Ejemplo: 10 + 5, 2^8, 100 / 4
		patron = re.compile(r'\b\d+(?:\.\d+)?\s*[\+\-\*/\^]\s*\d+(?:\.\d+)?(?:\s*[\+\-\*/\^]\s*\d+(?:\.\d+)?)*\b')
		matches = patron.findall(texto)
		
		resultados = []
		vistos = set()
		for match in matches:
			if match in vistos: continue
			vistos.add(match)
			try:
				# Limpiar expresión (cambiar ^ por ** para Python)
				expr = match.replace('^', '**')
				# Evaluar de forma segura (limitando caracteres)
				if all(c in '0123456789.+-*/ \t()e*' for c in expr):
					resultado = eval(expr, {"__builtins__": None}, {})
					resultados.append(f"{match} = {resultado}")
			except Exception:
				continue
				
		return resultados

	def terminar(self):
		pass
