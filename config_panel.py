###
# config_panel.py
# Configuration GUI panel for OSSL2Gif settings
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Optional, Dict
from config_manager import get_config, ConfigManager
from translations import tr
from logging_config import get_logger
from event_bus import get_event_bus, EventType

logger = get_logger(__name__)

class ConfigPanel:
	"""
	GUI Panel zum Ändern aller Anwendungseinstellungen.
	Wird als Modal Dialog angezeigt.
	"""
	
	def __init__(self, parent_app: Any):
		"""
		Args:
			parent_app: Referenz zur ModernApp Instanz
		"""
		self.parent_app = parent_app
		self.config = get_config()
		self.event_bus = get_event_bus()
		self.lang = parent_app.lang if hasattr(parent_app, 'lang') else 'de'
		
		# Dialog nicht noch erstellt
		self.window: Optional[tk.Toplevel] = None
		self.widgets: Dict[str, Any] = {}
	
	def show(self) -> None:
		"""Öffnet den Config Dialog"""
		if self.window is not None and self.window.winfo_exists():
			self.window.lift()
			self.window.focus()
			return
		
		# Toplevel Window erstellen
		self.window = tk.Toplevel(self.parent_app.root)
		self.window.title("OSSL2Gif Einstellungen" if self.lang == 'de' else "OSSL2Gif Settings")
		self.window.geometry("500x600")
		self.window.resizable(False, False)
		
		# Main Frame mit Scrolling
		main_frame = ttk.Frame(self.window)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		
		# Config Sections
		self._create_image_settings(main_frame)
		self._create_effect_settings(main_frame)
		self._create_ui_settings(main_frame)
		self._create_system_settings(main_frame)
		
		# Buttons
		button_frame = ttk.Frame(main_frame)
		button_frame.pack(fill=tk.X, pady=(10, 0))
		
		save_btn = ttk.Button(button_frame, text="Speichern" if self.lang == 'de' else "Save", command=self.save)
		save_btn.pack(side=tk.LEFT, padx=5)
		
		reset_btn = ttk.Button(button_frame, text="Zurücksetzen" if self.lang == 'de' else "Reset", command=self.reset_to_defaults)
		reset_btn.pack(side=tk.LEFT, padx=5)
		
		close_btn = ttk.Button(button_frame, text="Schließen" if self.lang == 'de' else "Close", command=self.window.destroy)
		close_btn.pack(side=tk.RIGHT, padx=5)
	
	def _create_image_settings(self, parent: ttk.Frame) -> None:
		"""Bildgröße und Frame-Einstellungen"""
		group = ttk.LabelFrame(parent, text="Bildeinstellungen" if self.lang == 'de' else "Image Settings", padding=10)
		group.pack(fill=tk.X, pady=5)
		
		# Texturgröße
		ttk.Label(group, text="Texturgröße:" if self.lang == 'de' else "Texture Size:").grid(row=0, column=0, sticky=tk.W)
		
		size_frame = ttk.Frame(group)
		size_frame.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
		
		size_var = tk.StringVar(value=str(self.config.get('texture_width')))
		self.widgets['texture_width'] = size_var
		
		ttk.Spinbox(size_frame, from_=256, to=8192, textvariable=size_var, width=10).pack(side=tk.LEFT)
		ttk.Label(size_frame, text="px").pack(side=tk.LEFT, padx=5)
		
		# Max Frames
		ttk.Label(group, text="Max Frames:" if self.lang == 'de' else "Max Frames:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
		max_frames_var = tk.IntVar(value=self.config.get('max_frames'))
		self.widgets['max_frames'] = max_frames_var
		ttk.Spinbox(group, from_=1, to=256, textvariable=max_frames_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
		
		# Framerate
		ttk.Label(group, text="Framerate:" if self.lang == 'de' else "Framerate:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
		framerate_var = tk.IntVar(value=self.config.get('default_framerate'))
		self.widgets['framerate'] = framerate_var
		ttk.Spinbox(group, from_=1, to=60, textvariable=framerate_var, width=10).grid(row=2, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
	
	def _create_effect_settings(self, parent: ttk.Frame) -> None:
		"""Effekt-Defaults"""
		group = ttk.LabelFrame(parent, text="Effekt-Defaults" if self.lang == 'de' else "Effect Defaults", padding=10)
		group.pack(fill=tk.X, pady=5)
		
		# Schärfe
		ttk.Label(group, text="Schärfe Standard:" if self.lang == 'de' else "Sharpen Default:").grid(row=0, column=0, sticky=tk.W)
		sharpen_var = tk.DoubleVar(value=self.config.get('effect_sharpen_default'))
		self.widgets['sharpen'] = sharpen_var
		ttk.Scale(group, from_=0, to=10, orient=tk.HORIZONTAL, variable=sharpen_var).grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
		ttk.Label(group, textvariable=sharpen_var, width=5).grid(row=0, column=2, padx=5)
		
		# Blur
		ttk.Label(group, text="Blur Standard:" if self.lang == 'de' else "Blur Default:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
		blur_var = tk.DoubleVar(value=self.config.get('effect_blur_default'))
		self.widgets['blur'] = blur_var
		ttk.Scale(group, from_=0, to=10, orient=tk.HORIZONTAL, variable=blur_var).grid(row=1, column=1, sticky=tk.EW, padx=(5, 0), pady=(5, 0))
		ttk.Label(group, textvariable=blur_var, width=5).grid(row=1, column=2, padx=5, pady=(5, 0))
		
		# Transparenz
		ttk.Label(group, text="Transparenz Standard:" if self.lang == 'de' else "Transparency Default:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
		transparency_var = tk.DoubleVar(value=self.config.get('effect_transparency_default'))
		self.widgets['transparency'] = transparency_var
		ttk.Scale(group, from_=0, to=1, orient=tk.HORIZONTAL, variable=transparency_var).grid(row=2, column=1, sticky=tk.EW, padx=(5, 0), pady=(5, 0))
		ttk.Label(group, textvariable=transparency_var, width=5).grid(row=2, column=2, padx=5, pady=(5, 0))
	
	def _create_ui_settings(self, parent: ttk.Frame) -> None:
		"""UI und Sprache"""
		group = ttk.LabelFrame(parent, text="UI Einstellungen" if self.lang == 'de' else "UI Settings", padding=10)
		group.pack(fill=tk.X, pady=5)
		
		# Sprache
		ttk.Label(group, text="Sprache:" if self.lang == 'de' else "Language:").grid(row=0, column=0, sticky=tk.W)
		
		lang_var = tk.StringVar(value=self.config.get('language'))
		self.widgets['language'] = lang_var
		
		lang_combo = ttk.Combobox(
			group,
			textvariable=lang_var,
			values=self.config.get('supported_languages'),
			state='readonly',
			width=20
		)
		lang_combo.grid(row=0, column=1, sticky=tk.EW, padx=(5, 0))
		
		# Window Size (Info only)
		ttk.Label(group, text="Fenster-Größe:" if self.lang == 'de' else "Window Size:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
		
		window_size = self.config.get('window_width'), self.config.get('window_height')
		ttk.Label(group, text=f"{window_size[0]}x{window_size[1]}").grid(row=1, column=1, sticky=tk.W, padx=(5, 0), pady=(5, 0))
	
	def _create_system_settings(self, parent: ttk.Frame) -> None:
		"""System und Logging"""
		group = ttk.LabelFrame(parent, text="System" if self.lang == 'de' else "System", padding=10)
		group.pack(fill=tk.X, pady=5)
		
		# Version
		version = self.config.get('version')
		ttk.Label(group, text=f"OSSL2Gif Version: {version}").pack(anchor=tk.W)
		
		# Debug Logging
		debug_var = tk.BooleanVar(value=self.config.get('enable_debug_logging'))
		self.widgets['debug_logging'] = debug_var
		
		ttk.Checkbutton(group, text="Debug Logging aktivieren" if self.lang == 'de' else "Enable Debug Logging", variable=debug_var).pack(anchor=tk.W, pady=(5, 0))
		
		# Log Level
		ttk.Label(group, text="Log Level:" if self.lang == 'de' else "Log Level:").pack(anchor=tk.W, pady=(5, 0))
		
		log_level_var = tk.StringVar(value=self.config.get('log_level'))
		self.widgets['log_level'] = log_level_var
		
		log_level_combo = ttk.Combobox(
			group,
			textvariable=log_level_var,
			values=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
			state='readonly',
			width=20
		)
		log_level_combo.pack(anchor=tk.W, padx=(5, 0), pady=(5, 0))
	
	def save(self) -> None:
		"""Speichert die Einstellungen"""
		try:
			# Neue Werte in Config schreiben
			for key, widget in self.widgets.items():
				if isinstance(widget, tk.Variable):
					value = widget.get()
					
					# Type conversion
					if key in ['texture_width', 'max_frames', 'framerate']:
						value = int(value)
					elif key in ['sharpen', 'blur', 'transparency']:
						value = float(value)
					
					self.config.set(key, value)
			
			# Config speichern
			self.config.save_to_file()
			
			# Event publishen
			self.event_bus.publish(
				EventType.SETTINGS_CHANGED,
				data={'changed_keys': list(self.widgets.keys())},
				source='config_panel'
			)
			
			messagebox.showinfo(
				"Erfolg" if self.lang == 'de' else "Success",
				"Einstellungen gespeichert" if self.lang == 'de' else "Settings saved"
			)
			
			logger.info("Configuration saved from settings panel")
		except Exception as e:
			logger.error(f"Error saving config: {type(e).__name__}: {e}", exc_info=True)
			messagebox.showerror(
				"Fehler" if self.lang == 'de' else "Error",
				f"Fehler beim Speichern: {e}" if self.lang == 'de' else f"Error saving: {e}"
			)
	
	def reset_to_defaults(self) -> None:
		"""Setzt alle Werte auf Defaults zurück"""
		if messagebox.askyesno(
			"Bestätigung" if self.lang == 'de' else "Confirm",
			"Alle Einstellungen zurücksetzen?" if self.lang == 'de' else "Reset all settings to defaults?"
		):
			self.config.reset_to_defaults()
			self._reload_window()

	def _reload_window(self) -> None:
		"""Lädt das Fenster neu mit aktuellen Werten"""
		if self.window is not None:
			self.window.destroy()
		self.show()
