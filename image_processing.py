###
# image_processing.py
# This file contains functions for processing images and GIFs within the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###


from typing import Any, List, Optional, Literal, Tuple
from PIL import Image, ImageTk
from PIL import ImageColor, ImageEnhance, ImageFilter
import math
import os
import threading
import queue
from threading_utils import gif_queue, texture_queue
from logging_config import get_logger
from exceptions import ImageProcessingError, TextureGenerationError, ThreadingError
from app_types import RGBAColor, EffectConfig, GIFFrameList, TextureData, ModernAppProtocol
from worker_pool import get_worker_pool
from event_bus import get_event_bus, EventType

logger = get_logger(__name__)

def calculate_optimal_grid(frame_count: int, prefer_single_row_odd: bool = True) -> tuple[int, int]:
	"""
	Berechnet optimale Raster-Aufteilung für Frames.
	Bevorzugt Layouts ohne Verschwendung (leere Zellen) und möglichst quadratische Form.
	
	Beispiele:
	- 10 Frames: 5x2 (besser als 4x3 mit 2 leeren Zellen)
	- 16 Frames: 4x4 (perfekt quadratisch)
	- 15 Frames: 5x3 (besser als 4x4 mit 1 leerer Zelle)
	
	Returns:
		(tiles_x, tiles_y) - Anzahl Spalten und Zeilen
	"""
	if frame_count <= 0:
		return (1, 1)
	if frame_count == 1:
		return (1, 1)
	
	# Finde beste Faktorisierung
	best_x, best_y = 1, frame_count
	best_waste = frame_count - 1  # Maximal mögliche Verschwendung
	best_ratio = float('inf')
	
	# Prüfe alle möglichen Aufteilungen bis sqrt(frame_count)
	# Wir müssen nur bis sqrt prüfen, da darüber hinaus die Faktoren sich wiederholen
	max_check = int(math.sqrt(frame_count * 2)) + 1  # Etwas Puffer für nicht-perfekte Quadrate
	
	for x in range(1, max_check + 1):
		y = math.ceil(frame_count / x)
		total_cells = x * y
		waste = total_cells - frame_count
		ratio = max(x, y) / min(x, y)  # Seitenverhältnis (>=1)
		
		# Entscheidungskriterien (Priorität absteigend):
		# 1. Minimiere Verschwendung (leere Zellen)
		# 2. Bei gleicher Verschwendung: bevorzuge quadratischere Form
		is_better = False
		if waste < best_waste:
			is_better = True
		elif waste == best_waste and ratio < best_ratio:
			is_better = True
		
		if is_better:
			best_x, best_y = x, y
			best_waste = waste
			best_ratio = ratio
	
	# Optional: Bei ungerader Frame-Zahl nicht einreihig anordnen.
	# Beispiel: 5 Frames -> 3x2 statt 5x1
	if not prefer_single_row_odd and frame_count > 3 and frame_count % 2 == 1 and min(best_x, best_y) == 1:
		compact_x = math.ceil(math.sqrt(frame_count))
		compact_y = math.ceil(frame_count / compact_x)
		best_x, best_y = compact_x, compact_y

	# Stelle sicher, dass tiles_x >= tiles_y (mehr Spalten als Zeilen)
	if best_x < best_y:
		best_x, best_y = best_y, best_x
	
	return (best_x, best_y)

def create_smart_scaled_texture(self: ModernAppProtocol, target_w: int, target_h: int, bg_rgba: RGBAColor, preview_mode: bool = True) -> Image.Image:
	"""
	Erstellt eine Texture mit intelligenter Skalierung:
	1. Berechnet optimale Größe basierend auf Frame-Größen
	2. Platziert Frames in optimaler Größe (ohne Ränder)
	3. Skaliert fertige Texture auf Zielgröße (nur wenn preview_mode=False)
	
	Args:
		self: Application instance
		target_w: Zielbreite
		target_h: Zielhöhe
		bg_rgba: Hintergrundfarbe
		preview_mode: True = nur Arbeitsbild (schnell), False = auf Zielgröße skalieren
	
	Returns:
		Arbeitsbild (preview_mode=True) oder skalierte Texture (preview_mode=False)
	"""
	try:
		frame_count = self.frame_count
		prefer_single_row_odd = True
		odd_row_var = getattr(self, 'odd_frames_single_row_var', None)
		if odd_row_var is not None:
			try:
				prefer_single_row_odd = bool(odd_row_var.get())
			except Exception:
				prefer_single_row_odd = True
		tiles_x, tiles_y = calculate_optimal_grid(frame_count, prefer_single_row_odd=prefer_single_row_odd)
		
		# Ermittle durchschnittliche Frame-Größe
		if self.gif_frames:
			first_frame = self.gif_frames[0]
			frame_w, frame_h = first_frame.size
		else:
			frame_w, frame_h = 256, 256
		
		# STEP 1: Berechne optimale Texture-Größe (ohne Ränder)
		optimal_w = tiles_x * frame_w
		optimal_h = tiles_y * frame_h
		
		if preview_mode:
			logger.info(f"Smart scale (preview): Optimal size {optimal_w}x{optimal_h}")
		else:
			logger.info(f"Smart scale (save): Optimal size {optimal_w}x{optimal_h} → Target size {target_w}x{target_h}")
		
		# STEP 2: Erstelle Texture in optimaler Größe
		optimal_sheet = Image.new("RGBA", (optimal_w, optimal_h), bg_rgba)
		
		for idx, frame in enumerate(self.gif_frames):
			tx = idx % tiles_x
			ty = idx // tiles_x
			
			# Frame mit Effekten, aber in Original-Größe
			f = apply_effects(self, frame, prefix="texture")
			
			# Stelle sicher dass f RGBA ist
			if f.mode != "RGBA":
				f = f.convert("RGBA")
			
			# Position berechnen
			x = tx * frame_w
			y = ty * frame_h
			
			# Frame direkt platzieren (ohne Resize)
			sheet_patch = optimal_sheet.crop((x, y, x + frame_w, y + frame_h))
			blended_patch = Image.alpha_composite(sheet_patch, f)
			optimal_sheet.paste(blended_patch, (x, y))
		
		# STEP 3: Skaliere auf Zielgröße (nur wenn nicht preview_mode)
		if not preview_mode and (optimal_w, optimal_h) != (target_w, target_h):
			scaled_sheet = optimal_sheet.resize((target_w, target_h), Image.Resampling.LANCZOS)
			logger.debug(f"Scaled from {optimal_w}x{optimal_h} to {target_w}x{target_h}")
			return scaled_sheet
		else:
			return optimal_sheet
		
	except Exception as e:
		logger.error(f"Smart scale failed: {e}", exc_info=True)
		# Fallback: Leere Textur zurückgeben
		fallback_sheet = Image.new("RGBA", (target_w, target_h), bg_rgba)
		return fallback_sheet

def _create_checkerboard_background(size: Tuple[int, int], square_size: int = 8) -> Image.Image:
	"""
	Creates a checkerboard pattern background for showing transparency.
	
	Args:
		size: (width, height) of the image
		square_size: Size of each checkerboard square in pixels
	
	Returns:
		Image with checkerboard pattern
	"""
	width, height = size
	
	# Erstelle Pixel-Liste für das Schachbrett
	pixels = []
	
	for y in range(height):
		for x in range(width):
			# Berechne Position im Schachbrett
			square_x = (x // square_size) % 2
			square_y = (y // square_size) % 2
			
			# Alterniere zwischen grau und weiß
			if (square_x + square_y) % 2 == 0:
				pixels.append((200, 200, 200))  # Hellgrau
			else:
				pixels.append((255, 255, 255))  # Weiß
	
	# Erstelle und fülle das Bild
	img = Image.new('RGB', size)
	img.putdata(pixels)
	
	return img

def _apply_bg_to_image_with_transparency(self: Any, img: Image.Image, show_transparency: bool = True) -> Image.Image:
	"""
	Applies background to image, optionally showing transparency with checkerboard.
	
	Args:
		self: The application instance
		img: The image to process
		show_transparency: Whether to show transparent areas with checkerboard pattern
	
	Returns:
		Image for display in GUI
	"""
	if img is None:
		return None
	
	try:
		# Stelle sicher dass img RGBA ist
		if img.mode != 'RGBA':
			img = img.convert('RGBA')
		
		# Wenn show_transparency, nutze Schachbrett statt Hintergrundfarbe
		if show_transparency:
			# Erstelle Schachbrett-Hintergrund als RGBA (muss gleicher Mode sein!)
			checkerboard = _create_checkerboard_background(img.size, square_size=8)
			# Konvertiere zu RGBA für alpha_composite
			checkerboard = checkerboard.convert('RGBA')
			# Composite image über Schachbrett
			result = Image.alpha_composite(checkerboard, img)
			# Zu RGB für Tkinter
			return result.convert('RGB')
		else:
			# Nutze normale Hintergrundfarbe
			return _apply_bg_to_image(self, img)
	
	except Exception as e:
		logger.error(f"Error applying background with transparency: {e}", exc_info=True)
		# Fallback: Nutze normale Hintergrundfarbe
		return _apply_bg_to_image(self, img)

def _apply_bg_to_image(self: Any, img: Image.Image) -> Image.Image:
	"""Wendet die Hintergrundfarbe auf ein RGBA-Bild an für korrekte Anzeige in Tkinter"""
	if img is None:
		return None
	
	try:
		# Hintergrundfarbe parsen
		bg_color = getattr(self, 'bg_color', '#00000000')
		bg_rgba: tuple[int, int, int, int] = (0, 0, 0, 0)
		
		try:
			if isinstance(bg_color, str) and len(bg_color) == 9 and bg_color.startswith('#'):
				# Format: #RRGGBBAA
				r = int(bg_color[1:3], 16)
				g = int(bg_color[3:5], 16)
				b = int(bg_color[5:7], 16)
				a = int(bg_color[7:9], 16)
				bg_rgba = (r, g, b, a)
			elif isinstance(bg_color, str) and len(bg_color) == 7 and bg_color.startswith('#'):
				# Format: #RRGGBB (vollständig undurchsichtig)
				r = int(bg_color[1:3], 16)
				g = int(bg_color[3:5], 16)
				b = int(bg_color[5:7], 16)
				bg_rgba = (r, g, b, 255)
		except Exception:
			bg_rgba = (0, 0, 0, 0)
		
		# Wenn Hintergrund vollständig transparent, nicht zusammenmischen
		if bg_rgba[3] == 0:
			return img
		
		# Hintergrund RGB (ohne Alpha)
		bg_rgb = bg_rgba[:3]
		
		# Bild sicherstellen ist RGBA
		if img.mode != "RGBA":
			img = img.convert("RGBA")
		
		# Hintergrundbild erstellen
		bg = Image.new("RGBA", img.size, bg_rgba)
		
		# Bild auf Hintergrund zusammenstellen
		combined = Image.alpha_composite(bg, img)
		
		# Zu RGB konvertieren (Tkinter PhotoImage unterstützt RGBA nicht gut)
		result = combined.convert("RGB")
		return result
	except Exception:
		# Fallback: Original zurückgeben
		if img.mode == "RGBA":
			return img.convert("RGB")
		return img

def _resize_to_fit(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
	"""
	Skaliert ein Bild auf die Zielgröße, behält das Seitenverhältnis und füllt mit schwarzem Hintergrund auf.
	"""
	if target_w < 10 or target_h < 10:
		return img.resize((256, 256), Image.Resampling.LANCZOS)
	
	# Berechne Seitenverhältnisse
	img_ratio = img.width / img.height
	target_ratio = target_w / target_h
	
	# Berechne die beste Skalierungsgröße
	if img_ratio > target_ratio:
		# Bild ist breiter: skaliere nach Breite
		new_w = target_w
		new_h = int(target_w / img_ratio)
	else:
		# Bild ist höher: skaliere nach Höhe
		new_h = target_h
		new_w = int(target_h * img_ratio)
	
	# Skaliere das Bild
	img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
	
	# Erstelle Hintergrund-Bild mit schwarzem Hintergrund
	background = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 255))
	
	# Berechne Position zum Zentrieren
	x = (target_w - new_w) // 2
	y = (target_h - new_h) // 2
	
	# Paste skaliertes Bild auf schwarzem Hintergrund
	background.paste(img_resized, (x, y), img_resized if img_resized.mode == "RGBA" else None)
	
	return background

def _process_gif_frame_worker(self: ModernAppProtocol, current_frame: int, canvas_w: int, canvas_h: int, texture_w: int, texture_h: int) -> None:
	"""Worker-Thread für GIF-Frame-Verarbeitung"""
	try:
		if not self.gif_frames or current_frame < 0 or current_frame >= len(self.gif_frames):
			gif_queue.put((self, None))
			return
		
		frame = self.gif_frames[current_frame]
		max_w = min(canvas_w, texture_w) if texture_w > 10 else canvas_w
		max_h = min(canvas_h, texture_h) if texture_h > 10 else canvas_h
		if max_w < 10 or max_h < 10:
			max_w, max_h = 256, 256
		
		# Skaliere mit proportionalem Seitenverhältnis und Letterboxing
		frame = _resize_to_fit(frame, max_w, max_h)
		frame = apply_effects(self, frame, prefix="gif")
		gif_queue.put((self, frame))
	except MemoryError as e:
		logger.error(f"Memory error in GIF frame processing: {e}")
		gif_queue.put((self, None))
	except Exception as e:
		logger.error(f"Error in GIF frame processing: {e}", exc_info=True)
		gif_queue.put((self, None))

def _check_gif_queue(self: ModernAppProtocol) -> None:
	"""Prüft die GIF-Queue und aktualisiert die Canvas"""
	try:
		while True:
			self_ref, processed_frame = gif_queue.get_nowait()
			if self_ref is self:
				if processed_frame is not None:
					# GIF-Frame ohne Hintergrundfarbe anzeigen (transparent)
					img = ImageTk.PhotoImage(processed_frame)
					self._gif_img_ref = img
					self.gif_canvas.config(image=img)
				# Textur-Update NICHT bei jedem Frame (zu langsam)
				# Wird nur bei Frame-Änderungen (Add/Remove) oder Einstellungsänderungen aufgerufen
				return
	except queue.Empty:
		pass  # Kein Element in Queue
	except Exception as e:
		logger.error(f"Error processing GIF frame from queue: {type(e).__name__}: {e}", exc_info=False)
	# Wiederholen
	if hasattr(self, 'root') and self.root:
		self.root.after(10, lambda: _check_gif_queue(self))

def show_gif_frame(self: ModernAppProtocol) -> None:
	"""Zeigt den aktuellen GIF-Frame mit Threading"""
	if not self.gif_frames:
		self.gif_canvas.config(image="")
		self.show_texture()
		return
	
	try:
		canvas_w = self.gif_canvas.winfo_width()
		canvas_h = self.gif_canvas.winfo_height()
		texture_w = self.texture_canvas.winfo_width()
		texture_h = self.texture_canvas.winfo_height()
		
		# Worker über Pool starten (nicht neuer Thread jedes Mal)
		pool = get_worker_pool(max_workers=2)
		task_name = f"gif_frame_{self.current_frame}"
		pool.submit(
			task_name,
			_process_gif_frame_worker,
			self, self.current_frame, canvas_w, canvas_h, texture_w, texture_h
		)
		
		# Queue-Prüfung starten
		_check_gif_queue(self)
	except Exception as e:
		from tkinter import messagebox
		messagebox.showerror("Fehler", f"Fehler bei GIF-Vorschau: {e}")

def _process_texture_worker(self: ModernAppProtocol) -> None:
	"""Worker-Thread für Texture-Sheet-Verarbeitung"""
	try:
		from tkinter import messagebox
		from PIL import ImageColor
		
		tex_w = self.width_var.get() if self.width_var.get() > 0 else 2048
		tex_h = self.height_var.get() if self.height_var.get() > 0 else 2048
		
		# Hintergrundfarbe parsen - unterstützt #RRGGBBAA Format
		bg_color = getattr(self, 'bg_color', '#00000000')
		bg_rgba: tuple[int, int, int, int] = (0, 0, 0, 0)  # Default: transparent
		try:
			if isinstance(bg_color, str) and len(bg_color) == 9 and bg_color.startswith('#'):
				# Format: #RRGGBBAA
				r = int(bg_color[1:3], 16)
				g = int(bg_color[3:5], 16)
				b = int(bg_color[5:7], 16)
				a = int(bg_color[7:9], 16)
				bg_rgba = (r, g, b, a)
			elif isinstance(bg_color, str) and len(bg_color) == 7 and bg_color.startswith('#'):
				# Format: #RRGGBB (vollständig undurchsichtig)
				color_result = ImageColor.getcolor(bg_color, "RGBA")
				# Stelle sicher, dass wir ein 4er-Tupel haben
				if isinstance(color_result, tuple) and len(color_result) >= 3:
					bg_rgba = (int(color_result[0]), int(color_result[1]), int(color_result[2]), 255)
			else:
				bg_rgba = (0, 0, 0, 0)
		except Exception:
			bg_rgba = (0, 0, 0, 0)

		# Sheet erzeugen
		try:
			use_source_image = getattr(self, 'texture_use_source_image', False)
			source_image = getattr(self, 'texture_source_image', None)
			if use_source_image and source_image is not None:
				# Direkt geladene Textur verwenden (Effekte anwenden)
				sheet = source_image
				if sheet.mode != "RGBA":
					sheet = sheet.convert("RGBA")
				sheet = apply_effects(self, sheet, prefix="texture")
			elif not self.gif_frames:
				sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
			else:
				# INTELLIGENTE SKALIERUNG: Arbeitsbild für Vorschau (SCHNELL!)
				sheet = create_smart_scaled_texture(self, tex_w, tex_h, bg_rgba, preview_mode=True)
			# WICHTIG: Sheet als aktuelle Textur speichern (Arbeitsbild, nicht skaliert)
			self.texture_image = sheet
		except MemoryError as e:
			logger.error(f"Memory error in texture generation: {e}")
			sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
			self.texture_image = sheet
		except Exception as e:
			logger.error(f"Error in texture generation: {e}", exc_info=True)
			sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
			self.texture_image = sheet

		# Vorschau erzeugen
		try:
			canvas_w = self.texture_canvas.winfo_width()
			canvas_h = self.texture_canvas.winfo_height()
			if canvas_w < 10 or canvas_h < 10:
				canvas_w, canvas_h = 256, 256
			preview = self.texture_image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
			texture_queue.put((self, preview))
		except MemoryError as e:
			logger.error(f"Memory error in texture preview generation: {e}")
			texture_queue.put((self, None))
		except Exception as e:
			logger.error(f"Error in texture preview generation: {e}", exc_info=True)
			texture_queue.put((self, None))
	except Exception as e:
		logger.error(f"Fatal error in texture worker thread: {e}", exc_info=True)
		texture_queue.put((self, None))

def _check_texture_queue(self: ModernAppProtocol) -> None:
	"""Prüft die Texture-Queue und aktualisiert die Canvas"""
	try:
		while True:
			self_ref, preview_img = texture_queue.get_nowait()
			if self_ref is self:
				if preview_img is not None:
					# Skaliere Texture proportional auf Canvas-Größe
					canvas_w = self.texture_canvas.winfo_width()
					canvas_h = self.texture_canvas.winfo_height()
					if canvas_w > 10 and canvas_h > 10:
						preview_img = _resize_to_fit(preview_img, canvas_w, canvas_h)
					
					# Zeige Transparenz mit Schachbrett-Muster an
					display_img = _apply_bg_to_image_with_transparency(self, preview_img, show_transparency=True)
					img = ImageTk.PhotoImage(display_img)
					self._texture_img_ref = img
					self.texture_canvas.config(image=img)
				return
	except queue.Empty:
		pass  # Kein Element in Queue
	except Exception as e:
		logger.error(f"Error processing texture from queue: {type(e).__name__}: {e}", exc_info=False)
	# Wiederholen
	if hasattr(self, 'root') and self.root:
		self.root.after(10, lambda: _check_texture_queue(self))

def show_texture(self: ModernAppProtocol) -> None:
	"""Erzeugt und zeigt das Texture-Sheet mit Threading"""
	# Worker über Pool starten (nicht neuer Thread jedes Mal)
	pool = get_worker_pool(max_workers=2)
	pool.submit(
		"texture_preview",
		_process_texture_worker,
		self
	)
	_check_texture_queue(self)


def apply_effects(self: Any, img: Image.Image, prefix: Literal["gif", "texture"]) -> Image.Image:
	"""
	Applies image effects (grayscale, sharpen, blur, transparency, color intensity) to an image.
	
	Raises:
		ImageProcessingError: If an error occurs during effect application
	"""
	try:
		from PIL import ImageEnhance, ImageFilter
		if self.__dict__[f'{prefix}_grayscale'].get():
			# Stelle sicher RGBA
			if img.mode != "RGBA":
				img = img.convert("RGBA")
			# Speichere Alpha-Kanal
			alpha = img.split()[-1]
			# Konvertiere RGB zu Graustufen
			gray = img.convert("L")
			# Wandle zu RGBA um
			gray = gray.convert("RGBA")
			# Stelle ursprüngliche Alpha wieder her
			gray.putalpha(alpha)
			img = gray
		else:
			if img.mode != "RGBA":
				img = img.convert("RGBA")
		if self.__dict__[f'{prefix}_sharpen'].get():
			factor = self.__dict__[f'{prefix}_sharpen_value'].get()
			img = ImageEnhance.Sharpness(img).enhance(factor)
		if self.__dict__[f'{prefix}_blur'].get():
			radius = self.__dict__[f'{prefix}_blur_value'].get()
			if radius > 0:
				img = img.filter(ImageFilter.GaussianBlur(radius))
		if self.__dict__[f'{prefix}_transparency'].get():
			value = self.__dict__[f'{prefix}_transparency_value'].get()
			alpha = img.split()[-1].point(lambda p: int(p * value))
			img.putalpha(alpha)
		if self.__dict__[f'{prefix}_colorintensity_active'].get():
			colorint = self.__dict__[f'{prefix}_colorintensity'].get()
			if colorint != 0.5:
				if colorint < 0.5:
					import numpy as np
					arr = np.array(img).astype(float)
					factor = colorint * 2
					arr[..., :3] = arr[..., :3] * factor + 255 * (1 - factor)
					if img.mode == "RGBA" or (arr.shape[-1] == 4):
						img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGBA")
					else:
						img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGB")
				else:
					from PIL import ImageEnhance
					factor = 1.0 + (colorint - 0.5) * 2
					img = ImageEnhance.Color(img).enhance(factor)
		return img
	except MemoryError as e:
		logger.error(f"Memory error applying effects to image: {e}")
		raise ImageProcessingError(f"Memory error applying effects: {str(e)}") from e
	except Exception as e:
		logger.error(f"Error applying effects to image: {e}", exc_info=True)
		raise ImageProcessingError(f"Failed to apply effects: {str(e)}") from e

def set_max_images(self: Any, value: int) -> None:
	"""Setzt die maximale Anzahl der Bilder und entfernt ggf. überschüssige Frames."""
	try:
		max_frames = int(value)
	except Exception:
		max_frames = self.maxframes_var.get() if hasattr(self, 'maxframes_var') else 64
	if hasattr(self, 'gif_frames') and len(self.gif_frames) > max_frames:
		self.gif_frames = self.gif_frames[:max_frames]
		self.frame_count = len(self.gif_frames)
		if hasattr(self, 'status'):
			self.status.config(text=f"Max. Bilder: {self.frame_count}")
		if hasattr(self, 'frame_select_var'):
			self.frame_select_var.set(min(self.frame_select_var.get(), self.frame_count-1))
		if hasattr(self, 'frame_select_spin'):
			self.frame_select_spin.config(to=max(0, self.frame_count-1))
		if hasattr(self, 'add_frame_btn'):
			self.add_frame_btn.config(state="normal" if self.frame_count < max_frames else "disabled")
		if hasattr(self, 'update_previews'):
			self.update_previews()

# --- Wiederverwendbare Bildbearbeitungs-Methoden ---
def grayscale_changed(frames: List[Image.Image], to_rgba: bool = True) -> List[Image.Image]:
	"""Wandelt alle Frames in Graustufen um und bewahrt die Alpha-Kanal."""
	from PIL import Image
	new_frames = []
	for frame in frames:
		# Stelle sicher RGBA
		if frame.mode != "RGBA":
			frame = frame.convert("RGBA")
		# Speichere Alpha-Kanal
		alpha = frame.split()[-1]
		# Konvertiere RGB zu Graustufen
		gray = frame.convert("L")
		# Wandle zu RGBA um
		gray = gray.convert("RGBA")
		# Stelle ursprüngliche Alpha wieder her
		gray.putalpha(alpha)
		if to_rgba:
			new_frames.append(gray)
		else:
			new_frames.append(gray.convert("L"))
	return new_frames

def sharpen_changed(frames: List[Image.Image], factor: float = 2.5) -> List[Image.Image]:
	from PIL import ImageEnhance
	new_frames: List[Image.Image] = []
	for frame in frames:
		img = ImageEnhance.Sharpness(frame).enhance(factor)
		new_frames.append(img)
	return new_frames

def blur_changed(frames: List[Image.Image], radius: float = 3.5) -> List[Image.Image]:
	from PIL import ImageFilter
	new_frames: List[Image.Image] = []
	for frame in frames:
		img = frame.filter(ImageFilter.GaussianBlur(radius))
		new_frames.append(img)
	return new_frames

def transparency_changed(frames: List[Image.Image], value: float = 0.5) -> List[Image.Image]:
	new_frames: List[Image.Image] = []
	for frame in frames:
		alpha = frame.split()[-1].point(lambda p: int(p * value))
		img = frame.copy()
		img.putalpha(alpha)
		new_frames.append(img)
	return new_frames

def colorintensity_changed(frames: List[Image.Image], colorint: float = 0.5) -> List[Image.Image]:
	new_frames: List[Image.Image] = []
	for frame in frames:
		if colorint < 0.5:
			import numpy as np
			arr = np.array(frame).astype(float)
			factor = colorint * 2
			arr[..., :3] = arr[..., :3] * factor + 255 * (1 - factor)
			if frame.mode == "RGBA" or (arr.shape[-1] == 4):
				img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGBA")
			else:
				img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGB")
		else:
			from PIL import ImageEnhance
			factor = 1.0 + (colorint - 0.5) * 2
			img = ImageEnhance.Color(frame).enhance(factor)
		new_frames.append(img)
	return new_frames