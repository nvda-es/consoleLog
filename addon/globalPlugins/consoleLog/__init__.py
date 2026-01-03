# -*- coding: utf-8 -*-
# consoleLog - Visor para las consolas de Windows
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
#
# Complemento completamente reescrito con arquitectura modular y sistema de plugins.

"""
consoleLog - Complemento para visualizar y gestionar consolas de Windows.

Este módulo proporciona:
- Visor de consola con funcionalidades avanzadas
- Lanzador de consolas con soporte para múltiples terminales
- Sistema de plugins extensible
- Extracción mejorada del contenido de consolas
"""

import globalPluginHandler
import addonHandler
import api
import globalVars
from scriptHandler import script
from logHandler import log
import wx

# Inicializar traducción
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from .nucleo.configuracion import Configuracion
from .nucleo.gestor_plugins import GestorPlugins
from .lectores.gestor_lectores import GestorLectores
from .lanzador.gestor_lanzador import GestorLanzador
from .interfaz.visor_consola import VisorConsola
from .interfaz.lanzador_dialogo import LanzadorDialogo
from .utilidades.mensajes import Mensajes


def deshabilitarEnModoSeguro(claseDecorada):
	"""Decorador que deshabilita una clase de complemento global en modo seguro.
	
	Args:
		claseDecorada: La clase a decorar.
	
	Returns:
		La clase original o GlobalPlugin base dependiendo del modo seguro.
	"""
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return claseDecorada


@deshabilitarEnModoSeguro
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	"""Plugin global principal de consoleLog.
	
	Proporciona funcionalidades para:
	- Visualizar contenido de consolas de Windows
	- Lanzar diferentes tipos de consolas
	- Gestionar plugins extensibles
	"""
	
	# TRANSLATORS: Nombre de la categoría en gestos de entrada
	scriptCategory = _("Visor de consola")
	
	def __init__(self, *args, **kwargs):
		"""Inicializa el plugin global y todos sus componentes."""
		super().__init__(*args, **kwargs)
		
		# Estado del plugin
		self._proceso_en_marcha = False
		self._dialogo_visor_abierto = False
		self._dialogo_lanzador_abierto = False
		
		# Inicializar componentes
		self._configuracion = Configuracion()
		self._gestor_plugins = GestorPlugins(self._configuracion)
		self._gestor_lectores = GestorLectores()
		self._gestor_lanzador = GestorLanzador()
		self._mensajes = Mensajes()
		
		# Cargar plugins
		self._gestor_plugins.cargar_plugins()
		
		log.debug("consoleLog: Plugin inicializado correctamente")
	
	def terminate(self):
		"""Libera recursos al terminar el plugin."""
		try:
			self._gestor_plugins.descargar_plugins()
			log.debug("consoleLog: Plugin terminado correctamente")
		except Exception as e:
			log.error(f"consoleLog: Error al terminar el plugin: {e}")
	
	@property
	def proceso_en_marcha(self) -> bool:
		"""Indica si hay un proceso de lectura en marcha."""
		return self._proceso_en_marcha
	
	@proceso_en_marcha.setter
	def proceso_en_marcha(self, valor: bool):
		"""Establece el estado del proceso de lectura."""
		self._proceso_en_marcha = valor
	
	@property
	def dialogo_visor_abierto(self) -> bool:
		"""Indica si el diálogo del visor está abierto."""
		return self._dialogo_visor_abierto
	
	@dialogo_visor_abierto.setter
	def dialogo_visor_abierto(self, valor: bool):
		"""Establece el estado del diálogo del visor."""
		self._dialogo_visor_abierto = valor
	
	@property
	def dialogo_lanzador_abierto(self) -> bool:
		"""Indica si el diálogo del lanzador está abierto."""
		return self._dialogo_lanzador_abierto
	
	@dialogo_lanzador_abierto.setter
	def dialogo_lanzador_abierto(self, valor: bool):
		"""Establece el estado del diálogo del lanzador."""
		self._dialogo_lanzador_abierto = valor
	
	def _es_ventana_consola(self, objeto=None) -> bool:
		"""Verifica si la ventana enfocada es una consola.
		
		Args:
			objeto: Objeto NVDA a verificar. Si es None, usa el objeto en primer plano.
		
		Returns:
			True si es una ventana de consola, False en caso contrario.
		"""
		if objeto is None:
			objeto = api.getForegroundObject()
		
		if not objeto:
			return False
		
		nombre_clase = getattr(objeto, 'windowClassName', '')
		appModule = getattr(objeto, 'appModule', None)
		nombre_producto = getattr(appModule, 'productName', '') if appModule else ''
		
		# Consolas clásicas
		if nombre_clase.startswith("ConsoleWindowClass"):
			return True
		
		# Windows Terminal
		if nombre_clase == "CASCADIA_HOSTING_WINDOW_CLASS":
			return True
		
		if nombre_producto in ["Microsoft.WindowsTerminal"]:
			return True
		
		return False
	
	def _obtener_tipo_consola(self, objeto=None) -> str:
		"""Determina el tipo de consola de la ventana enfocada.
		
		Args:
			objeto: Objeto NVDA a verificar.
		
		Returns:
			Tipo de consola: 'clasica', 'terminal' o 'desconocida'.
		"""
		if objeto is None:
			objeto = api.getForegroundObject()
		
		if not objeto:
			return 'desconocida'
		
		appModule = getattr(objeto, 'appModule', None)
		nombre_producto = getattr(appModule, 'productName', '') if appModule else ''
		
		if nombre_producto in ["Microsoft.WindowsTerminal"]:
			return 'terminal'
		
		nombre_clase = getattr(objeto, 'windowClassName', '')
		if nombre_clase.startswith("ConsoleWindowClass"):
			return 'clasica'
		
		if nombre_clase == "CASCADIA_HOSTING_WINDOW_CLASS":
			return 'terminal'
		
		return 'desconocida'
	
	@script(
		gesture=None,
		# TRANSLATORS: Descripción para el diálogo de gestos
		description=_("Muestra el visor de consola"),
	)
	def script_mostrarVisorConsola(self, gesture):
		"""Muestra el visor de consola para leer el contenido de la consola enfocada.
		
		Args:
			gesture: El gesto asociado con este script.
		"""
		if self._proceso_en_marcha:
			self._mensajes.anunciar(_("Por favor, espere. Hay otro proceso en marcha."))
			return
		
		if self._dialogo_visor_abierto:
			self._mensajes.anunciar(_("Por favor, cierre el diálogo actual antes de iniciar uno nuevo."))
			return
		
		if not self._es_ventana_consola():
			self._mensajes.anunciar(_("Esta no es una ventana de consola."))
			return
		
		self._proceso_en_marcha = True
		objeto = api.getForegroundObject()
		tipo_consola = self._obtener_tipo_consola(objeto)
		
		# Iniciar lectura asíncrona
		self._gestor_lectores.leer_consola(
			tipo_consola=tipo_consola,
			objeto_ventana=objeto,
			callback_exito=self._mostrar_visor,
			callback_error=self._error_lectura,
			callback_progreso=self._progreso_lectura
		)
	
	def _mostrar_visor(self, texto: str):
		"""Callback para mostrar el visor cuando la lectura es exitosa.
		
		Args:
			texto: Contenido de la consola.
		"""
		self._proceso_en_marcha = False
		
		if not texto or not texto.strip():
			self._mensajes.anunciar(_("No se encontró texto en la consola"))
			return
		
		# Mostrar visor
		wx.CallAfter(self._abrir_visor, texto)
	
	def _abrir_visor(self, texto: str):
		"""Abre el diálogo del visor de consola.
		
		Args:
			texto: Contenido a mostrar.
		"""
		import gui
		visor = VisorConsola(gui.mainFrame, self, texto)
		visor.Show()
		visor.Maximize()
		visor.Raise()
	
	@script(
		gesture=None,
		# TRANSLATORS: Descripción para el diálogo de gestos
		description=_("Copia el contenido completo de la consola al portapapeles (Rápido)"),
	)
	def script_copiarSalidaRapida(self, gesture):
		"""Copia la salida de la consola al portapapeles sin abrir el visor."""
		if self._proceso_en_marcha:
			return
			
		if not self._es_ventana_consola():
			self._mensajes.anunciar(_("Esta no es una ventana de consola."))
			return
			
		self._proceso_en_marcha = True
		objeto = api.getForegroundObject()
		tipo_consola = self._obtener_tipo_consola(objeto)
		
		def _copiar(texto):
			self._proceso_en_marcha = False
			plugin = self._gestor_plugins.obtener_plugin('copiar_salida')
			if plugin:
				if plugin.ejecutar(texto=texto):
					self._mensajes.anunciar(_("Contenido de consola copiado"))
				else:
					self._mensajes.anunciar(_("Error al copiar contenido"))
			else:
				# Fallback
				import api
				if api.copyToClip(texto):
					self._mensajes.anunciar(_("Contenido de consola copiado"))
					winsound.Beep(1200, 100)
		
		self._gestor_lectores.leer_consola(
			tipo_consola=tipo_consola,
			objeto_ventana=objeto,
			callback_exito=_copiar,
			callback_error=self._error_lectura
		)

	def _error_lectura(self, error: str):
		"""Callback para manejar errores de lectura.
		
		Args:
			error: Mensaje de error.
		"""
		self._proceso_en_marcha = False
		self._mensajes.anunciar(error)

	def _progreso_lectura(self):
		"""Callback para indicar progreso de lectura."""
		# Se emite un beep para indicar que se está procesando
		pass
	
	@script(
		gesture=None,
		# TRANSLATORS: Descripción para el diálogo de gestos
		description=_("Realiza un clic derecho en la ventana de consola enfocada para copiar el contenido del portapapeles"),
	)
	def script_clicDerechoConsola(self, gesture):
		"""Realiza un clic derecho en la consola para pegar contenido.
		
		Args:
			gesture: El gesto asociado con este script.
		"""
		if not self._es_ventana_consola():
			self._mensajes.anunciar(_("La ventana enfocada no es una consola."))
			return
		
		objeto = api.getForegroundObject()
		tipo_consola = self._obtener_tipo_consola(objeto)
		
		# Ejecutar plugin de clic derecho si está disponible
		plugin_clic = self._gestor_plugins.obtener_plugin('clic_derecho')
		if plugin_clic:
			plugin_clic.ejecutar(tipo_consola=tipo_consola, objeto=objeto)
		else:
			# Fallback a funcionalidad básica
			from .plugins.clic_derecho import PluginClicDerecho
			plugin = PluginClicDerecho()
			plugin.ejecutar(tipo_consola=tipo_consola, objeto=objeto)
	
	@script(
		gesture=None,
		# TRANSLATORS: Descripción para el diálogo de gestos
		description=_("Abre el lanzador de consolas de Windows"),
	)
	def script_abrirLanzador(self, gesture):
		"""Abre el lanzador de consolas de Windows.
		
		Args:
			gesture: El gesto asociado con este script.
		"""
		wx.CallAfter(self._abrir_lanzador)
	
	def _abrir_lanzador(self):
		"""Abre el diálogo del lanzador de consolas."""
		if self._dialogo_lanzador_abierto:
			self._mensajes.anunciar(_("Ya hay una instancia del lanzador de consolas abierta."))
			return
		
		# Obtener directorio desde explorador
		directorio = self._gestor_lanzador.obtener_directorio_actual()
		
		if not directorio:
			self._mensajes.anunciar(_("No se encontró una selección válida."))
			return
		
		import gui
		self._dialogo_lanzador_abierto = True
		
		gui.mainFrame.prePopup()
		dialogo = LanzadorDialogo(None, self, directorio)
		dialogo.ShowModal()
		dialogo.Destroy()
		gui.mainFrame.postPopup()
		
		self._dialogo_lanzador_abierto = False
