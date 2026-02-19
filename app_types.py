###
# app_types.py
# Type definitions and type aliases for OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Protocol, Any, Dict, List, Optional, Tuple
from PIL.Image import Image as PILImage

# Type Aliases für bessere Lesbarkeit und Wiederverwendbarkeit

# Effekt-Typen
EffectConfig = Dict[str, bool | float]  # z.B. {'grayscale': True, 'sharpen_value': 2.5}
EffectOperations = Dict[str, bool | float]  # Alias für Effekt-Dictonaries

# Farb-Typen
RGBAColor = Tuple[int, int, int, int]  # (Red, Green, Blue, Alpha)
HexColor = str  # z.B. "#FFFFFF" oder "#FFFFFF80"

# GIF/Texture-Daten
GIFFrameList = List[PILImage]
TextureData = PILImage

# Konfigurationstypen
ConfigDict = Dict[str, Any]

# Canvas-DimensionenCanvasDimensions = Tuple[int, int]  # (width, height)

# Protocol für ModernApp (um Circular Imports zu vermeiden)
class ModernAppProtocol(Protocol):
	"""
	Protocol für die ModernApp-Klasse.
	Definiert die notwendigen Methoden und Attribute für Funktionen, die ModernApp benötigen.
	Dies vermeidet Circular Imports.
	"""
	
	# Attribute
	gif_frames: GIFFrameList
	gif_image: Optional[PILImage]
	texture_image: Optional[PILImage]
	frame_count: int
	current_frame: int
	width_var: Any  # tk.IntVar
	height_var: Any  # tk.IntVar
	bg_color: HexColor
	
	# Effekt-Variablen
	gif_grayscale: Any  # tk.BooleanVar
	gif_sharpen: Any
	gif_blur: Any
	gif_transparency: Any
	gif_colorintensity_active: Any
	gif_sharpen_value: Any  # tk.DoubleVar
	gif_blur_value: Any
	gif_transparency_value: Any
	gif_colorintensity: Any
	
	texture_grayscale: Any
	texture_sharpen: Any
	texture_blur: Any
	texture_transparency: Any
	texture_colorintensity_active: Any
	texture_sharpen_value: Any
	texture_blur_value: Any
	texture_transparency_value: Any
	texture_colorintensity: Any
	
	# Canvas und UI
	gif_canvas: Any  # tk.Canvas
	texture_canvas: Any  # tk.Canvas
	status: Any  # tk.Label
	root: Any  # tk.Tk
	
	# PhotoImage-Referenzen (muss behalten werden, sonst Garbage Collection)
	_gif_img_ref: Any  # Für GIF-Frame PhotoImage
	_texture_img_ref: Any  # Für Texture-Preview PhotoImage
	
	# Methoden
	def show_gif_frame(self) -> None: ...
	def show_texture(self) -> None: ...
	def get_config(self) -> ConfigDict: ...
