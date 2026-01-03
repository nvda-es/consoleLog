# -*- coding: utf-8 -*-
# consoleLog - Plugin Timestamp Converter
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import re
from datetime import datetime
from typing import Any, List, Dict
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginTimestampConverter(PluginBase):
	"""Plugin para detectar y convertir Unix Timestamps a fechas legibles."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Conversor de Marcas de Tiempo"),
		version="1.0.0",
		descripcion=_("Convierte números de marcas de tiempo Unix a fechas y horas legibles"),
		autor="Héctor J. Benítez Corredera",
		categoria="analisis"
	)
	
	def inicializar(self) -> bool:
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> List[str]:
		texto = kwargs.get('texto', '')
		if not texto: return []
		
		# Buscar números de 10 dígitos (segundos) o 13 dígitos (milisegundos)
		# Filtramos para años razonables (aprox entre 2000 y 2100)
		patron = re.compile(r'\b(1[0-9]{9}|[45][0-9]{12})\b')
		matches = patron.findall(texto)
		
		resultados = []
		vistos = set()
		for match in matches:
			if match in vistos: continue
			vistos.add(match)
			try:
				ts = int(match)
				# Si tiene 13 dígitos, son milisegundos
				if ts > 10000000000:
					ts = ts / 1000.0
				
				fecha = datetime.fromtimestamp(ts)
				fecha_str = fecha.strftime('%d/%m/%Y %H:%M:%S')
				resultados.append(f"{match} -> {fecha_str}")
			except Exception:
				continue
				
		return resultados
	
	def terminar(self):
		pass
