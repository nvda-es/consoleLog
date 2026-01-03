# -*- coding: utf-8 -*-
# consoleLog - Visor de Consola Pro
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

import wx
import winsound
import os
from typing import Optional, List, Dict, Any
from logHandler import log
import api
import gui
from gui.nvdaControls import CustomCheckListBox
import ui

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class AjustesDialog(wx.Dialog):
	"""Diálogo avanzado para configurar todas las opciones del complemento."""
	def __init__(self, parent, config, gestor_plugins):
		super().__init__(parent, title=_("Opciones de Visor de consola"), size=(500, 450))
		self.config = config
		self.gestor_plugins = gestor_plugins
		
		sizer_principal = wx.BoxSizer(wx.VERTICAL)
		notebook = wx.Notebook(self)
		
		# Panel Visual
		p_visual = wx.Panel(notebook)
		s_visual = wx.BoxSizer(wx.VERTICAL)
		
		f_sizer = wx.BoxSizer(wx.HORIZONTAL)
		f_sizer.Add(wx.StaticText(p_visual, label=_("Tamaño de la fuente:")), 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		self.spn_fuente = wx.SpinCtrl(p_visual, value=str(self.config.visor.tamanio_fuente), min=8, max=30)
		f_sizer.Add(self.spn_fuente, 1, wx.ALL | wx.EXPAND, 5)
		s_visual.Add(f_sizer, 0, wx.EXPAND | wx.ALL, 5)
		
		self.chk_mono = wx.CheckBox(p_visual, label=_("Usar fuente monoespaciada (Consolas)"))
		self.chk_mono.SetValue(self.config.visor.fuente_monoespaciada)
		s_visual.Add(self.chk_mono, 0, wx.ALL, 10)
		
		self.chk_tam = wx.CheckBox(p_visual, label=_("Recordar tamaño y posición de la ventana"))
		self.chk_tam.SetValue(self.config.visor.recordar_tamano)
		s_visual.Add(self.chk_tam, 0, wx.ALL, 10)
		
		p_visual.SetSizer(s_visual)
		notebook.AddPage(p_visual, _("Visual"))
		
		# Panel Lanzador
		p_lanzador = wx.Panel(notebook)
		s_lanzador = wx.BoxSizer(wx.VERTICAL)
		
		self.chk_lanz_rec = wx.CheckBox(p_lanzador, label=_("Recordar última consola seleccionada"))
		self.chk_lanz_rec.SetValue(self.config.lanzador.recordar_ultima_opcion)
		s_lanzador.Add(self.chk_lanz_rec, 0, wx.ALL, 10)
		
		self.chk_lanz_todas = wx.CheckBox(p_lanzador, label=_("Mostrar consolas no instaladas en la lista"))
		self.chk_lanz_todas.SetValue(self.config.lanzador.mostrar_consolas_no_disponibles)
		s_lanzador.Add(self.chk_lanz_todas, 0, wx.ALL, 10)
		
		p_lanzador.SetSizer(s_lanzador)
		notebook.AddPage(p_lanzador, _("Lanzador"))
		
		# Panel Plugins
		p_plugins = wx.Panel(notebook)
		s_plugins = wx.BoxSizer(wx.VERTICAL)
		s_plugins.Add(wx.StaticText(p_plugins, label=_("Seleccione los plugins que desea activar:")), 0, wx.ALL, 5)
		
		# Usar el widget compatible con NVDA
		self.lst_plugins = CustomCheckListBox(p_plugins, choices=self.gestor_plugins.listar_plugins_disponibles())
		plugins_cargados = self.gestor_plugins.listar_plugins_cargados()
		for i, nombre in enumerate(self.gestor_plugins.listar_plugins_disponibles()):
			if nombre in plugins_cargados:
				self.lst_plugins.Check(i)
		
		s_plugins.Add(self.lst_plugins, 1, wx.EXPAND | wx.ALL, 5)
		p_plugins.SetSizer(s_plugins)
		notebook.AddPage(p_plugins, _("Plugins"))
		
		sizer_principal.Add(notebook, 1, wx.EXPAND | wx.ALL, 5)
		
		# Botones
		btn_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
		sizer_principal.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
		
		self.SetSizer(sizer_principal)
		self.Centre()
		
		# Poner el foco en el primer control para que no se pierda en el botón OK
		p_visual.SetFocus()

	def obtener_valores(self):
		indices = self.lst_plugins.GetCheckedItems()
		plugins_seleccionados = [self.lst_plugins.GetString(i) for i in indices]
		
		return {
			"visual": {
				"tamanio_fuente": self.spn_fuente.GetValue(),
				"fuente_monoespaciada": self.chk_mono.GetValue(),
				"recordar_tamano": self.chk_tam.GetValue()
			},
			"lanzador": {
				"recordar_ultima_opcion": self.chk_lanz_rec.GetValue(),
				"mostrar_consolas_no_disponibles": self.chk_lanz_todas.GetValue()
			},
			"plugins": plugins_seleccionados
		}

class VisorConsola(wx.Frame):
	"""Visor de consola avanzado con estética premium y soporte nativo para menús."""
	
	def __init__(self, parent, plugin, contenido: str):
		# TRANSLATORS: Título de la ventana del visor
		super(VisorConsola, self).__init__(parent, wx.ID_ANY, _("Visor de consola"))
		
		self._plugin = plugin
		self._plugin.dialogo_visor_abierto = True
		self._contenido = contenido
		self._ultima_busqueda = ""
		
		# Estructura de la interfaz (sin paneles intermedios para no bloquear Alt)
		self._crear_interfaz()
		self._crear_menu()
		self._configurar_eventos()
		
		# Cargar contenido y foco inicial
		self._texto_ctrl.SetValue(self._contenido)
		self._texto_ctrl.SetInsertionPoint(0)
		self._texto_ctrl.SetFocus()
		self._actualizar_barra_estado()

	def _crear_interfaz(self):
		"""Crea la interfaz premium directamente en el Frame."""
		sizer_principal = wx.BoxSizer(wx.VERTICAL)
		
		# Control de texto con estilo RICH para mejor rendimiento
		self._texto_ctrl = wx.TextCtrl(
			self,
			wx.ID_ANY,
			size=(800, 600),
			style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_NOHIDESEL
		)
		
		# Fuente de consola profesional
		fuente = wx.Font(10, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName="Consolas")
		self._texto_ctrl.SetFont(fuente)
		
		sizer_principal.Add(self._texto_ctrl, proportion=1, flag=wx.EXPAND | wx.ALL, border=2)
		
		# Barra de estado nativa
		self._barra_estado = self.CreateStatusBar(3)
		self._barra_estado.SetStatusWidths([150, 150, -1])
		
		self.SetSizer(sizer_principal)
		
		# SECRETO: El Fit debe ir antes del SetMenuBar para que Alt funcione correctamente
		sizer_principal.Fit(self)
		self.Centre()

	def _crear_menu(self):
		"""Crea una barra de menú completa y accesible."""
		barra_menu = wx.MenuBar()
		
		# Menú Archivo
		menu_archivo = wx.Menu()
		item_guardar = menu_archivo.Append(wx.ID_SAVEAS, _("&Guardar como...\tCtrl+S"))
		self.Bind(wx.EVT_MENU, self._al_guardar, item_guardar)
		menu_archivo.AppendSeparator()
		item_opciones = menu_archivo.Append(wx.ID_ANY, _("&Opciones...\tCtrl+P"))
		self.Bind(wx.EVT_MENU, self._al_abrir_opciones, item_opciones)
		menu_archivo.AppendSeparator()
		item_salir = menu_archivo.Append(wx.ID_EXIT, _("&Salir\tAlt+F4"))
		self.Bind(wx.EVT_MENU, self._al_cerrar, item_salir)
		barra_menu.Append(menu_archivo, _("&Archivo"))
		
		# Menú Edición
		menu_edicion = wx.Menu()
		item_copiar = menu_edicion.Append(wx.ID_COPY, _("&Copiar\tCtrl+C"))
		self.Bind(wx.EVT_MENU, self._al_copiar, item_copiar)
		item_seleccionar = menu_edicion.Append(wx.ID_SELECTALL, _("&Seleccionar todo\tCtrl+A"))
		self.Bind(wx.EVT_MENU, self._al_seleccionar_todo, item_seleccionar)
		menu_edicion.AppendSeparator()
		item_buscar = menu_edicion.Append(wx.ID_FIND, _("&Buscar...\tCtrl+F"))
		self.Bind(wx.EVT_MENU, self._al_buscar, item_buscar)
		barra_menu.Append(menu_edicion, _("&Edición"))
		
		# Menú Ver
		menu_ver = wx.Menu()
		item_posicion = menu_ver.Append(wx.ID_ANY, _("&Posición actual\tF1"))
		self.Bind(wx.EVT_MENU, self._al_mostrar_posicion, item_posicion)
		item_ir_linea = menu_ver.Append(wx.ID_ANY, _("&Ir a línea...\tCtrl+G"))
		self.Bind(wx.EVT_MENU, self._al_ir_a_linea, item_ir_linea)
		barra_menu.Append(menu_ver, _("&Ver"))
		
		# Menú Plugins (Dinámico)
		menu_plugins = wx.Menu()
		self._crear_menu_plugins(menu_plugins)
		barra_menu.Append(menu_plugins, _("&Plugins"))
		
		# Menú Ayuda
		menu_ayuda = wx.Menu()
		item_atajos = menu_ayuda.Append(wx.ID_HELP, _("&Atajos de teclado\tF2"))
		self.Bind(wx.EVT_MENU, self._al_mostrar_atajos, item_atajos)
		barra_menu.Append(menu_ayuda, _("A&yuda"))
		
		self.SetMenuBar(barra_menu)

	def _crear_menu_plugins(self, menu: wx.Menu):
		"""Carga los plugins en el menú."""
		try:
			gestor = self._plugin._gestor_plugins
			plugins_cargados = gestor.listar_plugins_cargados()
			self._mapa_plugins = {}
			
			for nombre in plugins_cargados:
				if nombre == 'clic_derecho': continue
				plugin_inst = gestor.obtener_plugin(nombre)
				if not plugin_inst: continue
				meta = plugin_inst.obtener_metadatos()
				if meta:
					item = menu.Append(wx.ID_ANY, meta.nombre)
					self._mapa_plugins[item.GetId()] = nombre
					self.Bind(wx.EVT_MENU, self._al_ejecutar_plugin, item)
			
			if not self._mapa_plugins:
				item_vacio = menu.Append(wx.ID_ANY, _("No hay plugins habilitados"))
				item_vacio.Enable(False)
		except Exception as e:
			log.error(f"consoleLog: Error en menú de plugins: {e}")

	def _configurar_eventos(self):
		"""Configura los eventos asegurando que el teclado sea fluido."""
		self.Bind(wx.EVT_CLOSE, self._al_cerrar)
		self._texto_ctrl.Bind(wx.EVT_KEY_DOWN, self._al_pulsar_tecla)
		self._texto_ctrl.Bind(wx.EVT_LEFT_UP, self._actualizar_barra_estado)
		self._texto_ctrl.Bind(wx.EVT_KEY_UP, self._actualizar_barra_estado)

	def _al_pulsar_tecla(self, evento):
		"""Maneja atajos de teclado y permite la propagación de la tecla Alt."""
		tecla = evento.GetKeyCode()
		mods = evento.GetModifiers()
		
		if tecla == wx.WXK_ESCAPE:
			self.Close()
			return
		elif tecla == wx.WXK_F1:
			self._al_mostrar_posicion(None)
			return
		elif tecla == wx.WXK_F2:
			self._al_mostrar_atajos(None)
			return
		elif tecla == wx.WXK_F3:
			direction = "backward" if mods == wx.MOD_SHIFT else "forward"
			self._buscar_siguiente_anterior(direction)
			return
		elif tecla == ord('G') and mods == wx.MOD_CONTROL:
			self._al_ir_a_linea(None)
			return
		elif tecla == ord('P') and mods == wx.MOD_CONTROL:
			self._al_abrir_opciones(None)
			return
			
		# CRÍTICO: Skip() permite que Alt llegue a la barra de menús
		evento.Skip()

	def _actualizar_barra_estado(self, evento=None):
		"""Actualiza la información de la barra de estado."""
		pos = self._texto_ctrl.GetInsertionPoint()
		_ok, x, y = self._texto_ctrl.PositionToXY(pos)
		lineas = self._texto_ctrl.GetNumberOfLines()
		
		self._barra_estado.SetStatusText(_("Línea: {} de {}").format(y + 1, lineas), 0)
		self._barra_estado.SetStatusText(_("Col: {}").format(x + 1), 1)
		
		if evento:
			evento.Skip()

	def _al_ejecutar_plugin(self, evento):
		"""Ejecuta un plugin y maneja sus resultados de forma dinámica."""
		nombre = self._mapa_plugins.get(evento.GetId())
		if not nombre: return
		
		plugin = self._plugin._gestor_plugins.obtener_plugin(nombre)
		meta = plugin.obtener_metadatos()
		resultado = plugin.ejecutar(
			texto=self._texto_ctrl.GetValue(),
			seleccionado=self._texto_ctrl.GetStringSelection(),
			visor=self
		)
		
		# Título genérico basado en el nombre del plugin si es posible
		titulo = meta.nombre if meta else _("Resultado del Plugin")
		
		if nombre == 'extractor_datos':
			self._mostrar_extractor(resultado)
		elif nombre == 'json_beauty' and isinstance(resultado, list):
			self._mostrar_json_resultado(resultado)
		elif nombre == 'copiar_salida' and resultado:
			self._barra_estado.SetStatusText(_("Contenido copiado"), 2)
			winsound.Beep(1000, 100)
		elif isinstance(resultado, list):
			# Manejo genérico para cualquier plugin que devuelva una lista (Historial, Base64, Calculadora, etc.)
			self._mostrar_seleccion_lista(resultado, titulo, _("Seleccione un elemento de la lista:"))

	def _mostrar_seleccion_lista(self, items: List[str], titulo: str, msg: str):
		if not items:
			wx.MessageBox(_("No se encontraron resultados para esta acción."), titulo, wx.OK | wx.ICON_INFORMATION, self)
			return
		dlg = wx.SingleChoiceDialog(self, msg, titulo, items)
		if dlg.ShowModal() == wx.ID_OK:
			api.copyToClip(dlg.GetStringSelection())
			self._barra_estado.SetStatusText(_("Copiado al portapapeles"), 2)
		dlg.Destroy()

	def _mostrar_extractor(self, resultados: Dict[str, List[str]]):
		opciones = []
		for cat, lista in resultados.items():
			for item in lista:
				opciones.append(f"[{cat.upper()}] {item}")
		if not opciones:
			wx.MessageBox(_("No se han podido extraer URLs, rutas de archivos ni direcciones IP del contenido actual."), _("Extractor de Datos"), wx.OK | wx.ICON_INFORMATION, self)
			return
		dlg = wx.SingleChoiceDialog(self, _("Seleccione elemento:"), _("Extractor de Datos"), opciones)
		if dlg.ShowModal() == wx.ID_OK:
			dato = dlg.GetStringSelection().split(']', 1)[1].strip()
			api.copyToClip(dato)
			self._barra_estado.SetStatusText(_("Dato copiado"), 2)
		dlg.Destroy()

	def _mostrar_json_resultado(self, bloques: List[str]):
		"""Muestra bloques JSON formateados en un diálogo especial."""
		if not bloques:
			wx.MessageBox(_("No se detectó ningún bloque JSON válido en la salida."), _("JSON Beauty"), wx.OK | wx.ICON_INFORMATION, self)
			return
			
		for i, json_text in enumerate(bloques):
			# Si hay varios, preguntamos o los mostramos en secuencia
			titulo = _("JSON Formateado ({}/{})").format(i+1, len(bloques))
			dlg = wx.TextEntryDialog(self, _("JSON detectado y procesado. Puede copiar este texto:"), titulo, json_text, style=wx.TE_MULTILINE | wx.OK | wx.CANCEL)
			dlg.SetSize(600, 400)
			if dlg.ShowModal() == wx.ID_OK:
				api.copyToClip(json_text)
				self._barra_estado.SetStatusText(_("JSON copiado al portapapeles"), 2)
			dlg.Destroy()

	def _al_guardar(self, evento):
		with wx.FileDialog(self, _("Guardar contenido"), wildcard="*.txt", style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				try:
					with open(dlg.GetPath(), 'w', encoding='utf-8') as f:
						f.write(self._texto_ctrl.GetValue())
					self._barra_estado.SetStatusText(_("Archivo guardado"), 2)
				except Exception as e:
					wx.MessageBox(str(e), _("Error"), wx.OK | wx.ICON_ERROR)

	def _al_buscar(self, evento):
		with wx.TextEntryDialog(self, _("Texto a buscar:"), _("Buscar"), self._ultima_busqueda) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				self._ultima_busqueda = dlg.GetValue()
				self._buscar_logic(self._ultima_busqueda, "forward")

	def _buscar_siguiente_anterior(self, direction):
		if not self._ultima_busqueda:
			self._al_buscar(None)
		else:
			self._buscar_logic(self._ultima_busqueda, direction)

	def _buscar_logic(self, texto, direccion):
		if not texto: return
		contenido = self._texto_ctrl.GetValue().lower()
		objetivo = texto.lower()
		inicio = self._texto_ctrl.GetInsertionPoint()
		
		if direccion == "forward":
			pos = contenido.find(objetivo, inicio)
			if pos == -1: pos = contenido.find(objetivo, 0)
		else:
			pos = contenido[:inicio].rfind(objetivo)
			if pos == -1: pos = contenido.rfind(objetivo)
			
		if pos != -1:
			self._texto_ctrl.SetSelection(pos, pos + len(objetivo))
			self._texto_ctrl.SetInsertionPoint(pos + len(objetivo))
			winsound.Beep(500, 50)
		else:
			ui.message(_("No se encontró: {}").format(texto))

	def _al_ir_a_linea(self, evento):
		num_lineas = self._texto_ctrl.GetNumberOfLines()
		with wx.TextEntryDialog(self, _("Ir a línea (1-{}):").format(num_lineas), _("Ir a línea")) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				try:
					linea = int(dlg.GetValue()) - 1
					if 0 <= linea < num_lineas:
						pos = self._texto_ctrl.XYToPosition(0, linea)
						self._texto_ctrl.SetInsertionPoint(pos)
						self._texto_ctrl.ShowPosition(pos)
					else:
						winsound.Beep(200, 100)
				except ValueError:
					pass

	def _al_copiar(self, evento):
		self._texto_ctrl.Copy()

	def _al_seleccionar_todo(self, evento):
		self._texto_ctrl.SetSelection(-1, -1)

	def _al_mostrar_posicion(self, evento):
		pos = self._texto_ctrl.GetInsertionPoint()
		_ok, x, y = self._texto_ctrl.PositionToXY(pos)
		ui.message(_("Línea {}, columna {}").format(y+1, x+1))

	def _al_mostrar_atajos(self, evento):
		msg = _(
			"Atajos de teclado:\n\n"
			"Alt: Activar barra de menús\n"
			"Control+F: Buscar texto\n"
			"F3 / Shift+F3: Buscar siguiente / anterior\n"
			"Control+G: Ir a línea\n"
			"Control+P: Opciones del visor\n"
			"Control+S: Guardar contenido\n"
			"Control+C: Copiar selección\n"
			"Control+A: Seleccionar todo\n"
			"F1: Posición del cursor\n"
			"F2: Esta ayuda\n"
			"Escape: Cerrar visor"
		)
		wx.MessageBox(msg, _("Atajos"), wx.OK | wx.ICON_INFORMATION, self)

	def _al_abrir_opciones(self, evento):
		config_gestor = self._plugin._configuracion
		gestor_plugins = self._plugin._gestor_plugins
		dlg = AjustesDialog(self, config_gestor, gestor_plugins)
		if dlg.ShowModal() == wx.ID_OK:
			valores = dlg.obtener_valores()
			
			# Aplicar Visual
			for clave, valor in valores["visual"].items():
				config_gestor.establecer_valor("visor", clave, valor)
				
			# Aplicar Lanzador
			for clave, valor in valores["lanzador"].items():
				config_gestor.establecer_valor("lanzador", clave, valor)
				
			# Aplicar Plugins (y recargar si es necesario)
			actuales = gestor_plugins.listar_plugins_cargados()
			nuevos = valores["plugins"]
			
			for p in gestor_plugins.listar_plugins_disponibles():
				if p in nuevos and p not in actuales:
					gestor_plugins.habilitar_plugin(p)
				elif p not in nuevos and p in actuales:
					gestor_plugins.deshabilitar_plugin(p)
			
			config_gestor.guardar_configuracion()
			self._aplicar_configuracion()
			# Re-crear menú de plugins para reflejar cambios
			# Para simplificar, avisamos que requiere reinicio si son cambios de plugins
			# Pero intentamos reconstruir el menú
			self._actualizar_menu_plugins()
		dlg.Destroy()

	def _actualizar_menu_plugins(self):
		"""Reconstruye el menú de plugins dinámicamente."""
		# Primero localizamos el menú de plugins en el MenuBar
		barra = self.GetMenuBar()
		index = -1
		for i in range(barra.GetMenuCount()):
			if barra.GetMenuLabel(i).replace("&", "") == _("Plugins"):
				index = i
				break
		
		if index != -1:
			nuevo_menu = wx.Menu()
			self._crear_menu_plugins(nuevo_menu)
			barra.Replace(index, nuevo_menu, _("&Plugins"))

	def _aplicar_configuracion(self):
		config = self._plugin._configuracion.visor
		family = wx.FONTFAMILY_TELETYPE if config.fuente_monoespaciada else wx.FONTFAMILY_DEFAULT
		face = "Consolas" if config.fuente_monoespaciada else ""
		fuente = wx.Font(config.tamanio_fuente, family, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, faceName=face)
		self._texto_ctrl.SetFont(fuente)
		self._texto_ctrl.Refresh()

	def _al_cerrar(self, evento):
		self._plugin.dialogo_visor_abierto = False
		self.Destroy()
