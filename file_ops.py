###
# file_ops.py
# This file contains file operations for the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import math
import os
from typing import Any, List, Optional
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from translations import tr
from image_processing import apply_effects, calculate_optimal_grid
from logging_config import get_logger
from exceptions import (
	ImageLoadError,
	FileOperationError,
	TextureGenerationError,
	LSLExportError,
)

logger = get_logger(__name__)

def import_frames_to_gif(self: Any) -> None:
	from tkinter import filedialog
	import zipfile
	from PIL import Image
	import tempfile
	import shutil
	from io import BytesIO
	import glob
	import os
	# Dialog: ZIP oder Verzeichnis
	filetypes = [("ZIP-Archiv", "*.zip"), ("Bilder-Ordner", "*")]
	path = filedialog.askopenfilename(title="ZIP oder Verzeichnis wählen", filetypes=filetypes)
	if not path:
		return
	tempdir = None
	image_files = []
	try:
		if path.lower().endswith('.zip'):
			tempdir = tempfile.mkdtemp()
			with zipfile.ZipFile(path, 'r') as zipf:
				zipf.extractall(tempdir)
			# Alle Bilddateien im tempdir suchen
			image_files = sorted(glob.glob(os.path.join(tempdir, '*')))
		else:
			# Verzeichnis: alle Bilddateien
			image_files = sorted(glob.glob(os.path.join(os.path.dirname(path), '*')))
		# Nur Bilddateien (PNG, JPG, BMP, GIF)
		image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
		if not image_files:
			if hasattr(self, 'status') and self.status:
				self.status.config(text=tr('status_no_images_found', self.lang) or "Keine Bilder gefunden.")
			return
		# Bilder laden
		frames = [Image.open(f).convert('RGBA') for f in image_files]
		# GIF speichern
		save_path = filedialog.asksaveasfilename(defaultextension='.gif', filetypes=[('GIF', '*.gif')], title="GIF speichern")
		if not save_path:
			return
		frames[0].save(save_path, save_all=True, append_images=frames[1:], loop=0, duration=100)
		# GIF laden
		self._load_gif_frames(save_path)
		self._setup_frame_select()
		self._reset_play_button()
		self._update_status()
		self._update_preview()
		if hasattr(self, '_update_texture'):
			self._update_texture()
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_gif_created', self.lang) or "GIF aus Einzelbildern erstellt.")
	except Exception as e:
		from tkinter import messagebox
		messagebox.showerror("Fehler", f"Fehler beim Importieren: {e}")
	finally:
		if tempdir:
			shutil.rmtree(tempdir)

def load_gif_compat(self: Any) -> None:
	"""
	Kompatibilitäts-Wrapper für alte Aufrufe: Lädt ein GIF und aktualisiert alle GUI-Elemente wie früher in einer Methode.
	"""
	file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
	if not file:
		return
	self._load_gif_frames(file)
	self._setup_frame_select()
	# Reihenfolge wird nur in _setup_frame_select gesetzt
	self._reset_play_button()
	self._update_status()
	self._update_preview()
	# Textur erst nach vollständigem Laden und Setup anzeigen
	if hasattr(self, '_update_texture'):
		self._update_texture()

def load_gif(self: Any) -> None:
	"""
	Öffnet einen Dialog, lädt ein GIF und initialisiert die GUI über Hilfsmethoden.
	"""
	file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
	if not file:
		return
	self._load_gif_frames(file)
	self._setup_frame_select()
	# Reihenfolge wird nur in _setup_frame_select gesetzt
	self._reset_play_button()
	self._update_status()
	self._update_preview()
	# Textur nach GIF-Ladevorgang immer anzeigen
	if hasattr(self, '_update_texture'):
		self._update_texture()

def _load_gif_frames(self: Any, file: str) -> None:
	"""Lädt die Frames aus einer GIF-Datei und setzt gif_image, gif_frames, frame_count, current_frame."""
	from PIL import UnidentifiedImageError
	frames = []
	logger.info(f"Loading GIF file: {file}")
	try:
		self.gif_image = Image.open(file)
		while True:
			frames.append(self.gif_image.copy())
			self.gif_image.seek(len(frames))
	except FileNotFoundError as e:
		error_msg = f"File not found: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", f"Datei nicht gefunden: {file}")
		raise ImageLoadError(error_msg) from e
	except UnidentifiedImageError as e:
		error_msg = f"File is not a valid or corrupted GIF: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", f"Die Datei ist kein gültiges GIF oder beschädigt: {file}")
		raise ImageLoadError(error_msg) from e
	except EOFError:
		pass
	except MemoryError as e:
		error_msg = f"Insufficient memory to load GIF: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", "Nicht genügend Speicher zum Laden des GIFs.")
		raise ImageLoadError(error_msg) from e
	except Exception as e:
		logger.error(f"Unknown error loading GIF {file}: {e}", exc_info=True)
		messagebox.showerror("Fehler", f"Unbekannter Fehler beim Laden des GIFs: {e}")
		raise ImageLoadError(f"Failed to load GIF: {str(e)}") from e
	
	logger.info(f"Successfully loaded GIF with {len(frames)} frames from {file}")
	
	# Schließe die GIF-Datei, um Ressourcen freizugeben (Frames sind bereits im Speicher kopiert)
	if hasattr(self, 'gif_image') and self.gif_image is not None:
		try:
			self.gif_image.close()
		except Exception as e:
			logger.debug(f"Error closing GIF image: {type(e).__name__}: {e}", exc_info=False)
	if not frames and hasattr(self, 'gif_image'):
		try:
			frames.append(self.gif_image.copy())
		except Exception as e:
			error_msg = f"Failed to copy GIF frame: {type(e).__name__}: {e}"
			logger.error(error_msg, exc_info=False)
			messagebox.showerror(tr('error', self.lang) or "Error", tr('status_gif_corrupted', self.lang) or "GIF konnte nicht geladen werden.")
			return
	logger.debug(f"Loaded frames: {len(frames)}")
	self.gif_frames = frames
	self.frame_count = len(frames)
	self.current_frame = 0
	self.playing = False

def _setup_frame_select(self: Any) -> None:
	"""Initialisiert die Spinbox für die Frame-Auswahl."""
	value = 0
	# Nur Werte und Limits anpassen, keine Widget-Erstellung/Packing mehr
	if hasattr(self, 'frame_select_spin') and self.frame_select_spin is not None:
		self.frame_select_spin.config(from_=0, to=max(0, self.frame_count-1))
	self.frame_select_var.set(value)
	self.current_frame = 0

def _reset_play_button(self: Any) -> None:
	"""Setzt den Play-Button auf den Startwert zurück."""
	self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

def _update_status(self: Any) -> None:
	"""Aktualisiert die Statusleiste mit der Frame-Anzahl."""
	self.maxframes_var.set(self.frame_count)
	self.status.config(text=f"{tr('frame_count', self.lang)}: {self.frame_count}")

def update_previews(self: Any) -> None:
	"""Updates the GIF and texture previews in the GUI."""
	if hasattr(self, 'gif_frames') and self.gif_frames and self.current_frame < len(self.gif_frames):
		frame = self.gif_frames[self.current_frame]
		from PIL import ImageTk
		photo = ImageTk.PhotoImage(frame.resize((self.gif_canvas.winfo_width() or 300, self.gif_canvas.winfo_height() or 300)))
		self.gif_canvas.create_image(0, 0, image=photo, anchor='nw')
		self.gif_canvas.image = photo

def _update_preview(self: Any) -> None:
	"""Aktualisiert die GIF-Vorschau in der GUI."""
	from image_processing import show_gif_frame
	if hasattr(self, 'root') and self.root is not None:
		self.root.update_idletasks()
		show_gif_frame(self)

def delete_gif(self: Any) -> None:
	"""
	Setzt alle GIF- und Textur-bezogenen Attribute und GUI-Elemente zurück.
	Wird z.B. aufgerufen, wenn ein GIF entladen oder ein neues geladen werden soll.
	"""
	self.gif_image = None
	self.gif_frames = []
	self.frame_count = 0
	self.current_frame = 0
	self.playing = False
	self.texture_image = None
	self.texture_canvas.config(image="")
	self.gif_canvas.config(image="")
	self.status.config(text="")
	self.maxframes_var.set(0)
	# Keine Widget-Zerstörung mehr, nur Wert-Updates
	if hasattr(self, 'add_frame_btn') and self.add_frame_btn is not None:
		self.add_frame_btn.config(state="disabled")
	if hasattr(self, 'play_btn') and self.play_btn is not None:
		self.play_btn.config(text=tr('play', self.lang) or "Play ▶", state="disabled")

def save_gif(self: Any) -> None:
	"""Speichert die GIF-Frames mit aktuellen Effekten als neue GIF-Datei."""
	if not self.gif_frames:
		error_msg = "No GIF loaded for saving"
		logger.warning(error_msg)
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
	if not file:
		return
	logger.info(f"Saving GIF to: {file}")
	try:
		frames = [apply_effects(self, f.resize((self.width_var.get(), self.height_var.get())), "gif") for f in self.gif_frames]
		duration = self.framerate_var.get()
		frames[0].save(file, save_all=True, append_images=frames[1:], loop=0, duration=duration)
		logger.info(f"GIF saved successfully with {len(frames)} frames: {file}")
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_gif_saved', self.lang) or "GIF gespeichert.")
	except FileNotFoundError as e:
		error_msg = f"File could not be saved: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden: {file}")
		raise FileOperationError(error_msg) from e
	except MemoryError as e:
		error_msg = f"Insufficient memory to save GIF: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", "Nicht genügend Speicher zum Speichern des GIFs.")
		raise FileOperationError(error_msg) from e
	except Exception as e:
		logger.error(f"Error saving GIF {file}: {e}", exc_info=True)
		messagebox.showerror("Fehler", f"Fehler beim Speichern des GIFs: {e}")
		raise FileOperationError(f"Failed to save GIF: {str(e)}") from e

def save_texture(self: Any) -> None:
	"""Speichert die aktuell generierte Texture."""
	if not hasattr(self, 'texture_image') or self.texture_image is None:
		messagebox.showerror("Fehler", "Keine Textur generiert. Bitte zuerst auf die Textur-Vorschau klicken.")
		return
	
	logger.info(f"Saving texture: {self.texture_image.size}")
	
	# Hol dir die Zielgröße
	tex_w = self.width_var.get() if self.width_var.get() > 0 else 2048
	tex_h = self.height_var.get() if self.height_var.get() > 0 else 2048
	
	# Skaliere das Arbeitsbild auf die Zielgröße (nur beim Speichern!)
	if self.texture_image.size != (tex_w, tex_h):
		logger.info(f"Scaling texture from {self.texture_image.size} to {tex_w}x{tex_h} for save")
		sheet = self.texture_image.resize((tex_w, tex_h), Image.Resampling.LANCZOS)
	else:
		sheet = self.texture_image
	
	# Extrahiere Metadaten
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	
	# Versuche Tile-Informationen zu extrahieren oder berechne sie neu
	try:
		# Wenn die Textur nicht optimiert wurde, berechne Tiles optimal
		default_x, default_y = calculate_optimal_grid(len(self.gif_frames))
		tiles_x = getattr(self, 'tiles_x', default_x)
		tiles_y = getattr(self, 'tiles_y', default_y)
	except:
		tiles_x, tiles_y = calculate_optimal_grid(len(self.gif_frames))
	
	speed_val = self.framerate_var.get()
	speed = f"{speed_val};0"
	ext = self.export_format_var.get().lower()
	defext = f".{ext}"
	filetypes = [(ext.upper(), f"*.{ext}") for ext in ["png", "jpg", "bmp"]]
	file = filedialog.asksaveasfilename(
		defaultextension=defext, 
		initialfile=f"{name};{tiles_x};{tiles_y};{speed}.{ext}", 
		filetypes=filetypes
	)
	if not file:
		return
	
	fmt = self.export_format_var.get().upper()
	
	# ZIP-Export: Speichere Einzelbilder
	if fmt == "ZIP":
		import zipfile
		try:
			with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
				for idx, frame in enumerate(self.gif_frames):
					img = apply_effects(self, frame.resize((self.width_var.get(), self.height_var.get())), "gif")
					from io import BytesIO
					img_bytes = BytesIO()
					img.save(img_bytes, format="PNG")
					img_bytes.seek(0)
					zipf.writestr(f"frame_{idx+1:03d}.png", img_bytes.read())
			logger.info(f"ZIP export saved successfully with {len(self.gif_frames)} frames: {file}")
			if hasattr(self, 'status') and self.status:
				self.status.config(text=tr('status_zip_saved', self.lang) or "GIF-Einzelbilder als ZIP gespeichert.")
		except Exception as e:
			logger.error(f"Error exporting ZIP: {e}", exc_info=True)
			messagebox.showerror("Fehler", f"Fehler beim ZIP-Export: {e}")
		return
	
	# PNG/JPG/BMP-Export: Speichere optimierte Textur
	if fmt == "JPG":
		fmt = "JPEG"
	
	try:
		img = sheet
		
		# JPG-Konvertierung (keine Transparenz möglich)
		if fmt == "JPEG":
			if img.mode == 'RGBA':
				# Erstelle weiß-Hintergrund für JPEG
				background = Image.new('RGB', img.size, (255, 255, 255))
				background.paste(img, mask=img.split()[3] if len(img.split()) > 3 else None)
				img = background
			else:
				img = img.convert('RGB')
		elif fmt == "PNG":
			# PNG: Stelle sicher RGBA Mode (für Alpha-Kanal)
			if img.mode != 'RGBA':
				img = img.convert('RGBA')
			
			# Warnung: Prüfe ob Alpha-Kanal zu transparent ist
			import numpy as np
			try:
				img_array = np.array(img)
				if img_array.shape[2] == 4:  # Hat Alpha-Kanal
					alpha_channel = img_array[:, :, 3]
					fully_transparent = np.sum(alpha_channel == 0)
					total_pixels = alpha_channel.size
					transparency_ratio = fully_transparent / total_pixels
					
					if transparency_ratio > 0.9:  # Mehr als 90% transparent
						logger.warning(f"Texture has very high transparency: {transparency_ratio*100:.1f}% fully transparent pixels")
						messagebox.showwarning(
							"Warnung",
							f"Die Texture ist zu {transparency_ratio*100:.1f}% durchsichtig.\n\n"
							f"Der Second Life Viewer könnte eine Warnung zeigen.\n"
							f"Stelle sicher, dass du einen nicht-transparenten Hintergrund verwenden möchtest."
						)
			except Exception as e:
				logger.debug(f"Could not check alpha channel: {e}")
		
		img.save(file, format=fmt)
		logger.info(f"Texture saved successfully: {file} ({img.size})")
		
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_saved', self.lang) or f"Textur gespeichert: {os.path.basename(file)}")

	
	except FileNotFoundError as e:
		logger.error(f"File not found when saving texture: {e}")
		messagebox.showerror("Fehler", f"Speicherort nicht gefunden: {e}")
		raise TextureGenerationError(f"Failed to save texture - file path not found: {str(e)}") from e
	except PermissionError as e:
		logger.error(f"Permission denied when saving texture: {e}")
		messagebox.showerror("Fehler", f"Berechtigung verweigert: {e}")
		raise TextureGenerationError(f"Failed to save texture - permission denied: {str(e)}") from e
	except Exception as e:
		logger.error(f"Error saving texture: {e}", exc_info=True)
		messagebox.showerror("Fehler", f"Fehler beim Speichern: {e}")
		raise TextureGenerationError(f"Failed to save texture: {str(e)}") from e

def export_lsl(self: Any) -> None:
	"""Exportiert ein LSL (Linden Scripting Language) Script für Texture-Animation in Second Life/OpenSim."""
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	logger.info("Starting LSL script export")
	frame_count = self.frame_count
	tiles_x, tiles_y = calculate_optimal_grid(frame_count)
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	speed = 10.0
	lsl = generate_lsl_script(self, name, tiles_x, tiles_y, speed)
	file = filedialog.asksaveasfilename(defaultextension=".lsl", initialfile=f"{name}.lsl", filetypes=[("LSL", "*.lsl"), ("Text", "*.txt")])
	if not file:
		logger.debug("LSL export cancelled by user")
		return
	logger.info(f"Saving LSL script to: {file}")
	try:
		with open(file, "w", encoding="utf-8") as f:
			f.write(lsl)
		logger.info(f"LSL script exported successfully: {file}")
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_lsl_exported', self.lang) or "LSL-Skript exportiert.")
	except FileNotFoundError as e:
		error_msg = f"Could not save LSL script: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", str(e))
		raise LSLExportError(error_msg) from e
	except IOError as e:
		error_msg = f"IO error when saving LSL script: {file}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", str(e))
		raise LSLExportError(error_msg) from e
	except Exception as e:
		error_msg = f"Error exporting LSL script: {str(e)}"
		logger.error(error_msg, exc_info=True)
		messagebox.showerror("Fehler", str(e))
		raise LSLExportError(error_msg) from e

def generate_lsl_script(self: Any, name: str, tiles_x: int, tiles_y: int, speed: float) -> str:
	"""Generiert ein LSL-Script für Texture-Animation mit den gegebenen Parametern."""
	length = tiles_x * tiles_y
	return f'''// LSL Texture Animation Script\n// Generated by OSSL2Gif\n// Texture: {name};{tiles_x};{tiles_y};{speed}\n\ninteger animOn = TRUE;\nlist effects = [LOOP];\ninteger movement = 0;\ninteger face = ALL_SIDES;\ninteger sideX = {tiles_x};\ninteger sideY = {tiles_y};\nfloat start = 0.0;\nfloat length = {length};\nfloat speed = {speed};\n\ninitAnim() {{\n    if(animOn) {{\n        integer effectBits;\n        integer i;\n        for(i = 0; i < llGetListLength(effects); i++) {{\n            effectBits = (effectBits | llList2Integer(effects,i));\n        }}\n        integer params = (effectBits|movement);\n        llSetTextureAnim(ANIM_ON|params,face,sideX,sideY,start,length,speed);\n    }}\n    else {{\n        llSetTextureAnim(0,face,sideX,sideY,start,length,speed);\n    }}\n}}\n\nfetch() {{\n     string texture = llGetInventoryName(INVENTORY_TEXTURE,0);\n            llSetTexture(texture,face);\n            // llParseString2List braucht als Trennzeichen eine Liste!\n            list data  = llParseString2List(texture,[";"],[]);\n            string X = llList2String(data,1);\n            string Y = llList2String(data,2);\n            string Z = llList2String(data,3);\n            sideX = (integer) X;\n            sideY = (integer) Y;\n            speed = (float) Z;\n            length = (float)(sideX * sideY);\n            if (speed) \n                initAnim();\n}}\n\ndefault\n{{\n    state_entry()\n    {{\n        llSetTextureAnim(FALSE, face, 0, 0, 0.0, 0.0, 1.0);\n        fetch();\n    }}\n    changed(integer what)\n    {{\n        if (what & CHANGED_INVENTORY)\n        {{\n            fetch();\n        }}\n    }}\n}}\n'''
