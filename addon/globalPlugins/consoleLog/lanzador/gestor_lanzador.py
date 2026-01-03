# -*- coding: utf-8 -*-
# consoleLog - Gestor del Lanzador de Consolas
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Gestor del lanzador de consolas.

Proporciona funcionalidades para:
- Detectar consolas disponibles en el sistema
- Obtener el directorio actual del explorador
- Abrir consolas en directorios específicos
"""

import os
import subprocess
import ctypes
import json
import threading
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
from logHandler import log
import api
from comtypes.client import CreateObject as COMCreate

import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


@dataclass
class InfoConsola:
	"""Información de una consola disponible."""
	nombre: str
	identificador: str
	disponible: bool
	ruta: str = ""
	descripcion: str = ""


class GestorLanzador:
	"""Gestor del lanzador de consolas.
	
	Detecta y gestiona las consolas disponibles en el sistema
	para permitir su apertura desde el explorador de Windows.
	"""
	
	def __init__(self):
		"""Inicializa el gestor del lanzador."""
		self._shell = None
		self._consolas_cache: Dict[str, InfoConsola] = {}
		self._detectar_consolas()
	
	def _detectar_consolas(self):
		"""Detecta las consolas disponibles en el sistema."""
		self._consolas_cache.clear()
		
		# CMD siempre disponible
		self._consolas_cache['cmd'] = InfoConsola(
			nombre=_("CMD (Símbolo del sistema)"),
			identificador='cmd',
			disponible=True,
			ruta='cmd.exe',
			descripcion=_("Consola de comandos clásica de Windows")
		)
		
		# PowerShell
		self._detectar_powershell()
		
		# Windows Terminal
		self._detectar_windows_terminal()
		
		# Git Bash
		self._detectar_git_bash()
		
		# Visual Studio
		self._detectar_visual_studio()
		
		# PowerShell Core (v7+)
		self._detectar_powershell_core()
		
		# WSL (Windows Subsystem for Linux)
		self._detectar_wsl()
		
		log.debug(f"consoleLog: Consolas detectadas: {list(self._consolas_cache.keys())}")
	
	def _detectar_powershell(self):
		"""Detecta si PowerShell está disponible."""
		try:
			resultado = subprocess.Popen(
				['powershell.exe', '-Command', "echo $null"],
				creationflags=subprocess.CREATE_NO_WINDOW,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			resultado.communicate(timeout=5)
			
			self._consolas_cache['powershell'] = InfoConsola(
				nombre=_("PowerShell"),
				identificador='powershell',
				disponible=True,
				ruta='powershell.exe',
				descripcion=_("Windows PowerShell para automatización y scripts")
			)
		except Exception as e:
			log.debug(f"consoleLog: PowerShell no disponible: {e}")
			self._consolas_cache['powershell'] = InfoConsola(
				nombre=_("PowerShell"),
				identificador='powershell',
				disponible=False
			)
		
	def _detectar_powershell_core(self):
		"""Detecta si PowerShell Core (v7+) está disponible."""
		try:
			# pwsh suele estar en el PATH
			self._consolas_cache['pwsh'] = InfoConsola(
				nombre=_("PowerShell 7 (Core)"),
				identificador='pwsh',
				disponible=False,
				ruta='pwsh.exe',
				descripcion=_("Versión moderna y multiplataforma de PowerShell")
			)
			
			resultado = subprocess.Popen(
				['pwsh.exe', '-Command', "echo $null"],
				creationflags=subprocess.CREATE_NO_WINDOW,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			resultado.communicate(timeout=3)
			if resultado.returncode == 0:
				self._consolas_cache['pwsh'].disponible = True
		except:
			pass

	def _detectar_wsl(self):
		"""Detecta si WSL está instalado."""
		try:
			self._consolas_cache['wsl'] = InfoConsola(
				nombre=_("WSL (Linux)"),
				identificador='wsl',
				disponible=False,
				ruta='wsl.exe',
				descripcion=_("Subsistema de Windows para Linux")
			)
			
			resultado = subprocess.Popen(
				['wsl.exe', '--status'],
				creationflags=subprocess.CREATE_NO_WINDOW,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE
			)
			resultado.communicate(timeout=3)
			if resultado.returncode == 0:
				self._consolas_cache['wsl'].disponible = True
		except:
			pass
	
	def _detectar_windows_terminal(self):
		"""Detecta si Windows Terminal está disponible."""
		disponible = any(
			os.access(os.path.join(path, 'wt.exe'), os.X_OK)
			for path in os.environ.get("PATH", "").split(os.pathsep)
		)
		
		self._consolas_cache['wt'] = InfoConsola(
			nombre=_("Windows Terminal"),
			identificador='wt',
			disponible=disponible,
			ruta='wt.exe' if disponible else '',
			descripcion=_("Terminal moderna de Windows con pestañas y temas")
		)
	
	def _detectar_git_bash(self):
		"""Detecta si Git Bash está disponible."""
		disponible = False
		ruta_git = ""
		
		try:
			comando_ps = "Get-Command git | Select-Object -ExpandProperty Source | ConvertTo-Json"
			resultado = subprocess.Popen(
				["powershell", "-Command", comando_ps],
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				creationflags=subprocess.CREATE_NO_WINDOW
			)
			salida, unused_ = resultado.communicate(timeout=5)
			
			if resultado.returncode == 0 and salida:
				ruta_git_completa = json.loads(salida.decode('utf-8'))
				ruta_git = os.path.dirname(os.path.dirname(ruta_git_completa))
				ruta_git_bash = os.path.join(ruta_git, 'git-bash.exe')
				disponible = os.path.exists(ruta_git_bash)
				
		except Exception as e:
			log.debug(f"consoleLog: Git Bash no detectado: {e}")
		
		self._consolas_cache['git-bash'] = InfoConsola(
			nombre=_("Git Bash"),
			identificador='git-bash',
			disponible=disponible,
			ruta=ruta_git,
			descripcion=_("Terminal Bash de Git para Windows")
		)
	
	def _detectar_visual_studio(self):
		"""Detecta las consolas de Visual Studio disponibles."""
		rutas_vs = [
			"C:\\Program Files\\Microsoft Visual Studio",
			"C:\\Program Files (x86)\\Microsoft Visual Studio"
		]
		
		vs_32_encontrado = False
		vs_64_encontrado = False
		ruta_vs_32 = ""
		ruta_vs_64 = ""
		
		for ruta in rutas_vs:
			if os.path.exists(ruta):
				for root, dirs, files in os.walk(ruta):
					if 'vcvars32.bat' in files and not vs_32_encontrado:
						vs_32_encontrado = True
						ruta_vs_32 = os.path.join(root, 'vcvars32.bat')
					if 'vcvars64.bat' in files and not vs_64_encontrado:
						vs_64_encontrado = True
						ruta_vs_64 = os.path.join(root, 'vcvars64.bat')
					
					if vs_32_encontrado and vs_64_encontrado:
						break
				
				if vs_32_encontrado and vs_64_encontrado:
					break
		
		self._consolas_cache['vs-32'] = InfoConsola(
			nombre=_("Visual Studio Developer (32-bit)"),
			identificador='vs-32',
			disponible=vs_32_encontrado,
			ruta=ruta_vs_32,
			descripcion=_("Consola de desarrollador de Visual Studio (32 bits)")
		)
		
		self._consolas_cache['vs-64'] = InfoConsola(
			nombre=_("Visual Studio Developer (64-bit)"),
			identificador='vs-64',
			disponible=vs_64_encontrado,
			ruta=ruta_vs_64,
			descripcion=_("Consola de desarrollador de Visual Studio (64 bits)")
		)
	
	def obtener_consolas_disponibles(self) -> List[InfoConsola]:
		"""Obtiene la lista de consolas disponibles.
		
		Returns:
			Lista de consolas disponibles.
		"""
		return [c for c in self._consolas_cache.values() if c.disponible]
	
	def obtener_todas_consolas(self) -> List[InfoConsola]:
		"""Obtiene todas las consolas (disponibles o no).
		
		Returns:
			Lista de todas las consolas.
		"""
		return list(self._consolas_cache.values())
	
	def obtener_directorio_actual(self) -> Optional[str]:
		"""Obtiene el directorio del elemento seleccionado en el Explorador.
		
		Returns:
			Ruta del directorio o None si no se puede determinar.
		"""
		try:
			objeto = api.getForegroundObject()
			
			if not self._es_explorador(objeto):
				# Intentar obtener desde el escritorio
				return self._obtener_directorio_desktop()
			
			ruta_seleccion = self._obtener_ruta_seleccion(objeto)
			return self._encontrar_directorio_valido(ruta_seleccion)
			
		except Exception as e:
			log.error(f"consoleLog: Error al obtener directorio: {e}")
			return None
		finally:
			self._shell = None
	
	def _es_explorador(self, objeto=None) -> bool:
		"""Verifica si el objeto es el Explorador de Windows.
		
		Args:
			objeto: Objeto NVDA a verificar.
		
		Returns:
			True si es el Explorador.
		"""
		if objeto is None:
			objeto = api.getForegroundObject()
		
		return (objeto and objeto.appModule and 
				objeto.appModule.appName == 'explorer')
	
	def _obtener_ruta_seleccion(self, objeto) -> Optional[str]:
		"""Obtiene la ruta del elemento seleccionado.
		
		Args:
			objeto: Objeto del Explorador.
		
		Returns:
			Ruta del elemento seleccionado.
		"""
		try:
			if not self._shell:
				self._shell = COMCreate("shell.application")
			
			for ventana in self._shell.Windows():
				if ventana.hwnd == objeto.windowHandle:
					return str(ventana.Document.FocusedItem.path)
			
			# Es el escritorio
			return self._obtener_directorio_desktop()
			
		except Exception:
			# Intentar con PowerShell como fallback
			return self._obtener_ruta_via_powershell(objeto)
	
	def _obtener_ruta_via_powershell(self, objeto) -> Optional[str]:
		"""Obtiene la ruta usando PowerShell.
		
		Args:
			objeto: Objeto del Explorador.
		
		Returns:
			Ruta obtenida o None.
		"""
		try:
			si = subprocess.STARTUPINFO()
			si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
			
			cmd = (
				"$OutputEncoding = [console]::InputEncoding = [console]::OutputEncoding = "
				"New-Object System.Text.UTF8Encoding; "
				"(New-Object -ComObject 'Shell.Application').Windows() | "
				"ForEach-Object { echo \\\"$($_.HWND):$($_.Document.FocusedItem.Path)\\\" }"
			)
			
			p = subprocess.Popen(
				f'powershell.exe "{cmd}"',
				stdin=subprocess.DEVNULL,
				stdout=subprocess.PIPE,
				stderr=subprocess.DEVNULL,
				startupinfo=si,
				encoding="utf-8",
				text=True
			)
			stdout, unused_ = p.communicate(timeout=5)
			
			if p.returncode == 0 and stdout:
				for linea in stdout.splitlines():
					hwnd, ruta = linea.split(':', 1)
					if str(objeto.windowHandle) == hwnd:
						return ruta
						
		except Exception as e:
			log.debug(f"consoleLog: Error en obtención PS: {e}")
		
		return None
	
	def _obtener_directorio_desktop(self) -> str:
		"""Obtiene el directorio del escritorio.
		
		Returns:
			Ruta completa al escritorio.
		"""
		try:
			desktop_path = os.path.join(os.environ['USERPROFILE'], 'Desktop')
			nombre_objeto = api.getDesktopObject().objectWithFocus().name
			return os.path.join(desktop_path, nombre_objeto) if nombre_objeto else desktop_path
		except Exception:
			return os.path.join(os.environ['USERPROFILE'], 'Desktop')
	
	def _encontrar_directorio_valido(self, ruta: Optional[str]) -> Optional[str]:
		"""Encuentra el directorio válido más cercano.
		
		Args:
			ruta: Ruta a analizar.
		
		Returns:
			Directorio válido o None.
		"""
		if not isinstance(ruta, str):
			return None
		
		if os.path.isdir(ruta):
			return ruta
		
		# Buscar hacia arriba en la jerarquía
		partes = ruta.split(os.sep)
		for i in range(len(partes), 0, -1):
			directorio = os.sep.join(partes[:i])
			if os.path.isdir(directorio):
				return directorio
		
		return None
	
	def abrir_consola(
		self,
		tipo: str,
		directorio: str,
		como_admin: bool = False,
		ruta_script: Optional[str] = None
	) -> bool:
		"""Abre una consola en el directorio especificado.
		
		Args:
			tipo: Tipo de consola (cmd, powershell, wt, git-bash, vs).
			directorio: Directorio donde abrir la consola.
			como_admin: Si debe abrirse como administrador.
			ruta_script: Para VS, ruta al script de inicialización.
		
		Returns:
			True si se abrió correctamente.
		"""
		def _abrir():
			oldValue = ctypes.c_void_p()
			ctypes.windll.kernel32.Wow64DisableWow64FsRedirection(ctypes.byref(oldValue))
			
			try:
				ejecutable, parametros = self._construir_comando(
					tipo, directorio, ruta_script
				)
				
				operacion = 'runas' if como_admin else 'open'
				
				resultado = ctypes.windll.shell32.ShellExecuteW(
					None, operacion, ejecutable, parametros, None, 1
				)
				
				return resultado > 32
				
			finally:
				ctypes.windll.kernel32.Wow64RevertWow64FsRedirection(oldValue)
		
		hilo = threading.Thread(target=_abrir, daemon=True)
		hilo.start()
		return True
	
	def _construir_comando(
		self,
		tipo: str,
		directorio: str,
		ruta_script: Optional[str] = None
	) -> Tuple[str, str]:
		"""Construye el comando para abrir la consola.
		
		Args:
			tipo: Tipo de consola.
			directorio: Directorio destino.
			ruta_script: Script de inicialización (para VS).
		
		Returns:
			Tupla (ejecutable, parámetros).
		"""
		if tipo == 'cmd':
			return ('cmd.exe', f'/k pushd "{directorio}"')
		
		elif tipo == 'powershell':
			return (
				'powershell.exe',
				f'-NoExit -Command "Set-Location -LiteralPath \\"{directorio}\\""'
			)
		
		elif tipo == 'wt':
			return ('wt.exe', f'-d "{directorio}"')
		
		elif tipo == 'git-bash':
			info_git = self._consolas_cache.get('git-bash')
			ruta_git = info_git.ruta if info_git else ''
			return (
				os.path.join(ruta_git, 'git-bash.exe'),
				f'--cd="{directorio}"'
			)
		
		elif tipo in ['vs-32', 'vs-64']:
			info_vs = self._consolas_cache.get(tipo)
			script = ruta_script or (info_vs.ruta if info_vs else '')
			dir_script = os.path.dirname(script)
			return (
				'cmd.exe',
				f'/k pushd "{dir_script}" && call "{script}" && pushd "{directorio}"'
			)
		
		elif tipo == 'pwsh':
			return (
				'pwsh.exe',
				f'-NoExit -Command "Set-Location -LiteralPath \\"{directorio}\\""'
			)
			
		elif tipo == 'wsl':
			# Convertir ruta de Windows a ruta de WSL (ej: C:\ -> /mnt/c/)
			# Simplificado: wsl se encarga de iniciar en el CWD si se llama correctamente
			# Pero por seguridad usamos --cd
			return ('wsl.exe', f'--cd "{directorio}"')
		
		else:
			raise ValueError(_("Tipo de consola no soportado: {}").format(tipo))
