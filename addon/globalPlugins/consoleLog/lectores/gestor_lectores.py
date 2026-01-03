# -*- coding: utf-8 -*-
# consoleLog - Gestor de Lectores de Consola
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Gestor de lectores de consola.

Proporciona una interfaz unificada para leer diferentes tipos de consolas:
- Consolas clásicas (CMD, PowerShell en modo legacy)
- Windows Terminal
"""

import threading
import queue
import wx
from typing import Callable, Optional, Any
from logHandler import log
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from .lector_clasico import LectorConsolaClasica
from .lector_terminal import LectorWindowsTerminal


class GestorLectores:
	"""Gestor unificado de lectores de consola.
	
	Proporciona una interfaz común para leer el contenido de
	diferentes tipos de consolas de Windows.
	"""
	
	def __init__(self):
		"""Inicializa el gestor de lectores."""
		self._lector_clasico = LectorConsolaClasica()
		self._lector_terminal = LectorWindowsTerminal()
		self._hilo_actual: Optional[threading.Thread] = None
		self._senal_parar = threading.Event()
	
	def leer_consola(
		self,
		tipo_consola: str,
		objeto_ventana: Any,
		callback_exito: Callable[[str], None],
		callback_error: Callable[[str], None],
		callback_progreso: Optional[Callable[[], None]] = None
	):
		"""Inicia la lectura asíncrona de una consola.
		
		Args:
			tipo_consola: Tipo de consola ('clasica' o 'terminal').
			objeto_ventana: Objeto NVDA de la ventana de consola.
			callback_exito: Función a llamar cuando la lectura sea exitosa.
			callback_error: Función a llamar si ocurre un error.
			callback_progreso: Función opcional para indicar progreso.
		"""
		self._senal_parar.clear()
		
		cola_datos = queue.Queue()
		
		# Iniciar hilo de lectura
		self._hilo_actual = threading.Thread(
			target=self._leer_en_hilo,
			args=(tipo_consola, objeto_ventana, cola_datos),
			daemon=True
		)
		self._hilo_actual.start()
		
		# Iniciar verificación de resultados
		wx.CallLater(100, self._verificar_resultado, 
			cola_datos, callback_exito, callback_error, callback_progreso)
	
	def _leer_en_hilo(
		self,
		tipo_consola: str,
		objeto_ventana: Any,
		cola_datos: queue.Queue
	):
		"""Ejecuta la lectura en un hilo separado.
		
		Args:
			tipo_consola: Tipo de consola.
			objeto_ventana: Objeto de la ventana.
			cola_datos: Cola para almacenar resultados.
		"""
		try:
			if tipo_consola == 'terminal':
				resultado = self._lector_terminal.leer(
					objeto_ventana,
					senal_parar=self._senal_parar
				)
			else:  # clasica
				try:
					resultado = self._lector_clasico.leer(
						objeto_ventana,
						senal_parar=self._senal_parar
					)
				except Exception as e:
					# Si falla el método clásico (ej: consola Admin), intentar vía UIA como fallback
					log.debug(f"consoleLog: Falló el lector clásico, intentando fallback UIA: {e}")
					try:
						# Reiniciar señal de parar para el nuevo intento
						self._senal_parar.clear()
						resultado = self._lector_terminal.leer(
							objeto_ventana,
							senal_parar=self._senal_parar
						)
					except Exception:
						# Si ambos fallan, relanzar el error original o uno más informativo
						if "adjuntar" in str(e).lower() or "5" in str(e): # Error 5 is Access Denied
							raise Exception(_("No se puede leer una consola administrada si NVDA no se ejecuta como administrador."))
						raise e
			
			cola_datos.put(('exito', resultado))
			
		except Exception as e:
			log.error(f"consoleLog: Error en lectura de consola: {e}")
			cola_datos.put(('error', str(e)))
	
	def _verificar_resultado(
		self,
		cola_datos: queue.Queue,
		callback_exito: Callable[[str], None],
		callback_error: Callable[[str], None],
		callback_progreso: Optional[Callable[[], None]]
	):
		"""Verifica si la lectura ha finalizado.
		
		Args:
			cola_datos: Cola con los resultados.
			callback_exito: Callback para éxito.
			callback_error: Callback para error.
			callback_progreso: Callback de progreso.
		"""
		try:
			tipo, resultado = cola_datos.get_nowait()
			
			if tipo == 'exito':
				callback_exito(resultado)
			else:
				callback_error(resultado)
			
		except queue.Empty:
			# Indicar progreso
			if callback_progreso:
				callback_progreso()
			
			# Continuar verificando
			wx.CallLater(100, self._verificar_resultado,
				cola_datos, callback_exito, callback_error, callback_progreso)
	
	def cancelar_lectura(self):
		"""Cancela la lectura en curso si existe."""
		self._senal_parar.set()
		
		if self._hilo_actual and self._hilo_actual.is_alive():
			log.debug("consoleLog: Cancelando lectura de consola")
