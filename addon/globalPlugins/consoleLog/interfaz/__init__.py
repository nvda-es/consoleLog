# -*- coding: utf-8 -*-
# consoleLog - Módulo de Interfaz
# Copyright (C) 2024-2026 Héctor J. Benítez Corredera <xebolax@gmail.com>
# Este archivo está cubierto por la Licencia Pública General de GNU.

"""
Módulo de interfaces gráficas.

Contiene:
- VisorConsola: Ventana del visor de contenido
- LanzadorDialogo: Diálogo para seleccionar consolas
"""

from .visor_consola import VisorConsola
from .lanzador_dialogo import LanzadorDialogo

__all__ = [
	'VisorConsola',
	'LanzadorDialogo'
]
