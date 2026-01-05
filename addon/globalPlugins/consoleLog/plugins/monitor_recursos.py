# -*- coding: utf-8 -*-
# consoleLog - Plugin Monitor de Recursos Lite
# Copyright (C) 2026 Héctor J. Benítez Corredera / Antigravity

import shutil
import ctypes
import os
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class PluginMonitorRecursos(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Monitor de Recursos"),
		version="1.0.0",
		descripcion=_("Muestra información básica de recursos del sistema"),
		autor="Héctor J. Benítez / Antigravity",
		categoria="utilidades"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		res = []
		
		# Uso de disco
		try:
			total, used, free = shutil.disk_usage(os.getenv('SystemDrive', 'C:'))
			libre_gb = free // (2**30)
			res.append(_("Espacio libre en disco: {} GB").format(libre_gb))
		except:
			pass
			
		# Memoria (Windows API via ctypes)
		try:
			class MEMORYSTATUSEX(ctypes.Structure):
				_fields_ = [
					("dwLength", ctypes.c_ulong),
					("dwMemoryLoad", ctypes.c_ulong),
					("ullTotalPhys", ctypes.c_ulonglong),
					("ullAvailPhys", ctypes.c_ulonglong),
					("ullTotalPageFile", ctypes.c_ulonglong),
					("ullAvailPageFile", ctypes.c_ulonglong),
					("ullTotalVirtual", ctypes.c_ulonglong),
					("ullAvailVirtual", ctypes.c_ulonglong),
					("sullAvailExtendedVirtual", ctypes.c_ulonglong),
				]
			
			stat = MEMORYSTATUSEX()
			stat.dwLength = ctypes.sizeof(stat)
			ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
			
			carga = stat.dwMemoryLoad
			dispon_mb = stat.ullAvailPhys // (1024 * 1024)
			total_mb = stat.ullTotalPhys // (1024 * 1024)
			
			res.append(_("Uso de memoria RAM: {}%").format(carga))
			res.append(_("RAM disponible: {} MB de {} MB").format(dispon_mb, total_mb))
		except:
			res.append(_("No se pudo obtener información detallada de la memoria."))
			
		# Sesión NVDA
		import versionInfo
		res.append(_("Versión de NVDA: {}").format(versionInfo.version))
		
		return res

	def terminar(self):
		pass
