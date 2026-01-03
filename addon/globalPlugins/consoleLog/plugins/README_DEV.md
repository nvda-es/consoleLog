# Guía de Desarrollo de Plugins para consoleLog

Esta guía está dirigida a desarrolladores que deseen extender las capacidades de **consoleLog** mediante la creación de nuevos plugins.

## Versión del Sistema: 2026.01.03
**Autor:** Héctor J. Benítez Corredera

---

## 1. Arquitectura de Plugins

El sistema de plugins se basa en una arquitectura modular donde cada plugin es una clase Python independiente que hereda de una clase base común. Los plugins se cargan dinámicamente desde el directorio `globalPlugins/visorConsolasXD/plugins/`.

### Requisitos Técnicos
- **NVDA** instalado (entorno Python 3.11+).
- Conocimientos básicos de **wxPython** (para plugins con interfaz).
- Conocimientos del sistema de archivos y módulos de Python.

## 2. Clase Base: `PluginBase`

Todos los plugins deben heredar de `PluginBase` definida en `..nucleo.gestor_plugins`.

### Métodos Obligatorios:
- `inicializar(self) -> bool`: Se llama al cargar el plugin. Debe devolver `True` si la inicialización fue exitosa.
- `ejecutar(self, **kwargs) -> Any`: Método principal de acción. Recibe argumentos variables.
- `terminar(self)`: Se llama al descargar el plugin o cerrar NVDA.

### Metadatos:
Cada plugin debe definir un objeto `MetadatosPlugin` con:
- `nombre`: Nombre legible para el usuario.
- `version`: Versión del plugin.
- `descripcion`: Qué hace el plugin.
- `autor`: Quién creó el plugin.
- `categoria`: Categoría (utilidades, ia, edición, etc.).

## 3. Ejemplo 1: Plugin Sencillo (Procesamiento de Texto)

Este plugin toma el texto del visor y cuenta cuántas palabras hay.

```python
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin
import addonHandler
_ = addonHandler.initTranslation()

class PluginContadorPalabras(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre=_("Contador de Palabras"),
		version="1.0.0",
		descripcion=_("Cuenta las palabras en el visor"),
		autor="Héctor J. Benítez Corredera",
		categoria="utilidades"
	)

	def inicializar(self):
		return True

	def ejecutar(self, **kwargs):
		texto = kwargs.get('texto', '')
		palabras = len(texto.split())
		# El visor maneja listas de strings mostrando un diálogo de selección
		return [f"Total de palabras: {palabras}"]

	def terminar(self):
		pass
```

## 4. Ejemplo 2: Plugin Avanzado (Interfaz Propia)

Si necesitas una ventana propia (como el plugin de Google AI):

```python
import wx
from ..nucleo.gestor_plugins import PluginBase, MetadatosPlugin

class PluginMiVentana(PluginBase):
	METADATOS = MetadatosPlugin(
		nombre="Mi Plugin Visual",
		version="1.0.0",
		descripcion="Muestra una ventana personalizada",
		autor="Héctor J. Benítez Corredera"
	)

	def inicializar(self):
		self._frame = None
		return True

	def ejecutar(self, **kwargs):
		parent = kwargs.get('visor') # El visor de consola actual
		if not self._frame:
			self._frame = wx.Frame(parent, title="Ventana del Plugin")
			self._frame.Show()
		else:
			self._frame.Raise()

	def terminar(self):
		if self._frame: self._frame.Close()
```

## 5. Argumentos Recibidos en `ejecutar()`

Cuando el visor llama a un plugin, envía los siguientes `kwargs`:
- `texto`: El contenido completo del texto visible en la consola.
- `seleccionado`: El texto que el usuario tiene seleccionado actualmente.
- `visor`: La instancia del objeto `VisorConsola` (un `wx.Frame`), útil para actuar como 'parent' de nuevos diálogos.
- `tipo_consola`: (Solo en llamadas directas desde scripts) 'clasica' o 'terminal'.
- `objeto`: (Solo en llamadas directas) El objeto NVDA de la ventana enfocada.

## 6. Integración con la Configuración

Para acceder a la configuración global desde un plugin:

```python
# Dentro de un método del plugin
configuracion = self._visor._plugin._configuracion
# O si tienes acceso al visor
config = visor._plugin._configuracion
```

## 7. Consejos de Desarrollo

1. **Traducciones**: Usa `addonHandler.initTranslation()` para que tu plugin sea multi-idioma.
2. **Hilos**: Si realizas peticiones de red (como en Google AI), usa `threading.Thread` para no congelar la interfaz de NVDA.
3. **Log Handler**: Usa `logHandler.log` para depurar errores.
4. **Seguridad**: Si manejas claves API, codifícalas o usa métodos de almacenamiento seguro.

---
© 2026 Héctor J. Benítez Corredera. Todos los derechos reservados.
