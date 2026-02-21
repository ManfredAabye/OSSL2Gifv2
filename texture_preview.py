###
# texture_preview.py
# Texture animation preview window für OSSL2Gif - zeigt wie die Animation in OpenSim/Second Life aussieht
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import math
from typing import Any, Optional
from translations import tr
from image_processing import calculate_optimal_grid, apply_effects
from logging_config import get_logger

logger = get_logger(__name__)

class TexturePreviewWindow:
	"""
	Zeigt eine Vorschau der Textur-Animation wie sie in OpenSim/Second Life abgespielt wird.
	Simuliert das Frame-by-Frame-Durchlaufen des Texture-Sheets.
	"""
	
	def __init__(self, parent_app: Any):
		self.app = parent_app
		self.window: Optional[tk.Toplevel] = None
		self.canvas: Optional[tk.Canvas] = None
		self.playing = False
		self.current_tile = 0
		self.tiles_x = 1
		self.tiles_y = 1
		self.texture_image: Optional[Image.Image] = None
		self.canvas_image_ref: Optional[ImageTk.PhotoImage] = None
		self.after_id: Optional[str] = None
		
	def show(self):
		"""Öffnet das Vorschaufenster und startet die Animation."""
		if not self.app.gif_frames:
			from tkinter import messagebox
			messagebox.showwarning("Keine Daten", "Bitte zuerst ein GIF laden.")
			return
		
		# Wenn Fenster bereits offen, in den Vordergrund holen
		if self.window and self.window.winfo_exists():
			self.window.lift()
			self.window.focus_force()
			return
		
		# Neues Fenster erstellen
		self.window = tk.Toplevel(self.app.root)
		self.window.title(f"Textur-Vorschau (OpenSim/SL) - {len(self.app.gif_frames)} Frames")
		
		# Dark Theme für Fenster
		try:
			self.window.configure(bg='#1e1e1e')
		except:
			pass
		
		# Hauptframe
		main_frame = ttk.Frame(self.window)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Info-Label
		info_text = f"Grid: {self.tiles_x}x{self.tiles_y} | Frames: {len(self.app.gif_frames)} | Geschwindigkeit: {self.app.framerate_var.get()}ms"
		info_label = ttk.Label(main_frame, text=info_text, font=("Segoe UI", 10))
		info_label.pack(pady=(0, 5))
		
		# Canvas für Animation
		self.canvas = tk.Canvas(main_frame, width=512, height=512, bg='#222222', highlightthickness=0)
		self.canvas.pack(pady=10)
		
		# Steuerung
		control_frame = ttk.Frame(main_frame)
		control_frame.pack(pady=10)
		
		self.play_btn = ttk.Button(control_frame, text="▶ Abspielen", command=self.toggle_play)
		self.play_btn.pack(side=tk.LEFT, padx=5)
		
		self.stop_btn = ttk.Button(control_frame, text="⏹ Stop", command=self.stop_preview)
		self.stop_btn.pack(side=tk.LEFT, padx=5)
		
		ttk.Button(control_frame, text="✖ Schließen", command=self.close).pack(side=tk.LEFT, padx=5)
		
		# Geschwindigkeits-Slider
		speed_frame = ttk.Frame(main_frame)
		speed_frame.pack(pady=10, fill=tk.X)
		
		ttk.Label(speed_frame, text="Geschwindigkeit:").pack(side=tk.LEFT, padx=5)
		self.speed_var = tk.IntVar(value=self.app.framerate_var.get())
		speed_scale = ttk.Scale(speed_frame, from_=10, to=500, orient=tk.HORIZONTAL, variable=self.speed_var, length=300)
		speed_scale.pack(side=tk.LEFT, padx=5)
		self.speed_label = ttk.Label(speed_frame, text=f"{self.speed_var.get()}ms")
		self.speed_label.pack(side=tk.LEFT, padx=5)
		self.speed_var.trace_add('write', lambda *args: self.speed_label.config(text=f"{self.speed_var.get()}ms"))
		
		# Textur vorbereiten
		self._prepare_texture()
		
		# Beim Schließen aufräumen
		self.window.protocol("WM_DELETE_WINDOW", self.close)
		
		# Fenster an Inhalt anpassen und zentrieren
		self.window.update_idletasks()
		width = max(self.window.winfo_reqwidth(), 700)  # Mindestbreite 700
		height = max(self.window.winfo_reqheight(), 700)  # Mindesthöhe 700
		x = (self.window.winfo_screenwidth() // 2) - (width // 2)
		y = (self.window.winfo_screenheight() // 2) - (height // 2)
		self.window.geometry(f'{width}x{height}+{x}+{y}')
		
		# Animation automatisch starten
		self.playing = True
		self._animate()
	
	def _prepare_texture(self):
		"""Bereitet die Textur für die Vorschau vor."""
		try:
			# Grid berechnen
			self.tiles_x, self.tiles_y = calculate_optimal_grid(len(self.app.gif_frames))
			
			# Textur generieren (wie beim Export)
			bg_color = self.app.bg_color
			if bg_color.startswith('#'):
				if len(bg_color) == 9:  # #RRGGBBAA
					bg_rgba = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5, 7))
				else:  # #RRGGBB
					rgb = tuple(int(bg_color[i:i+2], 16) for i in (1, 3, 5))
					bg_rgba = rgb + (255,)
			else:
				bg_rgba = (0, 0, 0, 0)
			
			# Erstelle Textur-Sheet
			frame_size = 512 // max(self.tiles_x, self.tiles_y)
			sheet_w = self.tiles_x * frame_size
			sheet_h = self.tiles_y * frame_size
			
			self.texture_image = Image.new("RGBA", (sheet_w, sheet_h), bg_rgba)
			
			# Frames platzieren
			for idx, frame in enumerate(self.app.gif_frames):
				tx = idx % self.tiles_x
				ty = idx // self.tiles_x
				
				# Frame mit Effekten
				f = apply_effects(self.app, frame, prefix="texture")
				f = f.resize((frame_size, frame_size), Image.Resampling.LANCZOS)
				
				if f.mode != "RGBA":
					f = f.convert("RGBA")
				
				x = tx * frame_size
				y = ty * frame_size
				
				# Frame platzieren
				self.texture_image.paste(f, (x, y), f if f.mode == "RGBA" else None)
			
			logger.info(f"Texture preview prepared: {sheet_w}x{sheet_h}, grid {self.tiles_x}x{self.tiles_y}")
			
		except Exception as e:
			logger.error(f"Failed to prepare texture preview: {e}", exc_info=True)
	
	def _animate(self):
		"""Animiert durch die Texture-Tiles."""
		if not self.playing or not self.window or not self.window.winfo_exists():
			return
		
		if not self.texture_image or not self.canvas:
			return
		
		try:
			# Berechne aktuelles Tile
			tx = self.current_tile % self.tiles_x
			ty = self.current_tile // self.tiles_x
			
			# Frame-Größe
			frame_size = self.texture_image.width // self.tiles_x
			
			# Extrahiere aktuelles Tile
			x1 = tx * frame_size
			y1 = ty * frame_size
			x2 = x1 + frame_size
			y2 = y1 + frame_size
			
			tile = self.texture_image.crop((x1, y1, x2, y2))
			
			# Auf Canvas-Größe skalieren
			canvas_size = 512
			tile_scaled = tile.resize((canvas_size, canvas_size), Image.Resampling.NEAREST)
			
			# Auf Canvas anzeigen
			self.canvas_image_ref = ImageTk.PhotoImage(tile_scaled)
			self.canvas.delete("all")
			self.canvas.create_image(256, 256, image=self.canvas_image_ref)
			
			# Nächstes Frame
			self.current_tile = (self.current_tile + 1) % len(self.app.gif_frames)
			
			# Timer für nächstes Frame
			delay = self.speed_var.get()
			self.after_id = self.window.after(delay, self._animate)
			
		except Exception as e:
			logger.error(f"Animation error: {e}", exc_info=True)
			self.playing = False
	
	def toggle_play(self):
		"""Startet/Pausiert die Animation."""
		if self.playing:
			self.playing = False
			if self.after_id and self.window:
				self.window.after_cancel(self.after_id)
				self.after_id = None
			self.play_btn.config(text="▶ Abspielen")
		else:
			self.playing = True
			self.play_btn.config(text="⏸ Pause")
			self._animate()
	
	def stop_preview(self):
		"""Stoppt die Animation und setzt zurück."""
		self.playing = False
		if self.after_id and self.window:
			self.window.after_cancel(self.after_id)
			self.after_id = None
		self.current_tile = 0
		self.play_btn.config(text="▶ Abspielen")
		# Zeige erstes Frame
		if self.texture_image and self.canvas:
			self._animate()
			self.playing = False
	
	def close(self):
		"""Schließt das Vorschaufenster."""
		self.playing = False
		if self.after_id and self.window:
			self.window.after_cancel(self.after_id)
			self.after_id = None
		if self.window:
			self.window.destroy()
			self.window = None

def show_texture_preview(app: Any):
	"""Öffnet das Textur-Vorschaufenster."""
	preview = TexturePreviewWindow(app)
	preview.show()
