# -*- coding: utf-8 -*-
# consoleLog - Plugin de Clic Derecho
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Plugin para realizar clic derecho en consolas.

Este plugin permite pegar el contenido del portapapeles en la consola
mediante la simulación de un clic derecho.
"""

import ctypes
import ctypes.wintypes
import winsound
from typing import Any
from logHandler import log
import UIAHandler

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin


class PluginClicDerecho(PluginBase):
	"""Plugin para realizar clic derecho en consolas.
	
	Simula un clic derecho en consolas clásicas y modernas
	para permitir pegar contenido del portapapeles.
	"""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Clic Derecho en Consola"),
		version="2.0.0",
		descripcion=_("Permite pegar el portapapeles en consolas mediante clic derecho"),
		autor="Héctor J. Benítez Corredera",
		categoria="acciones"
	)
	
	def __init__(self):
		"""Inicializa el plugin de clic derecho."""
		super().__init__()
		self._user32 = ctypes.windll.user32
	
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa.
		"""
		log.debug("consoleLog: Plugin ClicDerecho inicializado")
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> bool:
		"""Ejecuta el clic derecho en la consola.
		
		Args:
			tipo_consola: Tipo de consola ('clasica' o 'terminal').
			objeto: Objeto NVDA de la ventana de consola.
		
		Returns:
			True si se ejecutó correctamente.
		"""
		tipo_consola = kwargs.get('tipo_consola', 'clasica')
		objeto = kwargs.get('objeto')
		
		try:
			if tipo_consola == 'terminal':
				return self._clic_derecho_terminal_moderno()
			else:
				return self._clic_derecho_consola_clasica(objeto)
		except Exception as e:
			log.error(f"consoleLog: Error en clic derecho: {e}")
			return False
	
	def terminar(self):
		"""Libera recursos del plugin."""
		log.debug("consoleLog: Plugin ClicDerecho terminado")
	
	def _clic_derecho_consola_clasica(self, objeto: Any) -> bool:
		"""Realiza clic derecho en consola clásica.
		
		Args:
			objeto: Objeto de la ventana de consola.
		
		Returns:
			True si se realizó correctamente.
		"""
		try:
			hwnd = objeto.windowHandle
			rect = ctypes.wintypes.RECT()
			self._user32.GetWindowRect(hwnd, ctypes.byref(rect))
			
			# Calcular centro de la ventana
			x_centro = (rect.left + rect.right) // 2
			y_centro = (rect.top + rect.bottom) // 2
			
			# Mover cursor y simular clic
			self._user32.SetCursorPos(x_centro, y_centro)
			
			# Simular clic derecho
			self._user32.mouse_event(0x0008, 0, 0, 0, 0)  # Botón derecho presionado
			self._user32.mouse_event(0x0010, 0, 0, 0, 0)  # Botón derecho liberado
			
			# Beep de confirmación
			winsound.Beep(600, 200)
			
			return True
			
		except Exception as e:
			log.error(f"consoleLog: Error en clic derecho clásico: {e}")
			return False
	
	def _clic_derecho_terminal_moderno(self) -> bool:
		"""Realiza clic derecho en Windows Terminal.
		
		Returns:
			True si se realizó correctamente.
		"""
		elemento = None
		
		try:
			UIAHandler.initialize()
			
			elemento = UIAHandler.handler.clientObject.GetFocusedElement()
			if not elemento:
				log.warning("consoleLog: No se encontró elemento enfocado")
				return False
			
			# Obtener coordenadas del elemento
			bounds = elemento.GetCurrentPropertyValue(
				UIAHandler.UIA_BoundingRectanglePropertyId
			)
			
			if not bounds or not isinstance(bounds, tuple) or len(bounds) != 4:
				log.warning("consoleLog: No se pudieron obtener coordenadas")
				return False
			
			left, top, width, height = bounds
			
			# Calcular centro
			x_centro = int(left + width / 2)
			y_centro = int(top + height / 2)
			
			# Mover cursor y simular clic
			self._user32.SetCursorPos(x_centro, y_centro)
			
			# Simular clic derecho
			self._user32.mouse_event(0x0008, 0, 0, 0, 0)  # Presionar
			self._user32.mouse_event(0x0010, 0, 0, 0, 0)  # Soltar
			
			# Beep de confirmación
			winsound.Beep(600, 200)
			
			return True
			
		except Exception as e:
			log.error(f"consoleLog: Error en clic derecho terminal: {e}")
			return False
			
		finally:
			# Liberar objetos
			elemento = None
