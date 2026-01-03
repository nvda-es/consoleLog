# -*- coding: utf-8 -*-
# consoleLog - Lector de Consola Clásica
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Lector de consolas clásicas de Windows (CMD, PowerShell legacy).

Utiliza las APIs de Windows para leer el buffer de la consola,
incluyendo soporte para colores y atributos de texto.
"""

import ctypes
import ctypes.wintypes
import re
import threading
import winsound
import wx
from typing import Optional, Any, List
from logHandler import log
import api

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


# Constantes de Windows
STD_OUTPUT_HANDLE = -11


# Estructuras de datos para la API de Windows
class COORD(ctypes.Structure):
	"""Coordenadas de la consola."""
	_fields_ = [
		("X", ctypes.c_short),
		("Y", ctypes.c_short)
	]


class CHAR_INFO(ctypes.Structure):
	"""Información de carácter de la consola."""
	_fields_ = [
		("Char", ctypes.c_wchar),
		("Attributes", ctypes.c_ushort)
	]


class SMALL_RECT(ctypes.Structure):
	"""Rectángulo pequeño para la consola."""
	_fields_ = [
		("Left", ctypes.c_short),
		("Top", ctypes.c_short),
		("Right", ctypes.c_short),
		("Bottom", ctypes.c_short)
	]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
	"""Información del buffer de pantalla de la consola."""
	_fields_ = [
		("dwSize", COORD),
		("dwCursorPosition", COORD),
		("wAttributes", ctypes.c_ushort),
		("srWindow", SMALL_RECT),
		("dwMaximumWindowSize", COORD)
	]


class LectorConsolaClasica:
	"""Lector para consolas clásicas de Windows.
	
	Proporciona métodos para:
	- Adjuntar a una consola existente
	- Leer el buffer completo de la consola
	- Extraer texto con formato
	"""
	
	def __init__(self):
		"""Inicializa el lector de consola clásica."""
		self._kernel32 = ctypes.windll.kernel32
		self._user32 = ctypes.windll.user32
	
	def leer(
		self,
		objeto_ventana: Any,
		senal_parar: Optional[threading.Event] = None,
		emitir_beep: bool = True
	) -> str:
		"""Lee el contenido de una consola clásica.
		
		Args:
			objeto_ventana: Objeto NVDA de la ventana de consola.
			senal_parar: Evento para detener la lectura.
			emitir_beep: Si se debe emitir un beep durante la lectura.
		
		Returns:
			Texto extraído de la consola.
		
		Raises:
			Exception: Si no se puede leer la consola.
		"""
		hilo_beep = None
		
		try:
			# Iniciar beep de progreso en hilo separado
			if emitir_beep:
				hilo_beep = threading.Thread(
					target=self._emitir_beep_progreso,
					args=(senal_parar,),
					daemon=True
				)
				hilo_beep.start()
			
			# Obtener handle de la ventana
			hwnd = self._obtener_hwnd_consola(objeto_ventana)
			if hwnd == 0:
				raise Exception(_("No se pudo encontrar la ventana de la consola."))
			
			# Obtener ID del proceso
			process_id = ctypes.c_uint32()
			self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
			
			# Adjuntar a la consola
			self._kernel32.FreeConsole()
			if not self._kernel32.AttachConsole(process_id.value):
				error_code = self._kernel32.GetLastError()
				if error_code == 5:  # Access Denied
					raise Exception(_("Acceso denegado: No se puede leer una consola elevada desde una instancia de NVDA no elevada."))
				raise Exception(_("No se pudo adjuntar a la consola del proceso (Error {}).").format(error_code))
			
			try:
				# Obtener handle del buffer de salida
				hConsole = self._kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
				if hConsole == -1:
					raise Exception(_("No se pudo obtener el manejador de la consola."))
				
				# Leer contenido del buffer
				texto = self._leer_buffer_consola(hConsole)
				
			finally:
				# Siempre liberar la consola
				self._kernel32.FreeConsole()
			
			return texto
			
		finally:
			# Detener beep
			if senal_parar:
				senal_parar.set()
	
	def _obtener_hwnd_consola(self, objeto_ventana: Any) -> int:
		"""Obtiene el handle de la ventana de consola.
		
		Args:
			objeto_ventana: Objeto NVDA de la ventana.
		
		Returns:
			Handle de la ventana o 0 si no se encuentra.
		"""
		try:
			# Obtener título de la ventana
			hwnd = objeto_ventana.windowHandle
			longitud = self._user32.GetWindowTextLengthW(hwnd) + 1
			buffer_titulo = ctypes.create_unicode_buffer(longitud)
			self._user32.GetWindowTextW(hwnd, buffer_titulo, longitud)
			
			# Buscar ventana por título
			hwnd_consola = self._user32.FindWindowW(None, buffer_titulo.value)
			return hwnd_consola
			
		except Exception as e:
			log.error(f"consoleLog: Error al obtener handle de consola: {e}")
			return 0
	
	def _leer_buffer_consola(self, hConsole: int) -> str:
		"""Lee el buffer de la consola.
		
		Args:
			hConsole: Handle del buffer de consola.
		
		Returns:
			Texto del buffer.
		"""
		# Obtener información del buffer
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		self._kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))
		
		# Configurar parámetros de lectura
		buffer_size = COORD(csbi.dwSize.X, csbi.dwSize.Y)
		buffer_coord = COORD(0, 0)
		rect = SMALL_RECT(0, 0, csbi.dwSize.X - 1, csbi.dwSize.Y - 1)
		
		# Crear buffer para los datos
		char_info_buffer = (CHAR_INFO * (buffer_size.X * buffer_size.Y))()
		
		# Leer contenido
		self._kernel32.ReadConsoleOutputW(
			hConsole,
			char_info_buffer,
			buffer_size,
			buffer_coord,
			ctypes.byref(rect)
		)
		
		# Extraer texto
		lineas = []
		for y in range(csbi.dwSize.Y):
			linea = "".join([
				char_info_buffer[x + y * buffer_size.X].Char
				for x in range(buffer_size.X)
				if char_info_buffer[x + y * buffer_size.X].Char not in [None, '\x00']
			])
			lineas.append(linea.rstrip())
		
		texto = "\n".join(lineas)
		
		# Eliminar líneas en blanco al final
		texto = re.sub(r'\n\s*\Z', '', texto)
		
		return texto
	
	def _emitir_beep_progreso(self, senal_parar: Optional[threading.Event]):
		"""Emite beeps mientras se procesa la lectura.
		
		Args:
			senal_parar: Evento para detener los beeps.
		"""
		while senal_parar is None or not senal_parar.is_set():
			winsound.Beep(1000, 100)
			wx.MilliSleep(1000)
			
			if senal_parar and senal_parar.is_set():
				break
	
	def leer_buffer_visible(self, hConsole: int) -> List[str]:
		"""Lee solo las líneas visibles del buffer.
		
		Args:
			hConsole: Handle del buffer de consola.
		
		Returns:
			Lista de líneas visibles.
		"""
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		self._kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))
		
		linea_superior = csbi.srWindow.Top
		cantidad_lineas = (csbi.srWindow.Bottom - linea_superior) + 1
		longitud_linea = csbi.dwSize.X
		
		# Crear buffer para lectura
		buffer = ctypes.create_unicode_buffer(cantidad_lineas * longitud_linea)
		caracteres_leidos = ctypes.c_ulong()
		
		self._kernel32.ReadConsoleOutputCharacterW(
			hConsole,
			buffer,
			cantidad_lineas * longitud_linea,
			COORD(0, linea_superior),
			ctypes.byref(caracteres_leidos)
		)
		
		texto = buffer.value
		lineas = [texto[x:x + longitud_linea].rstrip() 
				  for x in range(0, len(texto), longitud_linea)]
		
		return lineas
	
	def obtener_posicion_cursor(self, hConsole: int) -> tuple:
		"""Obtiene la posición actual del cursor en la consola.
		
		Args:
			hConsole: Handle del buffer de consola.
		
		Returns:
			Tupla (x, y) con la posición del cursor.
		"""
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		self._kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))
		return (csbi.dwCursorPosition.X, csbi.dwCursorPosition.Y)
	
	def obtener_tamano_buffer(self, hConsole: int) -> tuple:
		"""Obtiene el tamaño del buffer de la consola.
		
		Args:
			hConsole: Handle del buffer de consola.
		
		Returns:
			Tupla (ancho, alto) del buffer.
		"""
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		self._kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))
		return (csbi.dwSize.X, csbi.dwSize.Y)
