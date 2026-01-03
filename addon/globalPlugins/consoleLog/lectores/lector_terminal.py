# -*- coding: utf-8 -*-
# consoleLog - Lector de Windows Terminal
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Lector de Windows Terminal (consolas modernas).

Utiliza UI Automation para leer el contenido de Windows Terminal
y otras consolas modernas que no usan el buffer clásico.
"""

import threading
import winsound
import wx
from typing import Optional, Any
from logHandler import log
import UIAHandler

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


class LectorWindowsTerminal:
	"""Lector para Windows Terminal y consolas modernas.
	
	Utiliza UI Automation para acceder al contenido de texto
	de las consolas modernas.
	"""
	
	def __init__(self):
		"""Inicializa el lector de Windows Terminal."""
		self._uia_inicializado = False
	
	def leer(
		self,
		objeto_ventana: Any,
		senal_parar: Optional[threading.Event] = None,
		emitir_beep: bool = True
	) -> str:
		"""Lee el contenido de Windows Terminal.
		
		Args:
			objeto_ventana: Objeto NVDA de la ventana de terminal.
			senal_parar: Evento para detener la lectura.
			emitir_beep: Si se debe emitir un beep durante la lectura.
		
		Returns:
			Texto extraído del terminal.
		
		Raises:
			Exception: Si no se puede leer el terminal.
		"""
		hilo_beep = None
		
		try:
			# Iniciar beep de progreso
			if emitir_beep:
				hilo_beep = threading.Thread(
					target=self._emitir_beep_progreso,
					args=(senal_parar,),
					daemon=True
				)
				hilo_beep.start()
			
			# Leer usando UI Automation
			texto = self._leer_via_uia(objeto_ventana)
			return texto
			
		finally:
			# Detener beep
			if senal_parar:
				senal_parar.set()
	
	def _leer_via_uia(self, objeto_ventana: Any) -> str:
		"""Lee el contenido usando UI Automation.
		
		Args:
			objeto_ventana: Objeto NVDA de la ventana.
		
		Returns:
			Texto del terminal.
		
		Raises:
			Exception: Si hay error al leer.
		"""
		try:
			# Inicializar UIA si es necesario
			UIAHandler.initialize()
			self._uia_inicializado = True
			
			# Intentar obtener el elemento desde el foco primero, ya que suele ser el control de texto
			elemento_consola = UIAHandler.handler.clientObject.GetFocusedElement()
			patron = None
			
			if elemento_consola:
				try:
					patron = elemento_consola.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
				except Exception:
					patron = None
			
			# Si el foco no funcionó o no tiene patrón, intentar desde el handle de la ventana
			if not patron:
				hwnd = getattr(objeto_ventana, 'windowHandle', 0)
				if hwnd:
					elemento_ventana = UIAHandler.handler.clientObject.ElementFromHandle(hwnd)
					try:
						# Intentar patrón directo en la ventana
						patron = elemento_ventana.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
						elemento_consola = elemento_ventana
					except Exception:
						# Windows Terminal: Buscar el descendiente que soporte el patrón de texto
						try:
							# Intentar obtener constantes de forma segura (Scope: Descendants=4, Prop: IsTextPatternAvailable=30030)
							scope = getattr(UIAHandler, 'TreeScope_Descendants', 4)
							prop_id = getattr(UIAHandler, 'UIA_IsTextPatternAvailablePropertyId', 30030)
							
							condicion = UIAHandler.handler.clientObject.CreatePropertyCondition(prop_id, True)
							elemento_consola = elemento_ventana.FindFirst(scope, condicion)
							if elemento_consola:
								patron = elemento_consola.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
						except Exception as e_search:
							log.debug(f"consoleLog: Error en búsqueda profunda de UIA: {e_search}")
			
			if not patron:
				raise Exception(_("El terminal no soporta el patrón de texto o no se pudo encontrar el control de lectura adecuado."))
			
			patron_texto = patron.QueryInterface(UIAHandler.IUIAutomationTextPattern)
			
			# Obtener rango de documento completo
			rango_texto = patron_texto.DocumentRange
			
			# Obtener texto (-1 para obtener todo el texto)
			texto_terminal = rango_texto.GetText(-1)
			
			# Limpiar el texto: eliminar líneas vacías excesivas
			texto_limpio = self._limpiar_texto(texto_terminal)
			
			return texto_limpio
			
		except Exception as e:
			log.error(f"consoleLog: Error al leer Windows Terminal: {e}")
			raise Exception(_("Error al leer el terminal: {}").format(str(e)))
			
		finally:
			# Terminar UIA
			if self._uia_inicializado:
				try:
					UIAHandler.terminate()
				except Exception:
					pass
				self._uia_inicializado = False
	
	def _limpiar_texto(self, texto: str) -> str:
		"""Limpia el texto extraído del terminal.
		
		Args:
			texto: Texto a limpiar.
		
		Returns:
			Texto limpio.
		"""
		if not texto:
			return ""
		
		# Dividir en líneas y limpiar cada una
		lineas = texto.splitlines()
		
		# Eliminar espacios al final de cada línea y filtrar líneas completamente vacías
		lineas_limpias = [linea.rstrip() for linea in lineas if linea.strip()]
		
		return '\n'.join(lineas_limpias)
	
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
	
	def leer_linea_actual(self) -> str:
		"""Lee solo la línea actual donde está el cursor.
		
		Returns:
			Texto de la línea actual.
		"""
		try:
			UIAHandler.initialize()
			
			elemento = UIAHandler.handler.clientObject.GetFocusedElement()
			patron = elemento.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
			patron_texto = patron.QueryInterface(UIAHandler.IUIAutomationTextPattern)
			
			# Obtener selección o caret
			rangos = patron_texto.GetSelection()
			
			if rangos.Length > 0:
				rango = rangos.GetElement(0)
				rango.ExpandToEnclosingUnit(UIAHandler.UIA.TextUnit_Line)
				return rango.GetText(-1).strip()
			
			return ""
			
		except Exception as e:
			log.error(f"consoleLog: Error al leer línea actual: {e}")
			return ""
			
		finally:
			try:
				UIAHandler.terminate()
			except Exception:
				pass
	
	def obtener_informacion_terminal(self) -> dict:
		"""Obtiene información sobre el terminal.
		
		Returns:
			Diccionario con información del terminal.
		"""
		info = {
			'nombre': '',
			'clase': '',
			'patron_texto_disponible': False
		}
		
		try:
			UIAHandler.initialize()
			
			elemento = UIAHandler.handler.clientObject.GetFocusedElement()
			
			if elemento:
				info['nombre'] = elemento.CurrentName or ''
				info['clase'] = elemento.CurrentClassName or ''
				
				try:
					patron = elemento.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
					info['patron_texto_disponible'] = patron is not None
				except Exception:
					info['patron_texto_disponible'] = False
			
		except Exception as e:
			log.error(f"consoleLog: Error al obtener información del terminal: {e}")
			
		finally:
			try:
				UIAHandler.terminate()
			except Exception:
				pass
		
		return info
