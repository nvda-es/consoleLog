# -*- coding: utf-8 -*-
# consoleLog - Plugin Decodificador JWT
# Copyright (C) 2026 Héctor J. Benítez / Antigravity

import json
import base64
import re
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class PluginJWTDecoder(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Decodificador JWT"),
		version="1.0.0",
		descripcion=_("Busca y decodifica tokens JWT en el texto"),
		autor="Héctor J. Benítez / Antigravity",
		categoria="edición"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		texto = kwargs.get('texto', '')
		# Patrón simple para JWT: header.payload.signature
		# [A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+
		patron = re.compile(r'ey[A-Za-z0-9-_]+\.ey[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+')
		tokens = patron.findall(texto)
		
		if not tokens:
			return [_("No se encontraron tokens JWT válidos.")]
			
		resultados = []
		for token in tokens:
			try:
				partes = token.split('.')
				# Decodificar Payload (parte 2)
				payload_b64 = partes[1]
				# Añadir padding si falta
				payload_b64 += '=' * (-len(payload_b64) % 4)
				decoded = base64.urlsafe_b64decode(payload_b64).decode('utf-8')
				data = json.loads(decoded)
				pretty = json.dumps(data, indent=2, ensure_ascii=False)
				resultados.append(f"JWT Payload:\n{pretty}")
			except Exception:
				continue
				
		return resultados

	def terminar(self):
		pass
