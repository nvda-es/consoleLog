# -*- coding: utf-8 -*-
# consoleLog - Utilidades de Mensajes
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Utilidades para manejo de mensajes y anuncios.

Proporciona una interfaz unificada para presentar mensajes
al usuario a través de voz y braille.
"""

from typing import Optional
from logHandler import log
import ui
import speech
import braille

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


class Mensajes:
	"""Gestor de mensajes para el complemento.
	
	Proporciona métodos para:
	- Anunciar mensajes por voz y braille
	- Manejar diferentes niveles de prioridad
	- Registrar mensajes en el log
	"""
	
	def __init__(self):
		"""Inicializa el gestor de mensajes."""
		self._ultimo_mensaje = ""
	
	def anunciar(
		self,
		texto: str,
		prioridad: Optional[speech.Spri] = None,
		texto_braille: Optional[str] = None,
		registrar: bool = True
	):
		"""Anuncia un mensaje al usuario.
		
		Args:
			texto: Texto del mensaje a anunciar.
			prioridad: Prioridad del mensaje de voz.
			texto_braille: Texto alternativo para braille (opcional).
			registrar: Si se debe registrar en el log.
		"""
		if not texto:
			return
		
		self._ultimo_mensaje = texto
		
		# Usar ui.message para anunciar por voz y braille
		ui.message(
			texto,
			speechPriority=prioridad,
			brailleText=texto_braille
		)
		
		if registrar:
			log.debug(f"consoleLog: Mensaje - {texto}")
	
	def anunciar_inmediato(self, texto: str):
		"""Anuncia un mensaje con prioridad inmediata.
		
		Args:
			texto: Texto del mensaje.
		"""
		self.anunciar(texto, prioridad=speech.Spri.NOW)
	
	def anunciar_informacion(self, texto: str):
		"""Anuncia un mensaje informativo.
		
		Args:
			texto: Texto del mensaje.
		"""
		self.anunciar(texto, prioridad=speech.Spri.NORMAL)
	
	def anunciar_error(self, texto: str):
		"""Anuncia un mensaje de error.
		
		Args:
			texto: Texto del error.
		"""
		# TRANSLATORS: Prefijo para mensajes de error
		mensaje = _("Error: {}").format(texto)
		self.anunciar(mensaje, prioridad=speech.Spri.NOW)
		log.error(f"consoleLog: {mensaje}")
	
	def anunciar_advertencia(self, texto: str):
		"""Anuncia un mensaje de advertencia.
		
		Args:
			texto: Texto de la advertencia.
		"""
		# TRANSLATORS: Prefijo para mensajes de advertencia
		mensaje = _("Advertencia: {}").format(texto)
		self.anunciar(mensaje, prioridad=speech.Spri.NORMAL)
		log.warning(f"consoleLog: {mensaje}")
	
	def anunciar_exito(self, texto: str):
		"""Anuncia un mensaje de éxito.
		
		Args:
			texto: Texto del mensaje.
		"""
		self.anunciar(texto, prioridad=speech.Spri.NORMAL)
	
	def mostrar_braille(self, texto: str):
		"""Muestra texto en la pantalla braille.
		
		Args:
			texto: Texto a mostrar.
		"""
		try:
			braille.handler.message(texto)
		except Exception as e:
			log.debug(f"consoleLog: No se pudo mostrar en braille: {e}")
	
	@property
	def ultimo_mensaje(self) -> str:
		"""Obtiene el último mensaje anunciado."""
		return self._ultimo_mensaje
	
	def repetir_ultimo(self):
		"""Repite el último mensaje anunciado."""
		if self._ultimo_mensaje:
			self.anunciar(self._ultimo_mensaje, registrar=False)
