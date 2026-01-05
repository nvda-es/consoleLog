# -*- coding: utf-8 -*-
# consoleLog - Módulo de Configuración
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Módulo de configuración del complemento.

Gestiona todas las configuraciones del complemento incluyendo:
- Preferencias del usuario
- Configuración de plugins
- Rutas y directorios
"""

import os
import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from logHandler import log
import globalVars


@dataclass
class ConfiguracionVisor:
	"""Configuración del visor de consola."""
	recordar_tamano: bool = True
	ancho: int = 800
	alto: int = 600
	maximizado: bool = True
	fuente_monoespaciada: bool = True
	tamanio_fuente: int = 10
	sonidos_seguimiento: bool = True
	categorizar_plugins: bool = True
	intervalo_seguimiento: int = 2
	sonidos_al_actualizar: bool = False


@dataclass
class ConfiguracionLanzador:
	"""Configuración del lanzador de consolas."""
	recordar_ultima_opcion: bool = False
	ultima_opcion: int = 0
	mostrar_consolas_no_disponibles: bool = False


@dataclass
class ConfiguracionPlugins:
	"""Configuración de plugins."""
	plugins_habilitados: list = field(default_factory=lambda: [
		'clic_derecho', 
		'copiar_salida', 
		'historial_comandos', 
		'extractor_datos', 
		'filtro_log',
		'json_beauty',
		'timestamp_converter',
		'base64_decoder',
		'calculadora_express',
		'resumen_actividad',
		'google_ai',
		'stacktrace_analyzer',
		'monitor_recursos',
		'ai_report_generator',
		'jwt_decoder',
		'sql_formatter'
	])
	auto_cargar_plugins: bool = True


@dataclass
class ConfiguracionGoogleAI:
	"""Configuración para el plugin de Google AI."""
	api_keys_codificadas: str = "" # Base64 del bloque de texto
	modelo_actual: str = "gemini-1.5-flash"
	mantener_historial: bool = True
	prompt_sistema: str = "Eres un asistente útil y experto en depuración de código y análisis de logs de consola."


@dataclass
class ConfiguracionAlertas:
	"""Configuración de alertas y marcadores de texto."""
	habilitar_alertas: bool = True
	patrones: List[Dict[str, Any]] = field(default_factory=lambda: [
		{"patron": "ERROR", "voz": True, "sonido": True},
		{"patron": "CRITICAL", "voz": True, "sonido": True},
		{"patron": "FATAL", "voz": True, "sonido": True}
	])

@dataclass
class ConfiguracionGeneral:
	"""Configuración general del complemento."""
	visor: ConfiguracionVisor = field(default_factory=ConfiguracionVisor)
	lanzador: ConfiguracionLanzador = field(default_factory=ConfiguracionLanzador)
	plugins: ConfiguracionPlugins = field(default_factory=ConfiguracionPlugins)
	google_ai: ConfiguracionGoogleAI = field(default_factory=ConfiguracionGoogleAI)
	alertas: ConfiguracionAlertas = field(default_factory=ConfiguracionAlertas)


class Configuracion:
	"""Gestor de configuración del complemento.
	
	Proporciona métodos para:
	- Cargar y guardar configuración
	- Acceder a secciones específicas
	- Manejar valores por defecto
	"""
	
	# Nombre del archivo de configuración
	NOMBRE_ARCHIVO_CONFIG = "consoleLog_config.json"
	
	def __init__(self):
		"""Inicializa el gestor de configuración."""
		self._ruta_config = self._obtener_ruta_configuracion()
		self._config = ConfiguracionGeneral()
		self._cargar_configuracion()
	
	def _obtener_ruta_configuracion(self) -> str:
		"""Obtiene la ruta del archivo de configuración.
		
		Returns:
			Ruta completa al archivo de configuración.
		"""
		# Usar el directorio de configuración de NVDA
		directorio_config = globalVars.appArgs.configPath
		return os.path.join(directorio_config, self.NOMBRE_ARCHIVO_CONFIG)
	
	def _cargar_configuracion(self):
		"""Carga la configuración desde el archivo."""
		try:
			if os.path.exists(self._ruta_config):
				with open(self._ruta_config, 'r', encoding='utf-8') as archivo:
					datos = json.load(archivo)
					self._aplicar_datos(datos)
				log.debug(f"consoleLog: Configuración cargada desde {self._ruta_config}")
		except Exception as e:
			log.warning(f"consoleLog: Error al cargar configuración, usando valores por defecto: {e}")
			self._config = ConfiguracionGeneral()
	
	def _aplicar_datos(self, datos: Dict[str, Any]):
		"""Aplica los datos cargados a la configuración de forma incremental.
		
		Args:
			datos: Diccionario con los datos de configuración.
		"""
		def actualizar_objeto(obj, nuevos_datos):
			for clave, valor in nuevos_datos.items():
				if hasattr(obj, clave):
					setattr(obj, clave, valor)

		if 'visor' in datos:
			actualizar_objeto(self._config.visor, datos['visor'])
		if 'lanzador' in datos:
			actualizar_objeto(self._config.lanzador, datos['lanzador'])
		if 'plugins' in datos:
			if 'plugins_habilitados' in datos['plugins']:
				self._config.plugins.plugins_habilitados = datos['plugins']['plugins_habilitados']
			
			if 'auto_cargar_plugins' in datos['plugins']:
				self._config.plugins.auto_cargar_plugins = datos['plugins']['auto_cargar_plugins']
		
		if 'google_ai' in datos:
			actualizar_objeto(self._config.google_ai, datos['google_ai'])
		if 'alertas' in datos:
			actualizar_objeto(self._config.alertas, datos['alertas'])
	
	def guardar_configuracion(self):
		"""Guarda la configuración actual en el archivo."""
		try:
			datos = {
				'visor': asdict(self._config.visor),
				'lanzador': asdict(self._config.lanzador),
				'plugins': asdict(self._config.plugins),
				'google_ai': asdict(self._config.google_ai),
				'alertas': asdict(self._config.alertas)
			}
			
			with open(self._ruta_config, 'w', encoding='utf-8') as archivo:
				json.dump(datos, archivo, indent=2, ensure_ascii=False)
			
			log.debug(f"consoleLog: Configuración guardada en {self._ruta_config}")
		except Exception as e:
			log.error(f"consoleLog: Error al guardar configuración: {e}")
	
	@property
	def visor(self) -> ConfiguracionVisor:
		"""Obtiene la configuración del visor."""
		return self._config.visor
	
	@property
	def lanzador(self) -> ConfiguracionLanzador:
		"""Obtiene la configuración del lanzador."""
		return self._config.lanzador
	
	@property
	def plugins(self) -> ConfiguracionPlugins:
		"""Obtiene la configuración de plugins."""
		return self._config.plugins
	
	@property
	def google_ai(self) -> ConfiguracionGoogleAI:
		"""Obtiene la configuración de Google AI."""
		return self._config.google_ai
	
	@property
	def alertas(self) -> ConfiguracionAlertas:
		"""Obtiene la configuración de alertas."""
		return self._config.alertas
	
	def obtener_valor(self, seccion: str, clave: str, valor_defecto: Any = None) -> Any:
		"""Obtiene un valor específico de la configuración.
		
		Args:
			seccion: Nombre de la sección (visor, lanzador, plugins).
			clave: Nombre de la clave.
			valor_defecto: Valor a retornar si no existe la clave.
		
		Returns:
			El valor de la configuración o el valor por defecto.
		"""
		try:
			config_seccion = getattr(self._config, seccion, None)
			if config_seccion:
				return getattr(config_seccion, clave, valor_defecto)
		except Exception:
			pass
		return valor_defecto
	
	def establecer_valor(self, seccion: str, clave: str, valor: Any):
		"""Establece un valor específico en la configuración.
		
		Args:
			seccion: Nombre de la sección.
			clave: Nombre de la clave.
			valor: Valor a establecer.
		"""
		try:
			config_seccion = getattr(self._config, seccion, None)
			if config_seccion and hasattr(config_seccion, clave):
				setattr(config_seccion, clave, valor)
		except Exception as e:
			log.error(f"consoleLog: Error al establecer valor de configuración: {e}")
	
	def restablecer_valores_defecto(self):
		"""Restablece toda la configuración a los valores por defecto."""
		self._config = ConfiguracionGeneral()
		self.guardar_configuracion()
		log.info("consoleLog: Configuración restablecida a valores por defecto")
