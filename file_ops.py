###
# file_ops.py
# This file contains file operations for the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import math
import os
from datetime import datetime
import tkinter as tk
from io import BytesIO
import glob
from typing import Any, List, Optional
from tkinter import filedialog, ttk, simpledialog
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen
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

def _set_status(self: Any, text: str) -> None:
	if hasattr(self, 'status') and self.status:
		self.status.config(text=text)

def _lang(self: Any) -> str:
	return str(getattr(self, 'lang', 'de'))

def _prefer_single_row_odd(self: Any) -> bool:
	try:
		if hasattr(self, 'odd_frames_single_row_var') and self.odd_frames_single_row_var is not None:
			return bool(self.odd_frames_single_row_var.get())
	except Exception:
		pass
	return True

def load_gif_from_path(self: Any, dropped_path: str) -> bool:
	"""Lädt ein GIF aus einem gedroppten Dateipfad oder aus einem Ordner (erstes GIF)."""
	if not dropped_path:
		return False

	path = os.path.normpath(dropped_path)
	if not os.path.exists(path):
		return False

	gif_file = None
	if os.path.isdir(path):
		gif_candidates = sorted(glob.glob(os.path.join(path, '*.gif')))
		if not gif_candidates:
			if hasattr(self, 'status') and self.status:
				self.status.config(text="Ordner enthält keine GIF-Datei.")
			return False
		gif_file = gif_candidates[0]
	else:
		if not path.lower().endswith('.gif'):
			return False
		gif_file = path

	try:
		self._load_gif_frames(gif_file)
		_post_gif_load_update(self)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('frame_count', self.lang) + f": {self.frame_count} | Drag&Drop geladen")
		return True
	except Exception as e:
		logger.error(f"Failed to load dropped GIF path {gif_file}: {e}", exc_info=True)
		return False

def _post_gif_load_update(self: Any) -> None:
	"""Führt alle notwendigen GUI-Updates nach dem Laden eines GIFs aus."""
	self._setup_frame_select()
	self._reset_play_button()
	self._update_status()
	self._update_preview()
	if hasattr(self, '_update_texture'):
		self._update_texture()

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
		logger.error(f"Fehler beim Importieren: {e}", exc_info=True)
		_set_status(self, f"Fehler beim Importieren: {e}")
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
	_post_gif_load_update(self)

def load_gif(self: Any) -> None:
	"""
	Öffnet einen Dialog, lädt ein GIF und initialisiert die GUI über Hilfsmethoden.
	"""
	file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
	if not file:
		return
	self._load_gif_frames(file)
	_post_gif_load_update(self)

def load_gif_from_clipboard(self: Any) -> None:
	"""Lädt ein GIF oder Bild aus der Zwischenablage."""
	clipboard_text = None
	if hasattr(self, 'root') and self.root is not None:
		try:
			clipboard_text = self.root.clipboard_get().strip()
		except tk.TclError:
			clipboard_text = None

	if clipboard_text and clipboard_text.lower().startswith(('http://', 'https://')):
		load_gif_from_url(self, clipboard_text)
		return

	try:
		from PIL import ImageGrab
	except Exception as e:
		logger.error(f"Clipboard support unavailable: {e}", exc_info=True)
		_set_status(self, "Zwischenablage wird auf diesem System nicht unterstützt.")
		return

	try:
		clipboard_data = ImageGrab.grabclipboard()
	except Exception as e:
		logger.error(f"Failed to read clipboard: {e}", exc_info=True)
		_set_status(self, f"Zwischenablage konnte nicht gelesen werden: {e}")
		return

	if isinstance(clipboard_data, list):
		gif_file = next(
			(
				path for path in clipboard_data
				if isinstance(path, str)
				and path.lower().endswith('.gif')
				and os.path.isfile(path)
			),
			None
		)
		if gif_file is not None:
			self._load_gif_frames(gif_file)
			_post_gif_load_update(self)
			if hasattr(self, 'status') and self.status:
				self.status.config(text=tr('frame_count', self.lang) + f": {self.frame_count} | GIF aus Zwischenablage geladen")
			return

	if isinstance(clipboard_data, Image.Image):
		frame = clipboard_data.convert('RGBA')
		self.gif_image = frame.copy()
		self.gif_frames = [frame]
		self.frame_count = 1
		self.current_frame = 0
		self.playing = False
		_post_gif_load_update(self)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('frame_count', self.lang) + f": {self.frame_count} | Bild aus Zwischenablage geladen")
		return

	if hasattr(self, 'status') and self.status:
		self.status.config(text="Zwischenablage enthält kein GIF/Bild.")

def load_gif_from_url(self: Any, image_url: Optional[str] = None) -> None:
	"""Lädt ein GIF/Bild von einer HTTP(S)-Adresse."""
	url = image_url
	if not url:
		parent = self.root if hasattr(self, 'root') else None
		url = simpledialog.askstring(
			"Grafikadresse",
			"Bitte Grafikadresse (http/https) eingeben:",
			parent=parent,
		)
	if not url:
		return

	url = url.strip()
	parsed = urlparse(url)
	if parsed.scheme not in ('http', 'https') or not parsed.netloc:
		_set_status(self, "Ungültige Grafikadresse. Bitte http/https verwenden.")
		return

	frames = []
	try:
		request = Request(url, headers={"User-Agent": "OSSL2Gif/2.0"})
		with urlopen(request, timeout=20) as response:
			image_data = response.read()

		if not image_data:
			_set_status(self, "Die angegebene Grafikadresse liefert keine Daten.")
			return

		image = Image.open(BytesIO(image_data))
		while True:
			frames.append(image.copy().convert('RGBA'))
			image.seek(len(frames))
	except EOFError:
		pass
	except HTTPError as e:
		logger.error(f"HTTP error loading image URL {url}: {e}", exc_info=True)
		_set_status(self, f"HTTP-Fehler beim Laden: {e.code}")
		return
	except URLError as e:
		logger.error(f"Network error loading image URL {url}: {e}", exc_info=True)
		_set_status(self, f"Netzwerkfehler beim Laden: {e.reason}")
		return
	except Exception as e:
		logger.error(f"Failed to load image from URL {url}: {e}", exc_info=True)
		_set_status(self, f"Grafik konnte nicht geladen werden: {e}")
		return

	if not frames:
		_set_status(self, "Die Grafikadresse enthält kein lesbares Bild.")
		return

	self.gif_image = frames[0].copy()
	self.gif_frames = frames
	self.frame_count = len(frames)
	self.current_frame = 0
	self.playing = False
	_post_gif_load_update(self)
	if hasattr(self, 'status') and self.status:
		self.status.config(text=tr('frame_count', self.lang) + f": {self.frame_count} | URL geladen")

def _load_gif_frames(self: Any, file: str) -> None:
	"""Lädt die Frames aus einer GIF-Datei und setzt gif_image, gif_frames, frame_count, current_frame."""
	from PIL import UnidentifiedImageError
	# Bei GIF-Ladevorgang auf GIF-Frames umschalten
	self.texture_use_source_image = False
	self.texture_source_image = None
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
		_set_status(self, f"Datei nicht gefunden: {file}")
		raise ImageLoadError(error_msg) from e
	except UnidentifiedImageError as e:
		error_msg = f"File is not a valid or corrupted GIF: {file}"
		logger.error(error_msg, exc_info=True)
		_set_status(self, f"Die Datei ist kein gültiges GIF oder beschädigt: {file}")
		raise ImageLoadError(error_msg) from e
	except EOFError:
		pass
	except MemoryError as e:
		error_msg = f"Insufficient memory to load GIF: {file}"
		logger.error(error_msg, exc_info=True)
		_set_status(self, "Nicht genügend Speicher zum Laden des GIFs.")
		raise ImageLoadError(error_msg) from e
	except Exception as e:
		logger.error(f"Unknown error loading GIF {file}: {e}", exc_info=True)
		_set_status(self, f"Unbekannter Fehler beim Laden des GIFs: {e}")
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
			_set_status(self, tr('status_gif_corrupted', self.lang) or "GIF konnte nicht geladen werden.")
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
		_set_status(self, "GIF-Speichern nicht möglich: Kein GIF geladen.")
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
		_set_status(self, f"GIF-Speichern fehlgeschlagen: Datei konnte nicht gespeichert werden: {file}")
		return
	except MemoryError as e:
		error_msg = f"Insufficient memory to save GIF: {file}"
		logger.error(error_msg, exc_info=True)
		_set_status(self, "GIF-Speichern fehlgeschlagen: Nicht genügend Speicher.")
		return
	except Exception as e:
		logger.error(f"Error saving GIF {file}: {e}", exc_info=True)
		_set_status(self, f"GIF-Speichern fehlgeschlagen: {e}")
		return

def load_texture(self: Any) -> None:
	"""Lädt eine Textur-Datei (PNG, JPG, BMP, etc.) und wendet alle Texture-Effekte an."""
	filetypes = [
		("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff"),
		("PNG files", "*.png"),
		("JPEG files", "*.jpg *.jpeg"),
		("BMP files", "*.bmp"),
		("TIFF files", "*.tiff"),
		("All files", "*.*")
	]
	
	file = filedialog.askopenfilename(
		title=tr('load_texture', self.lang) or "Textur laden",
		filetypes=filetypes
	)
	
	if not file:
		return
	
	try:
		logger.info(f"Loading texture from: {file}")
		img = Image.open(file)
		
		# Konvertiere zu RGBA
		if img.mode != 'RGBA':
			img = img.convert('RGBA')
		
		# Speichere als Textur-Quelle und nutze sie für Vorschau/Export (ohne GIF-Frames zu überschreiben)
		self.texture_source_image = img
		self.texture_use_source_image = True
		self.texture_image = img
		logger.info(f"Texture loaded: {img.size}")
		
		# Zeige die Textur mit allen Texture-Einstellungen (Effekte, Größe, etc.)
		from image_processing import show_texture
		show_texture(self)
		
		if hasattr(self, 'status') and self.status:
			self.status.config(
				text=f"{tr('texture_loaded', self.lang) or 'Textur geladen'}: {os.path.basename(file)} ({tr('size', self.lang) or 'Größe'}: {img.size[0]}x{img.size[1]})"
			)
	except Exception as e:
		logger.error(f"Error loading texture: {e}", exc_info=True)
		if hasattr(self, 'status') and self.status:
			self.status.config(
				text=f"{tr('error_loading_texture', self.lang) or 'Fehler beim Laden der Textur'}: {str(e)}"
			)

def save_texture(self: Any) -> None:
	"""Speichert die aktuell generierte Texture."""
	if not hasattr(self, 'texture_image') or self.texture_image is None:
		_set_status(self, "Textur-Speichern nicht möglich: Keine Textur generiert.")
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
	name = str(name).replace(";", "_")
	
	# Versuche Tile-Informationen zu extrahieren oder berechne sie neu
	try:
		# Wenn die Textur nicht optimiert wurde, berechne Tiles optimal
		default_x, default_y = calculate_optimal_grid(len(self.gif_frames), prefer_single_row_odd=_prefer_single_row_odd(self))
		tiles_x = getattr(self, 'tiles_x', default_x)
		tiles_y = getattr(self, 'tiles_y', default_y)
	except:
		tiles_x, tiles_y = calculate_optimal_grid(len(self.gif_frames), prefer_single_row_odd=_prefer_single_row_odd(self))
	
	default_texture_filename = name
	ext = self.export_format_var.get().lower()
	defext = f".{ext}"
	filetypes = [(ext.upper(), f"*.{ext}") for ext in ["png", "jpg", "bmp"]]
	file = filedialog.asksaveasfilename(
		defaultextension=defext, 
		initialfile=f"{default_texture_filename}.{ext}", 
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
				self.status.config(text=tr('status_zip_saved', _lang(self)) or "GIF-Einzelbilder als ZIP gespeichert.")
		except Exception as e:
			logger.error(f"Error exporting ZIP: {e}", exc_info=True)
			_set_status(self, f"ZIP-Export fehlgeschlagen: {e}")
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
						_set_status(self, f"Warnung: Textur ist zu {transparency_ratio*100:.1f}% durchsichtig.")
			except Exception as e:
				logger.debug(f"Could not check alpha channel: {e}")
		
		img.save(file, format=fmt)
		logger.info(f"Texture saved successfully: {file} ({img.size})")

		texture_base_name = os.path.splitext(os.path.basename(file))[0]
		notecard_content = generate_lsl_notecard(
			texture_base_name,
			tiles_x,
			tiles_y,
			float(self.framerate_var.get()) if hasattr(self, 'framerate_var') else 10.0,
			_get_lsl_default_effect_tokens(self),
			_get_lsl_default_movement(self),
		)
		notecard_file = os.path.join(os.path.dirname(file), f"{texture_base_name}.notecard")
		with open(notecard_file, "w", encoding="utf-8") as f:
			f.write(notecard_content)
		
		if hasattr(self, 'status') and self.status:
			self.status.config(text=(tr('status_saved', _lang(self)) or "Textur gespeichert") + f": {os.path.basename(file)} | Notecard: {texture_base_name}.notecard")

	
	except FileNotFoundError as e:
		logger.error(f"File not found when saving texture: {e}")
		_set_status(self, f"Textur-Speichern fehlgeschlagen: Speicherort nicht gefunden: {e}")
		return
	except PermissionError as e:
		logger.error(f"Permission denied when saving texture: {e}")
		_set_status(self, f"Textur-Speichern fehlgeschlagen: Berechtigung verweigert: {e}")
		return
	except Exception as e:
		logger.error(f"Error saving texture: {e}", exc_info=True)
		_set_status(self, f"Textur-Speichern fehlgeschlagen: {e}")
		return

def export_lsl(self: Any) -> None:
	"""Exportiert ein LSL (Linden Scripting Language) Script für Texture-Animation in Second Life/OpenSim."""
	if not self.gif_frames:
		if hasattr(self, 'status') and self.status:
			self.status.config(text="LSL-Export nicht möglich: Kein GIF geladen.")
		return
	logger.info("Starting LSL script export")
	frame_count = self.frame_count
	tiles_x, tiles_y = calculate_optimal_grid(frame_count, prefer_single_row_odd=_prefer_single_row_odd(self))
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	try:
		speed = float(self.framerate_var.get())
	except Exception:
		speed = 10.0
	lsl = generate_lsl_script_v2(self, name, tiles_x, tiles_y, speed)
	file = filedialog.asksaveasfilename(defaultextension=".lsl", initialfile="Texture-Animation-Script.lsl", filetypes=[("LSL", "*.lsl"), ("Text", "*.txt")])
	if not file:
		logger.debug("LSL export cancelled by user")
		return
	logger.info(f"Saving LSL script to: {file}")
	try:
		with open(file, "w", encoding="utf-8") as f:
			f.write(lsl)
		logger.info(f"LSL script exported successfully: {file}")
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_lsl_exported', _lang(self)) or "LSL-Skript exportiert. Notecard wird beim Textur-Speichern erzeugt.")
	except FileNotFoundError as e:
		error_msg = f"Could not save LSL script: {file}"
		logger.error(error_msg, exc_info=True)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=f"LSL-Export fehlgeschlagen: {e}")
		return
	except IOError as e:
		error_msg = f"IO error when saving LSL script: {file}"
		logger.error(error_msg, exc_info=True)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=f"LSL-Export fehlgeschlagen: {e}")
		return
	except Exception as e:
		error_msg = f"Error exporting LSL script: {str(e)}"
		logger.error(error_msg, exc_info=True)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=f"LSL-Export fehlgeschlagen: {e}")
		return

def _get_app_version() -> str:
	"""Liefert die App-Version ohne harten Modulimport zur Import-Zeit (verhindert Circular Imports)."""
	try:
		import main as app_main
		version = getattr(app_main, "Version", None)
		if isinstance(version, str) and version.strip():
			return version
	except Exception:
		pass
	return "2.2.0"

def generate_lsl_script(self: Any, name: str, tiles_x: int, tiles_y: int, speed: float) -> str:
	"""Kompatibilitäts-Wrapper: liefert das universelle Notecard-LSL-Script."""
	return generate_lsl_script_v2(self, name, tiles_x, tiles_y, speed)

def generate_lsl_notecard(name: str, tiles_x: int, tiles_y: int, speed: float, effect_tokens: list[str], movement_token: str) -> str:
	version = _get_app_version()
	created_at = datetime.now().strftime("%Y-%m-%d")
	effects = ", ".join(effect_tokens) if effect_tokens else "LOOP"
	movement = movement_token if movement_token in {"SLIDE", "ROTATE", "SCALE"} else "SLIDE"
	return f'''# OSSL2Gif {version}
# Copyright (c) 2026 Manfred Zainhofer
# Generated: {created_at}
# Texture Notecard: {name}.notecard

columns={tiles_x}
rows={tiles_y}
fps={speed}
start=0.0
effects={effects}
movement={movement}
face=ALL_SIDES
animOn=TRUE
'''

def _get_lsl_default_effect_tokens(self: Any) -> list[str]:
	effects: list[str] = []
	if not hasattr(self, 'lsl_effect_loop_var') or self.lsl_effect_loop_var.get():
		effects.append("LOOP")
	if hasattr(self, 'lsl_effect_smooth_var') and self.lsl_effect_smooth_var.get():
		effects.append("SMOOTH")
	if hasattr(self, 'lsl_effect_reverse_var') and self.lsl_effect_reverse_var.get():
		effects.append("REVERSE")
	if hasattr(self, 'lsl_effect_ping_pong_var') and self.lsl_effect_ping_pong_var.get():
		effects.append("PING_PONG")
	return effects

def _get_lsl_default_movement(self: Any) -> str:
	if hasattr(self, 'lsl_movement_var') and self.lsl_movement_var is not None:
		movement = str(self.lsl_movement_var.get()).strip().upper()
		if movement in {"SLIDE", "ROTATE", "SCALE"}:
			return movement
	return "SLIDE"

def generate_lsl_script_v2(self: Any, name: str, tiles_x: int, tiles_y: int, speed: float) -> str:
	"""Generiert ein universelles LSL-Script, das Parameter aus einer Notecard liest."""
	version = _get_app_version()
	created_at = datetime.now().strftime("%Y-%m-%d")
	default_effects = _get_lsl_default_effect_tokens(self)
	default_effects_lsl = ", ".join(default_effects) if default_effects else "LOOP"
	default_movement = _get_lsl_default_movement(self)
	movement_map = {
		"SLIDE": "0",
		"ROTATE": "ROTATE",
		"SCALE": "SCALE",
	}
	default_movement_lsl = movement_map.get(default_movement, "0")
	return f'''// Texture-Animation-Script.lsl
// Generated by OSSL2Gif {version}
// Copyright (c) 2026 Manfred Zainhofer
// Generated: {created_at}
// Universal: supports legacy texture names and multiple *.notecard playlists

integer animOn = TRUE;
list defaultEffects = [{default_effects_lsl}];
integer defaultMovement = {default_movement_lsl}; // 0=SLIDE, ROTATE, SCALE
integer face = ALL_SIDES;

integer sideX = {tiles_x};
integer sideY = {tiles_y};
float start = 0.0;
float length = (float)({tiles_x} * {tiles_y});
float speed = {speed};
string activeTexture = "{name}";

list playlistCards = [];
integer playlistIndex = 0;
string activeNotecard = "";

key notecardQuery;
integer notecardLine = 0;

string trimString(string value)
{{
	return llStringTrim(value, STRING_TRIM);
}}

integer isDigit(string c)
{{
	return (c == "0" || c == "1" || c == "2" || c == "3" || c == "4" || c == "5" || c == "6" || c == "7" || c == "8" || c == "9");
}}

integer isNumeric(string value)
{{
	string t = trimString(value);
	integer len = llStringLength(t);
	if(len == 0) return FALSE;

	integer dotSeen = FALSE;
	integer i;
	for(i = 0; i < len; i++)
	{{
		string c = llGetSubString(t, i, i);
		if(c == ".")
		{{
			if(dotSeen) return FALSE;
			dotSeen = TRUE;
		}}
		else if(c == "-")
		{{
			if(i != 0) return FALSE;
		}}
		else if(!isDigit(c))
		{{
			return FALSE;
		}}
	}}
	return TRUE;
}}

integer parseMovement(string value)
{{
	string token = llToUpper(trimString(value));
	if(token == "ROTATE") return ROTATE;
	if(token == "SCALE") return SCALE;
	if(token == "SLIDE") return 0;
	return defaultMovement;
}}

integer parseFace(string value)
{{
	string token = llToUpper(trimString(value));
	if(token == "ALL" || token == "ALL_SIDES") return ALL_SIDES;
	return (integer)token;
}}

list parseEffects(string value)
{{
	list tokens = llParseString2List(llToUpper(value), [",", ";", "|", " "], []);
	list resolved = [];
	integer i;
	for(i = 0; i < llGetListLength(tokens); i++)
	{{
		string token = trimString(llList2String(tokens, i));
		if(token == "LOOP") resolved += [LOOP];
		else if(token == "SMOOTH") resolved += [SMOOTH];
		else if(token == "REVERSE") resolved += [REVERSE];
		else if(token == "PING_PONG" || token == "PINGPONG") resolved += [PING_PONG];
	}}
	if(llGetListLength(resolved) == 0) return defaultEffects;
	return resolved;
}}

integer isNotecardConfig(string cardName)
{{
	string n = llToLower(trimString(cardName));
	integer end = llStringLength(n) - 1;
	if(end < 8) return FALSE;
	return (llGetSubString(n, end - 8, end) == ".notecard");
}}

string notecardToTexture(string cardName)
{{
	integer end = llStringLength(cardName) - 10;
	if(end < 0) return "";
	return llGetSubString(cardName, 0, end);
}}

list collectNotecardPlaylist()
{{
	list cards = [];
	integer i;
	integer count = llGetInventoryNumber(INVENTORY_NOTECARD);
	for(i = 0; i < count; i++)
	{{
		string card = llGetInventoryName(INVENTORY_NOTECARD, i);
		if(isNotecardConfig(card)) cards += [card];
	}}
	return cards;
}}

resetConfigDefaults()
{{
	sideX = {tiles_x};
	sideY = {tiles_y};
	start = 0.0;
	speed = {speed};
	face = ALL_SIDES;
	length = (float)(sideX * sideY);
}}

float getSwitchInterval()
{{
	float interval = 1.0;
	if(speed > 0.0) interval = length / speed;
	if(interval < 0.2) interval = 0.2;
	return interval;
}}

stopAnim()
{{
	llSetTextureAnim(FALSE, face, 0, 0, 0.0, 0.0, 0.0);
}}

startAnim(list effects, integer movement)
{{
	if(!animOn)
	{{
		stopAnim();
		llSetTimerEvent(0.0);
		return;
	}}

	integer effectBits = 0;
	integer i;
	for(i = 0; i < llGetListLength(effects); i++)
	{{
		effectBits = effectBits | llList2Integer(effects, i);
	}}
	llSetTextureAnim(ANIM_ON | effectBits | movement, face, sideX, sideY, start, length, speed);

	if(llGetListLength(playlistCards) > 1)
		llSetTimerEvent(getSwitchInterval());
	else
		llSetTimerEvent(0.0);
}}

applyConfig(list effects, integer movement)
{{
	if(activeTexture == "")
	{{
		activeTexture = llGetInventoryName(INVENTORY_TEXTURE, 0);
	}}

	if(activeTexture == "" || llGetInventoryType(activeTexture) != INVENTORY_TEXTURE)
	{{
		llOwnerSay("Keine passende Textur im Inventar gefunden.");
		stopAnim();
		return;
	}}

	if(sideX < 1) sideX = 1;
	if(sideY < 1) sideY = 1;
	if(speed <= 0.0) speed = 1.0;
	length = (float)(sideX * sideY);
	llSetTexture(activeTexture, face);
	startAnim(effects, movement);
}}

parseConfigLine(string line)
{{
	string cleaned = trimString(line);
	if(cleaned == "") return;
	if(llGetSubString(cleaned, 0, 0) == "#") return;
	if(llGetSubString(cleaned, 0, 1) == "//") return;

	integer eq = llSubStringIndex(cleaned, "=");
	if(eq == -1) return;

	string cfgKey = llToLower(trimString(llGetSubString(cleaned, 0, eq - 1)));
	string cfgValue = trimString(llGetSubString(cleaned, eq + 1, -1));

	if(cfgKey == "columns" || cfgKey == "tiles_x" || cfgKey == "sidex") sideX = (integer)cfgValue;
	else if(cfgKey == "rows" || cfgKey == "tiles_y" || cfgKey == "sidey") sideY = (integer)cfgValue;
	else if(cfgKey == "fps" || cfgKey == "speed" || cfgKey == "rate") speed = (float)cfgValue;
	else if(cfgKey == "start") start = (float)cfgValue;
	else if(cfgKey == "effects") defaultEffects = parseEffects(cfgValue);
	else if(cfgKey == "movement") defaultMovement = parseMovement(cfgValue);
	else if(cfgKey == "face") face = parseFace(cfgValue);
	else if(cfgKey == "animon")
	{{
		string b = llToUpper(cfgValue);
		animOn = (b == "TRUE" || b == "1" || b == "YES" || b == "ON");
	}}
}}

parseLegacyTextureName(string textureName)
{{
	list tokens = llParseString2List(textureName, ["_"], []);
	integer count = llGetListLength(tokens);
	integer i;
	integer startIndex = -1;

	for(i = 0; i <= count - 4; i++)
	{{
		if(isNumeric(llList2String(tokens, i)) && isNumeric(llList2String(tokens, i + 1)) && isNumeric(llList2String(tokens, i + 2)) && isNumeric(llList2String(tokens, i + 3)))
		{{
			startIndex = i;
			jump found_legacy;
		}}
	}}

	@found_legacy;
	if(startIndex == -1) return;

	sideX = (integer)llList2String(tokens, startIndex);
	sideY = (integer)llList2String(tokens, startIndex + 1);
	speed = (float)llList2String(tokens, startIndex + 2);
	start = (float)llList2String(tokens, startIndex + 3);

	list parsedEffects = [];
	integer parsedMovement = defaultMovement;
	for(i = startIndex + 4; i < count; i++)
	{{
		string token = llToUpper(trimString(llList2String(tokens, i)));
		if(token == "ROTATE" || token == "SCALE" || token == "SLIDE")
		{{
			parsedMovement = parseMovement(token);
		}}
		else if(token == "LOOP") parsedEffects += [LOOP];
		else if(token == "SMOOTH") parsedEffects += [SMOOTH];
		else if(token == "REVERSE") parsedEffects += [REVERSE];
		else if(token == "PING_PONG" || token == "PINGPONG") parsedEffects += [PING_PONG];
	}}

	if(llGetListLength(parsedEffects) > 0) defaultEffects = parsedEffects;
	defaultMovement = parsedMovement;
}}

loadNotecard(integer index)
{{
	integer count = llGetListLength(playlistCards);
	if(count == 0) return;

	if(index < 0) index = 0;
	if(index >= count) index = 0;
	playlistIndex = index;

	activeNotecard = llList2String(playlistCards, playlistIndex);
	activeTexture = notecardToTexture(activeNotecard);
	resetConfigDefaults();
	notecardLine = 0;
	notecardQuery = llGetNotecardLine(activeNotecard, notecardLine);
}}

loadCurrentAnimation()
{{
	playlistCards = collectNotecardPlaylist();
	if(llGetListLength(playlistCards) > 0)
	{{
		loadNotecard(playlistIndex);
		return;
	}}

	resetConfigDefaults();
	activeTexture = llGetInventoryName(INVENTORY_TEXTURE, 0);
	if(activeTexture != "")
	{{
		parseLegacyTextureName(activeTexture);
	}}
	applyConfig(defaultEffects, defaultMovement);
}}

default
{{
	state_entry()
	{{
		stopAnim();
		loadCurrentAnimation();
	}}

	on_rez(integer start_param)
	{{
		llResetScript();
	}}

	changed(integer what)
	{{
		if(what & CHANGED_INVENTORY)
		{{
			playlistIndex = 0;
			loadCurrentAnimation();
		}}
	}}

	dataserver(key query_id, string data)
	{{
		if(query_id != notecardQuery) return;

		if(data != EOF)
		{{
			parseConfigLine(data);
			notecardLine++;
			notecardQuery = llGetNotecardLine(activeNotecard, notecardLine);
		}}
		else
		{{
			applyConfig(defaultEffects, defaultMovement);
		}}
	}}

	timer()
	{{
		if(!animOn) return;
		if(llGetListLength(playlistCards) <= 1) return;
		playlistIndex++;
		if(playlistIndex >= llGetListLength(playlistCards)) playlistIndex = 0;
		loadNotecard(playlistIndex);
	}}

	touch_start(integer total_number)
	{{
		animOn = !animOn;
		applyConfig(defaultEffects, defaultMovement);
	}}
}}
'''
