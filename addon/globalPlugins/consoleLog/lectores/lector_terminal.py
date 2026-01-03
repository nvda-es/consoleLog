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
		"""Lee el contenido usando UI Automation con filtrado por visibilidad.
		
		Garantiza capturar la pestaña activa y evita repeticiones en NVDA.
		"""
		elemento_consola = None
		patron = None
		
		# NUNCA llamar a initialize ni terminate aquí para no corromper el motor de NVDA
		handler = getattr(UIAHandler, "handler", None)
		if not handler or not handler.clientObject:
			raise Exception(_("El sistema UI Automation de NVDA no está disponible."))
		
		client = handler.clientObject
		
		try:
			# 1. Prioridad: Intentar por foco (ideal para la primera vez)
			try:
				el = client.GetFocusedElement()
				if el:
					p = el.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
					if p:
						patron = p
						elemento_consola = el
			except:
				pass
			
			# 2. Estrategia para F5/Refresco: Buscar el control visible dentro del HWND
			if not patron:
				hwnd = getattr(objeto_ventana, 'windowHandle', 0)
				if hwnd:
					try:
						root = client.ElementFromHandle(hwnd)
						# Buscar todos los descendientes que soporten texto
						cond_texto = client.CreatePropertyCondition(UIAHandler.UIA_IsTextPatternAvailablePropertyId, True)
						elementos = root.FindAll(UIAHandler.TreeScope_Descendants, cond_texto)
						
						if elementos and elementos.Length > 0:
							mejor_el = None
							
							for i in range(elementos.Length):
								try:
									el_temp = elementos.GetElement(i)
									# FILTRO CLAVE: En Windows Terminal, las pestañas inactivas están "Offscreen"
									# La pestaña activa es la única que tiene IsOffscreen como False.
									if el_temp.CurrentIsOffscreen:
										continue
										
									p_temp = el_temp.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
									if p_temp:
										patron = p_temp
										mejor_el = el_temp
										break # Encontrado el control visible activo
								except:
									continue
							
							if mejor_el:
								elemento_consola = mejor_el
					except Exception as e_hwnd:
						log.debug(f"consoleLog: Falló búsqueda por HWND: {e_hwnd}")
			
			if not patron:
				# Si el filtro de visibilidad fue demasiado estricto (ventanas minimizadas), 
				# intentar capturar el primer elemento con texto que encontremos
				if hwnd:
					try:
						elemento_consola = root.FindFirst(UIAHandler.TreeScope_Descendants, cond_texto)
						if elemento_consola:
							patron = elemento_consola.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
					except: pass

			if not patron:
				raise Exception(_("No se pudo identificar el área de texto activa."))
			
			# Obtener texto actualizado del patrón
			patron_texto = patron.QueryInterface(UIAHandler.IUIAutomationTextPattern)
			rango = patron_texto.DocumentRange
			return self._limpiar_texto(rango.GetText(-1) or "")
			
		except Exception as e:
			log.error(f"consoleLog: Error en lectura UIA: {e}")
			raise Exception(_("Error al leer el terminal: {}").format(str(e)))
			
		finally:
			# Limpieza de referencias COM sin terminate
			rango = None
			patron_texto = None
			patron = None
			elemento_consola = None
	
	def _limpiar_texto(self, texto: str) -> str:
		"""Limpia el texto extraído conservando la estructura interna.
		
		Args:
			texto: Texto a limpiar.
		
		Returns:
			Texto limpio.
		"""
		if not texto:
			return ""
		
		# Dividir en líneas
		lineas = texto.splitlines()
		
		# Quitar espacios a la derecha pero mantener líneas vacías intermedias
		# (Importante para que la estructura visual coincida con la consola real)
		lineas_limpias = [linea.rstrip() for linea in lineas]
		
		# Eliminar solo las líneas vacías que queden al final del todo
		while lineas_limpias and not lineas_limpias[-1].strip():
			lineas_limpias.pop()
			
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
		elemento = None
		patron = None
		patron_texto = None
		rangos = None
		rango = None
		
		try:
			UIAHandler.initialize()
			
			elemento = UIAHandler.handler.clientObject.GetFocusedElement()
			if not elemento:
				return ""
				
			patron = elemento.GetCurrentPattern(UIAHandler.UIA_TextPatternId)
			patron_texto = patron.QueryInterface(UIAHandler.IUIAutomationTextPattern)
			
			# Obtener selección o caret
			rangos = patron_texto.GetSelection()
			
			if rangos and rangos.Length > 0:
				rango = rangos.GetElement(0)
				rango.ExpandToEnclosingUnit(UIAHandler.UIA.TextUnit_Line)
				return (rango.GetText(-1) or "").strip()
			
			return ""
			
		except Exception as e:
			log.error(f"consoleLog: Error al leer línea actual: {e}")
			return ""
			
		finally:
			# Liberar objetos
			rango = None
			rangos = None
			patron_texto = None
			patron = None
			elemento = None
	
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
		
		elemento = None
		patron = None
		
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
			# Liberar objetos
			patron = None
			elemento = None
		
		return info
