# -*- coding: utf-8 -*-
# consoleLog - Módulo de Lectores
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Módulo de lectores de consola.

Contiene:
- GestorLectores: Interfaz unificada de lectura
- LectorConsolaClasica: Lectura de consolas CMD/PowerShell
- LectorWindowsTerminal: Lectura de Windows Terminal
"""

from .gestor_lectores import GestorLectores
from .lector_clasico import LectorConsolaClasica
from .lector_terminal import LectorWindowsTerminal

__all__ = [
	'GestorLectores',
	'LectorConsolaClasica',
	'LectorWindowsTerminal'
]
