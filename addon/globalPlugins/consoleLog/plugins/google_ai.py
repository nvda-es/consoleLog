# -*- coding: utf-8 -*-
# consoleLog - Plugin Google AI (Gemini/Gemma)
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>

import json
import urllib.request
import urllib.parse
import urllib.error
import threading
import os
import base64
import time
import ssl
import wx
from typing import Any, List, Optional, Dict
from logHandler import log
import ui
import winsound

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
from ..nucleo.configuracion import Configuracion

def codificar_texto(texto: str) -> str:
	"""Codifica texto en base64 para ofuscación simple."""
	return base64.b64encode(texto.encode('utf-8')).decode('utf-8')

def decodificar_texto(texto: str) -> str:
	"""Decodifica texto de base64."""
	if not texto: return ""
	try:
		return base64.b64decode(texto.encode('utf-8')).decode('utf-8')
	except Exception:
		return ""

class PluginGoogleAI(PluginBase):
	"""Plugin avanzado para interactuar con Google AI Studio."""
	
	METADATOS = MetadatosPlugin(
		nombre=_("Google AI (Gemini/Gemma)"),
		version="1.2.0",
		descripcion=_("Asistente IA inteligente con soporte multi-key y archivos"),
		autor="Héctor J. Benítez Corredera",
		categoria="ia"
	)
	
	def inicializar(self) -> bool:
		self._dialogo = None
		self._inicializado = True
		return True
	
	def ejecutar(self, **kwargs) -> Any:
		visor = kwargs.get('visor')
		texto = kwargs.get('texto', '')
		seleccionado = kwargs.get('seleccionado', '')
		
		if not self._dialogo:
			self._dialogo = AIDialog(visor, self, texto, seleccionado)
			self._dialogo.Show()
		else:
			if seleccionado:
				self._dialogo.actualizar_contexto(seleccionado, true_selection=True)
			self._dialogo.Raise()
		return None

	def terminar(self):
		if self._dialogo:
			self._dialogo.Close()
			self._dialogo = None

class ListadorModelos:
	"""Gestiona la obtención y caché de modelos."""
	def __init__(self, config_path):
		self.ruta_cache = os.path.join(config_path, "google_ai_models.json")
		
	def obtener_modelos(self, api_keys: List[str]) -> List[str]:
		# Intentar cache
		if os.path.exists(self.ruta_cache):
			if time.time() - os.path.getmtime(self.ruta_cache) < 86400: # 1 día
				try:
					with open(self.ruta_cache, 'r', encoding='utf-8') as f:
						return json.load(f)
				except: pass
		
		# Intentar descargar usando la primera key válida
		base_url = "https://generativelanguage.googleapis.com/v1beta/models"
		for key in api_keys:
			try:
				url = f"{base_url}?key={key}"
				with urllib.request.urlopen(url, timeout=10) as response:
					data = json.loads(response.read().decode('utf-8'))
					modelos = []
					for m in data.get('models', []):
						name = m.get('name', '')
						if "gemini" in name or "gemma" in name:
							modelos.append(name.replace("models/", ""))
					if modelos:
						modelos.sort()
						try:
							with open(self.ruta_cache, 'w', encoding='utf-8') as f:
								json.dump(modelos, f)
						except: pass
						return modelos
			except: continue
		
		# Fallback si falla todo
		return ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]

class SystemPromptDialog(wx.Dialog):
	"""Diálogo para editar el prompt de sistema con opción de restablecer."""
	PROMPT_DEFECTO = "Eres un asistente útil y experto en depuración de código y análisis de logs de consola."
	
	def __init__(self, parent, valor_actual):
		super().__init__(parent, title=_("Instrucciones de Sistema"), size=(500, 400))
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.txt = wx.TextCtrl(self, style=wx.TE_MULTILINE, value=valor_actual)
		sizer.Add(self.txt, 1, wx.EXPAND | wx.ALL, 10)
		
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		btn_default = wx.Button(self, label=_("Restablecer por defecto"))
		btn_default.Bind(wx.EVT_BUTTON, self._al_defecto)
		
		btn_ok = wx.Button(self, wx.ID_OK, label=_("Guardar"))
		btn_cancel = wx.Button(self, wx.ID_CANCEL, label=_("Cancelar"))
		
		btn_sizer.Add(btn_default, 0, wx.ALL, 5)
		btn_sizer.AddStretchSpacer()
		btn_sizer.Add(btn_ok, 0, wx.ALL, 5)
		btn_sizer.Add(btn_cancel, 0, wx.ALL, 5)
		
		sizer.Add(btn_sizer, 0, wx.EXPAND | wx.BOTTOM, 10)
		self.SetSizer(sizer)

	def _al_defecto(self, evt):
		self.txt.SetValue(self.PROMPT_DEFECTO)

	def GetValue(self):
		return self.txt.GetValue()

class AIDialog(wx.Frame):
	"""Diálogo de Chat Premium con soporte avanzado."""
	
	def __init__(self, parent, plugin, texto_completo, seleccionado):
		super(AIDialog, self).__init__(parent, wx.ID_ANY, _("Chat con Google AI Studio"), size=(700, 600))
		self.plugin = plugin
		self.texto_completo = texto_completo
		self.seleccionado = seleccionado
		self.historial_mensajes = []
		self._mensajes_navegacion = []
		self._index_navegacion = -1
		self.archivos_adjuntos = [] # Lista de contenidos de archivos txt
		self.mapa_modelos = {}
		
		self.config = parent._plugin._configuracion
		self.listador = ListadorModelos(os.path.dirname(self.config._ruta_config))
		
		self._crear_interfaz()
		self._crear_menu()
		self.SetMinSize((500, 400))
		self.Centre()
		
		# Cargar modelos en segundo plano
		threading.Thread(target=self._actualizar_modelos_menu).start()

	def _crear_interfaz(self):
		panel = wx.Panel(self)
		sizer_principal = wx.BoxSizer(wx.VERTICAL)
		
		# Historial de chat con scroll y colores
		self.txt_historial = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
		self.txt_historial.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		sizer_principal.Add(self.txt_historial, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		
		# Resumen de adjuntos
		self.lbl_adjuntos = wx.StaticText(panel, label=_("Adjuntos: Ninguno"))
		sizer_principal.Add(self.lbl_adjuntos, 0, wx.LEFT | wx.RIGHT, 10)
		
		# Opciones
		sizer_opciones = wx.BoxSizer(wx.HORIZONTAL)
		self.cb_seleccion = wx.CheckBox(panel, label=_("Usar selección"))
		self.cb_seleccion.SetValue(bool(self.seleccionado))
		self.cb_consola = wx.CheckBox(panel, label=_("Usar consola"))
		
		btn_adjuntar = wx.Button(panel, label=_("Adjuntar .txt..."))
		btn_adjuntar.Bind(wx.EVT_BUTTON, self._al_adjuntar)
		
		btn_reparar = wx.Button(panel, label=_("Auto-reparar error"))
		btn_reparar.Bind(wx.EVT_BUTTON, self._al_reparar)
		
		btn_limpiar = wx.Button(panel, label=_("Limpiar chat"))
		btn_limpiar.Bind(wx.EVT_BUTTON, self._al_limpiar)
		
		sizer_opciones.Add(self.cb_seleccion, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		sizer_opciones.Add(self.cb_consola, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
		sizer_opciones.Add(btn_adjuntar, 0, wx.ALL, 5)
		sizer_opciones.Add(btn_reparar, 0, wx.ALL, 5)
		sizer_opciones.AddStretchSpacer()
		sizer_opciones.Add(btn_limpiar, 0, wx.ALL, 5)
		sizer_principal.Add(sizer_opciones, 0, wx.EXPAND)
		
		# Entrada
		sizer_entrada = wx.BoxSizer(wx.HORIZONTAL)
		self.txt_entrada = wx.TextCtrl(panel, wx.ID_ANY, style=wx.TE_MULTILINE | wx.TE_PROCESS_ENTER)
		self.txt_entrada.Bind(wx.EVT_TEXT_ENTER, self._al_enviar)
		
		btn_enviar = wx.Button(panel, label=_("Enviar (Ctrl+Enter)"))
		btn_enviar.Bind(wx.EVT_BUTTON, self._al_enviar)
		
		sizer_entrada.Add(self.txt_entrada, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		sizer_entrada.Add(btn_enviar, 0, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=5)
		sizer_principal.Add(sizer_entrada, 0, wx.EXPAND)
		
		panel.SetSizer(sizer_principal)
		
		# Eventos de teclado
		panel.Bind(wx.EVT_CHAR_HOOK, self._al_tecla_global)
		
		# Aceletadores
		accel = wx.AcceleratorTable([
			(wx.ACCEL_CTRL, ord('\r'), btn_enviar.GetId()),
			(wx.ACCEL_NORMAL, wx.WXK_ESCAPE, wx.ID_CLOSE)
		])
		self.SetAcceleratorTable(accel)
		self.Bind(wx.EVT_CLOSE, self._al_cerrar)

	def _crear_menu(self):
		self.barra_menu = wx.MenuBar()
		
		# Menú Configuración
		menu_config = wx.Menu()
		item_keys = menu_config.Append(wx.ID_ANY, _("Gestionar API Keys (una por línea)..."))
		self.Bind(wx.EVT_MENU, self._al_gestionar_keys, item_keys)
		
		self.menu_modelos = wx.Menu()
		menu_config.AppendSubMenu(self.menu_modelos, _("Modelo"))
		
		item_prompt = menu_config.Append(wx.ID_ANY, _("Editar Instrucciones de Sistema..."))
		self.Bind(wx.EVT_MENU, self._al_editar_prompt, item_prompt)
		
		menu_config.AppendSeparator()
		item_cerrar = menu_config.Append(wx.ID_CLOSE, _("Cerrar Chat\tAlt+F4"))
		self.Bind(wx.EVT_MENU, self._al_cerrar, item_cerrar)
		
		self.barra_menu.Append(menu_config, _("&IA"))
		
		# Menú Ayuda
		menu_ayuda = wx.Menu()
		item_ayuda = menu_ayuda.Append(wx.ID_ANY, _("Atajos de teclado..."))
		self.Bind(wx.EVT_MENU, self._al_atajos, item_ayuda)
		self.barra_menu.Append(menu_ayuda, _("Ayuda"))
		
		self.SetMenuBar(self.barra_menu)

	def _al_atajos(self, evt):
		msg = _(
			"Atajos de teclado del Chat IA:\n\n"
			"• J: Siguiente mensaje en el historial (hacia abajo)\n"
			"• K: Mensaje anterior en el historial (hacia arriba)\n"
			"• Ctrl+Enter: Enviar mensaje\n"
			"• Escape: Cerrar el chat\n"
			"• Alt+F4: Cerrar el chat\n\n"
			"Nota: Las teclas J y K funcionan cuando el cuadro de edición no tiene el foco."
		)
		wx.MessageBox(msg, _("Atajos de teclado"), wx.OK | wx.ICON_INFORMATION, self)

	def _al_tecla_global(self, evt):
		key = evt.GetKeyCode()
		# Si estamos en el cuadro de edición, permitimos escribir normalmente
		if self.FindFocus() == self.txt_entrada:
			evt.Skip()
			return
			
		if key == ord('J') or key == ord('j'):
			self._navegar_historial(1)
		elif key == ord('K') or key == ord('k'):
			self._navegar_historial(-1)
		else:
			evt.Skip()

	def _navegar_historial(self, direccion):
		if not self._mensajes_navegacion:
			return
			
		total = len(self._mensajes_navegacion)
		viejo_index = self._index_navegacion
		self._index_navegacion += direccion
		
		beep = False
		if self._index_navegacion >= total:
			self._index_navegacion = 0
			beep = True
		elif self._index_navegacion < 0:
			self._index_navegacion = total - 1
			beep = True
			
		if beep:
			winsound.Beep(1000, 100)
			
		msg = self._mensajes_navegacion[self._index_navegacion]
		ui.message(msg)

	def _actualizar_modelos_menu(self):
		keys = self._obtener_keys()
		modelos = self.listador.obtener_modelos(keys)
		
		def _update_ui():
			if not self: return
			# Limpiar menu
			for item in self.menu_modelos.GetMenuItems():
				self.menu_modelos.DestroyItem(item)
			
			self.mapa_modelos = {}
			try:
				modelo_actual = self.config.google_ai.modelo_actual
			except AttributeError:
				modelo_actual = "gemini-1.5-flash"
			
			for m in modelos:
				item = self.menu_modelos.AppendRadioItem(wx.ID_ANY, m)
				self.mapa_modelos[item.GetId()] = m
				if m == modelo_actual:
					item.Check(True)
				self.Bind(wx.EVT_MENU, self._al_cambiar_modelo, item)
		
		wx.CallAfter(_update_ui)

	def _obtener_keys(self) -> List[str]:
		try:
			val = self.config.google_ai.api_keys_codificadas
			txt = decodificar_texto(val)
			return [k.strip() for k in txt.splitlines() if k.strip()]
		except AttributeError:
			return []

	def _al_gestionar_keys(self, evt):
		try:
			txt_actual = decodificar_texto(self.config.google_ai.api_keys_codificadas)
		except AttributeError:
			txt_actual = ""

		dlg = wx.TextEntryDialog(self, _("Pega tus API Keys de Google Studio (una por línea):"), _("Gestionar Keys"), 
		                        value=txt_actual, style=wx.TE_MULTILINE | wx.OK | wx.CANCEL)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				self.config.google_ai.api_keys_codificadas = codificar_texto(dlg.GetValue())
				self.config.guardar_configuracion()
			except: pass
			threading.Thread(target=self._actualizar_modelos_menu).start()
		dlg.Destroy()

	def _al_editar_prompt(self, evt):
		try:
			prompt_actual = self.config.google_ai.prompt_sistema
		except AttributeError:
			prompt_actual = SystemPromptDialog.PROMPT_DEFECTO
			
		dlg = SystemPromptDialog(self, prompt_actual)
		if dlg.ShowModal() == wx.ID_OK:
			try:
				self.config.google_ai.prompt_sistema = dlg.GetValue()
				self.config.guardar_configuracion()
			except: pass
		dlg.Destroy()

	def _al_cambiar_modelo(self, evt):
		mod = self.mapa_modelos.get(evt.GetId())
		if mod:
			try:
				self.config.google_ai.modelo_actual = mod
				self.config.guardar_configuracion()
			except: pass

	def _al_adjuntar(self, evt):
		with wx.FileDialog(self, _("Seleccionar archivo de texto"), wildcard="*.txt", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_MULTIPLE) as dlg:
			if dlg.ShowModal() == wx.ID_OK:
				for paths in dlg.GetPaths():
					try:
						with open(paths, 'r', encoding='utf-8', errors='replace') as f:
							contenido = f.read()
							# Limitar tamaño de adjuntos por seguridad (5MB total aprox)
							if len(contenido) > 1024 * 1024:
								wx.MessageBox(_("El archivo {} es demasiado grande (máx 1MB).").format(os.path.basename(paths)), _("Advertencia"))
								continue
							nombre = os.path.basename(paths)
							self.archivos_adjuntos.append({"nombre": nombre, "texto": contenido})
					except Exception as e:
						wx.MessageBox(_("Error al leer {}: {}").format(paths, e), _("Error"))
				
				self.lbl_adjuntos.SetLabel(_("Adjuntos: {} archivos").format(len(self.archivos_adjuntos)))

	def _al_limpiar(self, evt):
		self.txt_historial.Clear()
		self.historial_mensajes = []
		self._mensajes_navegacion = []
		self._index_navegacion = -1
		self.archivos_adjuntos = []
		self.lbl_adjuntos.SetLabel(_("Adjuntos: Ninguno"))

	def actualizar_contexto(self, seleccionado, true_selection=False):
		if true_selection:
			self.seleccionado = seleccionado
			self.cb_seleccion.SetValue(True)
			self._agregar_mensaje(_("Sistema"), _("Nueva selección detectada de la consola."), color=wx.RED)

	def _agregar_mensaje(self, autor, texto, color=wx.BLACK):
		if not self: return
		self.txt_historial.SetInsertionPointEnd()
		self.txt_historial.SetDefaultStyle(wx.TextAttr(wx.BLUE if autor == _("Tú") else color, font=wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)))
		self.txt_historial.WriteText(f"{autor}: ")
		self.txt_historial.SetDefaultStyle(wx.TextAttr(wx.BLACK))
		# Eliminar posibles bloques de código triple backtick para que no rompa el estilo visual en el control simple
		self.txt_historial.WriteText(f"{texto}\n\n")
		self.txt_historial.ShowPosition(self.txt_historial.GetLastPosition())
		
		# Añadir a navegación
		self._mensajes_navegacion.append(f"{autor}: {texto}")
		# Si es el primer mensaje, o estábamos al final, resetear index (opcional)

	def _al_reparar(self, evt):
		"""Analiza errores actuales y propone parches o correcciones."""
		contexto = self.seleccionado if self.seleccionado else self.texto_completo[-20000:]
		if not contexto:
			wx.MessageBox(_("No hay contexto para analizar."), _("Auto-reparar"))
			return
			
		prompt = (
			"He encontrado un error en el log de mi consola. "
			"Por favor, analízalo y sugiéreme exactamente qué debo cambiar en mi código para solucionarlo. "
			"Si es posible, dame el bloque de código corregido."
		)
		
		self.txt_entrada.SetValue(prompt)
		self._al_enviar(None)

	def _al_enviar(self, evt):
		prompt_usuario = self.txt_entrada.GetValue().strip()
		if not prompt_usuario: return
		
		keys = self._obtener_keys()
		if not keys:
			wx.MessageBox(_("No hay API Keys configuradas en el menú IA."), _("Error"))
			return
		
		self.txt_entrada.Clear()
		self._index_navegacion = -1 # Resetear navegación al enviar
		self._agregar_mensaje(_("Tú"), prompt_usuario)
		
		# Construir contexto
		contextos = []
		if self.cb_seleccion.IsChecked() and self.seleccionado:
			contextos.append(f"[CONSOLA - SELECCIÓN]\n{self.seleccionado}")
		if self.cb_consola.IsChecked() and self.texto_completo:
			consola = self.texto_completo[-50000:]
			contextos.append(f"[CONSOLA - COMPLETO]\n{consola}")
		for adj in self.archivos_adjuntos:
			contextos.append(f"[ARCHIVO: {adj['nombre']}]\n{adj['texto']}")
		
		prompt_final = prompt_usuario
		if contextos:
			prompt_final = "Contexto adicional:\n" + "\n---\n".join(contextos) + f"\n\nPregunta: {prompt_usuario}"
		
		self._agregar_mensaje("Google AI", _("Pensando..."), color=wx.Colour(100, 100, 100))
		threading.Thread(target=self._ejecutar_peticion, args=(prompt_final,)).start()

	def _ejecutar_peticion(self, prompt_final):
		keys = self._obtener_keys()
		try:
			modelo = self.config.google_ai.modelo_actual
			prompt_sistema = self.config.google_ai.prompt_sistema
		except AttributeError:
			modelo = "gemini-1.5-flash"
			prompt_sistema = SystemPromptDialog.PROMPT_DEFECTO
		
		for i, key in enumerate(keys):
			url = f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent?key={key}"
			data = {
				"system_instruction": {"parts": [{"text": prompt_sistema}]},
				"contents": self._preparar_historial(prompt_final),
				"generationConfig": {"temperature": 0.7, "maxOutputTokens": 8192}
			}
			
			try:
				req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
				with urllib.request.urlopen(req, timeout=60) as response:
					res = json.loads(response.read().decode('utf-8'))
					try:
						texto_res = res['candidates'][0]['content']['parts'][0]['text']
						wx.CallAfter(self._finalizar_peticion, texto_res, prompt_final)
						return
					except (KeyError, IndexError):
						raise Exception(_("Formato de respuesta inválido de la API"))
			except urllib.error.HTTPError as e:
				if e.code in [401, 403, 429] and i < len(keys) - 1:
					log.warning(f"GoogleAI: Key {i+1} falló (Error {e.code}). Intentando siguiente...")
					continue
				mensaje = f"Error {e.code}: {e.reason}"
				wx.CallAfter(self._error_peticion, mensaje)
				return
			except Exception as e:
				wx.CallAfter(self._error_peticion, str(e))
				return
		
		wx.CallAfter(self._error_peticion, _("Todas las API Keys fallaron o están agotadas."))

	def _preparar_historial(self, nuevo_prompt):
		contents = []
		for msg in self.historial_mensajes[-10:]: # últimos 10 turnos
			contents.append({
				"role": "user" if msg['autor'] == 'user' else "model",
				"parts": [{"text": msg['texto']}]
			})
		contents.append({"role": "user", "parts": [{"text": nuevo_prompt}]})
		return contents

	def _finalizar_peticion(self, respuesta, prompt_final):
		if not self: return
		self._agregar_mensaje("Google AI", respuesta)
		self.historial_mensajes.append({"autor": "user", "texto": prompt_final})
		self.historial_mensajes.append({"autor": "model", "texto": respuesta})

	def _error_peticion(self, msg):
		if not self: return
		self._agregar_mensaje("Error", msg, color=wx.RED)

	def _al_cerrar(self, evt):
		self.plugin._dialogo = None
		self.Destroy()
