# -*- coding: utf-8 -*-
# consoleLog - Plugin Generador de Reportes IA
# Copyright (C) 2026 Héctor J. Benítez Corredera / Antigravity

import threading
import wx
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
from ..utilidades.ia_client import IAClient
import addonHandler
_ = addonHandler.initTranslation()
if not callable(_):
	_ = lambda x: x

class PluginAIReport(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Generador de Informe IA"),
		version="1.0.0",
		descripcion=_("Analiza el log completo y genera un reporte detallado con soluciones sugeridas"),
		autor="Héctor J. Benítez / Antigravity",
		categoria="ia"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		visor = kwargs.get('visor')
		texto = kwargs.get('texto', '')
		
		if not texto:
			wx.MessageBox(_("No hay contenido en la consola para analizar."), _("Informe IA"), wx.OK | wx.ICON_WARNING, visor)
			return
			
		# Diálogo de progreso
		progress = wx.ProgressDialog(
			_("IA pensando..."), 
			_("Analizando el log de consola para generar un informe detallado..."), 
			parent=visor, 
			style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
		)
		progress.Pulse()
		
		def _hilo_analisis():
			try:
				cliente = IAClient(visor._plugin._configuracion)
				prompt_sistema = (
					"Eres un experto en análisis de sistemas y depuración de software. "
					"Analiza el log de consola proporcionado y genera un reporte estructurado en Markdown que incluya: "
					"1. RESUMEN: Qué está ocurriendo en general.\n"
					"2. ERRORES DETECTADOS: Lista de fallos, advertencias o comportamientos anómalos.\n"
					"3. POSIBLES SOLUCIONES: Pasos específicos para resolver los problemas encontrados.\n"
					"Usa un tono profesional pero directo."
				)
				
				# Limitamos el texto si es demasiado largo (Gemini suele aguantar mucho, pero por seguridad)
				contexto = texto[-30000:] 
				respuesta = cliente.generar_contenido(contexto, prompt_sistema=prompt_sistema)
				
				wx.CallAfter(self._mostrar_reporte, visor, respuesta)
			except Exception as e:
				wx.CallAfter(wx.MessageBox, str(e), _("Error de IA"), wx.OK | wx.ICON_ERROR, visor)
			finally:
				wx.CallAfter(progress.Destroy)
				
		threading.Thread(target=_hilo_analisis).start()
		return None

	def _mostrar_reporte(self, visor, reporte):
		# Diálogo navegable para el reporte
		# Pero mejor definimos uno aquí o usamos el visor temporalmente
		dlg = wx.Dialog(visor, title=_("Informe de Análisis IA"), size=(600, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		txt = wx.TextCtrl(dlg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH | wx.TE_NOHIDESEL)
		txt.SetValue(reporte)
		
		sizer.Add(txt, 1, wx.EXPAND | wx.ALL, 10)
		btn = wx.Button(dlg, wx.ID_OK, label=_("Cerrar"))
		sizer.Add(btn, 0, wx.ALIGN_CENTER | wx.ALL, 10)
		
		dlg.SetSizer(sizer)
		dlg.Centre()
		txt.SetFocus()
		txt.SetInsertionPoint(0)
		dlg.ShowModal()
		dlg.Destroy()

	def terminar(self):
		pass
