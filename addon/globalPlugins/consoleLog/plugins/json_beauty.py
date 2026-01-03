# -*- coding: utf-8 -*-
# consoleLog - Plugin JSON Beauty
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import json
import re
from typing import Any, List
from logHandler import log
import wx

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginJSONBeauty(PluginBase):
	"""Plugin para detectar y formatear bloques JSON dentro de la salida de consola."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Embellecedor de JSON"),
		version="1.0.0",
		descripcion=_("Detecta bloques JSON en la consola y los muestra formateados y legibles"),
		autor="Héctor J. Benítez Corredera",
		categoria="desarrollo"
	)
	
	def inicializar(self) -> bool:
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> Any:
		texto = kwargs.get('texto', '')
		if not texto:
			return None
			
		# Buscar posibles bloques JSON (entre llaves o corchetes)
		# Filtramos para evitar capturar cosas demasiado pequeñas que no sean JSON
		patron = re.compile(r'(\{.*\}|\[.*\])', re.DOTALL)
		matches = patron.findall(texto)
		
		bloques_validos = []
		for match in matches:
			try:
				# Intentar parsear para validar si es JSON real
				datos = json.loads(match)
				# Si es válido, lo formateamos (pretty print)
				formateado = json.dumps(datos, indent=4, ensure_ascii=False)
				bloques_validos.append(formateado)
			except Exception:
				continue
				
		return bloques_validos
	
	def terminar(self):
		pass
