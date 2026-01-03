# -*- coding: utf-8 -*-
# consoleLog - Sistema de Plugins
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Sistema de gestión de plugins.

Proporciona:
- Carga dinámica de plugins
- Interfaz base para plugins
- Gestión del ciclo de vida de plugins
"""

import os
import importlib
import importlib.util
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Type, Any
from dataclasses import dataclass
from logHandler import log
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x


@dataclass
class MetadatosPlugin:
	"""Metadatos de un plugin."""
	nombre: str
	version: str
	descripcion: str
	autor: str
	categoria: str = "general"
	dependencias: List[str] = None
	
	def __post_init__(self):
		if self.dependencias is None:
			self.dependencias = []


class PluginBase(ABC):
	"""Clase base abstracta para todos los plugins.
	
	Todos los plugins deben heredar de esta clase e implementar
	los métodos abstractos requeridos.
	"""
	
	# Metadatos que deben ser definidos por cada plugin
	METADATOS: MetadatosPlugin = None
	
	def __init__(self):
		"""Inicializa el plugin base."""
		self._habilitado = True
		self._inicializado = False
	
	@property
	def habilitado(self) -> bool:
		"""Indica si el plugin está habilitado."""
		return self._habilitado
	
	@habilitado.setter
	def habilitado(self, valor: bool):
		"""Establece el estado de habilitación del plugin."""
		self._habilitado = valor
	
	@property
	def inicializado(self) -> bool:
		"""Indica si el plugin ha sido inicializado."""
		return self._inicializado
	
	@abstractmethod
	def inicializar(self) -> bool:
		"""Inicializa el plugin.
		
		Returns:
			True si la inicialización fue exitosa, False en caso contrario.
		"""
		pass
	
	@abstractmethod
	def ejecutar(self, **kwargs) -> Any:
		"""Ejecuta la funcionalidad principal del plugin.
		
		Args:
			**kwargs: Argumentos específicos del plugin.
		
		Returns:
			Resultado de la ejecución (depende del plugin).
		"""
		pass
	
	@abstractmethod
	def terminar(self):
		"""Libera recursos del plugin."""
		pass
	
	def obtener_metadatos(self) -> Optional[MetadatosPlugin]:
		"""Obtiene los metadatos del plugin.
		
		Returns:
			Metadatos del plugin o None si no están definidos.
		"""
		return self.METADATOS


class GestorPlugins:
	"""Gestor principal de plugins.
	
	Proporciona funcionalidades para:
	- Descubrir plugins disponibles
	- Cargar y descargar plugins
	- Gestionar el ciclo de vida
	"""
	
	def __init__(self, configuracion):
		"""Inicializa el gestor de plugins.
		
		Args:
			configuracion: Instancia del gestor de configuración.
		"""
		self._configuracion = configuracion
		self._plugins: Dict[str, PluginBase] = {}
		self._directorio_plugins = self._obtener_directorio_plugins()
	
	def _obtener_directorio_plugins(self) -> str:
		"""Obtiene el directorio donde se encuentran los plugins.
		
		Returns:
			Ruta al directorio de plugins.
		"""
		directorio_actual = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		return os.path.join(directorio_actual, 'plugins')
	
	def _descubrir_plugins(self) -> List[str]:
		"""Descubre los plugins disponibles en el directorio de plugins.
		
		Returns:
			Lista de nombres de archivos de plugins.
		"""
		plugins = []
		
		if not os.path.exists(self._directorio_plugins):
			log.warning(f"consoleLog: Directorio de plugins no encontrado: {self._directorio_plugins}")
			return plugins
		
		for archivo in os.listdir(self._directorio_plugins):
			if archivo.endswith('.py') and not archivo.startswith('_'):
				nombre_plugin = archivo[:-3]  # Remover .py
				plugins.append(nombre_plugin)
		
		log.debug(f"consoleLog: Plugins descubiertos: {plugins}")
		return plugins
	
	def cargar_plugins(self):
		"""Carga todos los plugins habilitados."""
		plugins_habilitados = self._configuracion.plugins.plugins_habilitados
		plugins_descubiertos = self._descubrir_plugins()
		
		cargados = 0
		errores = []
		
		for nombre_plugin in plugins_descubiertos:
			if nombre_plugin in plugins_habilitados:
				if self._cargar_plugin(nombre_plugin):
					cargados += 1
				else:
					errores.append(nombre_plugin)
		
		if errores:
			log.error(f"consoleLog: Complemento cargado con errores. {cargados} plugins cargados, {len(errores)} fallidos: {', '.join(errores)}")
		else:
			log.info(f"consoleLog: Complemento cargado exitosamente. {cargados} plugins cargados.")
	
	def _cargar_plugin(self, nombre: str) -> bool:
		"""Carga un plugin específico.
		
		Args:
			nombre: Nombre del plugin a cargar.
		
		Returns:
			True si se cargó correctamente, False en caso contrario.
		"""
		try:
			# Construir ruta del módulo
			ruta_plugin = os.path.join(self._directorio_plugins, f"{nombre}.py")
			
			if not os.path.exists(ruta_plugin):
				log.warning(f"consoleLog: Plugin no encontrado: {ruta_plugin}")
				return False
			
			# Cargar módulo usando el sistema de paquetes de forma relativa al gestor
			package_parts = __name__.split('.')[:-2] # Eliminar 'nucleo.gestor_plugins'
			package_base = '.'.join(package_parts)
			nombre_modulo = f"{package_base}.plugins.{nombre}"
			modulo = importlib.import_module(nombre_modulo)
			
			# Buscar clase del plugin
			clase_plugin = self._encontrar_clase_plugin(modulo)
			
			if clase_plugin is None:
				log.warning(f"consoleLog: No se encontró clase PluginBase en {nombre}")
				return False
			
			# Instanciar plugin
			plugin = clase_plugin()
			
			# Inicializar plugin
			if plugin.inicializar():
				self._plugins[nombre] = plugin
				plugin._inicializado = True
				log.debug(f"consoleLog: Plugin cargado exitosamente: {nombre}")
				return True
			else:
				log.warning(f"consoleLog: Error al inicializar plugin: {nombre}")
				return False
			
		except Exception as e:
			log.error(f"consoleLog: Error al cargar plugin {nombre}: {e}")
			return False
	
	def _encontrar_clase_plugin(self, modulo) -> Optional[Type[PluginBase]]:
		"""Encuentra la clase de plugin en un módulo.
		
		Args:
			modulo: Módulo donde buscar.
		
		Returns:
			Clase del plugin o None si no se encuentra.
		"""
		for nombre_atributo in dir(modulo):
			atributo = getattr(modulo, nombre_atributo)
			try:
				if (isinstance(atributo, type) and 
					issubclass(atributo, PluginBase) and 
					atributo is not PluginBase):
					return atributo
			except TypeError:
				continue
		return None
	
	def descargar_plugins(self):
		"""Descarga todos los plugins cargados."""
		total = len(self._plugins)
		for nombre, plugin in list(self._plugins.items()):
			self._descargar_plugin(nombre)
		log.info(f"consoleLog: {total} plugins descargados correctamente.")
	
	def _descargar_plugin(self, nombre: str) -> bool:
		"""Descarga un plugin específico.
		
		Args:
			nombre: Nombre del plugin a descargar.
		
		Returns:
			True si se descargó correctamente.
		"""
		try:
			if nombre in self._plugins:
				plugin = self._plugins[nombre]
				plugin.terminar()
				del self._plugins[nombre]
				log.debug(f"consoleLog: Plugin descargado: {nombre}")
				return True
		except Exception as e:
			log.error(f"consoleLog: Error al descargar plugin {nombre}: {e}")
		return False
	
	def obtener_plugin(self, nombre: str) -> Optional[PluginBase]:
		"""Obtiene una instancia de un plugin.
		
		Args:
			nombre: Nombre del plugin.
		
		Returns:
			Instancia del plugin o None si no existe.
		"""
		return self._plugins.get(nombre)
	
	def listar_plugins_cargados(self) -> List[str]:
		"""Lista los nombres de los plugins cargados.
		
		Returns:
			Lista de nombres de plugins.
		"""
		return list(self._plugins.keys())
	
	def listar_plugins_disponibles(self) -> List[str]:
		"""Lista los plugins disponibles para cargar.
		
		Returns:
			Lista de nombres de plugins disponibles.
		"""
		return self._descubrir_plugins()
	
	def habilitar_plugin(self, nombre: str) -> bool:
		"""Habilita un plugin.
		
		Args:
			nombre: Nombre del plugin.
		
		Returns:
			True si se habilitó correctamente.
		"""
		if nombre not in self._configuracion.plugins.plugins_habilitados:
			self._configuracion.plugins.plugins_habilitados.append(nombre)
			self._configuracion.guardar_configuracion()
		
		if nombre not in self._plugins:
			return self._cargar_plugin(nombre)
		return True
	
	def deshabilitar_plugin(self, nombre: str) -> bool:
		"""Deshabilita un plugin.
		
		Args:
			nombre: Nombre del plugin.
		
		Returns:
			True si se deshabilitó correctamente.
		"""
		if nombre in self._configuracion.plugins.plugins_habilitados:
			self._configuracion.plugins.plugins_habilitados.remove(nombre)
			self._configuracion.guardar_configuracion()
		
		return self._descargar_plugin(nombre)
