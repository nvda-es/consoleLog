# -*- coding: utf-8 -*-
# Copyright (C) 2023 Héctor J. Benítez Corredera <xebolax@gmail.com>
# This file is covered by the GNU General Public License.

import globalPluginHandler
import addonHandler
import api
import ui
import globalVars
import gui
import gui.contextHelp
from scriptHandler import script
import ctypes
import wx
import threading
import queue
import winsound
import os 
import tempfile
import re

addonHandler.initTranslation()

# Define las constantes necesarias
STD_OUTPUT_HANDLE = -11

# Define las estructuras de datos necesarias
class COORD(ctypes.Structure):
	_fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class CHAR_INFO(ctypes.Structure):
	_fields_ = [("Char", ctypes.c_wchar), ("Attributes", ctypes.c_short)]

class SMALL_RECT(ctypes.Structure):
	_fields_ = [("Left", ctypes.c_short), ("Top", ctypes.c_short), ("Right", ctypes.c_short), ("Bottom", ctypes.c_short)]

class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
	_fields_ = [("dwSize", COORD), ("dwCursorPosition", COORD), ("wAttributes", ctypes.c_ushort), 
				("srWindow", SMALL_RECT), ("dwMaximumWindowSize", COORD)]

# Función para leer el contenido de la consola
def leer_consola(data_queue):
	try:
		# Lógica para emitir un beep suave mientras el hilo está en funcionamiento, en otro hilo
		def beep_suave():
			while not leer_consola.stop_signal:
				winsound.Beep(1000, 100)
				wx.MilliSleep(1000)
        
		beep_thread = threading.Thread(target=beep_suave, daemon=True)
		beep_thread.start()
			
		# Aquí comienza la lógica para obtener el texto de la consola
		# Obtén el título de la ventana enfocada
		length = ctypes.windll.user32.GetWindowTextLengthW(api.getForegroundObject().windowHandle) + 1
		buffer = ctypes.create_unicode_buffer(length)
		ctypes.windll.user32.GetWindowTextW(api.getForegroundObject().windowHandle, buffer, length)

				# Encuentra la ventana de consola con el título obtenido
		hConWnd = ctypes.windll.user32.FindWindowW(None, buffer.value)
		if hConWnd == 0:
    # TRANSLATORS: Mensaje de error 
			data_queue.put(_("No se pudo encontrar la ventana de la consola."))
			return

		# Obtén el ID del proceso asociado con esa ventana
		process_id = ctypes.c_uint32()
		ctypes.windll.user32.GetWindowThreadProcessId(hConWnd, ctypes.byref(process_id))

		# Adjunta nuestra consola al proceso de esa ventana
		if not ctypes.windll.kernel32.AttachConsole(process_id.value):
    # TRANSLATORS: Mensaje de error
			data_queue.put(_("No se pudo adjuntar a la consola del proceso."))
			return

		# Obtén un manejador para el buffer de consola de ese proceso
		hConsole = ctypes.windll.kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
		if hConsole == -1:
			ctypes.windll.kernel32.FreeConsole()
    # TRANSLATORS: Mensaje de error
			data_queue.put(_("No se pudo obtener el manejador de la consola."))
			return

		# Obtiene la información de la pantalla de la consola
		csbi = CONSOLE_SCREEN_BUFFER_INFO()
		ctypes.windll.kernel32.GetConsoleScreenBufferInfo(hConsole, ctypes.byref(csbi))

		buffer_size = COORD(csbi.dwSize.X, csbi.dwSize.Y)
		buffer_coord = COORD(0, 0)
		rect = SMALL_RECT(0, 0, csbi.dwSize.X - 1, csbi.dwSize.Y - 1)

		# Crea un buffer para almacenar los datos leídos
		char_info_buffer = (CHAR_INFO * (buffer_size.X * buffer_size.Y))()

		# Llama a la función ReadConsoleOutput
		ctypes.windll.kernel32.ReadConsoleOutputW(hConsole, char_info_buffer, buffer_size, buffer_coord, ctypes.byref(rect))

		# Extrae el texto de los datos leídos
		lines = []
		for y in range(csbi.dwSize.Y):
			line = "".join([char_info_buffer[x + y * buffer_size.X].Char for x in range(buffer_size.X) if char_info_buffer[x + y * buffer_size.X].Char not in [None, '\x00']])
			lines.append(line.rstrip())  # rstrip para eliminar los espacios en blanco al final de cada línea
		text = "\n".join(lines)
# Eliminar todas las líneas en blanco al final del texto
		text = re.sub(r'\n\s*\Z', '', text)
		# Libera la consola adjunta
		ctypes.windll.kernel32.FreeConsole()

		# Retorna el texto extraído
		data_queue.put(text)
	except Exception as e:
    # TRANSLATORS: Mensaje de error
		data_queue.put(_("Error: {}").format(e))

def disableInSecureMode(decoratedCls):
	if globalVars.appArgs.secure:
		return globalPluginHandler.GlobalPlugin
	return decoratedCls

@disableInSecureMode
class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	def __init__(self, *args, **kwargs):
		super(GlobalPlugin, self).__init__(*args, **kwargs)

		self.proceso_en_marcha = False
		self.dialogo_abierto = False
		self.fichero_temporal = os.path.join(tempfile.gettempdir(),"consoleLog_temp.txt")

	@script(gesture=None,
		# TRANSLATORS: Descripción para el dialogo de gestos
		description= _("Muestra el visor de consola"),
		# TRANSLATORS: Nombre de la categoría en el dialogo de gestos
		category= _("Visor de consola")
	)
	def script_leerConsola(self, gesture):
		if self.proceso_en_marcha:
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Por favor, espere. Hay otro proceso en marcha."))
			return

		if self.dialogo_abierto:
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Por favor, cierre el diálogo actual antes de iniciar uno nuevo."))
			return
		
		foreground_window = api.getForegroundObject()
		if not foreground_window.windowClassName.startswith("ConsoleWindowClass"):
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Esta no es una ventana de consola."))
			return

		self.proceso_en_marcha = True

		data_queue = queue.Queue()
		leer_consola.stop_signal = False
		thread = threading.Thread(target=leer_consola, args=(data_queue,), daemon=True)
		thread.start()

		wx.CallLater(100, self.mostrar_dialogo, data_queue)

	def mostrar_dialogo(self, data_queue):
		try:
			texto = data_queue.get_nowait()
		except queue.Empty:
			wx.CallLater(100, self.mostrar_dialogo, data_queue)
			return

		leer_consola.stop_signal = True
		self.proceso_en_marcha = False

		# TRANSLATORS: Partes de texto a detectar
		if texto.startswith(_("No se pudo obtener")) or texto.startswith(_("Error:")):
			ui.message(texto)
			return

		try:
			with open(self.fichero_temporal, "w", encoding="utf-8") as file:
				file.write(texto)
		except Exception as e:
			# TRANSLATORS: Mensaje de error
			ui.message(_("Se ha producido un error: {} (tipo de error: {})").format(e, type(e).__name__))
			return

		self.activate()

	def activate(self):
		verLog = VerLog(gui.mainFrame, self)
		verLog.Raise()
		verLog.Maximize()
		verLog.Show()

class VerLog(wx.Frame):
	def __init__(self, parent, frame):
		# TRANSLATORS: Titulo de la ventana del visor de consola
		super(VerLog, self).__init__(parent, wx.ID_ANY, _("Visor de consola"))

		self.frame = frame
		self.frame.dialogo_abierto = True
		self.last_search = ""
		self._lastFilePos = 0

		self.Bind(wx.EVT_CLOSE, self.onClose)

		mainSizer = wx.BoxSizer(wx.VERTICAL)
		self.outputCtrl = wx.TextCtrl(self, wx.ID_ANY, size=(500, 500), style=wx.TE_MULTILINE | wx.TE_READONLY|wx.TE_RICH)
		self.outputCtrl.Bind(wx.EVT_KEY_DOWN, self.onOutputKeyDown)
		mainSizer.Add(self.outputCtrl, proportion=1, flag=wx.EXPAND)
		self.SetSizer(mainSizer)
		mainSizer.Fit(self)

		menuBar = wx.MenuBar()
		menu = wx.Menu()
		# TRANSLATORS: Item de menú en el dialogo de visor de consola
		item = menu.Append(0, _("&Buscar	Ctrl+F"))
		self.Bind(wx.EVT_MENU, self.onFind, item)
		# TRANSLATORS: Item de menú en el dialogo de visor de consola
		item = menu.Append(wx.ID_SAVEAS, _("&Guardar como...	Ctrl+S"))
		self.Bind(wx.EVT_MENU, self.onSaveAsCommand, item)
		menu.AppendSeparator()
		# TRANSLATORS: Item de menú en el dialogo de visor de consola
		item = menu.Append(wx.ID_EXIT, _("&Salir"))
		self.Bind(wx.EVT_MENU, self.onClose, item)
		# TRANSLATORS: Nombre del menú en el dialogo de visor de consola
		menuBar.Append(menu, _("&Registro"))
		self.SetMenuBar(menuBar)

		pos = self.outputCtrl.GetInsertionPoint()
		try:
			f = open(self.frame.fichero_temporal, "r", encoding="UTF-8")
			f.seek(self._lastFilePos)
			self.outputCtrl.AppendText(f.read())
			self._lastFilePos = f.tell()
			self.outputCtrl.SetInsertionPoint(pos)
			f.close()
		except IOError:
			pass

		self.outputCtrl.SetFocus()

	def showFindDialog(self):
		findDialog = CustomFindDialog(self, self.outputCtrl)
		findDialog.ShowModal()
		findDialog.Destroy()

	def findText(self, text, direction="forward"):
		text_string = self.outputCtrl.GetValue().lower()
		find_string = text.lower()
		current_pos = self.outputCtrl.GetInsertionPoint()

		if direction == "forward":
			match_pos = text_string.find(find_string, current_pos)
			# Búsqueda cíclica
			if match_pos == -1:
				match_pos = text_string.find(find_string, 0)
		else:  # direction == "backward"
			text_string_before_cursor = text_string[:current_pos]
			match_pos = text_string_before_cursor.rfind(find_string)
			# Búsqueda cíclica
			if match_pos == -1:
				match_pos = text_string.rfind(find_string)

		if match_pos != -1:
			self.outputCtrl.SetSelection(match_pos, match_pos + len(find_string))
			self.outputCtrl.SetInsertionPoint(match_pos + len(find_string))
			winsound.Beep(37, 100) # Añadiendo un beep suave aquí
		else:
			wx.MessageBox(
				# TRANSLATORS: Mensaje de error
				_("No hay coincidencias encontradas."),
				# TRANSLATORS: Titulo del mensaje de error
				_("Busqueda")
			)

	def onFind(self, evt):
		self.showFindDialog()

	def onSaveAsCommand(self, evt):
		# TRANSLATORS: Nombre para el dialogo de guardar archivo
		filename = wx.FileSelector(_("Guardar como..."), default_filename="", flags=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT, parent=self)
		if not filename:
			return
		try:
			with open(filename, "w", encoding="UTF-8") as f:
				f.write(self.outputCtrl.GetValue())
		except (IOError, OSError) as e:
			# TRANSLATORS: Mensaje de error
			gui.messageBox(_("Error guardando log: %s") % e.strerror, _("Error"), style=wx.OK | wx.ICON_ERROR, parent=self)

	def onOutputKeyDown(self, evt):
		key = evt.GetKeyCode()
		modifiers = evt.GetModifiers()
		if key == wx.WXK_ESCAPE:
			self.Close()
			return
		elif key == wx.WXK_F1:
			# Obtén la posición del cursor
			pos = self.outputCtrl.GetInsertionPoint()
			# Obtén la línea y la posición en la línea
			_Boleano, line_pos, line_num = self.outputCtrl.PositionToXY(pos)
			# Muestra la información con un mensaje
			# TRANSLATORS: Mensaje de información de la línea y posición
			ui.message(_("Línea: {}, Posición: {}").format(line_num + 1, line_pos +1))
		elif key == wx.WXK_F3:
			if not self.last_search:
			# Si no ha habido una búsqueda previa, muestra el cuadro de diálogo
				self.showFindDialog()
			else:
				# Buscar la siguiente (o anterior) coincidencia
				direction = "backward" if modifiers == wx.MOD_SHIFT else "forward"
				self.findText(self.last_search, direction)
		evt.Skip()

	def onClose(self, evt):
		try:
			os.remove(self.frame.fichero_temporal)
		except FileNotFoundError:
			# TRANSLATORS: Mensaje de error al borrar el fichero temporal
			ui.message(_("El archivo temporal no fue encontrado"))
		except PermissionError:
			# TRANSLATORS: Mensaje de error al borrar el fichero temporal
			ui.message(_("Permiso denegado para eliminar el archivo temporal"))
		except Exception as e:
			# TRANSLATORS: Mensaje de error al borrar el fichero temporal
			ui.message(_("Ocurrió un error al intentar eliminar el archivo temporal: {}").format(e))
		self.frame.dialogo_abierto = False
		self.Destroy()

class CustomFindDialog(wx.Dialog):
	def __init__(self, parent, text_ctrl):
		# TRANSLATORS: Titulo del dialogo buscar
		super().__init__(parent, title=_("Buscar"))
        
		self.text_ctrl = text_ctrl
		self.current_pos = 0

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.find_text_ctrl = wx.TextCtrl(self, style=wx.TE_PROCESS_ENTER)
		self.sizer.Add(self.find_text_ctrl, 0, wx.EXPAND | wx.ALL, 5)

		# TRANSLATORS: Nombre del botón buscar en el dialogo buscar
		self.find_button = wx.Button(self, label=_("&Buscar"))
		self.sizer.Add(self.find_button, 0, wx.ALL, 5)

		self.find_text_ctrl.Bind(wx.EVT_TEXT_ENTER, self.onFind)
		self.find_button.Bind(wx.EVT_BUTTON, self.onFind)
		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
		self.SetSizer(self.sizer)
    
	def onFind(self, event):
		find_string = self.find_text_ctrl.GetValue().lower()
		self.GetParent().last_search = find_string
		self.GetParent().findText(find_string, "forward")
		self.Close()

	def onKeyDown(self, event):
		key = event.GetKeyCode()
		modifiers = event.GetModifiers()
		if key == wx.WXK_ESCAPE or (key == wx.WXK_F4 and modifiers == wx.MOD_ALT):
			self.Close()
		else:
			event.Skip()