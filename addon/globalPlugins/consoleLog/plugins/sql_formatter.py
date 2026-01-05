# -*- coding: utf-8 -*-
# consoleLog - Plugin Formateador SQL
# Copyright (C) 2026 Héctor J. Benítez / Antigravity

import re
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class PluginSQLFormatter(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Formateador SQL Lite"),
		version="1.0.0",
		descripcion=_("Intenta dar formato legible a consultas SQL"),
		autor="Héctor J. Benítez / Antigravity",
		categoria="edición"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		texto = kwargs.get('seleccionado') or kwargs.get('texto', '')
		
		# Palabras clave para romper línea
		keywords = [
			"SELECT", "FROM", "WHERE", "INNER JOIN", "LEFT JOIN", 
			"RIGHT JOIN", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "INSERT INTO", "UPDATE", "SET", "DELETE FROM"
		]
		
		# Reemplazo simple
		sql = texto
		# Eliminar saltos de línea y espacios extra previos
		sql = " ".join(sql.split())
		
		for kw in keywords:
			# Añadir salto de línea antes de la palabra clave
			sql = re.sub(fr'\b{kw}\b', f'\n{kw}', sql, flags=re.IGNORECASE)
		
		return [sql.strip()]

	def terminar(self):
		pass
