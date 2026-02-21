###
# main.py
# This file contains the main application class ModernApp, which defines the GUI and core functionality of the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import math
import atexit
import logging
from typing import Optional, List, Any
from config import load_config, save_config
from translations import tr
from gui_layout import build_layout, create_effects_panel
from image_processing import apply_effects, show_gif_frame, show_texture
from file_ops import load_gif, save_gif, save_texture, export_lsl, generate_lsl_script
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
Version = "2.0.15"
WindowsSize  = "1650x1550"

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
        self._ensure_file_ops_methods()
        from image_processing import show_gif_frame
        self.show_gif_frame = show_gif_frame.__get__(self)
        # Sprache initial aus Combobox übernehmen, falls vorhanden, sonst Standard
        self.lang: str = 'de'
        self.lang_var: Optional[tk.StringVar] = None
        self.gif_image: Optional[Image.Image] = None
        self.gif_frames: List[Image.Image] = []
        self.texture_image: Optional[Image.Image] = None
        self.frame_count: int = 0
        self.current_frame: int = 0
        self.timer: Optional[Any] = None
        self.image_width: int = 2048
        self.image_height: int = 2048
        # PhotoImage-Referenzen (müssen behalten werden, sonst Garbage Collection)
        self._gif_img_ref: Optional[Any] = None
        self._texture_img_ref: Optional[Any] = None
        self.root.title(f"OSSL2Gif {Version}")
        self.root.geometry(WindowsSize)

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
        self.playing = False
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
        self.build_layout()
        if config:
            self.apply_config(config)
            self._config_loaded = True
        # Nach build_layout ist self.lang_var gesetzt
        if hasattr(self, 'lang_var') and self.lang_var is not None:
            self.lang = self.lang_var.get()
        self.update_language()
        self._setup_drag_and_drop()
        # Bindings für Effekte-Panels IMMER setzen
        self._bind_effects_panel_events()
        # Beim Beenden speichern
        atexit.register(self.save_config)

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
        return {
            'lang': self.lang,
            'width': self.width_var.get() if hasattr(self, 'width_var') and self.width_var is not None else 2048,
            'height': self.height_var.get() if hasattr(self, 'height_var') and self.height_var is not None else 2048,
            'bg_color': getattr(self, 'bg_color', '#00000000'),
            'framerate': self.framerate_var.get() if hasattr(self, 'framerate_var') and self.framerate_var is not None else 10,
            'export_format': self.export_format_var.get() if hasattr(self, 'export_format_var') and self.export_format_var is not None else 'PNG',
            'maxframes': self.maxframes_var.get() if hasattr(self, 'maxframes_var') and self.maxframes_var is not None else 64,
            'theme': self.theme_var.get() if hasattr(self, 'theme_var') and self.theme_var is not None else None
        }

    def save_config(self):
        save_config(self)

    def apply_config(self, config):
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
        if 'lang' in config and self.lang_var is not None:
            self.lang_var.set(config['lang'])
            self.lang = config['lang']
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
        # Nach dem Anwenden der Config: Effekt-Panel-Bindings erneut setzen
        self._bind_effects_panel_events()

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


    def change_language(self, event=None):
        change_language(self, event)


    def load_gif(self):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_compat
        load_gif_compat(self)

    def load_gif_from_clipboard(self, event=None):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_from_clipboard
        load_gif_from_clipboard(self)
        return "break"

    def load_gif_from_url(self):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_from_url
        load_gif_from_url(self)


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



