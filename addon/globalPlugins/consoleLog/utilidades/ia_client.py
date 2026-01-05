# -*- coding: utf-8 -*-
# consoleLog - Cliente Base de Google AI Studio
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import json
import urllib.request
import urllib.parse
import urllib.error
import base64
from typing import List, Optional, Any, Dict
from logHandler import log

def decodificar_texto(texto: str) -> str:
	"""Decodifica texto de base64."""
	if not texto: return ""
	try:
		return base64.b64decode(texto.encode('utf-8')).decode('utf-8')
	except Exception:
		return ""

class IAClient:
	"""Cliente reusable para realizar peticiones a Gemini."""
	
	def __init__(self, configuracion):
		self.config = configuracion
		
	def _obtener_keys(self) -> List[str]:
		try:
			val = self.config.google_ai.api_keys_codificadas
			txt = decodificar_texto(val)
			return [k.strip() for k in txt.splitlines() if k.strip()]
		except AttributeError:
			return []

	def generar_contenido(self, prompt: str, prompt_sistema: Optional[str] = None, max_tokens: int = 8192) -> str:
		"""Realiza una petición síncrona a la API de Gemini.
		
		Args:
			prompt: El texto a enviar a la IA.
			prompt_sistema: Instrucciones opcionales de sistema.
			max_tokens: Límite de tokens de salida.
			
		Returns:
			El texto de la respuesta o eleva una excepción con el error.
		"""
		keys = self._obtener_keys()
		if not keys:
			raise Exception("No hay API Keys configuradas en las opciones de IA.")
			
		modelo = getattr(self.config.google_ai, 'modelo_actual', "gemini-1.5-flash")
		if not prompt_sistema:
			prompt_sistema = getattr(self.config.google_ai, 'prompt_sistema', "Eres un asistente experto.")
			
		for i, key in enumerate(keys):
			url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={key}"
			data = {
				"system_instruction": {"parts": [{"text": prompt_sistema}]},
				"contents": [{"role": "user", "parts": [{"text": prompt}]}],
				"generationConfig": {"temperature": 0.7, "maxOutputTokens": max_tokens}
			}
			
			try:
				req = urllib.request.Request(
					url, 
					data=json.dumps(data).encode('utf-8'), 
					headers={'Content-Type': 'application/json'}
				)
				with urllib.request.urlopen(req, timeout=60) as response:
					res = json.loads(response.read().decode('utf-8'))
					try:
						return res['candidates'][0]['content']['parts'][0]['text']
					except (KeyError, IndexError):
						raise Exception("Formato de respuesta inválido de la API")
			except urllib.error.HTTPError as e:
				if e.code in [401, 403, 429] and i < len(keys) - 1:
					log.warning(f"IAClient: Key {i+1} falló (Error {e.code}). Intentando siguiente...")
					continue
				raise Exception(f"Error de API {e.code}: {e.reason}")
			except Exception as e:
				raise e
				
		raise Exception("Todas las API Keys fallaron o están agotadas.")
