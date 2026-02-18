###
# gui_layout.py
# This file contains the layout and GUI components for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from translations import tr
from tooltip import ToolTip

# === Hilfsfunktion für Transparenz-Anzeige ===
def create_checkerboard_with_color(hex_color, alpha=255, size=24, checker_size=4):
	"""
	Erstellt ein Schachbrett-Muster mit einer Farbe, die Transparenz anzeigt.
	hex_color: z.B. "#FF0000"
	alpha: 0-255 (0=transparent, 255=undurchsichtig)
	size: Größe des Bildes in Pixeln
	checker_size: Größe der Schachbrett-Quadrate
	"""
	# Schachbrett-Farben (grau/weiß)
	checker_light = (200, 200, 200)
	checker_dark = (100, 100, 100)
	
	# Farbe parsen
	try:
		r = int(hex_color[1:3], 16)
		g = int(hex_color[3:5], 16)
		b = int(hex_color[5:7], 16)
	except:
		r, g, b = 0, 0, 0
	
	# Bild mit RGBA-Modus erstellen
	img = Image.new("RGBA", (size, size), (255, 255, 255, 0))
	draw = ImageDraw.Draw(img)
	
	# Schachbrett zeichnen
	for y in range(0, size, checker_size):
		for x in range(0, size, checker_size):
			if ((x // checker_size) + (y // checker_size)) % 2 == 0:
				color = checker_light
			else:
				color = checker_dark
			draw.rectangle([x, y, x + checker_size, y + checker_size], fill=color + (255,))
	
	# Farbe mit Alpha über Schachbrett legen
	overlay = Image.new("RGBA", (size, size), (r, g, b, alpha))
	img = Image.alpha_composite(img, overlay)
	
	return ImageTk.PhotoImage(img)

# === Globale GUI-Design-Konstanten ===
GUI_FONT_FAMILY = "Segoe UI"
GUI_FONT_SIZE = 10
GUI_FONT = (GUI_FONT_FAMILY, GUI_FONT_SIZE)
GUI_LABEL_BG = "#f5f5f5"
GUI_LABEL_FG = "black"
# Standard-Button
GUI_BUTTON_BG = "#e0e0e0"
GUI_BUTTON_FG = "black"
GUI_BUTTON_WIDTH = 8
GUI_BUTTON_HEIGHT = 1
# Erfolgs-Button (z.B. Laden)
GUI_SUCCESS_BG = "#4CAF50"
GUI_SUCCESS_FG = "white"
GUI_SUCCESS_WIDTH = 8
GUI_SUCCESS_HEIGHT = 1
# Warn-/Löschen-Button (z.B. Reset, Clear)
GUI_WARN_BG = "#e53935"
GUI_WARN_FG = "white"
GUI_WARN_WIDTH = 14
GUI_WARN_HEIGHT = 1
# Info-Button (z.B. Export)
GUI_INFO_BG = "#90CAF9"
GUI_INFO_FG = "black"
GUI_INFO_WIDTH = 8
GUI_INFO_HEIGHT = 1
# Akzent-Button (z.B. Play, Next)
GUI_ACCENT_BG = "#e0f7fa"
GUI_ACCENT_FG = "black"
GUI_ACCENT_WIDTH = 8
GUI_ACCENT_HEIGHT = 1
# Label-Größen
GUI_LABEL_WIDTH = 12
GUI_LABEL_HEIGHT = 1

def create_effects_panel(self, parent, prefix):
	frame = ttk.LabelFrame(parent, text=tr(f'{prefix}_settings', self.lang) or "")
	self.__dict__[f'{prefix}_grayscale'] = tk.IntVar()
	self.__dict__[f'{prefix}_sharpen'] = tk.IntVar()
	self.__dict__[f'{prefix}_blur'] = tk.IntVar()
	self.__dict__[f'{prefix}_transparency'] = tk.IntVar()
	self.__dict__[f'{prefix}_transparency_value'] = tk.DoubleVar(value=0.5)
	self.__dict__[f'{prefix}_sharpen_value'] = tk.DoubleVar(value=2.5)
	self.__dict__[f'{prefix}_blur_value'] = tk.DoubleVar(value=3.5)
	grayscale_check = ttk.Checkbutton(frame, text=tr('effect_grayscale', self.lang) or "", variable=self.__dict__[f'{prefix}_grayscale'])
	grayscale_check.pack(anchor="w")
	self.__dict__[f'{prefix}_grayscale_check'] = grayscale_check
	# Schärfen
	sharpen_row = ttk.Frame(frame)
	sharpen_row.pack(fill=tk.X, pady=1)
	sharpen_row.columnconfigure(0, weight=1)
	sharpen_check = ttk.Checkbutton(sharpen_row, text=tr('effect_sharpen', self.lang) or "", variable=self.__dict__[f'{prefix}_sharpen'])
	sharpen_check.pack(side=tk.LEFT)
	self.__dict__[f'{prefix}_sharpen_check'] = sharpen_check
	sharpen_value_label = ttk.Label(sharpen_row, textvariable=self.__dict__[f'{prefix}_sharpen_value'], width=4)
	sharpen_value_label.pack(side=tk.LEFT, padx=(5,0))
	sharpen_inner = ttk.Frame(sharpen_row)
	sharpen_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
	sharpen_scale = ttk.Scale(sharpen_inner, from_=0.0, to=10.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_sharpen_value'], length=375)
	sharpen_scale.pack(side=tk.RIGHT, padx=5)
	self.__dict__[f'{prefix}_sharpen_scale'] = sharpen_scale
	# Weichzeichnen
	blur_row = ttk.Frame(frame)
	blur_row.pack(fill=tk.X, pady=1)
	blur_row.columnconfigure(0, weight=1)
	blur_check = ttk.Checkbutton(blur_row, text=tr('effect_blur', self.lang) or "", variable=self.__dict__[f'{prefix}_blur'])
	blur_check.pack(side=tk.LEFT)
	self.__dict__[f'{prefix}_blur_check'] = blur_check
	blur_value_label = ttk.Label(blur_row, textvariable=self.__dict__[f'{prefix}_blur_value'], width=4)
	blur_value_label.pack(side=tk.LEFT, padx=(5,0))
	blur_inner = ttk.Frame(blur_row)
	blur_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
	blur_scale = ttk.Scale(blur_inner, from_=0.0, to=10.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_blur_value'], length=375)
	blur_scale.pack(side=tk.RIGHT, padx=5)
	self.__dict__[f'{prefix}_blur_scale'] = blur_scale
	# Transparenz
	transparency_row = ttk.Frame(frame)
	transparency_row.pack(fill=tk.X, pady=1)
	transparency_row.columnconfigure(0, weight=1)
	transparency_label = tr('effect_transparency', self.lang)
	if not transparency_label:
		transparency_label = "Transparenz"
	transparency_check = ttk.Checkbutton(transparency_row, text=transparency_label, variable=self.__dict__[f'{prefix}_transparency'])
	transparency_check.pack(side=tk.LEFT)
	self.__dict__[f'{prefix}_transparency_check'] = transparency_check
	transparency_value_label = ttk.Label(transparency_row, textvariable=self.__dict__[f'{prefix}_transparency_value'], width=4)
	transparency_value_label.pack(side=tk.LEFT, padx=(5,0))
	transparency_inner = ttk.Frame(transparency_row)
	transparency_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
	transparency_scale = ttk.Scale(transparency_inner, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_transparency_value'], length=375)
	transparency_scale.pack(side=tk.RIGHT, padx=5)
	self.__dict__[f'{prefix}_transparency_scale'] = transparency_scale

	# Farbintensität (Pastell <-> Kräftig) mit Checkbox
	colorint_row = ttk.Frame(frame)
	colorint_row.pack(fill=tk.X, pady=1)
	colorint_row.columnconfigure(0, weight=1)
	colorint_label = tr('effect_colorintensity', self.lang) or "Farbintensität"
	self.__dict__[f'{prefix}_colorintensity'] = tk.DoubleVar(value=0.5)
	self.__dict__[f'{prefix}_colorintensity_active'] = tk.IntVar(value=0)
	colorint_check = ttk.Checkbutton(colorint_row, text=colorint_label, variable=self.__dict__[f'{prefix}_colorintensity_active'])
	colorint_check.pack(side=tk.LEFT)
	self.__dict__[f'{prefix}_colorint_check'] = colorint_check
	colorint_value_label = ttk.Label(colorint_row, textvariable=self.__dict__[f'{prefix}_colorintensity'], width=4)
	colorint_value_label.pack(side=tk.LEFT, padx=(5,0))
	colorint_inner = ttk.Frame(colorint_row)
	colorint_inner.pack(anchor="e", pady=(0,2), fill=tk.X)
	colorint_scale = ttk.Scale(colorint_inner, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.__dict__[f'{prefix}_colorintensity'], length=375)
	colorint_scale.pack(side=tk.RIGHT, padx=5)
	self.__dict__[f'{prefix}_colorint_scale'] = colorint_scale
	return frame

def build_layout(self):
	# --- Theme-Auswahl (nur wenn ttkbootstrap verfügbar) ---
	try:
		import ttkbootstrap as tb
		THEME_AVAILABLE = True
	except ImportError:
		tb = None
		THEME_AVAILABLE = False
	# Initialisierung für frame_select_var (wird für Spinbox benötigt)
    
	# Initialisierung für frame_select_var (wird für Spinbox benötigt)
	self.frame_select_var = tk.IntVar(value=0)

	# Haupt-Layout: 2 Spalten, unten Einstellungen
	main = ttk.Frame(self.root)
	main.pack(fill=tk.BOTH, expand=True)
	content = ttk.Frame(main)
	content.pack(fill=tk.BOTH, expand=True)
	content.columnconfigure(0, weight=1)
	content.columnconfigure(1, weight=1)
	content.rowconfigure(0, weight=1)

	# Linke Seite: GIF
	left = ttk.Frame(content)
	left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
	self.gif_label = ttk.Label(left, text="GIF-Vorschau", font=("Segoe UI", 12, "bold"))
	self.gif_label.pack(pady=(0,5))
	self.tooltips = {}
	self.tooltips['gif_label'] = ToolTip(self.gif_label, tr('tt_gif_label', self.lang))
	self.gif_canvas = tk.Label(left, bg="#222", width=40, height=16, relief=tk.SUNKEN)
	self.gif_canvas.pack(fill=tk.BOTH, expand=True)
	self.tooltips['gif_canvas'] = ToolTip(self.gif_canvas, tr('tt_gif_canvas', self.lang))
	# Mouse-Binding für GIF-Vorschau: Bei Klick GIF neu anzeigen
	def reload_gif_and_refresh_texture(event=None):
		self.load_gif()
		from image_processing import show_texture
		show_texture(self)
	self.gif_canvas.bind('<Button-1>', reload_gif_and_refresh_texture)
	self.gif_settings = self.create_effects_panel(left, prefix="gif")
	self.gif_settings.pack(fill=tk.X, pady=10)
	self.tooltips['gif_settings'] = ToolTip(self.gif_settings, tr('tt_gif_settings', self.lang))

	# Rechte Seite: Textur
	right = ttk.Frame(content)
	right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
	self.texture_label = ttk.Label(right, text="Textur-Vorschau", font=("Segoe UI", 12, "bold"))
	self.texture_label.pack(pady=(0,5))
	self.tooltips['texture_label'] = ToolTip(self.texture_label, tr('tt_texture_label', self.lang))
	self.texture_canvas = tk.Label(right, bg="#222", width=40, height=16, relief=tk.SUNKEN)
	self.texture_canvas.pack(fill=tk.BOTH, expand=True)
	self.tooltips['texture_canvas'] = ToolTip(self.texture_canvas, tr('tt_texture_canvas', self.lang))
	# Mouse-Binding für Textur-Vorschau: Bei Klick Textur neu generieren
	def refresh_texture(event=None):
		from image_processing import show_texture
		show_texture(self)
	self.texture_canvas.bind('<Button-1>', refresh_texture)
	self.texture_settings = self.create_effects_panel(right, prefix="texture")
	self.texture_settings.pack(fill=tk.X, pady=10)
	self.tooltips['texture_settings'] = ToolTip(self.texture_settings, tr('tt_texture_settings', self.lang))

	# --- Master Einstellungen ---
	self.master_group = ttk.LabelFrame(main, text=tr('master_settings', self.lang) or "Master Einstellungen")
	self.master_group.pack(fill=tk.X, padx=10, pady=(12,2))

	# --- Media ---
	self.media_group = ttk.LabelFrame(main, text=tr('media', self.lang) or "Media")
	self.media_group.pack(fill=tk.X, padx=10, pady=(12,2))

	# --- Datei-Gruppe ---
	self.file_group = ttk.LabelFrame(main, text=tr('file', self.lang) or "Datei")
	self.file_group.pack(fill=tk.X, padx=10, pady=(12,2))
	# --- Datei-Gruppe Controls ---

	# Datei-Buttons: Laden, Speichern, Exportieren, Clear
	try:
		import ttkbootstrap as tb
		THEME_AVAILABLE = True
	except ImportError:
		tb = None
		THEME_AVAILABLE = False
	if THEME_AVAILABLE and tb is not None:
		self.load_btn = tb.Button(self.file_group, text=tr('load_gif', self.lang) or "GIF laden", command=self.load_gif, bootstyle="success")
	else:
		self.load_btn = tk.Button(self.file_group, text=tr('load_gif', self.lang) or "GIF laden", command=self.load_gif, bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white")
	self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['load_btn'] = ToolTip(self.load_btn, tr('tt_load_btn', self.lang))
	self.save_gif_btn = ttk.Button(self.file_group, text=tr('save_gif', self.lang) or "GIF speichern", command=self.save_gif)
	self.save_gif_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['save_gif_btn'] = ToolTip(self.save_gif_btn, tr('tt_save_gif_btn', self.lang))
	self.save_texture_btn = ttk.Button(self.file_group, text=tr('save_texture', self.lang) or "Textur speichern", command=self.save_texture)
	self.save_texture_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['save_texture_btn'] = ToolTip(self.save_texture_btn, tr('tt_save_texture_btn', self.lang))
	self.export_lsl_btn = ttk.Button(self.file_group, text=tr('export_lsl', self.lang) or "LSL exportieren", command=self.export_lsl)
	self.export_lsl_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['export_lsl_btn'] = ToolTip(self.export_lsl_btn, tr('tt_export_lsl_btn', self.lang))

	# Button: Einzelbilder (ZIP/Ordner) zu GIF
	self.import_frames_btn = ttk.Button(self.file_group, text=tr('import_frames', self.lang) or "Bilder zu GIF", command=self.import_frames_to_gif)
	self.import_frames_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['import_frames_btn'] = ToolTip(self.import_frames_btn, tr('tt_import_frames_btn', self.lang))
	# Clear Button
	if THEME_AVAILABLE and tb is not None:
		style = tb.Style()
		style.configure("RedClear.TButton", background="#e53935", foreground="white")
		self.clear_btn = tb.Button(self.file_group, text=tr('clear', self.lang) or "", command=self.clear_texture, style="RedClear.TButton")
	else:
		self.clear_btn = tk.Button(self.file_group, text=tr('clear', self.lang) or "", command=self.clear_texture, bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white")
	self.clear_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['clear_btn'] = ToolTip(self.clear_btn, tr('tt_clear_btn', self.lang))
	# --- Media Controls ---
	media_row = ttk.Frame(self.media_group)
	media_row.pack(fill=tk.X)
	self.playing = False

	# Geschwindigkeit/Abspielrate-Slider für Media Play
	playrate_row = ttk.Frame(self.media_group)
	playrate_row.pack(fill=tk.X, pady=(4,2))
	self.media_playrate_label = ttk.Label(playrate_row, text=tr('playrate', self.lang) or "Abspielrate:", width=12, anchor="w")
	self.media_playrate_label.pack(side=tk.LEFT, padx=(0,4))
	self.tooltips['media_playrate_label'] = ToolTip(self.media_playrate_label, tr('tt_media_playrate_label', self.lang))
	self.media_playrate_var = tk.IntVar(value=100)
	self.media_playrate_slider = ttk.Scale(playrate_row, from_=10, to=500, orient=tk.HORIZONTAL, variable=self.media_playrate_var, length=120)
	self.media_playrate_slider.pack(side=tk.LEFT, padx=4)
	self.media_playrate_value = ttk.Label(playrate_row, text="100%", width=4)
	self.media_playrate_value.pack(side=tk.LEFT)
	if THEME_AVAILABLE and tb is not None:
		style = tb.Style()
		style.configure("PastellPrev.TButton", background="#B39DDB", foreground="black")
		style.configure("PastellPause.TButton", background="#90CAF9", foreground="black")
		style.configure("PastellPlay.TButton", background="#A5D6A7", foreground="black")
		style.configure("PastellStop.TButton", background="#EF9A9A", foreground="black")
		style.configure("PastellNext.TButton", background="#FFF59D", foreground="black")
		self.prev_btn = tb.Button(media_row, text="⏮", command=self.step_backward, style="PastellPrev.TButton")
		self.pause_btn = tb.Button(media_row, text="⏸", command=self.pause_animation, style="PastellPause.TButton")
		self.play_btn = tb.Button(media_row, text="▶", command=self.start_animation, style="PastellPlay.TButton")
		self.stop_btn = tb.Button(media_row, text="⏹", command=self.stop_animation, style="PastellStop.TButton")
		self.next_btn = tb.Button(media_row, text="⏭", command=self.step_forward, style="PastellNext.TButton")
	else:
		self.prev_btn = tk.Button(media_row, text="⏮", command=self.step_backward, bg="#B39DDB", fg="black", activebackground="#D1C4E9", activeforeground="black")
		self.pause_btn = tk.Button(media_row, text="⏸", command=self.pause_animation, bg="#90CAF9", fg="black", activebackground="#BBDEFB", activeforeground="black")
		self.play_btn = tk.Button(media_row, text="▶", command=self.start_animation, bg="#A5D6A7", fg="black", activebackground="#C8E6C9", activeforeground="black")
		self.stop_btn = tk.Button(media_row, text="⏹", command=self.stop_animation, bg="#EF9A9A", fg="black", activebackground="#FFCDD2", activeforeground="black")
		self.next_btn = tk.Button(media_row, text="⏭", command=self.step_forward, bg="#FFF59D", fg="black", activebackground="#FFF9C4", activeforeground="black")
	self.prev_btn.pack(side=tk.LEFT, padx=4)
	self.pause_btn.pack(side=tk.LEFT, padx=4)
	self.play_btn.pack(side=tk.LEFT, padx=4)
	self.stop_btn.pack(side=tk.LEFT, padx=4)
	self.next_btn.pack(side=tk.LEFT, padx=4)
	self.tooltips['prev_btn'] = ToolTip(self.prev_btn, tr('tt_prev_btn', self.lang))
	self.tooltips['pause_btn'] = ToolTip(self.pause_btn, tr('tt_pause_btn', self.lang))
	self.tooltips['play_btn'] = ToolTip(self.play_btn, tr('tt_play_btn', self.lang))
	self.tooltips['stop_btn'] = ToolTip(self.stop_btn, tr('tt_stop_btn', self.lang))
	self.tooltips['next_btn'] = ToolTip(self.next_btn, tr('tt_next_btn', self.lang))
	# --- Master Einstellungen Controls (3 Rahmen) ---
	master_row = ttk.Frame(self.master_group)
	master_row.pack(fill=tk.X)
	# Linker Rahmen: Bildgröße, Bildrate, Max. Bilder (jeweils Label links, Wert(e) rechts)
	left_frame = ttk.LabelFrame(master_row)
	left_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
	# Bildgröße
	size_row = ttk.Frame(left_frame)
	size_row.pack(fill=tk.X, pady=(4,2))
	self.size_label = ttk.Label(size_row, text="Bildgröße:", background="#e0f7fa", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="w", font=("Segoe UI", 10))
	self.size_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['size_label'] = ToolTip(self.size_label, tr('tt_size_label', self.lang))
	self.width_var = tk.IntVar(value=self.image_width)
	self.height_var = tk.IntVar(value=self.image_height)
	self.width_entry = ttk.Entry(size_row, textvariable=self.width_var, width=5)
	self.width_entry.pack(side=tk.LEFT, padx=2)
	self.tooltips['width_entry'] = ToolTip(self.width_entry, tr('tt_width_entry', self.lang))
	self.height_entry = ttk.Entry(size_row, textvariable=self.height_var, width=5)
	self.height_entry.pack(side=tk.LEFT, padx=2)
	self.tooltips['height_entry'] = ToolTip(self.height_entry, tr('tt_height_entry', self.lang))

	# Preview auch bei manueller Eingabe aktualisieren
	def _update_preview_if_gif_loaded(*args):
		if hasattr(self, 'gif_image') and self.gif_image is not None:
			try:
				from image_processing import show_texture
				show_texture(self)
			except Exception:
				pass
	self.width_var.trace_add('write', _update_preview_if_gif_loaded)
	self.height_var.trace_add('write', _update_preview_if_gif_loaded)

	# Preset-Combobox für Bildgrößen
	def set_image_size_from_preset(event=None):
		preset = self.size_preset_var.get()
		try:
			val = int(preset)
			self.width_var.set(val)
			self.height_var.set(val)
			# Automatisch Preview aktualisieren, falls GIF geladen
			if hasattr(self, 'gif_image') and self.gif_image is not None:
				try:
					from image_processing import show_texture
					show_texture(self)
				except Exception:
					pass
		except Exception:
			pass

	self.size_preset_var = tk.StringVar()
	self.size_preset_combo = ttk.Combobox(size_row, values=["128", "256", "512", "768", "1024", "1280", "1536", "1792", "2048"], textvariable=self.size_preset_var, width=5, state="readonly")
	self.size_preset_combo.pack(side=tk.LEFT, padx=(8,0))
	self.size_preset_combo.bind("<<ComboboxSelected>>", set_image_size_from_preset)
	self.tooltips['size_preset_combo'] = ToolTip(self.size_preset_combo, tr('tt_size_preset_combo', self.lang))
	# Bindings werden in main.py gesetzt
	# Bildrate
	framerate_row = ttk.Frame(left_frame)
	framerate_row.pack(fill=tk.X, pady=(4,2))
	self.framerate_label = ttk.Label(framerate_row, text=tr('framerate', self.lang) or "Framerate:", background="#bbdefb", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="w", font=("Segoe UI", 10))
	self.framerate_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['framerate_label'] = ToolTip(self.framerate_label, tr('tt_framerate_label', self.lang))
	self.framerate_var = tk.IntVar(value=10)
	self.framerate_spin = ttk.Spinbox(framerate_row, from_=1, to=10000, increment=1, textvariable=self.framerate_var, width=6)
	self.framerate_spin.pack(side=tk.LEFT)
	self.tooltips['framerate_spin'] = ToolTip(self.framerate_spin, tr('tt_framerate_spin', self.lang))
	# Max. Bilder
	maxframes_row = ttk.Frame(left_frame)
	maxframes_row.pack(fill=tk.X, pady=(4,2))
	self.maxframes_label = ttk.Label(maxframes_row, text=tr('max_images', self.lang) or "Max. Bilder:", background="#c8e6c9", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="w", font=("Segoe UI", 10))
	self.maxframes_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['maxframes_label'] = ToolTip(self.maxframes_label, tr('tt_maxframes_label', self.lang))
	self.maxframes_var = tk.IntVar(value=64)
	self.maxframes_spin = ttk.Spinbox(maxframes_row, from_=1, to=1024, increment=1, textvariable=self.maxframes_var, width=5, state="readonly")
	self.maxframes_spin.pack(side=tk.LEFT)
	self.tooltips['maxframes_spin'] = ToolTip(self.maxframes_spin, tr('tt_maxframes_spin', self.lang))
	# Neues Binding: Wertänderung ruft set_max_images auf
	def on_maxframes_change(*args):
		from image_processing import set_max_images
		set_max_images(self, self.maxframes_var.get())
	self.maxframes_var.trace_add('write', on_maxframes_change)
	# Mittlerer Rahmen: Hintergrundfarbe, Randlos, Bild hinzufügen (jeweils Label/Checkbutton links, Wert/Button rechts)
	middle_frame = ttk.LabelFrame(master_row)
	middle_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
	# Hintergrundfarbe
	bg_row = ttk.Frame(middle_frame)
	bg_row.pack(fill=tk.X, pady=(4,2))
	self.bg_label = ttk.Label(bg_row, text=tr('bg_color', self.lang) or "Hintergrundfarbe:", background="#fff9c4", foreground="black", relief=tk.FLAT, borderwidth=1, width=16, anchor="w", font=("Segoe UI", 10))
	self.bg_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['bg_label'] = ToolTip(self.bg_label, tr('tt_bg_label', self.lang))
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	# PhotoImage für Transparenz-Anzeige mit Schachbrett-Pattern
	self.bg_color_photo = create_checkerboard_with_color(self.bg_box_color, alpha=0, size=32, checker_size=4)
	self.bg_color_box = tk.Label(bg_row, image=self.bg_color_photo, relief=tk.SUNKEN, cursor="hand2", width=32, height=32)
	self.bg_color_box.pack(side=tk.LEFT, padx=2)
	# Bindings werden in main.py gesetzt
	self.tooltips['bg_color_box'] = ToolTip(self.bg_color_box, tr('tt_bg_color_box', self.lang))
	# Randlos
	borderless_row = ttk.Frame(middle_frame)
	borderless_row.pack(fill=tk.X, pady=(4,2))
	self.borderless_var = tk.IntVar(value=0)
	# Bindings werden in main.py gesetzt
	self.borderless_label = ttk.Label(
		borderless_row,
		text=tr('borderless', self.lang) or "Randlos:",
		background="#c4fff9",
		foreground="black",
		relief=tk.FLAT,
		borderwidth=1,
		width=16,
		anchor="w",
		font=("Segoe UI", 10)
	)
	self.borderless_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['borderless_label'] = ToolTip(self.borderless_label, tr('tt_borderless', self.lang))
	self.borderless_chk = ttk.Checkbutton(borderless_row, text="", variable=self.borderless_var)
	self.borderless_chk.pack(side=tk.LEFT)
	try:
		self.borderless_chk.configure(style="PastellBorderless.TCheckbutton")
		style = ttk.Style()
		style.configure("PastellBorderless.TCheckbutton")
	except Exception:
		pass
	# Bild hinzufügen
	add_row = ttk.Frame(middle_frame)
	add_row.pack(fill=tk.X, pady=(4,2))
	self.add_row = add_row  # Referenz speichern
	self.frame_select_spin = ttk.Spinbox(add_row, from_=0, to=0, textvariable=self.frame_select_var, width=5, state="readonly")
	self.frame_select_spin.pack(side=tk.RIGHT)
	self.tooltips['frame_select_spin'] = ToolTip(self.frame_select_spin, tr('tt_frame_select_spin', self.lang))
	self.add_frame_btn = ttk.Button(add_row, text=tr('add_frame', self.lang) or "")
	self.add_frame_btn.pack(side=tk.RIGHT, padx=(0,4))
	self.tooltips['add_frame_btn'] = ToolTip(self.add_frame_btn, tr('tt_add_frame_btn', self.lang))
	# Entfernen-Button für Frames
	# Korrektur: style-Parameter nur setzen, wenn Stilname existiert
	if 'RedClear.TButton' in ttk.Style().theme_names():
		self.remove_frame_btn = ttk.Button(add_row, text="Entfernen", style="RedClear.TButton")
	else:
		self.remove_frame_btn = ttk.Button(add_row, text="Entfernen")
	self.remove_frame_btn.pack(side=tk.RIGHT, padx=(0,4))
	self.tooltips['remove_frame_btn'] = ToolTip(self.remove_frame_btn, "Bild entfernen")

	# Rechter Rahmen: Sprache, Theme, Exportformat, Reset (jeweils Label links, Wert/Button rechts)
	right_frame = ttk.LabelFrame(master_row)
	right_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
	# Sprache
	lang_row = ttk.Frame(right_frame)
	lang_row.pack(fill=tk.X, pady=(4,2))
	self.lang_label = ttk.Label(
		lang_row,
		text=tr('language', self.lang) or "",
		background="#eeec7d",
		foreground=GUI_LABEL_FG,
		relief=tk.FLAT,
		borderwidth=1,
		width=GUI_LABEL_WIDTH,
		anchor="w",
		font=GUI_FONT
	)
	self.lang_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['lang_label'] = ToolTip(self.lang_label, tr('tt_lang_label', self.lang))
	self.lang_var = tk.StringVar(value=self.lang)
	self.lang_combo = ttk.Combobox(lang_row, values=['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt'], textvariable=self.lang_var, width=6, state="readonly", font=GUI_FONT)
	self.lang_combo.pack(side=tk.LEFT)
	self.tooltips['lang_combo'] = ToolTip(self.lang_combo, tr('tt_lang_combo', self.lang))
	# Bindings werden in main.py gesetzt

	# Theme-Auswahl zwischen Sprache und Exportformat
	if THEME_AVAILABLE and tb is not None:
		theme_row = ttk.Frame(right_frame)
		theme_row.pack(fill=tk.X, pady=(4,2))
		theme_label = ttk.Label(theme_row, text=tr('theme', self.lang) or "Theme:", background="#e0e0e0", foreground="black", relief=tk.FLAT, borderwidth=1, width=GUI_LABEL_WIDTH, anchor="w", font=GUI_FONT)
		theme_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
		self.tooltips['theme_label'] = ToolTip(theme_label, tr('tt_theme_label', self.lang) or "Wähle das Farbschema für die Oberfläche.")
		self.theme_label = theme_label
		current_theme = None
		theme_names = []
		if tb is not None:
			style = tb.Style()
			current_theme = getattr(style.theme, 'name', None) if getattr(style, 'theme', None) is not None else None
			theme_names = sorted(style.theme_names())
		else:
			import tkinter.ttk as ttk_mod
			style = ttk_mod.Style()
		self.theme_var = tk.StringVar(value=current_theme or "")
		self.theme_combo = ttk.Combobox(theme_row, textvariable=self.theme_var, values=theme_names, state="readonly", width=13, font=GUI_FONT)
		self.theme_combo.pack(side=tk.LEFT, padx=2)
		def on_theme_change(event=None):
			if tb is not None:
				new_theme = self.theme_var.get()
				tb.Style().theme_use(new_theme)
		self.theme_combo.bind('<<ComboboxSelected>>', on_theme_change)
		self.tooltips['theme_combo'] = ToolTip(self.theme_combo, tr('tt_theme_combo', self.lang) or "Theme-Auswahl für die Oberfläche.")

	# Exportformat in Master Einstellungen (rechter Rahmen) einfügen
	export_format_row = ttk.Frame(right_frame)
	export_format_row.pack(fill=tk.X, pady=(4,2))
	self.export_format_label = ttk.Label(
		export_format_row,
		text=tr('export_format', self.lang) or "Exportformat:",
		background="#FFB3A7",
		foreground=GUI_LABEL_FG,
		relief=tk.FLAT,
		borderwidth=1,
		width=GUI_LABEL_WIDTH,
		anchor="w",
		font=GUI_FONT
	)
	self.export_format_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['export_format_label'] = ToolTip(self.export_format_label, tr('tt_export_format_label', self.lang))
	self.export_format_var = tk.StringVar(value="PNG")
	self.export_format_combo = ttk.Combobox(export_format_row, values=["PNG", "JPG", "BMP", "ZIP"], textvariable=self.export_format_var, width=6, state="readonly", font=GUI_FONT)
	self.export_format_combo.pack(side=tk.LEFT)

	# Reset in eigenen vierten Rahmen ganz rechts
	reset_frame = ttk.LabelFrame(master_row)
	reset_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
	reset_row = ttk.Frame(reset_frame)
	reset_row.pack(fill=tk.X, pady=(8,2))
	if THEME_AVAILABLE and tb is not None:
		style = tb.Style()
		style.configure("RedReset.TButton", background=GUI_WARN_BG, foreground=GUI_WARN_FG)
		self.reset_btn = tb.Button(reset_row, text=tr('reset', self.lang) or "Reset", style="RedReset.TButton", width=GUI_WARN_WIDTH)
	else:
		self.reset_btn = tk.Button(reset_row, text=tr('reset', self.lang) or "Reset", bg=GUI_WARN_BG, fg=GUI_WARN_FG, activebackground="#b71c1c", activeforeground="white", width=GUI_WARN_WIDTH, height=GUI_WARN_HEIGHT, font=GUI_FONT)
	self.reset_btn.pack(side=tk.LEFT, padx=8, ipady=6)
	self.tooltips['reset_btn'] = ToolTip(self.reset_btn, tr('tt_reset_btn', self.lang))

	# --- Status-Gruppe ---
	self.status_group = ttk.LabelFrame(main, text=tr('status', self.lang) or "Status")
	self.status_group.pack(fill=tk.X, padx=10, pady=(12,8))
	self.status = ttk.Label(self.status_group, text=tr('ready', self.lang) or "Bereit", anchor="w")
	self.status.pack(fill=tk.X)

	# Übersetzung für Randlos-Label und Tooltip erfolgt ausschließlich in update_language für Konsistenz


