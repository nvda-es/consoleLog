# -*- coding: utf-8 -*-
# consoleLog - Módulo del Lanzador
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Módulo del lanzador de consolas.

Contiene:
- GestorLanzador: Gestor de consolas disponibles
- InfoConsola: Información de cada consola
"""

from .gestor_lanzador import GestorLanzador, InfoConsola

__all__ = [
	'GestorLanzador',
	'InfoConsola'
]
