###
# start.py
# This file serves as the entry point for the application. It initializes the main window and starts the application.
# OSSL2Gif OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###
import tkinter as tk
import logging
import platform
try:
	import ttkbootstrap as tb
	THEME_AVAILABLE = True
except ImportError:
	tb = None
	THEME_AVAILABLE = False
try:
	from tkinterdnd2 import TkinterDnD
	DND_AVAILABLE = True
except ImportError:
	TkinterDnD = None
	DND_AVAILABLE = False
from logging_config import setup_logging
from app_bootstrap import bootstrap_services, shutdown_services
from main import ModernApp

def _enable_windows_dpi_awareness() -> float:
	"""Ermittelt den DPI-Skalierungsfaktor plattformübergreifend (Windows/macOS/Linux)."""
	dpi_scale = 1.0
	system = platform.system()
	
	try:
		if system == 'Windows':
			# Windows: Verwende Windows API für DPI-Erkennung
			try:
				from ctypes import windll
				windll.user32.SetProcessDPIAware()
				
				# Versuche, den DPI-Skalierungsfaktor zu berechnen
				try:
					from ctypes import windll, c_uint
					# GetDpiForSystem gibt DPI zurück (Standard 96)
					dpi = windll.user32.GetDpiForSystem()
					dpi_scale = dpi / 96.0  # Standard-DPI ist 96
				except:
					# Fallback: Versuche über shcore.GetScaleFactorForDevice
					try:
						from ctypes import windll, c_uint, POINTER, byref
						scale = c_uint()
						hmon = windll.user32.MonitorFromPoint((0, 0), 0)
						result = windll.shcore.GetScaleFactorForMonitor(hmon, byref(scale))
						if result == 0:  # S_OK
							dpi_scale = scale.value / 100.0
					except:
						pass
			except:
				pass
		
		elif system == 'Darwin':
			# macOS: Nutze Cocoa/AppKit für Retina-Display-Erkennung
			try:
				import subprocess
				# Ermittle Skalierungsfaktor über macOS System-Info
				result = subprocess.run(
					['system_profiler', 'SPDisplaysDataType'],
					capture_output=True,
					text=True,
					timeout=5
				)
				if 'Retina' in result.stdout:
					dpi_scale = 2.0  # Retina = 2x Skalierung
				else:
					dpi_scale = 1.0
			except:
				# Fallback: Versuche über tkinter native DPI-Erkennung
				try:
					# Auf macOS kann tkinter mitunter die DPI ermitteln
					import tkinter as tk_temp
					root_temp = tk_temp.Tk()
					# macOS skaliert per default, aber wir können versuchen, den Faktor zu ermitteln
					dpi_scale = root_temp.winfo_fpixels('1i') / 72.0
					root_temp.destroy()
				except:
					dpi_scale = 1.0
		
		elif system == 'Linux':
			# Linux: Nutze verschiedene Methoden zur DPI-Erkennung
			try:
				# Versuche zuerst via Xlib (für X11-basierte Desktop-Umgebungen)
				try:
					import subprocess
					result = subprocess.run(
						['xdpyinfo'],
						capture_output=True,
						text=True,
						timeout=5
					)
					# Parse die DPI aus xdpyinfo output
					for line in result.stdout.split('\n'):
						if 'resolution' in line:
							# Beispiel: "  resolution:    96x96 dots per inch"
							parts = line.split()
							if parts:
								dpi_str = parts[-3]  # Erste DPI-Zahl
								dpi = int(dpi_str.rstrip('x'))
								dpi_scale = dpi / 96.0
								break
				except:
					pass
				
				# Fallback: Versuche über GSettings (für GNOME)
				if dpi_scale == 1.0:
					try:
						import subprocess
						result = subprocess.run(
							['gsettings', 'get', 'org.gnome.desktop.interface', 'text-scaling-factor'],
							capture_output=True,
							text=True,
							timeout=5
						)
						scale_str = result.stdout.strip()
						if scale_str:
							dpi_scale = float(scale_str)
					except:
						pass
				
				# Fallback: Versuche über environment VARIABLE
				if dpi_scale == 1.0:
					import os
					scaling_factor = os.environ.get('GDK_SCALE')
					if scaling_factor:
						try:
							dpi_scale = float(scaling_factor)
						except:
							pass
			except:
				dpi_scale = 1.0
	
	except Exception:
		dpi_scale = 1.0
	
	# Stelle sicher, dass der Skalierungsfaktor im vernünftigen Bereich liegt
	dpi_scale = max(0.5, min(3.0, dpi_scale))  # Min 50%, Max 300%
	
	return dpi_scale

def _enable_windows_dark_mode(root) -> None:
	"""Aktiviert Windows Dark Mode für Titelleiste und Menüleiste."""
	try:
		import ctypes
		from ctypes import windll, byref, c_int
		
		# Get window handle
		hwnd = windll.user32.GetParent(root.winfo_id())
		
		# DWMWA_USE_IMMERSIVE_DARK_MODE = 20 (Windows 11) or 19 (Windows 10 older builds)
		DWMWA_USE_IMMERSIVE_DARK_MODE = 20
		value = c_int(1)  # 1 = Dark Mode, 0 = Light Mode
		
		# Try Windows 11 attribute first
		result = windll.dwmapi.DwmSetWindowAttribute(
			hwnd,
			DWMWA_USE_IMMERSIVE_DARK_MODE,
			byref(value),
			ctypes.sizeof(value)
		)
		
		# If that fails, try Windows 10 attribute
		if result != 0:
			DWMWA_USE_IMMERSIVE_DARK_MODE = 19
			windll.dwmapi.DwmSetWindowAttribute(
				hwnd,
				DWMWA_USE_IMMERSIVE_DARK_MODE,
				byref(value),
				ctypes.sizeof(value)
			)
		
		# Force redraw
		root.update_idletasks()
	except Exception as e:
		pass  # Silently fail if not on Windows or API not available

def main():
	# Initialize logging
	logger = setup_logging(logging.INFO)
	logger.info("Starting OSSL2Gif application...")
	
	try:
		# Bootstrap application services (config, logging, etc.)
		bootstrap_services()
		dpi_scale = _enable_windows_dpi_awareness()
		
		if DND_AVAILABLE and TkinterDnD is not None:
			root = TkinterDnD.Tk()
			if THEME_AVAILABLE and tb is not None:
				tb.Style("superhero")
				logger.debug("TkinterDnD + ttkbootstrap theme 'superhero' loaded successfully")
			else:
				logger.debug("TkinterDnD loaded with standard tkinter style")
		elif THEME_AVAILABLE and tb is not None:
			root = tb.Window(themename="superhero")
			logger.debug("ttkbootstrap theme 'superhero' loaded successfully")
		else:
			root = tk.Tk()
			logger.debug("Using standard tkinter Tk")
		
		# Fenster verstecken, bis es vollständig initialisiert ist
		root.withdraw()
		
		app = ModernApp(root)
		app.dpi_scale = dpi_scale  # Speichere DPI-Faktor
		logger.info(f"DPI Scale Factor: {dpi_scale:.2f}")
		_enable_windows_dark_mode(root)
		logger.info("Application initialized successfully")
		root.mainloop()
	except Exception as e:
		logger.error(f"Fatal error in main application: {e}", exc_info=True)
		raise
	finally:
		shutdown_services()
		logger.info("Application closed")

if __name__ == "__main__":
	main()
