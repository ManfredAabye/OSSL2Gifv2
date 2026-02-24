###
# gui_layout.py
# This file contains the layout and GUI components for the OSSL2Gif application.
# OSSL2Gif OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import re
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageDraw, ImageTk
from translations import tr
from tooltip import ToolTip
from logging_config import get_logger
from events import reset_settings

logger = get_logger(__name__)

def normalize_label_text(text: str) -> str:
	"""Collapse any whitespace to single spaces for consistent labels."""
	return re.sub(r"\s+", " ", text, flags=re.UNICODE).strip()

def create_menubar(self):
	"""Erstellt die Menu Bar (Menüleiste) oben im Fenster.
	
	Die Menu Bar enthält die Hauptmenüs: File, Edit, View, Groups, Help.
	Nicht zu verwechseln mit der File Toolbar (Button-Leiste im File-Group).
	"""
	menubar = tk.Menu(self.root)
	
	# Style für Dark Theme anpassen
	try:
		import ttkbootstrap as tb
		if hasattr(self, 'root') and isinstance(self.root, (tk.Tk, tb.Window)):
			menubar.config(  # type: ignore
				bg='#2d2d2d',
				fg='#ffffff',
				activebg='#4a4a4a',
				activeforeground='#ffffff',
				borderwidth=0
			)
	except:
		pass
	
	# Datei-Menü
	file_menu = tk.Menu(menubar, tearoff=0)
	file_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	file_menu.add_command(label=f"📂 {tr('load_gif', self.lang) or 'GIF laden'}", command=self.load_gif, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+O")
	file_menu.add_command(label=f"🌐 {tr('load_url', self.lang) or 'URL laden'}", command=self.load_gif_from_url, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+U")
	file_menu.add_command(label=f"📋 {tr('load_clipboard', self.lang) or 'Aus Zwischenablage'}", command=self.load_gif_from_clipboard, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+V")
	file_menu.add_separator()
	file_menu.add_command(label=normalize_label_text(f"🖼 {tr('load_texture', self.lang) or 'Textur laden'}"), command=self.load_texture)
	file_menu.add_separator()
	file_menu.add_command(label=f"🧩 {tr('import_frames', self.lang) or 'Bilder zu GIF'}", command=self.import_frames_to_gif)
	file_menu.add_separator()
	file_menu.add_command(label=f"💾 {tr('save_gif', self.lang) or 'GIF speichern'}", command=self.save_gif, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+S")
	file_menu.add_command(label=f"🧵 {tr('save_texture', self.lang) or 'Textur speichern'}", command=self.save_texture, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+T")
	file_menu.add_command(label=f"🧾 {tr('export_lsl', self.lang) or 'LSL exportieren'}", command=self.export_lsl, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+E")
	file_menu.add_separator()
	file_menu.add_command(label=f"💾 {tr('save_settings', self.lang) or 'Einstellungen speichern'}", command=self.save_gui_config)
	file_menu.add_separator()
	file_menu.add_command(label=f"🧹 {tr('clear', self.lang) or 'Löschen'}", command=self.clear_texture)
	file_menu.add_separator()
	file_menu.add_command(label=f"{tr('exit', self.lang) or 'Beenden'}", command=self.root.quit, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+Q")
	menubar.add_cascade(label=f"📁 {tr('file', self.lang) or 'Datei'}", menu=file_menu)
	
	# Bearbeiten-Menü
	edit_menu = tk.Menu(menubar, tearoff=0)
	edit_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	
	# Master-Einstellungen direkt im Menü
	# Bildgröße
	edit_menu.add_command(label=f"📐 {tr('image_size', self.lang) or 'Bildgröße'}...", 
	                      command=self._show_image_size_dialog)
	
	# Bildrate
	edit_menu.add_command(label=f"⏱ {tr('framerate', self.lang) or 'Bildrate'}...", 
	                      command=self._show_framerate_dialog)
	
	# Max. Bilder
	edit_menu.add_command(label=f"🖼 {tr('max_images', self.lang) or 'Max. Bilder'}...", 
	                      command=self._show_max_frames_dialog)
	
	# Hintergrundfarbe & Transparenz
	edit_menu.add_command(label=f"🎨 {tr('bg_color', self.lang) or 'Hintergrundfarbe'}...", 
	                      command=self._show_background_dialog)
	
	edit_menu.add_separator()
	
	# Sprache Submenü
	lang_submenu = tk.Menu(edit_menu, tearoff=0)
	lang_submenu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	
	languages = [
		('Deutsch', 'de'),
		('English', 'en'),
		('Français', 'fr'),
		('Español', 'es'),
		('Italiano', 'it'),
		('Русский', 'ru'),
		('Nederlands', 'nl'),
		('Svenska', 'se'),
		('Polski', 'pl'),
		('Português', 'pt'),
		('Українська', 'uk'),
		('日本語', 'ja'),
		('中文', 'zh')
	]
	
	for lang_name, lang_code in languages:
		lang_submenu.add_command(label=lang_name, 
		                         command=lambda lc=lang_code: self._change_language_menu(lc))
	
	edit_menu.add_cascade(label=f"🌐 {tr('language', self.lang) or 'Sprache'}", menu=lang_submenu)
	
	# Theme Submenü (nur wenn ttkbootstrap verfügbar)
	try:
		import ttkbootstrap as tb
		if tb is not None:
			theme_submenu = tk.Menu(edit_menu, tearoff=0)
			theme_submenu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
			
			style = tb.Style()
			theme_names = sorted(style.theme_names())
			
			for theme_name in theme_names:
				theme_submenu.add_command(label=theme_name, 
				                        command=lambda tn=theme_name: self._change_theme_menu(tn))
			
			edit_menu.add_cascade(label=f"🎛 {tr('theme', self.lang) or 'Theme'}", menu=theme_submenu)
	except:
		pass
	
	# Exportformat Submenü
	export_format_submenu = tk.Menu(edit_menu, tearoff=0)
	export_format_submenu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	
	formats = ['PNG', 'JPG', 'BMP', 'ZIP']
	for fmt in formats:
		export_format_submenu.add_command(label=fmt, 
		                                  command=lambda f=fmt: self._change_export_format_menu(f))
	
	edit_menu.add_cascade(label=f"📤 {tr('export_format', self.lang) or 'Exportformat'}", menu=export_format_submenu)
	
	edit_menu.add_separator()
	edit_menu.add_command(label=f"🔄 {tr('reset', self.lang) or 'Zurücksetzen'}", command=lambda: reset_settings(self), accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+R")
	menubar.add_cascade(label=f"✏ {tr('edit', self.lang) or 'Bearbeiten'}", menu=edit_menu)
	
	# Ansicht-Menü
	view_menu = tk.Menu(menubar, tearoff=0)
	view_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	view_menu.add_command(label=tr('scene_standard', self.lang) or 'Standard', command=lambda: self._apply_view_preset('standard'))
	view_menu.add_command(label=tr('scene_media_player', self.lang) or 'Mediaplayer', command=lambda: self._apply_view_preset('media_player'))
	view_menu.add_command(label=tr('scene_gif_edit', self.lang) or 'GIF-Bearbeitung', command=lambda: self._apply_view_preset('gif_edit'))
	view_menu.add_command(label=tr('scene_texture_edit', self.lang) or 'Textur-Bearbeitung', command=lambda: self._apply_view_preset('texture_edit'))
	view_menu.add_separator()
	view_menu.add_command(label=f"🎬 {tr('texture_preview_sl', self.lang) or 'Textur-Vorschau (SL/OpenSim)'}", command=self.show_texture_preview_window, accelerator=f"{tr('key_ctrl', self.lang) or 'Strg'}+P")
	menubar.add_cascade(label=f"👁 {tr('view', self.lang) or 'Ansicht'}", menu=view_menu)

	# Media-Menü
	media_menu = tk.Menu(menubar, tearoff=0)
	media_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	media_menu.add_command(label=f"▶ {tr('play', self.lang) or 'Abspielen'}", command=self.start_animation, accelerator=tr('key_space', self.lang) or 'Leertaste')
	media_menu.add_command(label=f"⏸ {tr('pause', self.lang) or 'Pause'}", command=self.pause_animation)
	media_menu.add_command(label=f"⏹ {tr('stop', self.lang) or 'Stop'}", command=self.stop_animation)
	media_menu.add_separator()
	media_menu.add_command(label=f"⏮ {tr('prev_frame', self.lang) or 'Zurück'}", command=self.step_backward, accelerator=tr('key_left', self.lang) or '←')
	media_menu.add_command(label=f"⏭ {tr('next_frame', self.lang) or 'Vor'}", command=self.step_forward, accelerator=tr('key_right', self.lang) or '→')
	menubar.add_cascade(label=f"🎬 {tr('media', self.lang) or 'Media'}", menu=media_menu)
	
	# Gruppen-Menü
	groups_menu = tk.Menu(menubar, tearoff=0)
	groups_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	groups_menu.add_checkbutton(label=f"🎞 {tr('show_gif_preview', self.lang) or 'GIF-Vorschau anzeigen'}", 
	                           variable=self.show_gif_var, 
	                           command=self._toggle_gif_preview)
	groups_menu.add_checkbutton(label=f"⚙ {tr('show_gif_settings', self.lang) or 'GIF-Einstellungen anzeigen'}", 
	                           variable=self.show_gif_settings_var, 
	                           command=self._toggle_gif_settings)
	groups_menu.add_checkbutton(label=f"🖼 {tr('show_texture_preview', self.lang) or 'Textur-Vorschau anzeigen'}", 
	                           variable=self.show_texture_var, 
	                           command=self._toggle_texture_preview)
	groups_menu.add_checkbutton(label=f"⚙ {tr('show_texture_settings', self.lang) or 'Textur-Einstellungen anzeigen'}", 
	                           variable=self.show_texture_settings_var, 
	                           command=self._toggle_texture_settings)
	groups_menu.add_separator()
	groups_menu.add_checkbutton(label=f"🛠 {tr('show_master_settings', self.lang) or 'Master-Einstellungen anzeigen'}", 
	                           variable=self.show_master_var, 
	                           command=self._toggle_master_group)
	groups_menu.add_checkbutton(label=f"🎬 {tr('show_media', self.lang) or 'Media anzeigen'}", 
	                           variable=self.show_media_var, 
	                           command=self._toggle_media_group)
	groups_menu.add_checkbutton(label=f"📁 {tr('show_file', self.lang) or 'Datei anzeigen'}", 
	                           variable=self.show_file_var, 
	                           command=self._toggle_file_group)
	groups_menu.add_checkbutton(label=f"📋 {tr('show_status', self.lang) or 'Status anzeigen'}", 
	                           variable=self.show_status_var, 
	                           command=self._toggle_status_group)
	menubar.add_cascade(label=f"🗂 {tr('groups', self.lang) or 'Gruppen'}", menu=groups_menu)
	
	# Hilfe-Menü
	help_menu = tk.Menu(menubar, tearoff=0)
	help_menu.config(bg='#2d2d2d', fg='#ffffff', activebackground='#4a4a4a', activeforeground='#ffffff')  # type: ignore
	help_menu.add_command(label=f"ℹ {tr('about', self.lang) or 'Über'}", command=lambda: self._show_about_dialog())
	menubar.add_cascade(label=f"❓ {tr('help', self.lang) or 'Hilfe'}", menu=help_menu)
	
	self.root.config(menu=menubar)
	self.menubar = menubar
	return menubar

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

def create_effects_panel(self, parent, prefix):
	settings_icon = "⚙"
	frame = ttk.LabelFrame(parent, text=f"{settings_icon} {tr(f'{prefix}_settings', self.lang) or ''}")
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
	"""Erstellt das gesamte GUI-Layout."""
	
	# === Globale GUI-Design-Konstanten mit DPI-Skalierung ===
	dpi = getattr(self, 'dpi_scale', 1.0)
	
	GUI_FONT_FAMILY = "Segoe UI"
	GUI_FONT_SIZE = max(8, int(10 * dpi))  # Mindestens 8pt auch bei sehr niedrigem DPI
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
	GUI_WARN_WIDTH = 20
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
	GUI_LABEL_WIDTH = 20
	GUI_LABEL_HEIGHT = 1
	
	logger.debug(f"GUI Font size adjusted for DPI {dpi:.2f}: {GUI_FONT_SIZE}pt")
	
	# === MENU BAR (Menüleiste oben) ===
	# Erstellt die Hauptmenüleiste: File, Edit, View, Groups, Help
	# Definition in create_menubar() (Zeile 17)
	create_menubar(self)
	
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

	# === GLOBALER SCROLLBAR FÜR GESAMTES LAYOUT ===
	# Canvas + Scrollbar für das gesamte Fenster (Preview + Einstellungen)
	main = ttk.Frame(self.root)
	main.pack(fill=tk.BOTH, expand=True)
	
	scrollbar = ttk.Scrollbar(main)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	
	main_canvas = tk.Canvas(main, bg="#f5f5f5", yscrollcommand=scrollbar.set, highlightthickness=0)
	main_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
	self.main_canvas = main_canvas  # Speichere als Instanz-Variable für später Zugriff
	scrollbar.config(command=main_canvas.yview)
	
	# Innerer Frame für alle Inhalte
	main_inner = ttk.Frame(main_canvas, name='main_inner')
	main_canvas_window = main_canvas.create_window((0, 0), window=main_inner, anchor="nw")
	
	# Mousewheel/Scroll-Binding für Canvas
	def on_mousewheel(event):
		delta = event.delta if hasattr(event, 'delta') else 0
		main_canvas.yview_scroll(int(-1*(delta/120)), "units")
	def on_linux_scroll(event):
		if event.num == 4:
			main_canvas.yview_scroll(-1, "units")
		elif event.num == 5:
			main_canvas.yview_scroll(1, "units")
	main_canvas.bind("<MouseWheel>", on_mousewheel)
	main_canvas.bind("<Button-4>", on_linux_scroll)
	main_canvas.bind("<Button-5>", on_linux_scroll)
	
	# Größe des Canvas nach dem Befüllen anpassen (wird nachher aufgerufen)
	def on_full_frame_configure(event=None):
		main_canvas.configure(scrollregion=main_canvas.bbox("all"))
		# Canvas-Fenster so breit wie Canvas machen
		canvas_width = main_canvas.winfo_width()
		if canvas_width > 1:
			main_canvas.itemconfig(main_canvas_window, width=canvas_width)
	
	# Bind nur einmal beim Canvas-Resize, nicht bei jedem Configure-Event
	main_canvas.bind("<Configure>", on_full_frame_configure)

	# Haupt-Layout: 2 Spalten, unten Einstellungen
	content = ttk.Frame(main_inner)
	content.pack(fill=tk.BOTH, expand=True)
	self.content_frame = content
	content.columnconfigure(0, weight=1)
	content.columnconfigure(1, weight=1)
	content.rowconfigure(0, weight=1)

	# Linke Seite: GIF
	left = ttk.Frame(content)
	left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
	gif_preview_container = ttk.Frame(left)
	gif_preview_container.pack(fill=tk.BOTH, expand=True)
	self.gif_preview_frame = gif_preview_container  # Referenz für Ein-/Ausblenden speichern
	self.gif_label = ttk.Label(gif_preview_container, text="🎞 GIF-Vorschau", font=("Segoe UI", 12, "bold"))
	self.gif_label.pack(pady=(0,5))
	self.tooltips = {}
	self.tooltips['gif_label'] = ToolTip(self.gif_label, tr('tt_gif_label', self.lang))
	
	# Canvas-Container für quadratisches Aspekt-Verhältnis
	gif_canvas_frame = tk.Frame(gif_preview_container, width=800, height=800, bg="#222")
	gif_canvas_frame.pack(pady=(0, 10))
	gif_canvas_frame.pack_propagate(False)  # Verhindere Größenanpassung an Inhalt
	
	self.gif_canvas = tk.Label(gif_canvas_frame, bg="#222", relief=tk.SUNKEN)
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
	texture_preview_container = ttk.Frame(right)
	texture_preview_container.pack(fill=tk.BOTH, expand=True)
	self.texture_preview_frame = texture_preview_container  # Referenz für Ein-/Ausblenden speichern
	self.texture_label = ttk.Label(texture_preview_container, text="🖼 Textur-Vorschau", font=("Segoe UI", 12, "bold"))
	self.texture_label.pack(pady=(0,5))
	self.tooltips['texture_label'] = ToolTip(self.texture_label, tr('tt_texture_label', self.lang))
	
	# Canvas-Container für quadratisches Aspekt-Verhältnis
	texture_canvas_frame = tk.Frame(texture_preview_container, width=800, height=800, bg="#222")
	texture_canvas_frame.pack(pady=(0, 10))
	texture_canvas_frame.pack_propagate(False)  # Verhindere Größenanpassung an Inhalt
	
	self.texture_canvas = tk.Label(texture_canvas_frame, bg="#222", relief=tk.SUNKEN)
	self.texture_canvas.pack(fill=tk.BOTH, expand=True)
	self.tooltips['texture_canvas'] = ToolTip(self.texture_canvas, tr('tt_texture_canvas', self.lang))
	
	# Mouse-Binding für Textur-Vorschau: Bei Klick Textur laden
	def load_texture_on_click(event=None):
		self.load_texture()
	self.texture_canvas.bind('<Button-1>', load_texture_on_click)
	self.texture_settings = self.create_effects_panel(right, prefix="texture")
	self.texture_settings.pack(fill=tk.X, pady=10)
	self.tooltips['texture_settings'] = ToolTip(self.texture_settings, tr('tt_texture_settings', self.lang))

	# --- Master Einstellungen ---
	self.master_group = ttk.LabelFrame(main_inner, text=f"🛠 {tr('master_settings', self.lang) or 'Master Einstellungen'}")
	self.master_group.pack(fill=tk.X, padx=10, pady=(5,2))

	# --- Media ---
	self.media_group = ttk.LabelFrame(main_inner, text=f"🎬 {tr('media', self.lang) or 'Media'}")
	self.media_group.pack(fill=tk.X, padx=10, pady=(5,2))

	# --- Datei-Gruppe (File Group) ---
	# Diese LabelFrame enthält die Haupt-Funktions-Toolbar (Load, Save, Export, etc.)
	self.file_group = ttk.LabelFrame(main_inner, text=f"📁 {tr('file', self.lang) or 'Datei'}")
	self.file_group.pack(fill=tk.X, padx=10, pady=(5,2))
	
	try:
		import ttkbootstrap as tb
		THEME_AVAILABLE = True
	except ImportError:
		tb = None
		THEME_AVAILABLE = False
	
	# === FILE TOOLBAR (Button-Leiste) ===
	# Diese Buttons sind in der File-Group und bilden die Haupt-Funktions-Toolbar.
	# Nicht zu verwechseln mit der Menu Bar (Menüleiste) oben im Fenster.
	load_text = f"📂 {tr('load_gif', self.lang) or 'GIF laden'}"
	if THEME_AVAILABLE and tb is not None:
		self.load_btn = tb.Button(self.file_group, text=load_text, command=self.load_gif, bootstyle="success")
	else:
		self.load_btn = tk.Button(self.file_group, text=load_text, command=self.load_gif, bg="#4CAF50", fg="white", activebackground="#388E3C", activeforeground="white")
	self.load_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['load_btn'] = ToolTip(self.load_btn, tr('tt_load_btn', self.lang))
	self.load_url_btn = ttk.Button(self.file_group, text=f"🌐 {tr('load_url', self.lang) or 'URL laden'}", command=self.load_gif_from_url)
	self.load_url_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['load_url_btn'] = ToolTip(self.load_url_btn, tr('tt_load_url_btn', self.lang) or "Grafik direkt von einer URL laden")
	self.save_gif_btn = ttk.Button(self.file_group, text=f"💾 {tr('save_gif', self.lang) or 'GIF speichern'}", command=self.save_gif)
	self.save_gif_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['save_gif_btn'] = ToolTip(self.save_gif_btn, tr('tt_save_gif_btn', self.lang))
	self.load_texture_btn = ttk.Button(self.file_group, text=normalize_label_text(f"🖼 {tr('load_texture', self.lang) or 'Textur laden'}"), command=self.load_texture)
	self.load_texture_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['load_texture_btn'] = ToolTip(self.load_texture_btn, tr('tt_load_texture_btn', self.lang) or "Textur-Datei laden (PNG, JPG, BMP, etc.)")
	self.save_texture_btn = ttk.Button(self.file_group, text=f"🧵 {tr('save_texture', self.lang) or 'Textur speichern'}", command=self.save_texture)
	self.save_texture_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['save_texture_btn'] = ToolTip(self.save_texture_btn, tr('tt_save_texture_btn', self.lang))
	self.export_lsl_btn = ttk.Button(self.file_group, text=f"🧾 {tr('export_lsl', self.lang) or 'LSL exportieren'}", command=self.export_lsl)
	self.export_lsl_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['export_lsl_btn'] = ToolTip(self.export_lsl_btn, tr('tt_export_lsl_btn', self.lang))

	# Button: Einzelbilder (ZIP/Ordner) zu GIF
	self.import_frames_btn = ttk.Button(self.file_group, text=f"🧩 {tr('import_frames', self.lang) or 'Bilder zu GIF'}", command=self.import_frames_to_gif)
	self.import_frames_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['import_frames_btn'] = ToolTip(self.import_frames_btn, tr('tt_import_frames_btn', self.lang))
	# Clear Button
	if THEME_AVAILABLE and tb is not None:
		style = tb.Style()
		style.configure("RedClear.TButton", background="#e53935", foreground="white")
		self.clear_btn = tb.Button(self.file_group, text=f"🧹 {tr('clear', self.lang) or ''}", command=self.clear_texture, style="RedClear.TButton")
	else:
		self.clear_btn = tk.Button(self.file_group, text=f"🧹 {tr('clear', self.lang) or ''}", command=self.clear_texture, bg="#e53935", fg="white", activebackground="#b71c1c", activeforeground="white")
	self.clear_btn.pack(side=tk.LEFT, padx=2, pady=2)
	self.tooltips['clear_btn'] = ToolTip(self.clear_btn, tr('tt_clear_btn', self.lang))
	# --- Media Controls ---
	media_row = ttk.Frame(self.media_group)
	media_row.pack(fill=tk.X)
	self.playing = False

	# Geschwindigkeit/Abspielrate-Slider für Media Play
	playrate_row = ttk.Frame(self.media_group)
	playrate_row.pack(fill=tk.X, pady=(4,2))
	self.media_playrate_label = ttk.Label(playrate_row, text=f"🎚 {tr('playrate', self.lang) or 'Abspielrate:'}", width=12, anchor="w")
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
	self.size_label = ttk.Label(size_row, text=f"📐 {tr('image_size', self.lang) or 'Bildgröße:'}", background="#e0f7fa", foreground="black", relief=tk.FLAT, borderwidth=1, width=20, anchor="w", font=GUI_FONT)
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

	# Preset-Combobox für Bildgrößen
	self.size_preset_var = tk.StringVar(value=str(self.image_width))
	size_presets = ["256", "512", "768", "1024", "1280", "1536", "1792", "2048"]
	self.size_preset_combo = ttk.Combobox(size_row, textvariable=self.size_preset_var, values=size_presets, width=6, state="normal")
	self.size_preset_combo.pack(side=tk.LEFT, padx=(6, 0))
	self.tooltips['size_preset_combo'] = ToolTip(self.size_preset_combo, tr('tt_size_preset_combo', self.lang))

	# Preview auch bei manueller Eingabe aktualisieren
	def _update_preview_if_gif_loaded(*args):
		if hasattr(self, 'gif_image') and self.gif_image is not None:
			try:
				from image_processing import show_texture
				show_texture(self)
			except Exception as e:
				logger.debug(f"Failed to update texture preview: {type(e).__name__}: {e}", exc_info=False)
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
				except Exception as e:
					logger.debug(f"Failed to update texture from preset: {type(e).__name__}: {e}", exc_info=False)
		except ValueError:
			logger.debug(f"Invalid preset value: {preset}", exc_info=False)
	# Bindings werden in main.py gesetzt
	self.size_preset_combo.bind('<<ComboboxSelected>>', set_image_size_from_preset)
	# Bildrate
	framerate_row = ttk.Frame(left_frame)
	framerate_row.pack(fill=tk.X, pady=(4,2))
	self.framerate_label = ttk.Label(framerate_row, text=f"⏱ {tr('framerate', self.lang) or 'Framerate:'}", background="#bbdefb", foreground="black", relief=tk.FLAT, borderwidth=1, width=20, anchor="w", font=GUI_FONT)
	self.framerate_label.pack(side=tk.LEFT, padx=(0,4), ipady=6)
	self.tooltips['framerate_label'] = ToolTip(self.framerate_label, tr('tt_framerate_label', self.lang))
	self.framerate_var = tk.IntVar(value=10)
	self.framerate_spin = ttk.Spinbox(framerate_row, from_=1, to=10000, increment=1, textvariable=self.framerate_var, width=6)
	self.framerate_spin.pack(side=tk.LEFT)
	self.tooltips['framerate_spin'] = ToolTip(self.framerate_spin, tr('tt_framerate_spin', self.lang))
	# Max. Bilder
	maxframes_row = ttk.Frame(left_frame)
	maxframes_row.pack(fill=tk.X, pady=(4,2))
	self.maxframes_label = ttk.Label(maxframes_row, text=f"🖼 {tr('max_images', self.lang) or 'Max. Bilder:'}", background="#c8e6c9", foreground="black", relief=tk.FLAT, borderwidth=1, width=20, anchor="w", font=GUI_FONT)
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
	self.bg_label = ttk.Label(bg_row, text=f"🎨 {tr('bg_color', self.lang) or 'Hintergrundfarbe:'}", background="#fff9c4", foreground="black", relief=tk.FLAT, borderwidth=1, width=23, anchor="w", font=GUI_FONT)
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
	
	# Transparenz-Schieberegler für Hintergrundfarbe
	transparency_bg_row = ttk.Frame(middle_frame)
	transparency_bg_row.pack(fill=tk.X, pady=(2,4))
	self.transparency_bg_label = ttk.Label(
		transparency_bg_row,
		text=f"💧 {tr('bg_transparency', self.lang) or 'Transparenz:'}",
		background="#fff9c4",
		foreground="black",
		relief=tk.FLAT,
		borderwidth=1,
		width=23,
		anchor="w",
		font=GUI_FONT
	)
	self.transparency_bg_label.pack(side=tk.LEFT, padx=(0,4), ipady=3)
	
	# Schieberegler (0-100%, wobei 100% = vollständig transparent)
	self.bg_transparency_var = tk.IntVar(value=100)
	self.transparency_bg_scale = ttk.Scale(transparency_bg_row, from_=0, to=100, orient="horizontal", variable=self.bg_transparency_var, length=100)
	self.transparency_bg_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
	
	# Prozent-Label
	self.transparency_bg_percent = ttk.Label(transparency_bg_row, text="100%", width=4, font=GUI_FONT)
	self.transparency_bg_percent.pack(side=tk.LEFT)
	self.tooltips['transparency_bg_scale'] = ToolTip(
		self.transparency_bg_scale,
		tr('tt_bg_transparency', self.lang) or "Transparenz der Hintergrundfarbe einstellen"
	)
	
	# Bild hinzufügen
	add_row = ttk.Frame(middle_frame)
	add_row.pack(fill=tk.X, pady=(4,2))
	self.add_row = add_row  # Referenz speichern
	self.frame_select_spin = ttk.Spinbox(add_row, from_=0, to=0, textvariable=self.frame_select_var, width=5, state="readonly")
	self.frame_select_spin.pack(side=tk.RIGHT)
	self.tooltips['frame_select_spin'] = ToolTip(self.frame_select_spin, tr('tt_frame_select_spin', self.lang))
	self.add_frame_btn = ttk.Button(add_row, text=f"➕ {tr('add_frame', self.lang) or ''}")
	self.add_frame_btn.pack(side=tk.RIGHT, padx=(0,4))
	self.tooltips['add_frame_btn'] = ToolTip(self.add_frame_btn, tr('tt_add_frame_btn', self.lang))
	# Entfernen-Button für Frames
	# Korrektur: style-Parameter nur setzen, wenn Stilname existiert
	if 'RedClear.TButton' in ttk.Style().theme_names():
		self.remove_frame_btn = ttk.Button(add_row, text="➖ Entfernen", style="RedClear.TButton")
	else:
		self.remove_frame_btn = ttk.Button(add_row, text="➖ Entfernen")
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
		text=f"🌐 {tr('language', self.lang) or ''}",
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
	self.lang_combo = ttk.Combobox(lang_row, values=['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt', 'uk', 'ja', 'zh'], textvariable=self.lang_var, width=6, state="readonly", font=GUI_FONT)
	self.lang_combo.pack(side=tk.LEFT)
	self.tooltips['lang_combo'] = ToolTip(self.lang_combo, tr('tt_lang_combo', self.lang))
	# Bindings werden in main.py gesetzt

	# Theme-Auswahl zwischen Sprache und Exportformat
	if THEME_AVAILABLE and tb is not None:
		theme_row = ttk.Frame(right_frame)
		theme_row.pack(fill=tk.X, pady=(4,2))
		theme_label = ttk.Label(theme_row, text=f"🎛 {tr('theme', self.lang) or 'Theme:'}", background="#e0e0e0", foreground="black", relief=tk.FLAT, borderwidth=1, width=GUI_LABEL_WIDTH, anchor="w", font=GUI_FONT)
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
		text=f"📤 {tr('export_format', self.lang) or 'Exportformat:'}",
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
		self.reset_btn = tb.Button(reset_row, text=f"🔄 {tr('reset', self.lang) or 'Reset'}", style="RedReset.TButton", width=GUI_WARN_WIDTH)
	else:
		self.reset_btn = tk.Button(reset_row, text=f"🔄 {tr('reset', self.lang) or 'Reset'}", bg=GUI_WARN_BG, fg=GUI_WARN_FG, activebackground="#b71c1c", activeforeground="white", width=GUI_WARN_WIDTH, height=GUI_WARN_HEIGHT, font=GUI_FONT)
	self.reset_btn.pack(side=tk.LEFT, padx=8, ipady=6)
	self.tooltips['reset_btn'] = ToolTip(self.reset_btn, tr('tt_reset_btn', self.lang))

	# --- Status-Gruppe ---
	self.status_group = ttk.LabelFrame(main_inner, text=f"📋 {tr('status', self.lang) or 'Status'}")
	self.status_group.pack(fill=tk.X, padx=10, pady=(5,5))
	self.status = ttk.Label(self.status_group, text=tr('ready', self.lang) or "Bereit", anchor="w")
	self.status.pack(fill=tk.X)

	# Übersetzung für Randlos-Label und Tooltip erfolgt ausschließlich in update_language für Konsistenz


