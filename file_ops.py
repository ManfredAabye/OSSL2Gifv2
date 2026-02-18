###
# file_ops.py
# This file contains file operations for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

import math
import os
import logging
from typing import Any
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from translations import tr
from image_processing import apply_effects

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
	try:
		self.gif_image = Image.open(file)
		while True:
			frames.append(self.gif_image.copy())
			self.gif_image.seek(len(frames))
	except FileNotFoundError:
		messagebox.showerror("Fehler", f"Datei nicht gefunden: {file}")
		return
	except UnidentifiedImageError:
		messagebox.showerror("Fehler", f"Die Datei ist kein gültiges GIF oder beschädigt: {file}")
		return
	except EOFError:
		pass
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher zum Laden des GIFs.")
		return
	except Exception as e:
		messagebox.showerror("Fehler", f"Unbekannter Fehler beim Laden des GIFs: {e}")
		return
	finally:
		# Schließe die GIF-Datei, um Ressourcen freizugeben (Frames sind bereits im Speicher kopiert)
		if hasattr(self, 'gif_image') and self.gif_image is not None:
			try:
				self.gif_image.close()
			except Exception:
				pass
	if not frames and hasattr(self, 'gif_image'):
		try:
			frames.append(self.gif_image.copy())
		except Exception:
			messagebox.showerror("Fehler", "GIF konnte nicht geladen werden.")
			return
	logging.debug(f"Frames geladen: {len(frames)}")
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
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
	if not file:
		return
	try:
		frames = [apply_effects(self, f.resize((self.width_var.get(), self.height_var.get())), "gif") for f in self.gif_frames]
		duration = self.framerate_var.get()
		frames[0].save(file, save_all=True, append_images=frames[1:], loop=0, duration=duration)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_gif_saved', self.lang) or "GIF gespeichert.")
	except FileNotFoundError:
		messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden: {file}")
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher zum Speichern des GIFs.")
	except Exception as e:
		messagebox.showerror("Fehler", f"Fehler beim Speichern des GIFs: {e}")

def save_texture(self: Any) -> None:
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Keine Frames vorhanden.")
		return
	
	# Textur mit aktueller Hintergrundfarbe regenerieren (vor dem Speichern)
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
		elif isinstance(bg_color, str) and len(bg_color) == 7:
			# Format: #RRGGBB (vollständig undurchsichtig)
			color_result = ImageColor.getcolor(bg_color, "RGBA")
			# Stelle sicher, dass wir ein 4er-Tupel haben
			if isinstance(color_result, tuple) and len(color_result) >= 3:
				bg_rgba = (int(color_result[0]), int(color_result[1]), int(color_result[2]), 255)
		else:
			bg_rgba = (0, 0, 0, 0)
	except Exception:
		bg_rgba = (0, 0, 0, 0)
	
	# Sheet mit aktueller Hintergrundfarbe erzeugen
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
	
	# WICHTIG: Hintergrundfarbe in die Texture einbetten (nicht nur als Hintergrund)
	# Wenn nicht vollständig transparent, composite gegen den Hintergrund
	if bg_rgba[3] > 0:  # Nicht vollständig transparent
		background = Image.new("RGBA", sheet.size, bg_rgba)
		sheet = Image.alpha_composite(background, sheet)
	
	# Gespeicherte Textur für Datei-Dialog vorbereiten
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	speed_val = self.framerate_var.get()
	speed = f"{speed_val};0"
	ext = self.export_format_var.get().lower()
	defext = f".{ext}"
	filetypes = [(ext.upper(), f"*.{ext}") for ext in ["png", "jpg", "bmp"]]
	file = filedialog.asksaveasfilename(defaultextension=defext, initialfile=f"{name};{tiles_x};{tiles_y};{speed}.{ext}", filetypes=filetypes)
	if not file:
		return
	fmt = self.export_format_var.get().upper()
	if fmt == "ZIP":
		import zipfile
		try:
			with zipfile.ZipFile(file, 'w', zipfile.ZIP_DEFLATED) as zipf:
				for idx, frame in enumerate(self.gif_frames):
					img = apply_effects(self, frame.resize((self.width_var.get(), self.height_var.get())), "gif")
					img_bytes = None
					from io import BytesIO
					img_bytes = BytesIO()
					img.save(img_bytes, format="PNG")
					img_bytes.seek(0)
					zipf.writestr(f"frame_{idx+1:03d}.png", img_bytes.read())
			if hasattr(self, 'status') and self.status:
				self.status.config(text=tr('status_zip_saved', self.lang) or "GIF-Einzelbilder als ZIP gespeichert.")
		except Exception as e:
			messagebox.showerror("Fehler", f"Fehler beim ZIP-Export: {e}")
		return
	if fmt == "JPG":
		fmt = "JPEG"
	try:
		img = sheet
		if fmt == "JPEG":
			# Bei JPG: Immer zu RGB konvertieren (mit eingebetteter Hintergrundfarbe)
			img = img.convert("RGB")
		# Bei PNG: RGBA behalten (mit eingebetteter Hintergrundfarbe) oder zu RGB wenn nötig
		elif fmt == "PNG":
			if img.mode != "RGBA":
				img = img.convert("RGBA")
		img.save(file, format=fmt)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_texture_saved', self.lang) or "Textur gespeichert.")
	except FileNotFoundError:
		messagebox.showerror("Fehler", f"Datei konnte nicht gespeichert werden: {file}")
	except MemoryError:
		messagebox.showerror("Fehler", "Nicht genügend Speicher zum Speichern der Textur.")
	except Exception as e:
		messagebox.showerror("Fehler", f"Fehler beim Speichern der Textur: {e}")

def export_lsl(self: Any) -> None:
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	frame_count = self.frame_count
	tiles_x = math.ceil(math.sqrt(frame_count))
	tiles_y = math.ceil(frame_count / tiles_x)
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	speed = 10.0
	lsl = generate_lsl_script(self, name, tiles_x, tiles_y, speed)
	file = filedialog.asksaveasfilename(defaultextension=".lsl", initialfile=f"{name}.lsl", filetypes=[("LSL", "*.lsl"), ("Text", "*.txt")])
	if not file:
		return
	try:
		with open(file, "w", encoding="utf-8") as f:
			f.write(lsl)
		if hasattr(self, 'status') and self.status:
			self.status.config(text=tr('status_lsl_exported', self.lang) or "LSL-Skript exportiert.")
	except Exception as e:
		messagebox.showerror("Fehler", str(e))

def generate_lsl_script(self: Any, name: str, tiles_x: int, tiles_y: int, speed: float) -> str:
		length = tiles_x * tiles_y
		return f'''// LSL Texture Animation Script\n// Generated by OSSL2Gif\n// Texture: {name};{tiles_x};{tiles_y};{speed}\n\ninteger animOn = TRUE;\nlist effects = [LOOP];\ninteger movement = 0;\ninteger face = ALL_SIDES;\ninteger sideX = {tiles_x};\ninteger sideY = {tiles_y};\nfloat start = 0.0;\nfloat length = {length};\nfloat speed = {speed};\n\ninitAnim() {{\n    if(animOn) {{\n        integer effectBits;\n        integer i;\n        for(i = 0; i < llGetListLength(effects); i++) {{\n            effectBits = (effectBits | llList2Integer(effects,i));\n        }}\n        integer params = (effectBits|movement);\n        llSetTextureAnim(ANIM_ON|params,face,sideX,sideY,start,length,speed);\n    }}\n    else {{\n        llSetTextureAnim(0,face,sideX,sideY,start,length,speed);\n    }}\n}}\n\nfetch() {{\n     string texture = llGetInventoryName(INVENTORY_TEXTURE,0);\n            llSetTexture(texture,face);\n            // llParseString2List braucht als Trennzeichen eine Liste!\n            list data  = llParseString2List(texture,[";"],[]);\n            string X = llList2String(data,1);\n            string Y = llList2String(data,2);\n            string Z = llList2String(data,3);\n            sideX = (integer) X;\n            sideY = (integer) Y;\n            speed = (float) Z;\n            length = (float)(sideX * sideY);\n            if (speed) \n                initAnim();\n}}\n\ndefault\n{{\n    state_entry()\n    {{\n        llSetTextureAnim(FALSE, face, 0, 0, 0.0, 0.0, 1.0);\n        fetch();\n    }}\n    changed(integer what)\n    {{\n        if (what & CHANGED_INVENTORY)\n        {{\n            fetch();\n        }}\n    }}\n}}\n'''
