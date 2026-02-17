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
from threading_utils import frame_queue

# Für Borderless-Originalspeicherung
borderless_original = {}

def check_queue_for_frame(self: Any) -> None:
	try:
		while True:
			self_ref, processed_frame = frame_queue.get_nowait()
			img = ImageTk.PhotoImage(processed_frame)
			self_ref._gif_img_ref = img
			self_ref.gif_canvas.config(image=img)
	except Exception:
		pass
	# Wiederholen, falls noch nicht fertig
	self.root.after(10, lambda: check_queue_for_frame(self))

def show_gif_frame(self: Any) -> None:
	from tkinter import messagebox
	if not self.gif_frames:
		self.gif_canvas.config(image="")
		self.show_texture()
		return
	try:
		frame = self.gif_frames[self.current_frame]
		canvas_w = self.gif_canvas.winfo_width()
		canvas_h = self.gif_canvas.winfo_height()
		texture_w = self.texture_canvas.winfo_width()
		texture_h = self.texture_canvas.winfo_height()
		max_w = min(canvas_w, texture_w) if texture_w > 10 else canvas_w
		max_h = min(canvas_h, texture_h) if texture_h > 10 else canvas_h
		if max_w < 10 or max_h < 10:
			max_w, max_h = 256, 256
		frame = frame.resize((max_w, max_h), Image.Resampling.LANCZOS)
		frame = apply_effects(self, frame, prefix="gif")
		img = ImageTk.PhotoImage(frame)
		self._gif_img_ref = img
		self.gif_canvas.config(image=img)
		self.show_texture()
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher für GIF-Vorschau.")
	except Exception as e:
		messagebox.showerror("Fehler", f"Fehler bei GIF-Vorschau: {e}")

def show_texture(self: Any) -> None:
	from tkinter import messagebox
	tex_w = self.width_var.get() if self.width_var.get() > 0 else 2048
	tex_h = self.height_var.get() if self.height_var.get() > 0 else 2048
	from PIL import ImageColor
	bg_rgba = (0,0,0,0)
	try:
		bg_rgba = ImageColor.getcolor(getattr(self, 'bg_color', '#00000000'), "RGBA")
	except Exception:
		bg_rgba = (0,0,0,0)

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
				x = tx * tile_w
				y = ty * tile_h
				sheet.paste(f, (x, y))
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher für Textur-Erstellung.")
		sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
	except Exception as e:
		messagebox.showerror("Fehler", f"Fehler bei der Textur-Erstellung: {e}")
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
		img = ImageTk.PhotoImage(preview)
		self._texture_img_ref = img
		self.texture_canvas.config(image=img)
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher für Textur-Vorschau.")
	except Exception as e:
		messagebox.showerror("Fehler", f"Fehler bei der Textur-Vorschau: {e}")

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

def update_previews(self: Any) -> None:
	show_gif_frame(self)

def apply_effects(self: Any, img: Image.Image, prefix: str) -> Image.Image:
	from PIL import ImageEnhance, ImageFilter
	if self.__dict__[f'{prefix}_grayscale'].get():
		img = img.convert("L").convert("RGBA")
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
