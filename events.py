###
# events.py
# This file contains event handlers for the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###
from tkinter import messagebox, colorchooser, ttk
import tkinter as tk
from PIL import Image
from translations import tr
from image_processing import show_gif_frame
from logging_config import get_logger
import threading

logger = get_logger(__name__)

def reset_settings(self):
	self.width_var.set(2048)
	self.height_var.set(2048)
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	self.bg_transparency_var.set(0)  # Transparenz-Schieberegler zurücksetzen
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
			pass  # Normal: End of GIF reached
		except Exception as e:
			logger.warning(f"Error reloading GIF during reset: {type(e).__name__}: {e}", exc_info=False)
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
	color = colorchooser.askcolor(color=self.bg_box_color, title="Hintergrundfarbe wählen")
	if color and color[1]:
		self.bg_box_color = color[1]
		# Update Schachbrett-Pattern mit aktueller Transparenz
		from gui_layout import create_checkerboard_with_color
		current_alpha = self.bg_transparency_var.get()
		alpha_hex = format(current_alpha, '02x')
		self.bg_color = self.bg_box_color + alpha_hex
		self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=current_alpha, size=32, checker_size=4)
		self.bg_color_box.config(image=self.bg_color_photo)
		update_previews(self)

def on_bg_transparency_changed(self, *args):
	"""Callback wenn der Transparenz-Schieberegler für Hintergrund bewegt wird."""
	alpha = self.bg_transparency_var.get()
	percent = int((alpha / 255) * 100)
	self.transparency_bg_percent.config(text=f"{percent}%")
	
	# Update Hintergrundfarbe mit neuer Transparenz
	alpha_hex = format(alpha, '02x')
	self.bg_color = self.bg_box_color + alpha_hex
	
	# Update Schachbrett-Pattern
	from gui_layout import create_checkerboard_with_color
	self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=alpha, size=32, checker_size=4)
	self.bg_color_box.config(image=self.bg_color_photo)
	
	# Update Previews
	update_previews(self)

def set_transparent_bg(self):
	"""Setzt die Hintergrundfarbe auf 100% transparent (Rechtsklick auf bg_color_box)."""
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	self.bg_transparency_var.set(0)  # Transparenz-Schieberegler auf 0
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
