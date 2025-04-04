# -*- coding: utf-8 -*-
# Copyright (C) 2024 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.
#
# Agradecimientos a los creadores del complemento NAO.
#
# Autores: Alessandro Albano, Davide De Carne y Simone Dal  Maso
#
# Por las funciones extraídas de dicho complemento para obtener rutas.
#
# Las funciones extraídas son:
# is_explorer, get_selected_files_explorer_ps y get_selected_file_explorer
#
import globalPluginHandler
import addonHandler
import api
import ui
import globalVars
import gui
import UIAHandler
from scriptHandler import script
from comtypes.client import CreateObject as COMCreate
import ctypes
import wx
import threading
import queue
import winsound
import os 
import tempfile
import re
import subprocess
import json

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
	"""
	Lee el contenido de la consola clásica y lo coloca en una cola para procesarlo más tarde.

	Args:
		data_queue (queue.Queue): Cola donde se colocará el texto extraído de la consola.
	"""
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
		ctypes.windll.kernel32.FreeConsole()
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

def leer_consola_wt(data_queue):
	"""
	Lee el contenido de la consola moderna (Windows Terminal) y lo coloca en una cola para procesarlo más tarde.

	Args:
		data_queue (queue.Queue): Cola donde se colocará el texto extraído de la consola.
	"""
	try:
		# Lógica para emitir un beep suave mientras el hilo está en funcionamiento, en otro hilo
		def beep_suave():
			while not leer_consola_wt.stop_signal:
				winsound.Beep(1000, 100)
				wx.MilliSleep(1000)
        
		beep_thread = threading.Thread(target=beep_suave, daemon=True)
		beep_thread.start()
			
		# Aquí comienza la lógica para obtener el texto de la consola
#		UIAHandler.initialize()
		focused_element = UIAHandler.handler.clientObject.getFocusedElement()
		pattern = focused_element.getCurrentPattern(UIAHandler.UIA_TextPatternId)
		text_pattern = pattern.QueryInterface(UIAHandler.IUIAutomationTextPattern)
		text_range = text_pattern.documentRange
		texto_terminal = text_range.getText(-1)
		text = '\n'.join(line.rstrip() for line in texto_terminal.splitlines() if line.strip())
		data_queue.put(text)
	except Exception as e:
		# TRANSLATORS: Mensaje de error
		data_queue.put(_("Error: {}").format(e))
	finally:
		pass #UIAHandler.terminate()

# Función para realizar un clic derecho en Windows Terminal
def realizar_clic_derecho_terminal_moderno():
	"""
	Realiza un clic derecho en la ventana de consola moderna enfocada (Windows Terminal).

	Nota:
		Simula un clic derecho utilizando la API de UI Automation para obtener las coordenadas de la consola.
	"""
	try:
		#UIAHandler.initialize()
		focused_element = UIAHandler.handler.clientObject.getFocusedElement()
		if not focused_element:
			ui.message(_("No se pudo encontrar la ventana de la consola."))
			return

		# Obtén las coordenadas de la ventana de la consola como una tupla
		bounds = focused_element.getCurrentPropertyValue(UIAHandler.UIA_BoundingRectanglePropertyId)
		if not bounds or not isinstance(bounds, tuple) or len(bounds) != 4:
			ui.message(_("No se pudieron obtener las coordenadas de la ventana de la consola."))
			return

		# Asignar los valores de la tupla
		left, top, right, bottom = bounds

		# Calcula el centro de la ventana para simular el clic
		x_center = int((left + right) / 2)
		y_center = int((top + bottom) / 2)

		# Mueve el cursor al centro de la ventana
		ctypes.windll.user32.SetCursorPos(x_center, y_center)

		# Envía el clic derecho (down y up)
		ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # Botón derecho presionado
		ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # Botón derecho liberado

		winsound.Beep(600, 200)  # Beep para consola moderna
	finally:
		pass #UIAHandler.terminate()

# Función general para realizar clic derecho
def realizar_clic_derecho():
	"""
	Determina si la ventana enfocada es una consola y realiza un clic derecho en ella.

	Nota:
		El clic derecho se simula dependiendo de si es una consola clásica o moderna.
	"""
	try:
		foreground_window = api.getForegroundObject()
		class_name = foreground_window.windowClassName
		product_name = getattr(foreground_window.appModule, "productName", "")

		# Detectar consolas modernas como Windows Terminal
		if product_name in ["Microsoft.WindowsTerminal"]:
			realizar_clic_derecho_terminal_moderno()
			return

		# Detectar consolas clásicas
		if class_name.startswith("ConsoleWindowClass"):
			# Simula clic derecho en consola clásica
			hwnd = foreground_window.windowHandle
			rect = ctypes.wintypes.RECT()
			ctypes.windll.user32.GetWindowRect(hwnd, ctypes.byref(rect))
			x_center = (rect.left + rect.right) // 2
			y_center = (rect.top + rect.bottom) // 2
			ctypes.windll.user32.SetCursorPos(x_center, y_center)
			ctypes.windll.user32.mouse_event(0x0008, 0, 0, 0, 0)  # Botón derecho presionado
			ctypes.windll.user32.mouse_event(0x0010, 0, 0, 0, 0)  # Botón derecho liberado

			winsound.Beep(600, 200)  # Beep para consola clásica
			return

		ui.message(_("La ventana enfocada no es una consola."))
	except Exception as e:
		ui.message(_("Error al intentar realizar el clic derecho: {}").format(e))

def disableInSecureMode(decoratedCls):
	"""Decorador que deshabilita una clase de complemento global en modo seguro.

	Args:
		decoratedCls (class): La clase a decorar.

	Returns:
		class: La clase original o GlobalPlugin dependiendo del modo seguro.
	"""
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
		self.foreground_window = None
		self._shell = None
		self.is_run = False
		self.terminales = self.comprobar_terminales()
		self.git_disponibilidad, self.git_ruta = self.comprobar_git_powershell()

	@script(gesture=None,
		# TRANSLATORS: Descripción para el dialogo de gestos
		description= _("Muestra el visor de consola"),
		# TRANSLATORS: Nombre de la categoría en el dialogo de gestos
		category= _("Visor de consola")
	)
	def script_leerConsola(self, gesture):
		"""
		Muestra el visor de consola para leer el contenido de la consola enfocada.

		Args:
			gesture (Gesture): El gesto asociado con este script.
		"""
		if self.proceso_en_marcha:
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Por favor, espere. Hay otro proceso en marcha."))
			return

		if self.dialogo_abierto:
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Por favor, cierre el diálogo actual antes de iniciar uno nuevo."))
			return
		
		self.foreground_window = api.getForegroundObject()
		if not (
			self.foreground_window.windowClassName.startswith("ConsoleWindowClass")
			or self.foreground_window.windowClassName == "CASCADIA_HOSTING_WINDOW_CLASS"
		):
			# TRANSLATORS: Mensaje informativo
			ui.message(_("Esta no es una ventana de consola."))
			return

		self.proceso_en_marcha = True

		data_queue = queue.Queue()
		if self.foreground_window.appModule.productName in ['Microsoft.WindowsTerminal']:
			leer_consola_wt.stop_signal = False
			thread = threading.Thread(target=leer_consola_wt, args=(data_queue,), daemon=True)
			thread.start()
		else:
			leer_consola.stop_signal = False
			thread = threading.Thread(target=leer_consola, args=(data_queue,), daemon=True)
			thread.start()

		wx.CallLater(100, self.mostrar_dialogo, data_queue)

	def mostrar_dialogo(self, data_queue):
		"""
		Muestra un cuadro de diálogo con el contenido extraído de la consola.

		Args:
			data_queue (queue.Queue): Cola que contiene el texto extraído de la consola.
		"""
		try:
			texto = data_queue.get_nowait()
		except queue.Empty:
			wx.CallLater(100, self.mostrar_dialogo, data_queue)
			return

		if self.foreground_window.appModule.productName in ['Microsoft.WindowsTerminal']:
			leer_consola_wt.stop_signal = True
		else:
			leer_consola.stop_signal = True

		self.proceso_en_marcha = False

		try:
			#TRANSLATORS: Partes de texto a detectar
			if re.match("|".join([re.escape(_("No se pudo obtener")), re.escape(_("Error:"))]), texto):
				ui.message(texto)
				return
		except:
			ui.message(texto)
			return

		if not texto:
			# TRANSLATORS: Mensaje informativo
			ui.message(_("No se encontró texto en la consola"))
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
		"""
		Activa y muestra el visor de consola en la interfaz gráfica.
		"""
		verLog = VerLog(gui.mainFrame, self)
		verLog.Raise()
		verLog.Maximize()
		verLog.Show()

	@script(gesture=None,
		# TRANSLATORS: Descripción para el dialogo de gestos
		description=_("Realiza un clic derecho en la ventana de consola enfocada para copiar el contenido del portapapeles."),
		# TRANSLATORS: Nombre de la categoría en el dialogo de gestos
		category=_("Visor de consola")
	)
	def script_realizarClicDerecho(self, gesture):
		"""
		Realiza un clic derecho en la ventana de consola enfocada para copiar el contenido del portapapeles.

		Args:
			gesture (Gesture): El gesto asociado con este script.
		"""
		realizar_clic_derecho()

	def comprobar_terminales(self):
		"""
		Comprueba la disponibilidad de cmd, PowerShell, Windows Terminal (wt),
		y consolas de Visual Studio si están en el sistema.

		Returns:
			dict: Un diccionario indicando la disponibilidad de 'cmd', 'PowerShell', 'wt',
			y 'Visual Studio' si están disponibles.
		"""
		resultados = {'cmd': False, 'PowerShell': False, 'wt': False, 'Visual Studio': False}

		# Comprobar cmd y PowerShell mediante la ejecución de un comando simple
		comandos = {
			'cmd': ['cmd.exe', '/c', 'echo'],
			'PowerShell': ['powershell.exe', '-Command', "echo $null"],
		}

		for terminal, comando in comandos.items():
			try:
				subprocess.Popen(comando, creationflags=subprocess.CREATE_NO_WINDOW, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
				resultados[terminal] = True
			except Exception:
				pass

		# Intenta encontrar 'wt.exe' en el PATH para verificar la disponibilidad de Windows Terminal
		resultados['wt'] = any(os.access(os.path.join(path, 'wt.exe'), os.X_OK) for path in os.environ["PATH"].split(os.pathsep))

		# Intenta encontrar las consolas de Visual Studio
		rutas_vs = ["C:\\Program Files\\Microsoft Visual Studio", "C:\\Program Files (x86)\\Microsoft Visual Studio"]
		for ruta in rutas_vs:
			if os.path.exists(ruta):
				for root, dirs, files in os.walk(ruta):
					if 'vcvars32.bat' in files or 'vcvars64.bat' in files:
						resultados['Visual Studio'] = True
						break
			if resultados['Visual Studio']:
				break

		return resultados

	def comprobar_git_powershell(self):
		"""
		Comprueba si Git está instalado y encuentra su ubicación utilizando PowerShell.

		Returns:
			tuple: (bool, str) Un booleano que indica si Git está instalado, y una cadena
			con la ubicación de Git si está instalado, de lo contrario, una cadena vacía.
		"""
		comando_ps = "Get-Command git | Select-Object -ExpandProperty Source | ConvertTo-Json"
		try:
			resultado = subprocess.Popen(["powershell", "-Command", comando_ps], stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=subprocess.CREATE_NO_WINDOW)
			salida, error = resultado.communicate()
			if resultado.returncode == 0 and salida:
				ruta_git = json.loads(salida.decode('utf-8'))
				return (True, os.path.dirname(os.path.dirname(ruta_git)))
			else:
				return (False, "")
		except Exception:
			return (False, "")

	def is_explorer(self, obj=None):
		"""Determina si el objeto en primer plano es el explorador de Windows.

		Args:
			obj (NVDA object, optional): Objeto a comprobar. Si no se proporciona, se utiliza el objeto en primer plano.

		Returns:
			bool: True si el objeto en primer plano es el explorador de Windows, False en caso contrario.
		"""
		if obj is None: obj = api.getForegroundObject()
		return obj and obj.appModule and obj.appModule.appName and obj.appModule.appName == 'explorer'

	def get_selected_files_explorer_ps(self):
		"""
		Obtiene los archivos seleccionados en el explorador de Windows usando PowerShell.
    
		Este método intenta ejecutar un script de PowerShell que recupera los elementos actualmente seleccionados en todas las ventanas abiertas del explorador de Windows. Cada elemento seleccionado se identifica por el manejador de ventana (HWND) y la ruta del archivo seleccionado.
    
		Returns:
			dict: Un diccionario donde cada clave es el HWND de una ventana del explorador y cada valor es la ruta del archivo seleccionado en esa ventana. Retorna un diccionario vacío si no hay selecciones o en caso de error.
		"""
		import subprocess
		si = subprocess.STARTUPINFO()
		si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
		cmd = "$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = New-Object System.Text.UTF8Encoding; (New-Object -ComObject 'Shell.Application').Windows() | ForEach-Object { echo \\\"$($_.HWND):$($_.Document.FocusedItem.Path)\\\" }"
		cmd = "powershell.exe \"{}\"".format(cmd)
		try:
			p = subprocess.Popen(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, startupinfo=si, encoding="utf-8", text=True)
			stdout, stderr = p.communicate()
			if p.returncode == 0 and stdout:
				ret = {}
				lines = stdout.splitlines()
				for line in lines:
					hwnd, name = line.split(':',1)
					ret[str(hwnd)] = name
				return ret
		except:
			pass
		return False

	def get_selected_file_explorer(self, obj=None):
		"""
		Obtiene la ruta del archivo seleccionado en el explorador de Windows.

		Args:
			obj (NVDA object, optional): Objeto del explorador de Windows. Si no se proporciona, se utiliza el objeto en primer plano.

		Returns:
			str or None: La ruta del archivo seleccionado si hay alguno, None si no hay selección o si ocurre un error.
		"""
		if obj is None: obj = api.getForegroundObject()
		file_path = False
		if self.is_explorer(obj):
			desktop = False
			try:
				if not self._shell:
					self._shell = COMCreate("shell.application")
				for window in self._shell.Windows():
					if window.hwnd == obj.windowHandle:
						file_path = str(window.Document.FocusedItem.path)
						break
				else:
					desktop = True
			except:
				try:
					windows = self.get_selected_files_explorer_ps()
					if windows:
						if str(obj.windowHandle) in windows:
							file_path = windows[str(obj.windowHandle)]
						else:
							desktop = True
				except:
					pass
			if desktop:
				desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
				file_path = desktop_path + '\\' + api.getDesktopObject().objectWithFocus().name
		return file_path

	def encontrar_directorio_valido(self, ruta):
		"""
		Encuentra el directorio válido más cercano para una ruta dada.

		Args:
			ruta (str): La ruta a analizar.

		Returns:
			str or None: El directorio encontrado o None si no se encuentra un directorio válido.
		"""
		if not isinstance(ruta, str):
			return None

		if os.path.isdir(ruta):
			return ruta

		partes_ruta = ruta.split(os.sep)

		for i in range(len(partes_ruta), 0, -1):
			directorio = os.sep.join(partes_ruta[:i])
			if os.path.isdir(directorio):
				return directorio

		return None

	def cmd_asincrona(self, directorio, tipo='cmd', admin=False, script_path=None):
		"""
		Ejecuta un comando en un directorio específico, opcionalmente con privilegios de administrador.

		Args:
			directorio (str): El directorio en el cual ejecutar el comando.
			tipo (str, opcional): Tipo de terminal a abrir ('cmd', 'powershell', 'wt', 'git-bash').
			admin (bool, opcional): Si es True, ejecuta el comando con privilegios de administrador.
		"""
		oldValue = ctypes.c_void_p()
		ctypes.windll.kernel32.Wow64DisableWow64FsRedirection(ctypes.byref(oldValue))
		try:
			if tipo == 'cmd':
				ejecutable = 'cmd.exe'
				parametros = '/k pushd "{}"'.format(directorio)
			elif tipo == 'powershell':
				ejecutable = 'powershell.exe'
				parametros = f'-NoExit -Command "Set-Location -LiteralPath \\"{directorio}\\""'
			elif tipo == 'wt':
				ejecutable = 'wt.exe'
				parametros = f'-d "{directorio}"'
			elif tipo == 'git-bash':
				ejecutable = os.path.join(self.git_ruta, 'git-bash.exe')
				parametros = f'--cd="{directorio}"'
			elif tipo == 'vs' and script_path:
				# Primero carga las variables de entorno de Visual Studio, luego cambia al directorio deseado
				ejecutable = 'cmd.exe'
				parametros = f'/k pushd "{os.path.dirname(script_path)}" && call "{script_path}" && pushd "{directorio}"'
			else:
				raise ValueError(_("Tipo de terminal no soportado."))

			ret = ctypes.windll.shell32.ShellExecuteW(None, 'runas' if admin else 'open', ejecutable, parametros, None, 1)
		finally:
			ctypes.windll.kernel32.Wow64RevertWow64FsRedirection(oldValue)

	@script(gesture=None,
		# TRANSLATORS: Descripción para el dialogo de gestos
		description=_("Abrir el lanzador de consolas de Windows."),
		# TRANSLATORS: Nombre de la categoría en el dialogo de gestos
		category=_("Visor de consola")
	)
	def script_run_launcher(self, gesture):
		"""
		Abre el lanzador de consolas de Windows.

		Args:
			gesture (Gesture): El gesto asociado con este script.
		"""
		wx.CallAfter(self.lanzar)

	def lanzar(self):
		"""
		Función para abrir el cuadro de diálogo del lanzador de consolas.
		"""
		if not self.is_run:
			directorio = self.encontrar_directorio_valido(self.get_selected_file_explorer())
			self._shell = None
			if not directorio:
				ui.message(_('No se encontró una selección válida.'))
				return
			gui.mainFrame.prePopup()
			dlg = OpcionesConsolas(None, self, directorio)
			dlg.ShowModal()
			dlg.Destroy()
			gui.mainFrame.postPopup()
		else:
			ui.message(_("Ya hay una instancia de lanzador de consolas abierta."))

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
		"""
		Muestra un cuadro de diálogo para buscar texto en el visor de consola.
		"""
		findDialog = CustomFindDialog(self, self.outputCtrl)
		findDialog.ShowModal()
		findDialog.Destroy()

	def findText(self, text, direction="forward"):
		"""
		Busca texto en el visor de consola.

		Args:
			text (str): El texto a buscar.
			direction (str, opcional): Dirección de la búsqueda ('forward' o 'backward').
		"""
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
		"""
		Controlador de eventos para iniciar la búsqueda de texto en el visor de consola.

		Args:
			evt (Event): Evento asociado.
		"""
		self.showFindDialog()

	def onSaveAsCommand(self, evt):
		"""
		Controlador de eventos para guardar el contenido del visor de consola como archivo.

		Args:
			evt (Event): Evento asociado.
		"""
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
		"""
		Controlador de eventos para gestionar atajos de teclado en el visor de consola.

		Args:
			evt (Event): Evento asociado.
		"""
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
		"""
		Controlador de eventos para cerrar el visor de consola.

		Args:
			evt (Event): Evento asociado.
		"""
		if self.frame.foreground_window:
			api.setForegroundObject(self.frame.foreground_window)
   
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
		"""
		Controlador de eventos para gestionar atajos de teclado en el cuadro de diálogo de búsqueda.

		Args:
			event (Event): Evento asociado.
		"""
		key = event.GetKeyCode()
		modifiers = event.GetModifiers()
		if key == wx.WXK_ESCAPE or (key == wx.WXK_F4 and modifiers == wx.MOD_ALT):
			self.Close()
		else:
			event.Skip()

class OpcionesConsolas(wx.Dialog):
	def __init__(self, parent, frame, directorio, title=_("Lanzador de consolas")):
		super(OpcionesConsolas, self).__init__(parent, title=title)

		self.frame = frame
		self.directorio = directorio
		self.frame.is_run = True
		self.SetSize((300, 250))
		self.Centre()

		# Lista de opciones para el menú.
		self.opciones = [
			_("Abrir CMD aquí"),
			_("Abrir CMD como Administrador"),
			_("Abrir PowerShell aquí"),
			_("Abrir PowerShell como Administrador"),
			_("Abrir Windows Terminal aquí"),
			_("Abrir Windows Terminal como Administrador"),
			_("Abrir git-bash aquí"),
			_("Abrir git-bash como Administrador"),
			_("Abrir consola de Visual Studio (32-bit)"),
			_("Abrir consola de Visual Studio (32-bit) como Administrador"),
			_("Abrir consola de Visual Studio (64-bit)"),
			_("Abrir consola de Visual Studio (64-bit) como Administrador")
		]

		# Filtra las opciones basándote en la disponibilidad
		opciones_filtradas = self._filtrar_opciones()
		self.listBox = wx.ListBox(self, choices=opciones_filtradas, style=wx.LB_SINGLE)
		self.listBox.SetFocus()
		self.listBox.SetSelection(0)

		# Configura el layout.
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(self.listBox, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
		self.SetSizer(sizer)

		self.Bind(wx.EVT_CHAR_HOOK, self.onKeyPress)

	def _filtrar_opciones(self):
		"""
		Filtra las opciones disponibles para el lanzador de consolas según las terminales detectadas en el sistema.

		Returns:
			list: Lista de opciones filtradas.
		"""
		opciones_filtradas = self.opciones[:2]
		if self.frame.terminales['PowerShell']:
			opciones_filtradas.extend(self.opciones[2:4])
		if self.frame.terminales['wt']:
			opciones_filtradas.extend(self.opciones[4:6])
		if self.frame.git_disponibilidad:
			opciones_filtradas.extend(self.opciones[6:8])
		if self.frame.terminales['Visual Studio']:
			opciones_filtradas.extend(self.opciones[8:12])
		return opciones_filtradas

	def ejecutarSeleccion(self):
		"""
		Ejecuta la opción seleccionada en el lanzador de consolas.
		"""
		seleccion = self.opciones.index(self.listBox.GetString(self.listBox.GetSelection()))
		if seleccion == 0:
			self.abrirCMD(asAdmin=False)
		elif seleccion == 1:
			self.abrirCMD(asAdmin=True)
		elif seleccion == 2:
			self.abrirPOWERSHELL(asAdmin=False)
		elif seleccion == 3:
			self.abrirPOWERSHELL(asAdmin=True)
		elif seleccion == 4:
			self.abrirWT(asAdmin=False)
		elif seleccion == 5:
			self.abrirWT(asAdmin=True)
		elif seleccion == 6:
			self.abrirGITBASH(asAdmin=False)
		elif seleccion == 7:
			self.abrirGITBASH(asAdmin=True)
		elif seleccion == 8:
			self.abrirVS(bits="32", admin=False)
		elif seleccion == 9:
			self.abrirVS(bits="32", admin=True)
		elif seleccion == 10:
			self.abrirVS(bits="64", admin=False)
		elif seleccion == 11:
			self.abrirVS(bits="64", admin=True)
		self.frame.is_run = False
		self.Close()

	def abrirCMD(self, asAdmin):
		"""
		Abre la línea de comandos (CMD), opcionalmente con privilegios de administrador.

		Args:
			asAdmin (bool): Determina si CMD debe abrirse con privilegios de administrador.
		"""
		if asAdmin:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "cmd", True,), daemon=True).start()
		else:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "cmd", False,), daemon=True).start()

	def abrirPOWERSHELL(self, asAdmin):
		"""
		Abre la línea de comandos (PowerShell), opcionalmente con privilegios de administrador.

		Args:
			asAdmin (bool): Determina si PowerShell debe abrirse con privilegios de administrador.
		"""
		if asAdmin:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "powershell", True,), daemon=True).start()
		else:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "powershell", False,), daemon=True).start()

	def abrirWT(self, asAdmin):
		"""
		Abre la línea de comandos (Windows Terminal), opcionalmente con privilegios de administrador.

		Args:
			asAdmin (bool): Determina si Windows Terminal debe abrirse con privilegios de administrador.
		"""
		if asAdmin:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "wt", True,), daemon=True).start()
		else:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "wt", False,), daemon=True).start()

	def abrirGITBASH(self, asAdmin):
		"""
		Abre la línea de comandos (git-bash), opcionalmente con privilegios de administrador.

		Args:
			asAdmin (bool): Determina si git-bash debe abrirse con privilegios de administrador.
		"""
		if asAdmin:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "git-bash", True,), daemon=True).start()
		else:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, "git-bash", False,), daemon=True).start()

	def abrirVS(self, bits, admin):
		"""
		Abre la consola de Visual Studio de 32 o 64 bits, opcionalmente con privilegios de administrador.

		Args:
			bits (str): Puede ser '32' o '64' para especificar la versión de la consola.
			admin (bool): Determina si la consola debe abrirse con privilegios de administrador.
		"""
		script = 'vcvars32.bat' if bits == '32' else 'vcvars64.bat'
		vs_path = self.encontrar_ruta_vs(script)
		if vs_path:
			threading.Thread(target=self.frame.cmd_asincrona, args=(self.directorio, 'vs', admin, vs_path), daemon=True).start()

	def encontrar_ruta_vs(self, script):
		"""
		Encuentra la ruta de un script de inicialización de Visual Studio.

		Args:
			script (str): Nombre del script a buscar (ej., 'vcvars32.bat' o 'vcvars64.bat').

		Returns:
			str or None: Ruta al script encontrado, o None si no se encuentra.
		"""
		rutas_vs = ["C:\\Program Files\\Microsoft Visual Studio", "C:\\Program Files (x86)\\Microsoft Visual Studio"]
		for ruta in rutas_vs:
			for root, dirs, files in os.walk(ruta):
				if script in files:
					return os.path.join(root, script)
		return None

	def onKeyPress(self, event):
		"""
		Controlador de eventos para gestionar atajos de teclado en el lanzador de consolas.

		Args:
			event (Event): Evento asociado.
		"""
		if event.GetKeyCode() == wx.WXK_RETURN:
			self.ejecutarSeleccion()
		elif event.GetKeyCode() == wx.WXK_ESCAPE:
			self.frame.is_run = False
			self.Close()
		event.Skip()
