###
# main.py
# This file contains the main application class ModernApp, which defines the GUI and core functionality of the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, colorchooser
from PIL import Image, ImageTk
import math
import atexit
import logging
from typing import Optional, List, Any
from config import load_config, save_config
from translations import tr
from gui_layout import build_layout, create_effects_panel, normalize_label_text
from image_processing import apply_effects, show_gif_frame, show_texture
from file_ops import load_gif, save_gif, save_texture, load_texture, export_lsl, generate_lsl_script
from events import reset_settings, change_language, on_maxframes_changed, add_selected_frame_to_texture, choose_bg_color, set_transparent_bg, on_bg_transparency_changed, apply_background_from_config
from logging_config import get_logger
try:
    from tkinterdnd2 import DND_FILES
    TKDND_AVAILABLE = True
except ImportError:
    DND_FILES = None
    TKDND_AVAILABLE = False

try:
    import ttkbootstrap as tb
    THEME_AVAILABLE = True
except ImportError:
    tb = None
    THEME_AVAILABLE = False

# Initialize logger
logger = get_logger(__name__)

# Detect keyboard layout and system language on startup
try:
    import ctypes
    import locale

    def get_keyboard_layout():
        # Windows-spezifisch: Tastaturlayout ermitteln
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        hWnd = user32.GetForegroundWindow()
        thread_id = user32.GetWindowThreadProcessId(hWnd, 0)
        klid = user32.GetKeyboardLayout(thread_id)
        # Die unteren 16 Bit enthalten die Sprachkennung (LANGID)
        lid = klid & 0xFFFF
        # Sprachcode (z.B. 0x407 = Deutsch, 0x409 = Englisch)
        lang_map = {
            0x407: 'de',
            0x409: 'en',
            0x40c: 'fr',
            0x410: 'it',
            0x419: 'ru',
            0x40a: 'es',
            0x413: 'nl',
            0x41d: 'se',
            0x415: 'pl',
            0x816: 'pt',
            0x422: 'uk',
            0x411: 'ja',
            0x804: 'zh'
            # Weitere Codes nach Bedarf ergänzen
        }
        return lang_map.get(lid, f'unknown({lid})')

    def get_system_language():
        # Systemweite Sprache ermitteln
        lang, _ = locale.getdefaultlocale()
        return lang

    # Voreinstellungen setzen
    DEFAULT_KEYBOARD_LAYOUT = get_keyboard_layout()
    DEFAULT_LANGUAGE = get_system_language()
    
    logger.debug(f"Detected keyboard layout: {DEFAULT_KEYBOARD_LAYOUT}")
    logger.debug(f"Detected system language: {DEFAULT_LANGUAGE}")
except Exception as e:
    logger.warning(f"Failed to detect keyboard layout or system language: {e}")
    DEFAULT_KEYBOARD_LAYOUT = 'unknown'
    DEFAULT_LANGUAGE = 'unknown'

LANGUAGES = ['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt', 'uk', 'ja', 'zh']
Version = "2.1.2"
WindowsSize  = "1650x950"

class ModernApp:
    def _bind_effects_panel_events(self):
        """Bindet alle Effekt-Einstellungen an ihre jeweiligen Update-Funktionen."""
        # Hilfsfunktion: Trace auf Variable-Änderung mit sofortiger Aktualisierung
        def create_trace_callback(effect_type, is_gif=True):
            def callback(*args):
                if is_gif:
                    self._apply_gif_effect(effect_type)
                else:
                    self._apply_texture_effect(effect_type)
            return callback
        
        # GIF-Effekte binding
        for effect in ['grayscale', 'sharpen', 'blur', 'transparency', 'colorintensity_active']:
            var_name = f'gif_{effect}'
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                var.trace_add('write', create_trace_callback(effect.replace('_active', ''), is_gif=True))
        
        # GIF-Wert-Slider binding
        for effect in ['sharpen_value', 'blur_value', 'transparency_value', 'colorintensity']:
            var_name = f'gif_{effect}'
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                var.trace_add('write', create_trace_callback(effect, is_gif=True))
        
        # Textur-Effekte binding
        for effect in ['grayscale', 'sharpen', 'blur', 'transparency', 'colorintensity_active']:
            var_name = f'texture_{effect}'
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                var.trace_add('write', create_trace_callback(effect.replace('_active', ''), is_gif=False))
        
        # Textur-Wert-Slider binding
        for effect in ['sharpen_value', 'blur_value', 'transparency_value', 'colorintensity']:
            var_name = f'texture_{effect}'
            if hasattr(self, var_name):
                var = getattr(self, var_name)
                var.trace_add('write', create_trace_callback(effect, is_gif=False))

    def _apply_gif_effect(self, effect_type):
        if not self.gif_frames:
            return
        # Effekte werden nur bei der Anzeige angewendet, nicht hier auf den Frames selbst gespeichert
        self.show_gif_frame()
        if hasattr(self, 'root') and self.root:
            self.root.update_idletasks()

    def _apply_texture_effect(self, effect_type):
        if not self.gif_frames:
            return
        # Effekte werden nur bei der Anzeige angewendet, nicht hier auf den Frames selbst gespeichert
        self.show_texture()
        if hasattr(self, 'root') and self.root:
            self.root.update_idletasks()
    def import_frames_to_gif(self):
        from file_ops import import_frames_to_gif
        import_frames_to_gif(self)
    # Entfernt: Fehlerhafte Zeile außerhalb von Methoden

    def show_texture(self):
        # Kompatibilitäts-Wrapper, damit show_texture(self) immer funktioniert
        if hasattr(self, '_update_texture'):
            self._update_texture()

    # Methoden aus file_ops an die Instanz binden, falls nicht schon vorhanden
    def _ensure_file_ops_methods(self):
        from file_ops import _load_gif_frames, _setup_frame_select, _reset_play_button, _update_status, _update_preview
        from image_processing import show_texture
        self._load_gif_frames = _load_gif_frames.__get__(self)
        self._setup_frame_select = _setup_frame_select.__get__(self)
        self._reset_play_button = _reset_play_button.__get__(self)
        self._update_status = _update_status.__get__(self)
        self._update_preview = _update_preview.__get__(self)
        self._update_texture = show_texture.__get__(self)
        # Kein automatisches Anzeigen der Textur hier – dies erfolgt gezielt nach GIF-Ladevorgängen


    def __init__(self, root):
        self.root = root
        
        # Setze Standardfarben für Menüs auf dunkel
        try:
            self.root.option_add('*Menu.background', '#2d2d2d')
            self.root.option_add('*Menu.foreground', '#ffffff')
            self.root.option_add('*Menu.activeBackground', '#4a4a4a')
            self.root.option_add('*Menu.activeForeground', '#ffffff')
            self.root.option_add('*Menu.selectColor', '#ffffff')
        except Exception as e:
            logger.debug(f"Could not set menu colors: {e}")
        
        self._ensure_file_ops_methods()
        from image_processing import show_gif_frame
        self.show_gif_frame = show_gif_frame.__get__(self)
        # Sprache initial aus Combobox übernehmen, falls vorhanden, sonst Standard
        self.lang: str = 'de'
        self.lang_var: Optional[tk.StringVar] = None
        self.gif_image: Optional[Image.Image] = None
        self.gif_frames: List[Image.Image] = []
        self.texture_image: Optional[Image.Image] = None
        self.texture_source_image: Optional[Image.Image] = None
        self.texture_use_source_image: bool = False
        self.frame_count: int = 0
        self.current_frame: int = 0
        self.timer: Optional[Any] = None
        self.image_width: int = 2048
        self.image_height: int = 2048
        # PhotoImage-Referenzen (müssen behalten werden, sonst Garbage Collection)
        self._gif_img_ref: Optional[Any] = None
        self._texture_img_ref: Optional[Any] = None
        self.root.title(f"OSSL2Gif {Version}")
        # Fenstergeometrie wird nach build_layout() gesetzt

        # Effekt-Variablen initialisieren (für Pylance und Code-Vervollständigung)
        self.gif_sharpen_value = tk.DoubleVar(value=2.5)
        self.gif_blur_value = tk.DoubleVar(value=3.5)
        self.gif_transparency_value = tk.DoubleVar(value=0.5)
        self.gif_colorintensity = tk.DoubleVar(value=0.5)
        self.gif_grayscale = tk.BooleanVar(value=False)
        self.gif_sharpen = tk.BooleanVar(value=False)
        self.gif_blur = tk.BooleanVar(value=False)
        self.gif_transparency = tk.BooleanVar(value=False)
        self.gif_colorintensity_active = tk.BooleanVar(value=False)

        self.texture_sharpen_value = tk.DoubleVar(value=2.5)
        self.texture_blur_value = tk.DoubleVar(value=3.5)
        self.texture_transparency_value = tk.DoubleVar(value=0.5)
        self.texture_colorintensity = tk.DoubleVar(value=0.5)
        self.texture_grayscale = tk.BooleanVar(value=False)
        self.texture_sharpen = tk.BooleanVar(value=False)
        self.texture_blur = tk.BooleanVar(value=False)
        self.texture_transparency = tk.BooleanVar(value=False)
        self.texture_colorintensity_active = tk.BooleanVar(value=False)

        # Initialize dynamically set GUI attributes
        self.gif_label = None
        self.gif_canvas = None
        self.gif_settings = None
        self.texture_label = None
        self.texture_canvas = None
        self.texture_settings = None
        self.status = None
        self.status_group = None
        self.file_group = None
        self.master_group = None
        self.theme_label = None  # Für Theme-Label (wird in gui_layout.py gesetzt)
        self.theme_combo = None  # Für Theme-Combobox (wird in gui_layout.py gesetzt)
        self.theme_var = None    # Für Theme-Variable (wird in gui_layout.py gesetzt)
        self.width_entry = None
        self.width_var = tk.IntVar(value=2048)
        self.height_entry = None
        self.height_var = tk.IntVar(value=2048)
        self.load_btn = None
        self.load_url_btn = None
        self.load_texture_btn = None
        self.remove_frame_btn = None  # Für Entfernen-Button (Frames)
        self.save_gif_btn = None
        self.save_texture_btn = None
        self.export_lsl_btn = None
        self.clear_btn = None
        self.import_frames_btn = None  # Für "Bilder zu GIF"-Button
        self.size_label = None
        self.size_preset_var = None
        self.size_preset_combo = None
        self.bg_label = None
        self.bg_color_box = None
        self.bg_color_photo = None  # PhotoImage für Transparenz-Anzeige
        self.bg_color = '#00000000'
        self.bg_box_color = '#000000'
        self.bg_transparency_var = tk.IntVar(value=100)
        self.transparency_bg_scale = None
        self.transparency_bg_percent = None
        self.transparency_bg_label = None
        self.framerate_label = None
        self.framerate_var = tk.IntVar(value=10)
        self.framerate_spin = None
        self.lang_label = None
        self.lang_combo = None
        self.frame_select_spin = None
        self.add_frame_btn = None
        self.maxframes_label = None
        self.maxframes_var = tk.IntVar(value=64)
        self.maxframes_spin = None
        self.reset_btn = None
        self.media_group = None
        self.prev_btn = None
        self.pause_btn = None
        self.play_btn = None
        self.stop_btn = None
        self.next_btn = None
        
        self.export_format_label = None
        self.export_format_var = tk.StringVar(value='PNG')
        self.media_playrate_var = None  # Wird in gui_layout.py gesetzt
        self.media_playrate_label = None  # Für Media-Abspielrate-Label (Tooltip/Übersetzung)
        self.menubar = None  # Menu Bar (Menüleiste oben: File, Edit, View, Groups, Help) - wird in gui_layout.py create_menubar() gesetzt
        self.playing = False
        
        # BooleanVars für Gruppen-Sichtbarkeit
        self.show_gif_var = tk.BooleanVar(value=True)
        self.show_gif_settings_var = tk.BooleanVar(value=True)
        self.show_texture_var = tk.BooleanVar(value=True)
        self.show_texture_settings_var = tk.BooleanVar(value=True)
        self.show_master_var = tk.BooleanVar(value=True)
        self.show_media_var = tk.BooleanVar(value=True)
        self.show_file_var = tk.BooleanVar(value=True)
        self.show_status_var = tk.BooleanVar(value=True)
        
        # Frame-Referenzen (werden in gui_layout.py gesetzt)
        self.gif_preview_frame = None
        self.texture_preview_frame = None
        
        # Icon nur unter Windows laden (.ico wird nur von Windows unterstützt)
        import platform
        if platform.system() == "Windows":
            try:
                self.root.iconbitmap("icon.ico")
            except FileNotFoundError:
                logger.debug("Icon file 'icon.ico' not found - continuing without icon")
            except Exception as e:
                logger.warning(f"Failed to load icon: {type(e).__name__}: {e}", exc_info=False)
        if THEME_AVAILABLE and tb is not None:
            tb.Style("superhero")
        self.tooltips = {}
        # Konfiguration laden (vor build_layout, damit Werte übernommen werden)
        self._config_loaded = False
        config = load_config()
        
        # Debug-Logging für Config-Laden
        if config:
            logger.debug(f"Configuration loaded: {list(config.keys())}")
        else:
            logger.debug("No configuration file found - using defaults")
        
        # Sprache VORHER aus Config laden, damit build_layout() mit der richtigen Sprache arbeitet
        if config and 'lang' in config:
            self.lang = config['lang']
            logger.debug(f"Language loaded from config: {self.lang}")
        
        # Gruppen-Einstellungen aus Config laden, falls vorhanden
        if config:
            group_settings_loaded = False
            if 'show_gif_preview' in config:
                self.show_gif_var.set(config['show_gif_preview'])
                group_settings_loaded = True
            if 'show_gif_settings' in config:
                self.show_gif_settings_var.set(config['show_gif_settings'])
                group_settings_loaded = True
            if 'show_texture_preview' in config:
                self.show_texture_var.set(config['show_texture_preview'])
                group_settings_loaded = True
            if 'show_texture_settings' in config:
                self.show_texture_settings_var.set(config['show_texture_settings'])
                group_settings_loaded = True
            if 'show_master_settings' in config:
                self.show_master_var.set(config['show_master_settings'])
                group_settings_loaded = True
            if 'show_media' in config:
                self.show_media_var.set(config['show_media'])
                group_settings_loaded = True
            if 'show_file' in config:
                self.show_file_var.set(config['show_file'])
                group_settings_loaded = True
            if 'show_status' in config:
                self.show_status_var.set(config['show_status'])
                group_settings_loaded = True
            if group_settings_loaded:
                logger.debug("Group visibility settings loaded from config")
        self.build_layout()
        # Nach build_layout ist self.lang_var gesetzt
        if hasattr(self, 'lang_var') and self.lang_var is not None:
            self.lang_var.set(self.lang)  # Setze lang_var auf den geladenen Sprachcode
            self.lang = self.lang_var.get()
        # ZUERST die Sprache aktualisieren, damit die Textlängen korrekt sind
        self.update_language()
        # DANN alle Größen berechnen, NACHDEM die Texte gesetzt sind
        self.root.update_idletasks()
        
        # Konfiguration anwenden (PRIOITÄT: Config vor _optimize_window_size)
        if config:
            self.apply_config(config)
            self._config_loaded = True
        else:
            # Nur optimieren, wenn KEINE config vorhanden ist
            self._optimize_window_size()
        self._setup_drag_and_drop()
        # Bindings für Effekte-Panels IMMER setzen
        self._bind_effects_panel_events()
        # Hinweis: Automatisches Speichern beim Beenden ist deaktiviert.
        # Verwenden Sie stattdessen 'Datei > Einstellungen speichern' um Einstellungen manuell zu speichern.
        
        # Fenster aktualisieren und anzeigen
        self.root.update()
        self.root.deiconify()  # Zeige Fenster an (es wurde mit withdraw() versteckt)
        logger.info("Application window displayed")

        # --- Event-Bindings zentral setzen ---
        # Entfernen-Button für Frames verbinden
        if hasattr(self, 'remove_frame_btn') and self.remove_frame_btn is not None:
            from events import remove_selected_frame_from_texture
            self.remove_frame_btn.config(command=lambda: remove_selected_frame_from_texture(self))

        # Bildgröße-Eingaben
        if self.width_entry is not None:
            self.width_entry.bind('<FocusOut>', lambda e: (self.show_gif_frame(), self.show_texture()))
        if self.height_entry is not None:
            self.height_entry.bind('<FocusOut>', lambda e: (self.show_gif_frame(), self.show_texture()))

        # Maxframes
        if self.maxframes_spin is not None:
            self.maxframes_spin.bind('<FocusOut>', lambda e: on_maxframes_changed(self))
        self.maxframes_var.trace_add('write', lambda *args: on_maxframes_changed(self))

        # Hintergrundfarbe
        if self.bg_color_box is not None:
            self.bg_color_box.bind('<Button-1>', lambda e: choose_bg_color(self, e))
            self.bg_color_box.bind('<Button-3>', lambda e: set_transparent_bg(self))
        
        # Transparenz-Schieberegler für Hintergrund
        if hasattr(self, 'bg_transparency_var'):
            self.bg_transparency_var.trace_add('write', lambda *args: on_bg_transparency_changed(self))

        # Bild hinzufügen
        if self.add_frame_btn is not None:
            self.add_frame_btn.config(command=lambda: add_selected_frame_to_texture(self))

        # Sprache
        if self.lang_combo is not None:
            self.lang_combo.bind('<<ComboboxSelected>>', lambda e: change_language(self, e))

        # Reset
        if self.reset_btn is not None:
            self.reset_btn.config(command=lambda: reset_settings(self))

        # Zwischenablage: GIF/Bild mit Strg+V einfügen
        self.root.bind_all('<Control-v>', self.load_gif_from_clipboard)
        self.root.bind_all('<Control-V>', self.load_gif_from_clipboard)
        
        # Keyboard Shortcuts für Menü
        self.root.bind('<Control-o>', lambda e: self.load_gif())
        self.root.bind('<Control-O>', lambda e: self.load_gif())
        self.root.bind('<Control-u>', lambda e: self.load_gif_from_url())
        self.root.bind('<Control-U>', lambda e: self.load_gif_from_url())
        self.root.bind('<Control-s>', lambda e: self.save_gif())
        self.root.bind('<Control-S>', lambda e: self.save_gif())
        self.root.bind('<Control-t>', lambda e: self.save_texture())
        self.root.bind('<Control-T>', lambda e: self.save_texture())
        self.root.bind('<Control-e>', lambda e: self.export_lsl())
        self.root.bind('<Control-E>', lambda e: self.export_lsl())
        self.root.bind('<Control-r>', lambda e: reset_settings(self))
        self.root.bind('<Control-R>', lambda e: reset_settings(self))
        self.root.bind('<Control-q>', lambda e: self.root.quit())
        self.root.bind('<Control-Q>', lambda e: self.root.quit())
        self.root.bind('<Control-p>', lambda e: self.show_texture_preview_window())
        self.root.bind('<Control-P>', lambda e: self.show_texture_preview_window())
        self.root.bind('<space>', lambda e: self.start_animation() if not self.playing else self.pause_animation())
        self.root.bind('<Left>', lambda e: self.step_backward())
        self.root.bind('<Right>', lambda e: self.step_forward())
        
        # Stelle sicher, dass ALLES komplett berechnet ist, bevor Fenster angezeigt wird
        self.root.update_idletasks()
        # Fenster nach vollständiger Initialisierung anzeigen
        self.root.deiconify()

    def _setup_drag_and_drop(self):
        self.dragdrop_enabled = False
        if not TKDND_AVAILABLE or DND_FILES is None:
            logger.info("tkinterdnd2 not available - drag and drop disabled")
            return

        targets = [self.root]
        if hasattr(self, 'gif_canvas') and self.gif_canvas is not None:
            targets.append(self.gif_canvas)
        if hasattr(self, 'load_btn') and self.load_btn is not None:
            targets.append(self.load_btn)

        for widget in targets:
            try:
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind('<<Drop>>', self.on_gif_drop)
                self.dragdrop_enabled = True
            except Exception as e:
                logger.debug(f"Could not register DnD on widget {widget}: {type(e).__name__}: {e}", exc_info=False)

        if self.dragdrop_enabled:
            logger.info("Drag and drop for GIF files enabled")

    def on_gif_drop(self, event):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_from_path

        dropped_items = []
        try:
            dropped_items = list(self.root.tk.splitlist(event.data))
        except Exception:
            if event.data:
                dropped_items = [event.data]

        for item in dropped_items:
            clean_item = str(item).strip().strip('{}').strip('"')
            if not clean_item:
                continue
            if load_gif_from_path(self, clean_item):
                return "break"

        if hasattr(self, 'status') and self.status:
            self.status.config(text="Drop enthält keine gültige GIF-Datei.")
        return "break"

    def get_config(self):
        # Alle relevanten Einstellungen als dict zurückgeben
        # Windowgeometrie speichern: z.B. "1200x800+100+50"
        window_geometry = self.root.geometry()
        return {
            'lang': self.lang,
            'width': self.width_var.get() if hasattr(self, 'width_var') and self.width_var is not None else 2048,
            'height': self.height_var.get() if hasattr(self, 'height_var') and self.height_var is not None else 2048,
            'bg_color': getattr(self, 'bg_color', '#00000000'),
            'framerate': self.framerate_var.get() if hasattr(self, 'framerate_var') and self.framerate_var is not None else 10,
            'export_format': self.export_format_var.get() if hasattr(self, 'export_format_var') and self.export_format_var is not None else 'PNG',
            'maxframes': self.maxframes_var.get() if hasattr(self, 'maxframes_var') and self.maxframes_var is not None else 64,
            'theme': self.theme_var.get() if hasattr(self, 'theme_var') and self.theme_var is not None else None,
            'window_geometry': window_geometry,
            'show_gif_preview': self.show_gif_var.get(),
            'show_gif_settings': self.show_gif_settings_var.get(),
            'show_texture_preview': self.show_texture_var.get(),
            'show_texture_settings': self.show_texture_settings_var.get(),
            'show_master_settings': self.show_master_var.get(),
            'show_media': self.show_media_var.get(),
            'show_file': self.show_file_var.get(),
            'show_status': self.show_status_var.get()
        }

    def save_config(self):
        save_config(self)

    def save_gui_config(self):
        """Speichert die aktuellen GUI-Einstellungen manuell (inkl. Gruppen-Sichtbarkeit)."""
        self.save_config()
        messagebox.showinfo(tr('save_settings', self.lang) or 'Einstellungen speichern', 
                           f"{tr('save_settings', self.lang) or 'Einstellungen'} {tr('ready', self.lang) or 'gespeichert'}!")

    def apply_config(self, config):
        """Wendet die Konfiguration auf die GUI an.
        
        HINWEIS: Gruppen-Einstellungen und Sprache werden bereits VORHER geladen.
        Diese Methode wendet nur die restlichen Einstellungen an (Größen, Theme, etc.)
        """
        logger.debug(f"Applying configuration with keys: {list(config.keys())}")
        
        window_geometry_restored = False
        
        if 'theme' in config and hasattr(self, 'theme_var') and self.theme_var is not None:
            self.theme_var.set(config['theme'])
            # Theme auch auf ttkbootstrap anwenden, falls verfügbar
            try:
                import ttkbootstrap as tb
                if config['theme']:
                    tb.Style().theme_use(config['theme'])
            except KeyError as e:
                logger.warning(f"Theme configuration key missing: {e}", exc_info=False)
            except Exception as e:
                logger.warning(f"Failed to apply theme from config: {type(e).__name__}: {e}", exc_info=False)
        
        # Werte aus config dict auf GUI anwenden
        if 'width' in config:
            self.width_var.set(config['width'])
            if hasattr(self, 'size_preset_var') and self.size_preset_var is not None:
                self.size_preset_var.set(str(config['width']))
        if 'height' in config:
            self.height_var.set(config['height'])
        if 'bg_color' in config and self.bg_color_box is not None:
            apply_background_from_config(self, config['bg_color'])
        if 'framerate' in config:
            self.framerate_var.set(config['framerate'])
        if 'export_format' in config:
            self.export_format_var.set(config['export_format'])
        if 'maxframes' in config:
            self.maxframes_var.set(config['maxframes'])
        
        # Fenster-Geometrie aus config wiederherstellen (z.B. "1200x800+100+50")
        if 'window_geometry' in config and config['window_geometry']:
            try:
                geometry = config['window_geometry']
                self.root.geometry(geometry)
                window_geometry_restored = True
                logger.debug(f"Restored window geometry from config: {geometry}")
            except Exception as e:
                logger.warning(f"Failed to restore window geometry '{config['window_geometry']}': {e}", exc_info=False)
        elif 'window_width' in config and 'window_height' in config:
            # Fallback für ältere configs (mit separaten width/height)
            window_width = config['window_width']
            window_height = config['window_height']
            if window_width > 1000 and window_height > 600:  # Sanity check, nur wenn sinnvolle Größen
                # Zentriere das Fenster auf dem Bildschirm
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                x = (screen_width // 2) - (window_width // 2)
                y = (screen_height // 2) - (window_height // 2)
                self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
                window_geometry_restored = True
                logger.debug(f"Restored window size from config (fallback): {window_width}x{window_height}")
        
        # Wenn KEINE gespeicherte Fenster-Geometrie gefunden, optimiere die Größe
        if not window_geometry_restored:
            logger.debug("No window geometry in config, optimizing window size")
            self._optimize_window_size()

        # Für Pylance: Initialisiere dynamisch gesetzte GUI-Attribute
        self.gif_label = getattr(self, 'gif_label', None)
        self.gif_settings = getattr(self, 'gif_settings', None)
        self.texture_label = getattr(self, 'texture_label', None)
        self.texture_settings = getattr(self, 'texture_settings', None)
        self.status = getattr(self, 'status', None)
        self.status_group = getattr(self, 'status_group', None)
        self.texture_canvas = getattr(self, 'texture_canvas', None)
        self.gif_canvas = getattr(self, 'gif_canvas', None)
        self.file_group = getattr(self, 'file_group', None)
        
        # Wende die geladenen Gruppen-Sichtbarkeitseinstellungen auf die GUI an
        self._apply_group_visibility()
        
        # Nach dem Anwenden der Config: Effekt-Panel-Bindings erneut setzen
        self._bind_effects_panel_events()

    def _apply_group_visibility(self):
        """Wendet die geladenen Gruppen-Sichtbarkeitseinstellungen auf die GUI an.
        Dies wird beim Start aufgerufen, nachdem die Config geladen wurde."""
        logger.debug("Applying group visibility settings from config")
        
        # Lade und wende jeden Group-Visibilität-Toggle an
        self._toggle_gif_preview()
        self._toggle_gif_settings()
        self._toggle_texture_preview()
        self._toggle_texture_settings()
        self._repack_groups()
        
        logger.debug("Group visibility settings applied")

    def _optimize_window_size(self):
        """Passt die Fenstergeometrie automatisch an den Inhalt an."""
        try:
            # Berechne erforderliche Größe
            req_width = self.root.winfo_reqwidth()
            req_height = self.root.winfo_reqheight()
            logger.debug(f"Window requested size: {req_width}x{req_height}")
            
            # Multiplier basierend auf Sprache: Längere Sprachen brauchen mehr Platz
            lang_multipliers = {
                'ru': 1.3,  # Russisch ist länger
                'uk': 1.3,  # Ukrainisch ist länger
                'pt': 1.1,  # Portugiesisch ist etwas länger
                'de': 1.1,  # Deutsch ist etwas länger
                'en': 1.0,  # Englisch Basis
                'fr': 1.0,
                'es': 1.0,
                'it': 0.95,
                'nl': 1.05,
                'se': 0.95,
                'pl': 1.1,
                'ja': 0.9,  # Japanisch ist kompakter
                'zh': 0.9   # Chinesisch ist kompakter
            }
            
            current_lang = getattr(self, 'lang', 'en')
            multiplier = lang_multipliers.get(current_lang, 1.0)
            
            # Setze Mindest- und Maximalgrößen
            min_width = max(int(req_width * multiplier), 1300)
            min_height = max(req_height, 950)  # 50 Pixel höher
            
            # Begrenze die Größe auf den verfügbaren Bildschirmbereich
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            logger.debug(f"Screen size: {screen_width}x{screen_height}")
            
            # Verwende max. 90% des Bildschirms, aber mind. 1300x900
            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9)
            
            window_width = min(min_width, max_width)
            window_height = min(min_height, max_height)
            
            # Zentriere das Fenster auf dem Bildschirm
            x = (screen_width // 2) - (window_width // 2)
            y = (screen_height // 2) - (window_height // 2)
            
            self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
            logger.info(f"Window optimized to size: {window_width}x{window_height} at position +{x}+{y}")
        except Exception as e:
            logger.error(f"Could not optimize window size: {e}", exc_info=True)
            # Fallback auf Standard-Größe
            self.root.geometry(WindowsSize)
            logger.info(f"Fallback to default window size: {WindowsSize}")

    def build_layout(self):
        build_layout(self)
        # Datei-Gruppe wird vollständig in gui_layout.py erzeugt und gepackt

    def reset_settings(self):
        reset_settings(self)

    def on_maxframes_changed(self, *args):
        on_maxframes_changed(self, *args)

    def choose_bg_color(self, event=None):
        choose_bg_color(self, event)

    def add_selected_frame_to_texture(self):
        add_selected_frame_to_texture(self)



    def start_animation(self):
        if not self.gif_frames:
            return
        self.playing = True
        self._run_animation()

    def _run_animation(self):
        if not self.playing or not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        # Frame-Anzeige in Thread auslagern für flüssigere UI
        import threading
        threading.Thread(target=lambda: show_gif_frame(self), daemon=True).start()
        # Media-Play-Geschwindigkeit: Slider aus Media-Bereich bevorzugen
        delay = 100
        if hasattr(self, 'media_playrate_var') and self.media_playrate_var is not None:
            playrate = self.media_playrate_var.get()
            delay = int(10000 / playrate)  # Konvertiere Prozentatz zu Verzögerung in ms
        elif self.framerate_var is not None:
            delay = self.framerate_var.get()
        self.root.after(delay, self._run_animation)

    def pause_animation(self):
        self.playing = False
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        if self.play_btn is not None:
            self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

    def stop_animation(self):
        self.playing = False
        self.current_frame = 0
        # Frame-Anzeige in Thread auslagern für flüssigere UI
        import threading
        threading.Thread(target=lambda: show_gif_frame(self), daemon=True).start()
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        if self.play_btn is not None:
            self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

    def step_forward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        # Frame-Anzeige in Thread auslagern für flüssigere UI
        import threading
        threading.Thread(target=lambda: show_gif_frame(self), daemon=True).start()

    def step_backward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame - 1) % self.frame_count
        # Frame-Anzeige in Thread auslagern für flüssigere UI
        import threading
        threading.Thread(target=lambda: show_gif_frame(self), daemon=True).start()



    def create_effects_panel(self, parent, prefix):
        return create_effects_panel(self, parent, prefix)


    def update_language(self):
        l = self.lang
        # Import Frames Button und Tooltip aktualisieren
        if hasattr(self, 'import_frames_btn') and self.import_frames_btn is not None:
            self.import_frames_btn.config(text=f"🧩 {tr('import_frames', l) or 'Bilder zu GIF'}")
        if 'import_frames_btn' in self.tooltips:
            self.tooltips['import_frames_btn'].set_text(tr('tt_import_frames_btn', l))
        # Tooltips dynamisch aktualisieren
        tooltip_keys = {
            'gif_label': 'tt_gif_label',
            'gif_canvas': 'tt_gif_canvas',
            'gif_settings': 'tt_gif_settings',
            'texture_label': 'tt_texture_label',
            'texture_canvas': 'tt_texture_canvas',
            'texture_settings': 'tt_texture_settings',
            'load_btn': 'tt_load_btn',
            'save_gif_btn': 'tt_save_gif_btn',
            'save_texture_btn': 'tt_save_texture_btn',
            'export_lsl_btn': 'tt_export_lsl_btn',
            'clear_btn': 'tt_clear_btn',
            'size_label': 'tt_size_label',
            'width_entry': 'tt_width_entry',
            'height_entry': 'tt_height_entry',
            'bg_label': 'tt_bg_label',
            'bg_color_box': 'tt_bg_color_box',
            'transparency_bg_scale': 'tt_bg_transparency',
            'framerate_label': 'tt_framerate_label',
            'framerate_spin': 'tt_framerate_spin',
            'lang_label': 'tt_lang_label',
            'lang_combo': 'tt_lang_combo',
            'frame_select_spin': 'tt_frame_select_spin',
            'add_frame_btn': 'tt_add_frame_btn',
            'maxframes_label': 'tt_maxframes_label',
            'maxframes_spin': 'tt_maxframes_spin',
            'reset_btn': 'tt_reset_btn',
            'media_group': 'tt_media_group',
            'media_playrate_label': 'tt_media_playrate_label',
            'prev_btn': 'tt_prev_btn',
            'pause_btn': 'tt_pause_btn',
            'play_btn': 'tt_play_btn',
            'stop_btn': 'tt_stop_btn',
            'next_btn': 'tt_next_btn',
            'export_format_label': 'tt_export_format_label',
            'size_preset_combo': 'tt_size_preset_combo',
        }
        for k, v in tooltip_keys.items():
            if k in self.tooltips:
                self.tooltips[k].set_text(tr(v, l))
        # Media-Abspielrate-Label und Tooltip übersetzen
        if hasattr(self, 'media_playrate_label') and self.media_playrate_label is not None:
            self.media_playrate_label.config(text=f"🎚 {tr('playrate', l) or 'Abspielrate:'}")
        if 'media_playrate_label' in self.tooltips:
            self.tooltips['media_playrate_label'].set_text(tr('tt_media_playrate_label', l))
        # Theme-Label und Combobox übersetzen (analog zu anderen Labels)
        if hasattr(self, 'theme_label') and self.theme_label is not None:
            theme_text = tr('theme', l) or tr('theme', 'en') or 'Theme:'
            self.theme_label.config(text=f"🎛 {theme_text}")
        if 'theme_label' in self.tooltips:
            tt_theme_label = tr('tt_theme_label', l) or tr('tt_theme_label', 'en') or 'Theme-Label-Tooltip'
            self.tooltips['theme_label'].set_text(tt_theme_label)
        if hasattr(self, 'theme_combo') and self.theme_combo is not None:
            if 'theme_combo' in self.tooltips:
                tt_theme_combo = tr('tt_theme_combo', l) or tr('tt_theme_combo', 'en') or 'Theme-Combo-Tooltip'
                self.tooltips['theme_combo'].set_text(tt_theme_combo)
        if self.gif_label is not None:
            self.gif_label.config(text=f"🎞 {tr('gif_preview', l) or ''}")
        if self.gif_settings is not None:
            self.gif_settings.config(text=f"⚙ {tr('gif_settings', l) or ''}")
        if self.texture_label is not None:
            self.texture_label.config(text=f"🖼 {tr('texture_preview', l) or ''}")
        if self.texture_settings is not None:
            self.texture_settings.config(text=f"⚙ {tr('texture_settings', l) or ''}")
        if self.size_label is not None:
            self.size_label.config(text=f"📐 {tr('image_size', l) or ''}")
        if self.lang_label is not None:
            self.lang_label.config(text=f"🌐 {tr('language', l) or ''}")
        if self.bg_label is not None:
            self.bg_label.config(text=f"🎨 {tr('bg_color', l) or 'Hintergrundfarbe:'}")
        if hasattr(self, 'transparency_bg_label') and self.transparency_bg_label is not None:
            self.transparency_bg_label.config(text=f"💧 {tr('bg_transparency', l) or 'Transparenz:'}")
        if self.load_btn is not None:
            self.load_btn.config(text=f"📂 {tr('load_gif', l) or ''}")
        if hasattr(self, 'load_url_btn') and self.load_url_btn is not None:
            self.load_url_btn.config(text=f"🌐 {tr('load_url', l) or 'URL laden'}")
        if 'load_url_btn' in self.tooltips:
            self.tooltips['load_url_btn'].set_text(tr('tt_load_url_btn', l) or 'Grafik direkt von einer URL laden')
        if self.save_gif_btn is not None:
            self.save_gif_btn.config(text=f"💾 {tr('save_gif', l) or ''}")
        if self.save_texture_btn is not None:
            self.save_texture_btn.config(text=f"🧵 {tr('save_texture', l) or ''}")
        if hasattr(self, 'load_texture_btn') and self.load_texture_btn is not None:
            self.load_texture_btn.config(text=normalize_label_text(f"🖼 {tr('load_texture', l) or 'Textur laden'}"))
        if 'load_texture_btn' in self.tooltips:
            self.tooltips['load_texture_btn'].set_text(tr('tt_load_texture_btn', l) or "Textur-Datei laden (PNG, JPG, BMP, etc.)")
        if self.export_lsl_btn is not None:
            self.export_lsl_btn.config(text=f"🧾 {tr('export_lsl', l) or ''}")
        if self.status is not None:
            self.status.config(text=tr('ready', l) or "")
        # Gruppenüberschriften
        if self.master_group is not None:
            self.master_group.config(text=f"🛠 {tr('master_settings', l) or ''}")
        if self.file_group is not None:
            self.file_group.config(text=f"📁 {tr('file', l) or ''}")
        if self.status_group is not None:
            self.status_group.config(text=f"📋 {tr('status', l) or ''}")
        if self.media_group is not None:
            self.media_group.config(text=f"🎬 {tr('media', l) or 'Media'}")
        # Buttons
        if self.clear_btn is not None:
            clear_text = tr('clear', l) or tr('clear', 'en') or 'Clear'
            self.clear_btn.config(text=f"🧹 {clear_text}")
        if self.reset_btn is not None:
            reset_text = tr('reset', l) or tr('reset', 'en') or 'Reset'
            self.reset_btn.config(text=f"🔄 {reset_text}")
        if self.play_btn is not None:
            self.play_btn.config(text=tr('play', l) if not self.playing else tr('pause', l) or "")
        if self.add_frame_btn is not None:
            self.add_frame_btn.config(text=f"➕ {tr('add_frame', l) or ''}")
        if self.remove_frame_btn is not None:
            self.remove_frame_btn.config(text=f"➖ {tr('remove_frame', l) or 'Entfernen'}")
        if 'remove_frame_btn' in self.tooltips:
            self.tooltips['remove_frame_btn'].set_text(tr('tt_remove_frame_btn', l))
        # Effekte-Labels aktualisieren
        for prefix in ("gif", "texture"):
            panel = getattr(self, f"{prefix}_settings", None)
            if panel is not None:
                panel.config(text=f"⚙ {tr(f'{prefix}_settings', l) or ''}")
                children = panel.winfo_children()
                idx = 0
                # Graustufen-Checkbutton
                if idx < len(children) and isinstance(children[idx], ttk.Checkbutton):
                    children[idx].config(text=tr('effect_grayscale', l) or "")
                idx += 1
                # Schärfe-Frame (enthält Checkbutton und Slider)
                if idx < len(children):
                    sharpen_row = children[idx]
                    sharpen_btn = sharpen_row.winfo_children()[0]
                    if isinstance(sharpen_btn, ttk.Checkbutton):
                        sharpen_btn.config(text=tr('effect_sharpen', l) or "")
                idx += 1
                # Blur-Frame (enthält Checkbutton und Slider)
                if idx < len(children):
                    blur_row = children[idx]
                    blur_btn = blur_row.winfo_children()[0]
                    if isinstance(blur_btn, ttk.Checkbutton):
                        blur_btn.config(text=tr('effect_blur', l) or "")
                idx += 1
                # Transparenz-Frame (enthält Checkbutton und Slider)
                if idx < len(children):
                    transparency_row = children[idx]
                    transparency_btn = transparency_row.winfo_children()[0]
                    if isinstance(transparency_btn, ttk.Checkbutton):
                        transparency_btn.config(text=tr('effect_transparency', l) or "")
                idx += 1
                # Farbintensität-Frame (enthält Checkbutton und Slider)
                if idx < len(children):
                    colorint_row = children[idx]
                    colorint_btn = colorint_row.winfo_children()[0]
                    if isinstance(colorint_btn, ttk.Checkbutton):
                        colorint_btn.config(text=tr('effect_colorintensity', l) or "")
                        if self.bg_label is not None:
                            self.bg_label.config(text=f"🎨 {tr('bg_color', l) or 'Hintergrundfarbe:'}")
        # Neue Funktionen in Master Einstellungen
        if self.framerate_label is not None:
            self.framerate_label.config(text=f"⏱ {tr('framerate', l) or 'Framerate:'}")
        if self.export_format_label is not None:
            self.export_format_label.config(text=f"📤 {tr('export_format', l) or 'Exportformat:'}")
        if self.maxframes_label is not None:
            self.maxframes_label.config(text=f"🖼 {tr('max_images', l) or 'Max. Bilder:'}")
        
        # Menu Bar (Menüleiste oben) aktualisieren
        if hasattr(self, 'menubar') and self.menubar is not None:
            # Alte Menüleiste vollständig entfernen
            try:
                self.menubar.destroy()
            except:
                pass
            self.root.config(menu=None)
            # Wichtig: root.update() statt update_idletasks() um sicherzustellen,
            # dass das Menü vollständig entfernt wird
            self.root.update()
            # Neues Menü mit aktualisierter Sprache erstellen
            from gui_layout import create_menubar
            create_menubar(self)
            # Layout aktualisieren
            self.root.update_idletasks()


    def change_language(self, event=None):
        change_language(self, event)


    def load_gif(self):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_compat
        load_gif_compat(self)

    def load_texture(self):
        """Lädt eine Textur-Datei."""
        self._ensure_file_ops_methods()
        from file_ops import load_texture
        load_texture(self)

    def load_gif_from_clipboard(self, event=None):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_from_clipboard
        load_gif_from_clipboard(self)
        return "break"

    def load_gif_from_url(self):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_from_url
        load_gif_from_url(self)
    
    def _show_about_dialog(self):
        """Zeigt einen Über-Dialog mit Versionsinformationen."""
        l = self.lang
        about_text = f"""OSSL2Gif {Version}
© 2026 by Manfred Zainhofer

{tr('about_description', l)}

{tr('features', l)}
• {tr('about_feature1', l)}
• {tr('about_feature2', l)}
• {tr('about_feature3', l)}
• {tr('about_feature4', l)}
• {tr('about_feature5', l)}

Python {'.'.join(map(str, __import__('sys').version_info[:3]))}
        """
        messagebox.showinfo(tr('about', l), about_text)
    
    def _show_image_size_dialog(self):
        """Zeigt einen Dialog zur Eingabe der Bildgröße."""
        dialog = tk.Toplevel(self.root)
        dialog.title(tr('image_size', self.lang) or "Bildgröße")
        dialog.transient(self.root)
        dialog.configure(bg='#2d2d2d')
        
        # Aktuell Werte
        current_width = self.width_var.get()
        current_height = self.height_var.get()
        
        # Frame für Eingaben
        input_frame = ttk.Frame(dialog)
        input_frame.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)
        
        # Breite
        width_label = ttk.Label(input_frame, text=f"{tr('width', self.lang) or 'Breite'}:")
        width_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        width_entry = ttk.Entry(input_frame, width=10)
        width_entry.insert(0, str(current_width))
        width_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Höhe
        height_label = ttk.Label(input_frame, text=f"{tr('height', self.lang) or 'Höhe'}:")
        height_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        height_entry = ttk.Entry(input_frame, width=10)
        height_entry.insert(0, str(current_height))
        height_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Preset-Buttons
        preset_frame = ttk.Frame(input_frame)
        preset_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        presets = [256, 512, 768, 1024, 1280, 1536, 1792, 2048]
        for i, preset in enumerate(presets):
            btn = ttk.Button(preset_frame, text=str(preset), width=6,
                           command=lambda p=preset: (width_entry.delete(0, tk.END),
                                                    width_entry.insert(0, str(p)),
                                                    height_entry.delete(0, tk.END),
                                                    height_entry.insert(0, str(p))))
            btn.grid(row=i // 4, column=i % 4, padx=2, pady=2)
        
        # OK/Abbrechen Buttons
        def apply_size():
            try:
                w = int(width_entry.get())
                h = int(height_entry.get())
                if w > 0 and h > 0:
                    self.width_var.set(w)
                    self.height_var.set(h)
                    dialog.destroy()
                else:
                    msgtext = tr('valid_numbers', self.lang) or 'Breite und Höhe müssen positive Zahlen sein!'
                    messagebox.showerror(tr('error', self.lang) or 'Fehler', msgtext)
            except ValueError:
                msgtext = tr('invalid_input', self.lang) or 'Bitte gültige Zahlen eingeben!'
                messagebox.showerror(tr('error', self.lang) or 'Fehler', msgtext)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ok_btn = ttk.Button(button_frame, text=tr('ok', self.lang) or 'OK', command=apply_size)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text=tr('cancel', self.lang) or 'Abbrechen', command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Fenster an Inhalt anpassen und zentrieren
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        dialog.grab_set()
    
    def _show_framerate_dialog(self):
        """Zeigt einen Dialog zur Eingabe der Bildrate."""
        current = self.framerate_var.get()
        title = tr('framerate', self.lang) or "Bildrate"
        msg = f"{tr('framerate', self.lang) or 'Bildrate'} {tr('current', self.lang) or 'Aktuell'}: {current} FPS"
        result = simpledialog.askinteger(title, 
                                        f"{msg}\n\n1-10000:",
                                        initialvalue=current,
                                        minvalue=1,
                                        maxvalue=10000,
                                        parent=self.root)
        if result is not None:
            self.framerate_var.set(result)
    
    def _show_max_frames_dialog(self):
        """Zeigt einen Dialog zur Eingabe der maximalen Bildanzahl."""
        current = self.maxframes_var.get()
        title = tr('max_images', self.lang) or "Max. Bilder"
        msg = f"{title} - {tr('current', self.lang) or 'Aktuell'}: {current}"
        result = simpledialog.askinteger(title,
                                        f"{msg}\n\n1-1024:",
                                        initialvalue=current,
                                        minvalue=1,
                                        maxvalue=1024,
                                        parent=self.root)
        if result is not None:
            self.maxframes_var.set(result)
    
    def _show_background_dialog(self):
        """Zeigt einen Dialog zur Auswahl der Hintergrundfarbe und Transparenz."""
        dialog = tk.Toplevel(self.root)
        dialog.title(tr('bg_color', self.lang) or "Hintergrundfarbe")
        dialog.transient(self.root)
        dialog.configure(bg='#2d2d2d')
        
        # Aktueller Wert
        current_color = self.bg_box_color
        current_alpha = self.bg_transparency_var.get()
        
        # Frame für Vorschau
        preview_frame = ttk.Frame(dialog)
        preview_frame.pack(pady=20)
        
        preview_label = ttk.Label(preview_frame, text=f"{tr('preview', self.lang) or 'Vorschau'}:")
        preview_label.pack(side=tk.LEFT, padx=5)
        
        # Vorschau-Box
        from gui_layout import create_checkerboard_with_color
        alpha_val = int((100 - current_alpha) * 2.55)
        preview_photo = create_checkerboard_with_color(current_color, alpha=alpha_val, size=64, checker_size=8)
        preview_box = tk.Label(preview_frame, image=preview_photo, relief=tk.SUNKEN)
        preview_box.image = preview_photo  # type: ignore # Referenz halten
        preview_box.pack(side=tk.LEFT, padx=5)
        
        # Farbe wählen Button
        def choose_color():
            nonlocal current_color
            from tkinter import colorchooser
            color = colorchooser.askcolor(title=tr('bg_color', self.lang) or "Farbe wählen", initialcolor=current_color)
            if color[1]:
                current_color = color[1]
                # Vorschau aktualisieren
                alpha_val = int((100 - transparency_scale.get()) * 2.55)
                new_photo = create_checkerboard_with_color(current_color, alpha=alpha_val, size=64, checker_size=8)
                preview_box.config(image=new_photo)
                preview_box.image = new_photo  # type: ignore # Referenz halten
        
        color_btn = ttk.Button(dialog, text=f"🎨 {tr('choose_color', self.lang) or 'Farbe wählen'}", command=choose_color)
        color_btn.pack(pady=10)
        
        # Transparenz-Slider
        transparency_frame = ttk.Frame(dialog)
        transparency_frame.pack(pady=10, padx=20, fill=tk.X)
        
        transparency_label = ttk.Label(transparency_frame, text=f"{tr('bg_transparency', self.lang) or 'Transparenz'}:")
        transparency_label.pack(side=tk.LEFT, padx=5)
        
        transparency_scale = ttk.Scale(transparency_frame, from_=0, to=100, orient=tk.HORIZONTAL, value=current_alpha)
        transparency_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        transparency_value_label = ttk.Label(transparency_frame, text=f"{current_alpha}%", width=5)
        transparency_value_label.pack(side=tk.LEFT)
        
        def update_transparency(*args):
            val = int(transparency_scale.get())
            transparency_value_label.config(text=f"{val}%")
            # Vorschau aktualisieren
            alpha_val = int((100 - val) * 2.55)
            new_photo = create_checkerboard_with_color(current_color, alpha=alpha_val, size=64, checker_size=8)
            preview_box.config(image=new_photo)
            preview_box.image = new_photo  # type: ignore # Referenz halten
        
        transparency_scale.config(command=update_transparency)
        
        # OK/Abbrechen Buttons
        def apply_background():
            self.bg_box_color = current_color
            self.bg_transparency_var.set(int(transparency_scale.get()))
            # BG-Color mit Alpha setzen
            alpha_val = int((100 - transparency_scale.get()) * 2.55)
            self.bg_color = f"{current_color}{alpha_val:02X}"
            # Vorschau aktualisieren
            if hasattr(self, 'bg_color_box') and self.bg_color_box is not None:
                new_photo = create_checkerboard_with_color(current_color, alpha=alpha_val, size=32, checker_size=4)
                self.bg_color_photo = new_photo
                self.bg_color_box.config(image=new_photo)
            # Texture neu rendern wenn GIF geladen
            if hasattr(self, 'gif_image') and self.gif_image is not None:
                try:
                    from image_processing import show_texture
                    show_texture(self)
                except Exception as e:
                    logger.debug(f"Failed to update texture: {e}", exc_info=False)
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        ok_btn = ttk.Button(button_frame, text=tr('ok', self.lang) or 'OK', command=apply_background)
        ok_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text=tr('cancel', self.lang) or 'Abbrechen', command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)
        
        # Fenster an Inhalt anpassen und zentrieren
        dialog.update_idletasks()
        width = dialog.winfo_reqwidth()
        height = dialog.winfo_reqheight()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry(f'{width}x{height}+{x}+{y}')
        
        dialog.grab_set()
    
    def _change_language_menu(self, lang_code):
        """Ändert die Sprache über das Menü."""
        if self.lang_var is not None:
            self.lang_var.set(lang_code)
            change_language(self, None)
    
    def _change_theme_menu(self, theme_name):
        """Ändert das Theme über das Menü."""
        if THEME_AVAILABLE and tb is not None:
            try:
                if self.theme_var is not None:
                    self.theme_var.set(theme_name)
                tb.Style().theme_use(theme_name)
            except Exception as e:
                logger.error(f"Failed to change theme: {e}")
    
    def _change_export_format_menu(self, format_name):
        """Ändert das Exportformat über das Menü."""
        self.export_format_var.set(format_name)
    
    def _toggle_gif_preview(self):
        """Toggle GIF-Vorschau ein/aus."""
        if self.gif_preview_frame is not None:
            if self.show_gif_var.get():
                self.gif_preview_frame.pack(fill=tk.BOTH, expand=True)
            else:
                self.gif_preview_frame.pack_forget()
        self._adjust_window_size_to_content()
    
    def _toggle_texture_preview(self):
        """Toggle Textur-Vorschau ein/aus."""
        if self.texture_preview_frame is not None:
            if self.show_texture_var.get():
                self.texture_preview_frame.pack(fill=tk.BOTH, expand=True)
            else:
                self.texture_preview_frame.pack_forget()
        self._adjust_window_size_to_content()

    def _toggle_gif_settings(self):
        """Toggle GIF-Einstellungen ein/aus."""
        if self.gif_settings is not None:
            if self.show_gif_settings_var.get():
                self.gif_settings.pack(fill=tk.X, pady=10)
            else:
                self.gif_settings.pack_forget()
        self._adjust_window_size_to_content()

    def _toggle_texture_settings(self):
        """Toggle Textur-Einstellungen ein/aus."""
        if self.texture_settings is not None:
            if self.show_texture_settings_var.get():
                self.texture_settings.pack(fill=tk.X, pady=10)
            else:
                self.texture_settings.pack_forget()
        self._adjust_window_size_to_content()

    def _apply_view_preset(self, preset_name):
        """Wendet eine Schnellauswahl für die Sichtbarkeit von Gruppen an."""
        presets = {
            'standard': {
                'show_gif_var': True,
                'show_gif_settings_var': True,
                'show_texture_var': True,
                'show_texture_settings_var': True,
                'show_master_var': True,
                'show_media_var': True,
                'show_file_var': True,
                'show_status_var': True,
            },
            'media_player': {
                'show_gif_var': True,
                'show_gif_settings_var': False,
                'show_texture_var': False,
                'show_texture_settings_var': False,
                'show_master_var': False,
                'show_media_var': True,
                'show_file_var': False,
                'show_status_var': True,
            },
            'gif_edit': {
                'show_gif_var': True,
                'show_gif_settings_var': True,
                'show_texture_var': False,
                'show_texture_settings_var': False,
                'show_master_var': True,
                'show_media_var': True,
                'show_file_var': True,
                'show_status_var': True,
            },
            'texture_edit': {
                'show_gif_var': False,
                'show_gif_settings_var': False,
                'show_texture_var': True,
                'show_texture_settings_var': True,
                'show_master_var': True,
                'show_media_var': False,
                'show_file_var': True,
                'show_status_var': True,
            },
        }

        preset = presets.get(preset_name)
        if preset is None:
            return

        for var_name, is_visible in preset.items():
            var = getattr(self, var_name, None)
            if var is not None:
                var.set(is_visible)

        self._toggle_gif_preview()
        self._toggle_gif_settings()
        self._toggle_texture_preview()
        self._toggle_texture_settings()
        self._repack_groups()

    def _adjust_window_size_to_content(self):
        """Passt die Fenstergröße an den aktuellen Inhalt an."""
        self.root.update_idletasks()
        try:
            req_width = self.root.winfo_reqwidth()
            req_height = self.root.winfo_reqheight()

            min_width = 1300
            min_height = 450

            new_width = max(req_width, min_width)
            new_height = max(req_height, min_height)

            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            max_width = int(screen_width * 0.9)
            max_height = int(screen_height * 0.9)

            new_width = min(new_width, max_width)
            new_height = min(new_height, max_height)

            x = (screen_width // 2) - (new_width // 2)
            y = (screen_height // 2) - (new_height // 2)

            self.root.geometry(f'{new_width}x{new_height}+{x}+{y}')
        except Exception as e:
            logger.debug(f"Could not adjust window size: {e}", exc_info=False)
    
    def _repack_groups(self):
        """Packt alle Gruppen in der richtigen Reihenfolge neu."""
        # Erst alle entfernen
        if self.master_group is not None:
            self.master_group.pack_forget()
        if self.media_group is not None:
            self.media_group.pack_forget()
        if self.file_group is not None:
            self.file_group.pack_forget()
        if self.status_group is not None:
            self.status_group.pack_forget()
        
        # Dann in der richtigen Reihenfolge wieder einblenden (nur sichtbare)
        if self.master_group is not None and self.show_master_var.get():
            self.master_group.pack(fill=tk.X, padx=10, pady=(5,2))
        if self.media_group is not None and self.show_media_var.get():
            self.media_group.pack(fill=tk.X, padx=10, pady=(5,2))
        if self.file_group is not None and self.show_file_var.get():
            self.file_group.pack(fill=tk.X, padx=10, pady=(5,2))
        if self.status_group is not None and self.show_status_var.get():
            self.status_group.pack(fill=tk.X, padx=10, pady=(5,5))
        
        self._adjust_window_size_to_content()
    
    def _toggle_master_group(self):
        """Toggle Master-Einstellungen ein/aus."""
        self._repack_groups()
    
    def _toggle_media_group(self):
        """Toggle Media-Gruppe ein/aus."""
        self._repack_groups()
    
    def _toggle_file_group(self):
        """Toggle Datei-Gruppe ein/aus."""
        self._repack_groups()
    
    def _toggle_status_group(self):
        """Toggle Status-Gruppe ein/aus."""
        self._repack_groups()
    
    def show_texture_preview_window(self):
        """Zeigt Textur-Vorschau wie in OpenSim/Second Life."""
        from texture_preview import show_texture_preview
        show_texture_preview(self)


    def clear_texture(self):
        self.texture_image = None
        if self.texture_canvas is not None:
            self.texture_canvas.config(image="")
        self.gif_image = None
        self.gif_frames = []
        self.frame_count = 0
        self.current_frame = 0
        if self.gif_canvas is not None:
            self.gif_canvas.config(image="")
        self._gif_img_ref = None


    # Bildverarbeitungsfunktionen werden direkt aus image_processing.py importiert und verwendet


    def save_gif(self):
        save_gif(self)


    def save_texture(self):
        save_texture(self)


    def export_lsl(self):
        export_lsl(self)

    def generate_lsl_script(self, name, tiles_x, tiles_y, speed):
        return generate_lsl_script(self, name, tiles_x, tiles_y, speed)



