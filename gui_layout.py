###
# gui_layout.py
# This file contains the layout and GUI components for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###
import tkinter as tk
from tkinter import ttk
from translations import tr
from tooltip import ToolTip

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
	export_format_frame = ttk.Frame(self.file_group)
	export_format_frame.pack(side=tk.LEFT, padx=5)
	self.export_format_label = tk.Label(export_format_frame, text=tr('export_format', self.lang) or "Exportformat:", bg="#FFB3A7", fg="black", height=1, padx=8, pady=0)
	self.export_format_label.pack(side=tk.LEFT, ipadx=0, ipady=0, padx=2, pady=2, fill=tk.Y)
	self.tooltips['export_format_label'] = ToolTip(self.export_format_label, tr('tt_export_format_label', self.lang))
	self.export_format_var = tk.StringVar(value="PNG")
	self.export_format_combo = ttk.Combobox(export_format_frame, values=["PNG", "JPG", "BMP"], textvariable=self.export_format_var, width=5, state="readonly")
	self.export_format_combo.pack(side=tk.LEFT)
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

	# Geschwindigkeit/Framerate-Slider für Media Play
	framerate_row = ttk.Frame(self.media_group)
	framerate_row.pack(fill=tk.X, pady=(4,2))
	self.media_framerate_label = ttk.Label(framerate_row, text=tr('framerate', self.lang) or "Framerate:", width=12, anchor="w")
	self.media_framerate_label.pack(side=tk.LEFT, padx=(0,4))
	self.tooltips['media_framerate_label'] = ToolTip(self.media_framerate_label, tr('tt_media_framerate_label', self.lang))
	self.media_framerate_var = tk.IntVar(value=100)
	self.media_framerate_slider = ttk.Scale(framerate_row, from_=1, to=1000, orient=tk.HORIZONTAL, variable=self.media_framerate_var, length=120)
	self.media_framerate_slider.pack(side=tk.LEFT, padx=4)
	self.media_framerate_value = ttk.Label(framerate_row, textvariable=self.media_framerate_var, width=4)
	self.media_framerate_value.pack(side=tk.LEFT)
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
	self.bg_color_box = tk.Label(bg_row, width=3, relief=tk.SUNKEN, bg=self.bg_box_color, cursor="hand2")
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
	# Rechter Rahmen: Sprache, Reset (jeweils Label links, Wert/Button rechts)
	right_frame = ttk.LabelFrame(master_row)
	right_frame.pack(side=tk.LEFT, padx=5, fill=tk.Y)
	# Sprache
	lang_row = ttk.Frame(right_frame)
	lang_row.pack(fill=tk.X, pady=(4,2))
	self.lang_label = ttk.Label(lang_row, text=tr('language', self.lang) or "", background="#eeec7d", foreground="black", relief=tk.FLAT, borderwidth=1, width=12, anchor="w", font=("Segoe UI", 10))
	self.lang_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['lang_label'] = ToolTip(self.lang_label, tr('tt_lang_label', self.lang))
	self.lang_var = tk.StringVar(value=self.lang)
	self.lang_combo = ttk.Combobox(lang_row, values=['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt'], textvariable=self.lang_var, width=6, state="readonly")
	self.lang_combo.pack(side=tk.LEFT)
	self.tooltips['lang_combo'] = ToolTip(self.lang_combo, tr('tt_lang_combo', self.lang))
	# Bindings werden in main.py gesetzt
	# Reset
	reset_row = ttk.Frame(right_frame)
	reset_row.pack(fill=tk.X, pady=(8,2))
	if THEME_AVAILABLE and tb is not None:
		style = tb.Style()
		style.configure("RedReset.TButton", background="#e53935", foreground="white")
		self.reset_btn = tb.Button(reset_row, text="Reset", style="RedReset.TButton")
	else:
		self.reset_btn = tk.Button(reset_row, text="Reset", bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white")
	self.reset_btn.pack(side=tk.LEFT, padx=8)
	self.tooltips['reset_btn'] = ToolTip(self.reset_btn, tr('tt_reset_btn', self.lang))

	# --- Status-Gruppe ---
	self.status_group = ttk.LabelFrame(main, text=tr('status', self.lang) or "Status")
	self.status_group.pack(fill=tk.X, padx=10, pady=(12,8))
	self.status = ttk.Label(self.status_group, text=tr('ready', self.lang) or "Bereit", anchor="w")
	self.status.pack(fill=tk.X)

	# Übersetzung für Randlos-Label und Tooltip erfolgt ausschließlich in update_language für Konsistenz


