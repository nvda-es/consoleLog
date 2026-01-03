# -*- coding: utf-8 -*-
# consoleLog - Plugin Base64 Decoder
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import base64
import re
from typing import Any, List
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginBase64Decoder(PluginBase):
	"""Plugin para detectar y decodificar cadenas en Base64."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Decodificador Base64"),
		version="1.0.0",
		descripcion=_("Busca y decodifica cadenas de texto en formato Base64"),
		autor="Héctor J. Benítez Corredera",
		categoria="desarrollo"
	)
	
	def inicializar(self) -> bool:
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		texto = kwargs.get('texto', '')
		if not texto: return []
		
		# Patrón para Base64 (mínimo 8 caracteres para evitar falsos positivos)
		patron = re.compile(r'\b(?:[A-Za-z0-9+/]{4}){2,}(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?\b')
		matches = patron.findall(texto)
		
		resultados = []
		vistos = set()
		for match in matches:
			if match in vistos or len(match) < 8: continue
			vistos.add(match)
			try:
				decoded = base64.b64decode(match).decode('utf-8', errors='ignore')
				# Si el resultado es legible (sin caracteres de control raros)
				if any(c.isalnum() for c in decoded):
					resultados.append(f"{match} -> {decoded}")
			except Exception:
				continue
				
		return resultados

	def terminar(self):
		pass
