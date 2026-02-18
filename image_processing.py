###
# image_processing.py
# This file contains functions for processing images and GIFs within the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###


from typing import Any
from PIL import Image, ImageTk
from PIL import ImageColor, ImageEnhance, ImageFilter
import math
import os
import threading
from threading_utils import gif_queue, texture_queue

# Für Borderless-Originalspeicherung
borderless_original = {}

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

def _process_gif_frame_worker(self, current_frame, canvas_w, canvas_h, texture_w, texture_h) -> None:
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
		
		frame = frame.resize((max_w, max_h), Image.Resampling.LANCZOS)
		frame = apply_effects(self, frame, prefix="gif")
		gif_queue.put((self, frame))
	except Exception as e:
		gif_queue.put((self, None))

def _check_gif_queue(self: Any) -> None:
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
	except Exception:
		pass
	# Wiederholen
	if hasattr(self, 'root') and self.root:
		self.root.after(10, lambda: _check_gif_queue(self))

def show_gif_frame(self: Any) -> None:
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
		
		# Worker in separatem Thread starten
		worker_thread = threading.Thread(
			target=_process_gif_frame_worker,
			args=(self, self.current_frame, canvas_w, canvas_h, texture_w, texture_h),
			daemon=True
		)
		worker_thread.start()
		
		# Queue-Prüfung starten
		_check_gif_queue(self)
	except Exception as e:
		from tkinter import messagebox
		messagebox.showerror("Fehler", f"Fehler bei GIF-Vorschau: {e}")

def _process_texture_worker(self) -> None:
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
		tiles_x = 1
		tiles_y = 1
		try:
			if not self.gif_frames:
				sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
			else:
				frame_count = self.frame_count
				tiles_x = math.ceil(math.sqrt(frame_count))
				tiles_y = math.ceil(frame_count / tiles_x)
				tile_w = tex_w // tiles_x
				tile_h = tex_h // tiles_y
				sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
				for idx, frame in enumerate(self.gif_frames):
					tx = idx % tiles_x
					ty = idx // tiles_x
					f = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
					f = apply_effects(self, f, prefix="texture")
					# Stelle sicher dass f RGBA ist
					if f.mode != "RGBA":
						f = f.convert("RGBA")
					x = tx * tile_w
					y = ty * tile_h
					# Extrahiere die vorhandene Patch aus Sheet und composite darauf
					sheet_patch = sheet.crop((x, y, x + tile_w, y + tile_h))
					# Composite F gegen den Patch
					blended_patch = Image.alpha_composite(sheet_patch, f)
					# Paste zurück
					sheet.paste(blended_patch, (x, y))
			# WICHTIG: Sheet als aktuelle Textur speichern
			self.texture_image = sheet
		except MemoryError:
			sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
		except Exception as e:
			sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)

		# Borderless-Logik
		if hasattr(self, 'borderless_var') and self.borderless_var.get():
			self.apply_borderless(sheet, tex_w, tex_h, tiles_x, tiles_y)
		else:
			self.remove_borderless(sheet, tex_w, tex_h)

		# Vorschau erzeugen
		try:
			canvas_w = self.texture_canvas.winfo_width()
			canvas_h = self.texture_canvas.winfo_height()
			if canvas_w < 10 or canvas_h < 10:
				canvas_w, canvas_h = 256, 256
			preview = self.texture_image.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
			texture_queue.put((self, preview))
		except MemoryError:
			texture_queue.put((self, None))
		except Exception as e:
			texture_queue.put((self, None))
	except Exception as e:
		texture_queue.put((self, None))

def _check_texture_queue(self: Any) -> None:
	"""Prüft die Texture-Queue und aktualisiert die Canvas"""
	try:
		while True:
			self_ref, preview_img = texture_queue.get_nowait()
			if self_ref is self:
				if preview_img is not None:
					# Hintergrundfarbe auf Vorschau anwenden
					display_img = _apply_bg_to_image(self, preview_img)
					img = ImageTk.PhotoImage(display_img)
					self._texture_img_ref = img
					self.texture_canvas.config(image=img)
				return
	except Exception:
		pass
	# Wiederholen
	if hasattr(self, 'root') and self.root:
		self.root.after(10, lambda: _check_texture_queue(self))

def show_texture(self: Any) -> None:
	"""Erzeugt und zeigt das Texture-Sheet mit Threading"""
	# Worker in separatem Thread starten
	worker_thread = threading.Thread(
		target=_process_texture_worker,
		args=(self,),
		daemon=True
	)
	worker_thread.start()
	
	# Queue-Prüfung starten
	_check_texture_queue(self)


def toggle_borderless(self: Any) -> None:
	"""Schaltet den Borderless-Modus um"""
	if hasattr(self, 'borderless_var'):
		if self.borderless_var.get():
			self.show_texture()
		else:
			self.show_texture()

def apply_borderless(self: Any, sheet: Image.Image, tex_w: int, tex_h: int, tiles_x: int, tiles_y: int) -> None:
	"""Entfernt Ränder für nahtloses Tiling"""
	# Original speichern
	global borderless_original
	borderless_original[self] = sheet.copy()
	# Berechne die tatsächliche gefüllte Fläche (nur Tiles, keine Restpixel)
	tile_w = tex_w // tiles_x
	tile_h = tex_h // tiles_y
	filled_w = tile_w * tiles_x
	filled_h = tile_h * tiles_y
	# Crop auf gefüllte Fläche
	cropped = sheet.crop((0, 0, filled_w, filled_h))
	self.texture_image = cropped

def remove_borderless(self: Any, sheet: Image.Image, tex_w: int, tex_h: int) -> None:
	"""Stellt das Originalbild wieder her"""
	global borderless_original
	# Immer das Sheet als Original verwenden
	self.texture_image = sheet

def remove_borderless_transparency(img: Image.Image, alpha_threshold: int = 8, softness: int = 8) -> Image.Image:
	"""
	Schneidet das Bild so zu, dass auch weiche Schatten/Anti-Aliasing-Ränder (Transparenz) erhalten bleiben.
	alpha_threshold: Minimaler Alphawert (0-255), der als "sichtbar" gilt.
	softness: Wie viele Pixel mit weichem Übergang (Schatten) zusätzlich erhalten bleiben (Padding).
	"""
	if img.mode != "RGBA":
		img = img.convert("RGBA")
	arr = img.getchannel("A")
	# Suche sichtbare Pixel (Alpha > threshold)
	bbox = arr.point(lambda a: 255 if isinstance(a, (int, float)) and int(a) > alpha_threshold else 0).getbbox()
	if not bbox:
		return img  # Nur transparent
	# Padding für weiche Schatten
	left, upper, right, lower = bbox
	left = max(0, left - softness)
	upper = max(0, upper - softness)
	right = min(img.width, right + softness)
	lower = min(img.height, lower + softness)
	cropped = img.crop((left, upper, right, lower))
	return cropped

def apply_effects(self: Any, img: Image.Image, prefix: str) -> Image.Image:
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
def grayscale_changed(frames, to_rgba=True):
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

def sharpen_changed(frames, factor=2.5):
	from PIL import ImageEnhance
	new_frames = []
	for frame in frames:
		img = ImageEnhance.Sharpness(frame).enhance(factor)
		new_frames.append(img)
	return new_frames

def blur_changed(frames, radius=3.5):
	from PIL import ImageFilter
	new_frames = []
	for frame in frames:
		img = frame.filter(ImageFilter.GaussianBlur(radius))
		new_frames.append(img)
	return new_frames

def transparency_changed(frames, value=0.5):
	new_frames = []
	for frame in frames:
		alpha = frame.split()[-1].point(lambda p: int(p * value))
		img = frame.copy()
		img.putalpha(alpha)
		new_frames.append(img)
	return new_frames

def colorintensity_changed(frames, colorint=0.5):
	new_frames = []
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