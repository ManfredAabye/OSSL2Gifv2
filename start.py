###
# start.py
# This file serves as the entry point for the application. It initializes the main window and starts the application.
# OSSL2Gif OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###
import tkinter as tk
import logging
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

def _enable_windows_dpi_awareness() -> None:
	"""Aktiviert DPI-Awareness unter Windows vor dem Erstellen des Tk-Root-Fensters."""
	try:
		from ctypes import windll
		windll.user32.SetProcessDPIAware()
	except Exception:
		pass

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
		_enable_windows_dpi_awareness()
		
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
