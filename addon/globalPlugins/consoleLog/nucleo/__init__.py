# -*- coding: utf-8 -*-
# consoleLog - Módulo Nucleo
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Módulo nucleo del complemento.

Contiene:
- Configuración
- Gestión de plugins
"""

from .configuracion import (
	Configuracion,
	ConfiguracionVisor,
	ConfiguracionLanzador,
	ConfiguracionPlugins,
	ConfiguracionGeneral
)
from .gestor_plugins import (
	GestorPlugins,
	PluginBase,
	MetadatosPlugin
)

__all__ = [
	'Configuracion',
	'ConfiguracionVisor',
	'ConfiguracionLanzador',
	'ConfiguracionPlugins',
	'ConfiguracionGeneral',
	'GestorPlugins',
	'PluginBase',
	'MetadatosPlugin'
]
