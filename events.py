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

def _clamp_int(value, min_value, max_value, default_value):
	try:
		parsed = int(round(float(value)))
	except Exception:
		parsed = default_value
	return max(min_value, min(max_value, parsed))

def _cancel_background_preview_update(self):
	after_id = getattr(self, '_bg_preview_after_id', None)
	if after_id and hasattr(self, 'root') and self.root is not None:
		try:
			self.root.after_cancel(after_id)
		except Exception:
			pass
	self._bg_preview_after_id = None

def _schedule_background_preview_update(self, delay_ms=90):
	if not hasattr(self, 'root') or self.root is None:
		update_previews(self)
		return

	_cancel_background_preview_update(self)

	def _run():
		self._bg_preview_after_id = None
		update_previews(self)

	self._bg_preview_after_id = self.root.after(delay_ms, _run)

def _apply_background_state(self, color_hex=None, transparency_percent=None, refresh_previews=True, sync_slider=False):
	"""Zentralisiert Hintergrundfarbe + Transparenz (0-100%, 100 = voll transparent)."""
	if color_hex is not None and isinstance(color_hex, str) and len(color_hex) == 7 and color_hex.startswith('#'):
		self.bg_box_color = color_hex
	elif not hasattr(self, 'bg_box_color'):
		self.bg_box_color = "#000000"

	if transparency_percent is None:
		if hasattr(self, 'bg_transparency_var') and self.bg_transparency_var is not None:
			transparency_percent = _clamp_int(self.bg_transparency_var.get(), 0, 100, 100)
		else:
			transparency_percent = 100
	else:
		transparency_percent = _clamp_int(transparency_percent, 0, 100, 100)

	alpha = int(round(255 * (100 - transparency_percent) / 100))
	self.bg_color = f"{self.bg_box_color}{alpha:02x}"

	from gui_layout import create_checkerboard_with_color
	self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=alpha, size=32, checker_size=4)
	self.bg_color_box.config(image=self.bg_color_photo)

	if hasattr(self, 'transparency_bg_percent') and self.transparency_bg_percent is not None:
		self.transparency_bg_percent.config(text=f"{transparency_percent}%")

	if sync_slider and hasattr(self, 'bg_transparency_var') and self.bg_transparency_var is not None:
		current_value = _clamp_int(self.bg_transparency_var.get(), 0, 100, 100)
		if current_value != transparency_percent:
			self._bg_sync_in_progress = True
			self.bg_transparency_var.set(transparency_percent)
			self._bg_sync_in_progress = False

	if refresh_previews:
		update_previews(self)

def apply_background_from_config(self, color_value):
	"""Wendet konfigurierte Hintergrundfarbe robust an. Unterstützt #RRGGBBAA und #RRGGBB."""
	if isinstance(color_value, str) and len(color_value) == 9 and color_value.startswith('#'):
		base_color = color_value[:7]
		try:
			alpha_raw = int(color_value[7:9], 16)
		except Exception:
			alpha_raw = 0
		alpha = _clamp_int(alpha_raw, 0, 255, 0)
		transparency_percent = int(round((255 - alpha) * 100 / 255))
		_apply_background_state(self, color_hex=base_color, transparency_percent=transparency_percent, refresh_previews=False, sync_slider=True)
	elif isinstance(color_value, str) and len(color_value) == 7 and color_value.startswith('#'):
		_apply_background_state(self, color_hex=color_value, transparency_percent=0, refresh_previews=False, sync_slider=True)
	else:
		_apply_background_state(self, color_hex="#000000", transparency_percent=100, refresh_previews=False, sync_slider=True)

def reset_settings(self):
	self.width_var.set(2048)
	self.height_var.set(2048)
	if hasattr(self, 'size_preset_var') and self.size_preset_var is not None:
		self.size_preset_var.set("2048")
	_apply_background_state(self, color_hex="#000000", transparency_percent=100, refresh_previews=False, sync_slider=True)
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
		update_previews(self)
	else:
		self.texture_image = None
		if hasattr(self, 'gif_canvas') and self.gif_canvas is not None:
			self.gif_canvas.config(image="")
		if hasattr(self, 'texture_canvas') and self.texture_canvas is not None:
			self.texture_canvas.config(image="")
		self._gif_img_ref = None
		self._texture_img_ref = None

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
		_cancel_background_preview_update(self)
		current_transparency = _clamp_int(self.bg_transparency_var.get(), 0, 100, 100)
		_apply_background_state(self, color_hex=color[1], transparency_percent=current_transparency, refresh_previews=True, sync_slider=False)

def on_bg_transparency_changed(self, *args):
	"""Callback wenn der Transparenz-Schieberegler für Hintergrund bewegt wird."""
	if getattr(self, '_bg_sync_in_progress', False):
		return
	transparency_percent = _clamp_int(self.bg_transparency_var.get(), 0, 100, 100)
	_apply_background_state(self, transparency_percent=transparency_percent, refresh_previews=False, sync_slider=False)
	_schedule_background_preview_update(self)

def set_transparent_bg(self):
	"""Setzt die Hintergrundfarbe auf 100% transparent (Rechtsklick auf bg_color_box)."""
	_cancel_background_preview_update(self)
	_apply_background_state(self, color_hex="#000000", transparency_percent=100, refresh_previews=True, sync_slider=True)

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
