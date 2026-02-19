###
# events.py
# This file contains event handlers for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###
from tkinter import messagebox, colorchooser, ttk
from PIL import Image
from translations import tr
from image_processing import show_gif_frame
import threading

def reset_settings(self):
	self.width_var.set(2048)
	self.height_var.set(2048)
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	# Schachbrett-Pattern zurücksetzen (vollständig transparent)
	from gui_layout import create_checkerboard_with_color
	self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=0, size=32, checker_size=4)
	self.bg_color_box.config(image=self.bg_color_photo)
	# Intelligente Skalierung ist jetzt immer aktiv
	self.framerate_var.set(10)
	self.export_format_var.set("PNG")
	self.maxframes_var.set(64)
	self.lang_var.set("de")
	for prefix in ("gif", "texture"):
		self.__dict__[f'{prefix}_grayscale'].set(0)
		self.__dict__[f'{prefix}_sharpen'].set(0)
		self.__dict__[f'{prefix}_blur'].set(0)
		self.__dict__[f'{prefix}_transparency'].set(0)
		self.__dict__[f'{prefix}_sharpen_value'].set(2.5)
		self.__dict__[f'{prefix}_blur_value'].set(3.5)
		self.__dict__[f'{prefix}_transparency_value'].set(0.5)
		self.__dict__[f'{prefix}_colorintensity'].set(0.5)
		self.__dict__[f'{prefix}_colorintensity_active'].set(0)
	self.update_language()
	self.current_frame = 0
	self.playing = False
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		file = self.gif_image.filename
		try:
			self.gif_image = Image.open(file)
			self.gif_frames = []
			while True:
				self.gif_frames.append(self.gif_image.copy())
				self.gif_image.seek(len(self.gif_frames))
		except EOFError:
			pass
		except Exception:
			self.gif_frames = []
		self.frame_count = len(self.gif_frames)
		self.current_frame = 0
		if self.gif_frames:
			show_gif_frame(self)
	else:
		update_previews(self)

def on_maxframes_changed(self, *args):
	max_frames = self.maxframes_var.get()
	if hasattr(self, 'gif_frames') and len(self.gif_frames) > max_frames:
		removed = len(self.gif_frames) - max_frames
		self.gif_frames = self.gif_frames[:max_frames]
		self.frame_count = len(self.gif_frames)
		self.status.config(text=f"{removed} Bilder entfernt. Gesamt: {self.frame_count}")
		value = self.frame_select_var.get()
		self.frame_select_spin.destroy()
		self.frame_select_spin = ttk.Spinbox(self.add_row, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
		# Beide Widgets neu packen, Reihenfolge: erst Spinbox, dann Button
		self.add_frame_btn.pack_forget()
		self.frame_select_spin.pack_forget()
		self.frame_select_spin.pack(side="right")
		self.add_frame_btn.pack(side="right", padx=(0,4))
		self.frame_select_var.set(min(value, self.frame_count-1))
		update_previews(self)

def choose_bg_color(self, event=None):
	"""Öffnet einen Color-Chooser und erlaubt die Auswahl einer transparenten Hintergrundfarbe."""
	from tkinter import simpledialog
	color = colorchooser.askcolor(color=self.bg_box_color, title="Hintergrundfarbe wählen")
	if color and color[1]:
		self.bg_box_color = color[1]
		# Frage nach Transparenz
		transparency = simpledialog.askinteger(
			"Transparenz",
			"Transparenz (0=vollständig transparent, 255=undurchsichtig):",
			initialvalue=255,
			minvalue=0,
			maxvalue=255
		)
		if transparency is not None:
			# Konvertiere RGB zu RGBA mit Alpha-Wert
			alpha_hex = format(transparency, '02x')
			self.bg_color = self.bg_box_color + alpha_hex
		else:
			# Falls abgebrochen, verwende vollständig undurchsichtig
			self.bg_color = self.bg_box_color + "ff"
		# Update Schachbrett-Pattern mit neuer Farbe und Transparenz
		from gui_layout import create_checkerboard_with_color
		alpha_value = int(self.bg_color[7:9], 16) if len(self.bg_color) == 9 else 255
		self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=alpha_value, size=32, checker_size=4)
		self.bg_color_box.config(image=self.bg_color_photo)
		update_previews(self)

def set_transparent_bg(self):
	"""Setzt die Hintergrundfarbe auf 100% transparent (Rechtsklick auf bg_color_box)."""
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	# Update Schachbrett-Pattern mit vollständiger Transparenz
	from gui_layout import create_checkerboard_with_color
	self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=0, size=32, checker_size=4)
	self.bg_color_box.config(image=self.bg_color_photo)
	update_previews(self)

def add_selected_frame_to_texture(self):
	import threading
	def do_add():
		idx = self.frame_select_var.get()
		if not self.gif_frames or idx < 0 or idx >= len(self.gif_frames):
			messagebox.showerror("Fehler", "Ungültige Bildnummer.")
			return
		max_frames = self.maxframes_var.get()
		if len(self.gif_frames) >= max_frames:
			messagebox.showerror("Fehler", f"Maximale Bildanzahl ({max_frames}) erreicht.")
			return
		frame = self.gif_frames[idx].copy()
		self.gif_frames.append(frame)
		self.frame_count = len(self.gif_frames)
		value = self.frame_select_var.get()
		self.frame_select_spin.config(to=max(0, self.frame_count-1))
		self.frame_select_var.set(value)
		self.status.config(text=f"Bild {idx} hinzugefügt. Gesamt: {self.frame_count}")
		update_previews(self)
	threading.Thread(target=do_add).start()

def remove_selected_frame_from_texture(self):
	import threading
	def do_remove():
		idx = self.frame_select_var.get()
		if not self.gif_frames or idx < 0 or idx >= len(self.gif_frames):
			messagebox.showerror("Fehler", "Ungültige Bildnummer.")
			return
		if len(self.gif_frames) <= 1:
			messagebox.showerror("Fehler", "Mindestens ein Bild muss erhalten bleiben.")
			return
		del self.gif_frames[idx]
		self.frame_count = len(self.gif_frames)
		# ACHTUNG: maxframes_var NICHT verändern, damit kein weiteres Bild entfernt wird!
		value = min(self.frame_select_var.get(), self.frame_count-1)
		self.frame_select_spin.config(to=max(0, self.frame_count-1))
		self.frame_select_var.set(value)
		self.status.config(text=f"Bild {idx} entfernt. Gesamt: {self.frame_count}")
		update_previews(self)
	threading.Thread(target=do_remove).start()

def change_language(self, event=None):
	self.lang = self.lang_var.get()
	self.update_language()  # Tooltips und Labels übersetzen
	update_previews(self)

def update_previews(self):
	"""Aktualisiert beide Vorschau-Canvas mit aktueller Hintergrundfarbe"""
	from image_processing import show_gif_frame
	if self.gif_frames:
		show_gif_frame(self)
	# Textur IMMER aktualisieren, wenn Frames vorhanden sind
	if self.gif_frames and hasattr(self, 'show_texture'):
		self.show_texture()
	elif hasattr(self, 'show_texture'):
		# Falls kein GIF, nur Textur mit aktuellem Hintergrund anzeigen
		self.show_texture()
