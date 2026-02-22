###
# config_manager.py
# Centralized configuration management for OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Any, Dict, Optional
import json
import os
import sys
import logging

logger = logging.getLogger(__name__)

class ConfigValue:
	"""Wrapper für Config-Werte mit Validierung"""
	def __init__(self, name: str, default: Any, value_type: type, min_val: Optional[Any] = None, max_val: Optional[Any] = None):
		self.name = name
		self.default = default
		self.value_type = value_type
		self.min_val = min_val
		self.max_val = max_val
		self.value = default
	
	def validate(self, value: Any) -> bool:
		"""Validiert einen Wert bevor er gespeichert wird"""
		try:
			if not isinstance(value, self.value_type):
				return False
			if self.min_val is not None and value < self.min_val:
				return False
			if self.max_val is not None and value > self.max_val:
				return False
			return True
		except (TypeError, ValueError):
			return False
	
	def set(self, value: Any) -> bool:
		"""Setzt Wert nach Validierung"""
		if self.validate(value):
			self.value = value
			return True
		logger.warning(f"Invalid value for {self.name}: {value} (expected {self.value_type.__name__})")
		return False
	
	def get(self) -> Any:
		"""Gibt aktuellen Wert oder Default zurück"""
		return self.value

class ConfigManager:
	"""
	Zentrale Konfigurationsverwaltung für OSSL2Gif.
	Verwaltet alle Magic Numbers, Defaults und Anwendungseinstellungen.
	"""
	
	# === HARD-CODED CONFIGURATION (Application Constants) ===
	# Format: (default_value, type, min, max)
	CONFIG_SCHEMA = {
		# Bildgröße und Layout
		'texture_width': (2048, int, 256, 8192),
		'texture_height': (2048, int, 256, 8192),
		'width': (2048, int, 256, 8192),  # Alias für texture_width
		'height': (2048, int, 256, 8192),  # Alias für texture_height
		
		# Frame-Management
		'max_frames': (64, int, 1, 256),
		'default_framerate': (10, int, 1, 60),
		'framerate': (10, int, 1, 60),  # Alias für default_framerate
		'maxframes': (64, int, 1, 256),  # Alias für max_frames
		
		# Effekte - Standardwerte
		'effect_sharpen_default': (2.5, float, 0.0, 10.0),
		'effect_blur_default': (3.5, float, 0.0, 10.0),
		'effect_transparency_default': (0.5, float, 0.0, 1.0),
		'effect_colorintensity_default': (0.5, float, 0.0, 1.0),
		
		# UI - Window-Geometrie
		'window_width': (1500, int, 800, 2048),
		'window_height': (1550, int, 600, 2048),
		'window_geometry': ('', str, None, None),  # Format: "WxH+X+Y" (z.B. "1200x800+100+50")
		'checkerboard_size': (32, int, 8, 64),
		'checkerboard_checker_size': (4, int, 2, 16),
		
		# Sprache und Farbe
		'language': ('de', str, None, None),
		'lang': ('de', str, None, None),  # Alias für language
		'supported_languages': (['de', 'en', 'fr', 'es', 'it', 'ru', 'nl', 'se', 'pl', 'pt', 'uk', 'ja', 'zh'], list, None, None),
		'bg_color': ('#00000000', str, None, None),  # Hintergrundfarbe
		'theme': (None, str, None, None),  # UI-Theme
		
		# Gruppen-Sichtbarkeit
		'show_gif_preview': (True, bool, None, None),
		'show_gif_settings': (True, bool, None, None),
		'show_texture_preview': (True, bool, None, None),
		'show_texture_settings': (True, bool, None, None),
		'show_master_settings': (True, bool, None, None),
		'show_media': (True, bool, None, None),
		'show_file': (True, bool, None, None),
		'show_status': (True, bool, None, None),
		
		# Export
		'default_export_format': ('PNG', str, None, None),
		'export_format': ('PNG', str, None, None),  # Alias für default_export_format
		'supported_export_formats': (['PNG', 'DDS', 'JPG', 'BMP'], list, None, None),
		
		# System
		'version': ('2.0.8', str, None, None),
		'log_level': ('INFO', str, None, None),
		'enable_debug_logging': (False, bool, None, None),
	}
	def __init__(self):
		"""Initialisiert den ConfigManager mit Standard-Werten"""
		self._values: Dict[str, ConfigValue] = {}
		self._config_file = self._get_config_file_path()
		self._init_schema()
		self.load_from_file()
	
	def _init_schema(self) -> None:
		"""Initialisiert alle Config-Werte aus dem Schema"""
		for key, (default, val_type, min_val, max_val) in self.CONFIG_SCHEMA.items():
			self._values[key] = ConfigValue(key, default, val_type, min_val, max_val)
	
	def _get_config_file_path(self) -> str:
		"""Bestimmt den Pfad zur config.json"""
		if getattr(sys, 'frozen', False):
			# Im PyInstaller-Bundle: Schreibe config.json ins aktuelle Arbeitsverzeichnis
			return os.path.join(os.getcwd(), 'config.json')
		else:
			# Im normalen Python: Schreibe ins Quellverzeichnis
			return os.path.join(os.path.dirname(__file__), 'config.json')
	
	def get(self, key: str, default: Optional[Any] = None) -> Any:
		"""
		Gibt einen Config-Wert zurück.
		
		Args:
			key: Konfigurationsschlüssel
			default: Fallback-Wert falls Schlüssel nicht existiert
		
		Returns:
			Konfigurationswert oder default
		"""
		if key in self._values:
			return self._values[key].get()
		elif key in self.CONFIG_SCHEMA:
			return self.CONFIG_SCHEMA[key][0]
		else:
			logger.warning(f"Unknown config key: {key}")
			return default
	
	def set(self, key: str, value: Any) -> bool:
		"""
		Setzt einen Config-Wert nach Validierung.
		
		Args:
			key: Konfigurationsschlüssel
			value: Zu setzender Wert
		
		Returns:
			True wenn erfolgreich, sonst False
		"""
		if key in self._values:
			return self._values[key].set(value)
		else:
			logger.warning(f"Unknown config key: {key}")
			return False
	
	def to_dict(self) -> Dict[str, Any]:
		"""Konvertiert alle Config-Werte zu Dictionary"""
		return {key: val.get() for key, val in self._values.items()}
	
	def load_from_file(self) -> bool:
		"""
		Lädt Konfiguration aus JSON-Datei.
		
		Returns:
			True wenn erfolgreich, sonst False
		"""
		if not os.path.exists(self._config_file):
			logger.debug(f"Config file not found: {self._config_file}")
			return False
		
		try:
			with open(self._config_file, 'r', encoding='utf-8') as f:
				data = json.load(f)
			
			for key, value in data.items():
				self.set(key, value)
			
			logger.info(f"Configuration loaded from {self._config_file}")
			return True
		except json.JSONDecodeError as e:
			logger.error(f"Invalid JSON in config file: {e}", exc_info=False)
			return False
		except Exception as e:
			logger.error(f"Error loading config file: {type(e).__name__}: {e}", exc_info=False)
			return False
	
	def save_to_file(self) -> bool:
		"""
		Speichert Konfiguration in JSON-Datei.
		
		Returns:
			True wenn erfolgreich, sonst False
		"""
		try:
			with open(self._config_file, 'w', encoding='utf-8') as f:
				json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
			
			logger.info(f"Configuration saved to {self._config_file}")
			return True
		except Exception as e:
			logger.error(f"Error saving config file: {type(e).__name__}: {e}", exc_info=False)
			return False
	
	def reset_to_defaults(self) -> None:
		"""Setzt alle Werte auf ihre Defaults zurück"""
		for key, config_value in self._values.items():
			config_value.value = config_value.default
		logger.info("Configuration reset to defaults")
	
	# === Convenience Properties ===
	@property
	def texture_size(self) -> tuple[int, int]:
		"""Gibt (width, height) der Texture zurück"""
		return (self.get('texture_width'), self.get('texture_height'))
	
	@property
	def window_size(self) -> str:
		"""Gibt Window-Größe als "WxH" String zurück (für tkinter)"""
		w = self.get('window_width')
		h = self.get('window_height')
		return f"{w}x{h}"
	
	@property
	def effect_defaults(self) -> Dict[str, float]:
		"""Gibt alle Effekt-Defaults als Dictionary zurück"""
		return {
			'sharpen': self.get('effect_sharpen_default'),
			'blur': self.get('effect_blur_default'),
			'transparency': self.get('effect_transparency_default'),
			'colorintensity': self.get('effect_colorintensity_default'),
		}

# Global singleton instance
_config_instance: Optional[ConfigManager] = None

def get_config() -> ConfigManager:
	"""Gibt die globale ConfigManager-Instanz zurück"""
	global _config_instance
	if _config_instance is None:
		_config_instance = ConfigManager()
	return _config_instance

def reset_config() -> None:
	"""Setzt die globale ConfigManager-Instanz zurück (für Tests)"""
	global _config_instance
	_config_instance = None
