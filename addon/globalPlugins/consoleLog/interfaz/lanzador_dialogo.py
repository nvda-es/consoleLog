# -*- coding: utf-8 -*-
# consoleLog - Diálogo del Lanzador de Consolas
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Diálogo del lanzador de consolas.

Proporciona una interfaz para seleccionar y abrir diferentes
tipos de consolas en el directorio actual.
"""

import wx
from typing import List, Optional
from logHandler import log

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


class OpcionConsola:
	"""Representa una opción de consola en el lanzador."""
	
	def __init__(
		self,
		nombre: str,
		tipo: str,
		como_admin: bool = False,
		script_vs: Optional[str] = None
	):
		"""Inicializa una opción de consola.
		
		Args:
			nombre: Nombre a mostrar al usuario.
			tipo: Tipo de consola (cmd, powershell, wt, git-bash, vs-32, vs-64).
			como_admin: Si debe abrirse como administrador.
			script_vs: Ruta al script de Visual Studio (si aplica).
		"""
		self.nombre = nombre
		self.tipo = tipo
		self.como_admin = como_admin
		self.script_vs = script_vs


class LanzadorDialogo(wx.Dialog):
	"""Diálogo del lanzador de consolas.
	
	Permite al usuario seleccionar y abrir diferentes tipos de consolas
	en el directorio especificado.
	"""
	
	def __init__(self, parent, plugin, directorio: str):
		"""Inicializa el diálogo del lanzador.
		
		Args:
			parent: Ventana padre.
			plugin: Referencia al plugin principal.
			directorio: Directorio donde abrir las consolas.
		"""
		# TRANSLATORS: Título del diálogo del lanzador
		super().__init__(
			parent,
			title=_("Lanzador de Consolas"),
			style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
		)
		
		self._plugin = plugin
		self._directorio = directorio
		self._gestor_lanzador = plugin._gestor_lanzador
		self._opciones: List[OpcionConsola] = []
		
		self._crear_opciones()
		self._crear_interfaz()
		self._configurar_eventos()
	
	def _crear_opciones(self):
		"""Crea la lista de opciones disponibles."""
		consolas = self._gestor_lanzador.obtener_consolas_disponibles()
		
		for consola in consolas:
			if consola.identificador == 'cmd':
				# TRANSLATORS: Opción de CMD
				self._opciones.append(OpcionConsola(
					_("Abrir CMD aquí"),
					'cmd',
					como_admin=False
				))
				# TRANSLATORS: Opción de CMD como admin
				self._opciones.append(OpcionConsola(
					_("Abrir CMD como Administrador"),
					'cmd',
					como_admin=True
				))
			
			elif consola.identificador == 'powershell':
				# TRANSLATORS: Opción de PowerShell
				self._opciones.append(OpcionConsola(
					_("Abrir PowerShell aquí"),
					'powershell',
					como_admin=False
				))
				# TRANSLATORS: Opción de PowerShell como admin
				self._opciones.append(OpcionConsola(
					_("Abrir PowerShell como Administrador"),
					'powershell',
					como_admin=True
				))
			
			elif consola.identificador == 'wt':
				# TRANSLATORS: Opción de Windows Terminal
				self._opciones.append(OpcionConsola(
					_("Abrir Windows Terminal aquí"),
					'wt',
					como_admin=False
				))
				# TRANSLATORS: Opción de Windows Terminal como admin
				self._opciones.append(OpcionConsola(
					_("Abrir Windows Terminal como Administrador"),
					'wt',
					como_admin=True
				))
			
			elif consola.identificador == 'git-bash':
				# TRANSLATORS: Opción de Git Bash
				self._opciones.append(OpcionConsola(
					_("Abrir Git Bash aquí"),
					'git-bash',
					como_admin=False
				))
				# TRANSLATORS: Opción de Git Bash como admin
				self._opciones.append(OpcionConsola(
					_("Abrir Git Bash como Administrador"),
					'git-bash',
					como_admin=True
				))
			
			elif consola.identificador == 'vs-32':
				# TRANSLATORS: Opción de Visual Studio 32-bit
				self._opciones.append(OpcionConsola(
					_("Abrir Visual Studio Developer (32-bit)"),
					'vs-32',
					como_admin=False,
					script_vs=consola.ruta
				))
				# TRANSLATORS: Opción de Visual Studio 32-bit como admin
				self._opciones.append(OpcionConsola(
					_("Abrir Visual Studio Developer (32-bit) como Administrador"),
					'vs-32',
					como_admin=True,
					script_vs=consola.ruta
				))
			
			elif consola.identificador == 'vs-64':
				# TRANSLATORS: Opción de Visual Studio 64-bit
				self._opciones.append(OpcionConsola(
					_("Abrir Visual Studio Developer (64-bit)"),
					'vs-64',
					como_admin=False,
					script_vs=consola.ruta
				))
				# TRANSLATORS: Opción de Visual Studio 64-bit como admin
				self._opciones.append(OpcionConsola(
					_("Abrir Visual Studio Developer (64-bit) como Administrador"),
					'vs-64',
					como_admin=True,
					script_vs=consola.ruta
				))
	
	def _crear_interfaz(self):
		"""Crea los elementos de la interfaz."""
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Etiqueta del directorio
		# TRANSLATORS: Etiqueta que muestra el directorio actual
		etiqueta_dir = wx.StaticText(
			self,
			label=_("Directorio: {}").format(self._directorio)
		)
		sizer.Add(etiqueta_dir, flag=wx.ALL | wx.EXPAND, border=10)
		
		# Lista de opciones
		# TRANSLATORS: Etiqueta de la lista de consolas
		etiqueta_lista = wx.StaticText(self, label=_("Seleccione una consola:"))
		sizer.Add(etiqueta_lista, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=10)
		
		nombres_opciones = [opcion.nombre for opcion in self._opciones]
		
		self._lista = wx.ListBox(
			self,
			choices=nombres_opciones,
			style=wx.LB_SINGLE
		)
		
		if nombres_opciones:
			# Aplicar selección guardada si está habilitado
			config_lanzador = self._plugin._configuracion.lanzador
			seleccion = 0
			if config_lanzador.recordar_ultima_opcion:
				seleccion = config_lanzador.ultima_opcion
				if seleccion >= len(self._opciones):
					seleccion = 0
			self._lista.SetSelection(seleccion)
		
		sizer.Add(self._lista, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
		
		# Panel de botones
		sizer_botones = wx.BoxSizer(wx.HORIZONTAL)
		
		# TRANSLATORS: Botón para abrir la consola
		self._boton_abrir = wx.Button(self, wx.ID_OK, _("&Abrir"))
		self._boton_abrir.SetDefault()
		sizer_botones.Add(self._boton_abrir, flag=wx.RIGHT, border=5)
		
		# TRANSLATORS: Botón para cancelar
		self._boton_cancelar = wx.Button(self, wx.ID_CANCEL, _("&Cancelar"))
		sizer_botones.Add(self._boton_cancelar)
		
		sizer.Add(sizer_botones, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
		
		self.SetSizer(sizer)
		self.SetSize(400, 350)
		self.Centre()
		
		self._lista.SetFocus()
	
	def _configurar_eventos(self):
		"""Configura los manejadores de eventos."""
		self.Bind(wx.EVT_BUTTON, self._al_abrir, self._boton_abrir)
		self.Bind(wx.EVT_BUTTON, self._al_cancelar, self._boton_cancelar)
		self._lista.Bind(wx.EVT_LISTBOX_DCLICK, self._al_abrir)
		self.Bind(wx.EVT_CHAR_HOOK, self._al_tecla)
	
	def _al_tecla(self, evento):
		"""Maneja eventos de teclado.
		
		Args:
			evento: Evento de teclado.
		"""
		tecla = evento.GetKeyCode()
		
		if tecla == wx.WXK_RETURN or tecla == wx.WXK_NUMPAD_ENTER:
			self._ejecutar_seleccion()
		elif tecla == wx.WXK_ESCAPE:
			self.EndModal(wx.ID_CANCEL)
		else:
			evento.Skip()
	
	def _al_abrir(self, evento):
		"""Maneja el clic en el botón Abrir.
		
		Args:
			evento: Evento de botón.
		"""
		self._ejecutar_seleccion()
	
	def _al_cancelar(self, evento):
		"""Maneja el clic en el botón Cancelar.
		
		Args:
			evento: Evento de botón.
		"""
		self.EndModal(wx.ID_CANCEL)
	
	def _ejecutar_seleccion(self):
		"""Ejecuta la opción seleccionada."""
		indice = self._lista.GetSelection()
		
		if indice == wx.NOT_FOUND:
			return
		
		opcion = self._opciones[indice]
		
		# Guardar selección si está habilitado
		config_gestor = self._plugin._configuracion
		if config_gestor.lanzador.recordar_ultima_opcion:
			config_gestor.lanzador.ultima_opcion = indice
			config_gestor.guardar_configuracion()
		
		try:
			self._gestor_lanzador.abrir_consola(
				tipo=opcion.tipo,
				directorio=self._directorio,
				como_admin=opcion.como_admin,
				ruta_script=opcion.script_vs
			)
			log.debug(f"consoleLog: Abriendo {opcion.tipo} en {self._directorio}")
		except Exception as e:
			wx.MessageBox(
				# TRANSLATORS: Mensaje de error al abrir consola
				_("Error al abrir la consola: {}").format(str(e)),
				_("Error"),
				wx.OK | wx.ICON_ERROR,
				self
			)
			return
		
		self.EndModal(wx.ID_OK)
