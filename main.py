###
# main.py
# This file contains the main application class ModernApp, which defines the GUI and core functionality of the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import math
import atexit
from config import load_config, save_config
from translations import tr
from gui_layout import build_layout, create_effects_panel
from image_processing import apply_effects, show_gif_frame, show_texture, update_previews
from file_ops import load_gif, save_gif, save_texture, export_lsl, generate_lsl_script
from events import reset_settings, change_language, on_maxframes_changed, add_selected_frame_to_texture, choose_bg_color

try:
    import ttkbootstrap as tb
    THEME_AVAILABLE = True
except ImportError:
    tb = None
    THEME_AVAILABLE = False
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
            0x816: 'pt'
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

    import logging
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
    logging.info(f"Tastaturlayout erkannt: {DEFAULT_KEYBOARD_LAYOUT}")
    logging.info(f"Systemsprache erkannt: {DEFAULT_LANGUAGE}")

LANGUAGES = ['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt']

class ModernApp:
    # Entfernt: Fehlerhafte Zeile außerhalb von Methoden

    def show_texture(self):
        # Kompatibilitäts-Wrapper, damit show_texture(self) immer funktioniert
        if hasattr(self, '_update_texture'):
            self._update_texture()

    # Borderless-Methoden an die Instanz binden
    def _ensure_borderless_methods(self):
        from image_processing import apply_borderless, remove_borderless
        self.apply_borderless = apply_borderless.__get__(self)
        self.remove_borderless = remove_borderless.__get__(self)

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
        # Sprache initial aus Combobox übernehmen, falls vorhanden, sonst Standard
        self.lang = 'de'
        self.lang_var = None
        self.gif_image = None
        self.gif_frames = []
        self.texture_image = None
        self.frame_count = 0
        self.current_frame = 0
        self.timer = None
        self.image_width = 2048
        self.image_height = 2048
        self.root.title("OSSL2Gif")
        self.root.geometry("1500x1300")
        
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
        self.width_entry = None
        self.width_var = tk.IntVar(value=2048)
        self.height_entry = None
        self.height_var = tk.IntVar(value=2048)
        self.load_btn = None
        self.remove_frame_btn = None  # Für Entfernen-Button (Frames)
        self.save_gif_btn = None
        self.save_texture_btn = None
        self.export_lsl_btn = None
        self.clear_btn = None
        self.size_label = None
        self.bg_label = None
        self.bg_color_box = None
        self.bg_color = '#000000'
        self.bg_box_color = '#000000'
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
        self.borderless_label = None
        self.borderless_var = tk.IntVar(value=0)
        self.borderless_chk = None
        self.export_format_label = None
        self.export_format_var = tk.StringVar(value='PNG')
        self.media_framerate_var = None  # Wird in gui_layout.py gesetzt
        self.media_framerate_label = None  # Für Media-Framerate-Label (Tooltip/Übersetzung)
        self.playing = False
        try:
            self.root.iconbitmap("icon.ico")
        except Exception:
            pass  # Icon laden ignorieren, falls Datei fehlt oder Fehler
        if THEME_AVAILABLE and tb is not None:
            tb.Style("superhero")
        self.tooltips = {}
        # Konfiguration laden (vor build_layout, damit Werte übernommen werden)
        self._config_loaded = False
        config = load_config()
        self._ensure_borderless_methods()
        self.build_layout()
        if config:
            self.apply_config(config)
            self._config_loaded = True
        # Nach build_layout ist self.lang_var gesetzt
        if hasattr(self, 'lang_var') and self.lang_var is not None:
            self.lang = self.lang_var.get()
        self.update_language()
        # Beim Beenden speichern
        atexit.register(self.save_config)
        
        # --- Event-Bindings zentral setzen ---
        # Entfernen-Button für Frames verbinden
        if hasattr(self, 'remove_frame_btn') and self.remove_frame_btn is not None:
            from events import remove_selected_frame_from_texture
            self.remove_frame_btn.config(command=lambda: remove_selected_frame_from_texture(self))
        # Effekte-Panel (GIF)
        if self.gif_settings is not None and hasattr(self.gif_settings, 'grayscale_check'):
            self.gif_settings.grayscale_check.config(command=lambda: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'sharpen_check'):
            self.gif_settings.sharpen_check.config(command=lambda: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'sharpen_scale'):
            self.gif_settings.sharpen_scale.config(command=lambda e: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'blur_check'):
            self.gif_settings.blur_check.config(command=lambda: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'blur_scale'):
            self.gif_settings.blur_scale.config(command=lambda e: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'transparency_check'):
            self.gif_settings.transparency_check.config(command=lambda: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'transparency_scale'):
            self.gif_settings.transparency_scale.config(command=lambda e: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'colorint_check'):
            self.gif_settings.colorint_check.config(command=lambda: update_previews(self))
        if self.gif_settings is not None and hasattr(self.gif_settings, 'colorint_scale'):
            self.gif_settings.colorint_scale.config(command=lambda e: update_previews(self))

        # Effekte-Panel (Textur)
        if self.texture_settings is not None and hasattr(self.texture_settings, 'grayscale_check'):
            self.texture_settings.grayscale_check.config(command=lambda: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'sharpen_check'):
            self.texture_settings.sharpen_check.config(command=lambda: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'sharpen_scale'):
            self.texture_settings.sharpen_scale.config(command=lambda e: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'blur_check'):
            self.texture_settings.blur_check.config(command=lambda: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'blur_scale'):
            self.texture_settings.blur_scale.config(command=lambda e: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'transparency_check'):
            self.texture_settings.transparency_check.config(command=lambda: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'transparency_scale'):
            self.texture_settings.transparency_scale.config(command=lambda e: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'colorint_check'):
            self.texture_settings.colorint_check.config(command=lambda: update_previews(self))
        if self.texture_settings is not None and hasattr(self.texture_settings, 'colorint_scale'):
            self.texture_settings.colorint_scale.config(command=lambda e: update_previews(self))

        # Bildgröße-Eingaben
        if self.width_entry is not None:
            self.width_entry.bind('<FocusOut>', lambda e: update_previews(self))
        if self.height_entry is not None:
            self.height_entry.bind('<FocusOut>', lambda e: update_previews(self))

        # Maxframes
        if self.maxframes_spin is not None:
            self.maxframes_spin.bind('<FocusOut>', lambda e: on_maxframes_changed(self))
        self.maxframes_var.trace_add('write', lambda *args: on_maxframes_changed(self))

        # Hintergrundfarbe
        if self.bg_color_box is not None:
            self.bg_color_box.bind('<Button-1>', lambda e: choose_bg_color(self, e))

        # Randlos
        self.borderless_var.trace_add('write', lambda *args: update_previews(self))
        if self.borderless_chk is not None:
            self.borderless_chk.config(command=lambda: update_previews(self))

        # Bild hinzufügen
        if self.add_frame_btn is not None:
            self.add_frame_btn.config(command=lambda: add_selected_frame_to_texture(self))

        # Sprache
        if self.lang_combo is not None:
            self.lang_combo.bind('<<ComboboxSelected>>', lambda e: change_language(self, e))

        # Reset
        if self.reset_btn is not None:
            self.reset_btn.config(command=lambda: reset_settings(self))

    def get_config(self):
        # Alle relevanten Einstellungen als dict zurückgeben
        return {
            'lang': self.lang,
            'width': self.width_var.get() if hasattr(self, 'width_var') and self.width_var is not None else 2048,
            'height': self.height_var.get() if hasattr(self, 'height_var') and self.height_var is not None else 2048,
            'bg_color': getattr(self, 'bg_color', '#00000000'),
            'borderless': self.borderless_var.get() if hasattr(self, 'borderless_var') and self.borderless_var is not None else 0,
            'framerate': self.framerate_var.get() if hasattr(self, 'framerate_var') and self.framerate_var is not None else 10,
            'export_format': self.export_format_var.get() if hasattr(self, 'export_format_var') and self.export_format_var is not None else 'PNG',
            'maxframes': self.maxframes_var.get() if hasattr(self, 'maxframes_var') and self.maxframes_var is not None else 64
        }

    def save_config(self):
        save_config(self.get_config())

    def apply_config(self, config):
        # Werte aus config dict auf GUI anwenden
        if 'lang' in config and self.lang_var is not None:
            self.lang_var.set(config['lang'])
            self.lang = config['lang']
        if 'width' in config:
            self.width_var.set(config['width'])
        if 'height' in config:
            self.height_var.set(config['height'])
        if 'bg_color' in config and self.bg_color_box is not None:
            color = config['bg_color']
            # Prüfe, ob die Farbe gültig ist (Tkinter akzeptiert keine 8-stelligen Hexwerte)
            if isinstance(color, str) and (len(color) == 7 or (len(color) == 9 and color.endswith('00'))):
                # Falls 8-stellig, entferne Alpha
                if len(color) == 9:
                    color = color[:7]
            else:
                color = '#000000'
            self.bg_color = color
            self.bg_box_color = color
            self.bg_color_box.config(bg=self.bg_box_color)
        if 'borderless' in config:
            self.borderless_var.set(config['borderless'])
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
        show_gif_frame(self)
        # Media-Play-Geschwindigkeit: Slider aus Media-Bereich bevorzugen
        delay = 100
        if hasattr(self, 'media_framerate_var') and self.media_framerate_var is not None:
            delay = self.media_framerate_var.get()
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
        show_gif_frame(self)
        # Play/Pause-Button immer auf "Abspielen" (Play) setzen, auch sprachabhängig
        if self.play_btn is not None:
            self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

    def step_forward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame + 1) % self.frame_count
        show_gif_frame(self)

    def step_backward(self):
        if not self.gif_frames:
            return
        self.current_frame = (self.current_frame - 1) % self.frame_count
        show_gif_frame(self)



    def create_effects_panel(self, parent, prefix):
        return create_effects_panel(self, parent, prefix)


    def update_language(self):
        l = self.lang
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
            'media_framerate_label': 'tt_media_framerate_label',
            'prev_btn': 'tt_prev_btn',
            'pause_btn': 'tt_pause_btn',
            'play_btn': 'tt_play_btn',
            'stop_btn': 'tt_stop_btn',
            'next_btn': 'tt_next_btn',
            'borderless_label': 'tt_borderless',
            'export_format_label': 'tt_export_format_label',
        }
        for k, v in tooltip_keys.items():
            if k in self.tooltips:
                self.tooltips[k].set_text(tr(v, l))
        # Media-Framerate-Label und Tooltip übersetzen
        if hasattr(self, 'media_framerate_label') and self.media_framerate_label is not None:
            self.media_framerate_label.config(text=tr('framerate', l) or "Framerate:")
        if 'media_framerate_label' in self.tooltips:
            self.tooltips['media_framerate_label'].set_text(tr('tt_media_framerate_label', l))
        # Label für Randlos explizit übersetzen
        if hasattr(self, 'borderless_label') and self.borderless_label is not None:
            self.borderless_label.config(text=tr('borderless', l) or "Randlos")
        if self.gif_label is not None:
            self.gif_label.config(text=tr('gif_preview', l) or "")
        if self.gif_settings is not None:
            self.gif_settings.config(text=tr('gif_settings', l) or "")
        if self.texture_label is not None:
            self.texture_label.config(text=tr('texture_preview', l) or "")
        if self.texture_settings is not None:
            self.texture_settings.config(text=tr('texture_settings', l) or "")
        if self.size_label is not None:
            self.size_label.config(text=tr('image_size', l) or "")
        if self.lang_label is not None:
            self.lang_label.config(text=tr('language', l) or "")
        if self.load_btn is not None:
            self.load_btn.config(text=tr('load_gif', l) or "")
        if self.save_gif_btn is not None:
            self.save_gif_btn.config(text=tr('save_gif', l) or "")
        if self.save_texture_btn is not None:
            self.save_texture_btn.config(text=tr('save_texture', l) or "")
        if self.export_lsl_btn is not None:
            self.export_lsl_btn.config(text=tr('export_lsl', l) or "")
        if self.status is not None:
            self.status.config(text=tr('ready', l) or "")
        # Gruppenüberschriften
        if self.master_group is not None:
            self.master_group.config(text=tr('master_settings', l) or "")
        if self.file_group is not None:
            self.file_group.config(text=tr('file', l) or "")
        if self.status_group is not None:
            self.status_group.config(text=tr('status', l) or "")
        if self.media_group is not None:
            self.media_group.config(text=tr('media', l) or "Media")
        # Buttons
        if self.clear_btn is not None:
            self.clear_btn.config(text=tr('clear', l) or "")
        if self.borderless_chk is not None:
            #self.borderless_chk.config(text=tr('borderless', l) or "")
            self.borderless_chk.config(text="")
        if self.play_btn is not None:
            self.play_btn.config(text=tr('play', l) if not self.playing else tr('pause', l) or "")
        if self.add_frame_btn is not None:
            self.add_frame_btn.config(text=tr('add_frame', l) or "")
        if self.remove_frame_btn is not None:
            self.remove_frame_btn.config(text=tr('remove_frame', l) or "Entfernen")
        if 'remove_frame_btn' in self.tooltips:
            self.tooltips['remove_frame_btn'].set_text(tr('tt_remove_frame_btn', l))
        # Effekte-Labels aktualisieren
        for prefix in ("gif", "texture"):
            panel = getattr(self, f"{prefix}_settings", None)
            if panel is not None:
                panel.config(text=tr(f'{prefix}_settings', l) or "")
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
                            self.bg_label.config(text=tr('bg_color', l) or "Hintergrundfarbe:")
        # Neue Funktionen in Master Einstellungen
        if self.framerate_label is not None:
            self.framerate_label.config(text=tr('framerate', l) or "Framerate:")
        if self.export_format_label is not None:
            self.export_format_label.config(text=tr('export_format', l) or "Exportformat:", bg="#FFB3A7", fg="black", height=1)
        if self.maxframes_label is not None:
            self.maxframes_label.config(text=tr('max_images', l) or "Max. Bilder:")


    def change_language(self, event=None):
        change_language(self, event)


    def load_gif(self):
        self._ensure_file_ops_methods()
        from file_ops import load_gif_compat
        load_gif_compat(self)


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



