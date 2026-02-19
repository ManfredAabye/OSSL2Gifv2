###
# start.py
# This file serves as the entry point for the application. It initializes the main window and starts the application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###
import tkinter as tk
import logging
try:
	import ttkbootstrap as tb
	THEME_AVAILABLE = True
except ImportError:
	tb = None
	THEME_AVAILABLE = False
from logging_config import setup_logging
from main import ModernApp

def main():
	# Initialize logging
	logger = setup_logging(logging.INFO)
	logger.info("Starting OSSL2Gif application...")
	
	try:
		if THEME_AVAILABLE and tb is not None:
			root = tb.Window(themename="superhero")
			logger.debug("ttkbootstrap theme 'superhero' loaded successfully")
		else:
			root = tk.Tk()
			logger.debug("Using standard tkinter Tk")
		
		app = ModernApp(root)
		logger.info("Application initialized successfully")
		root.mainloop()
	except Exception as e:
		logger.error(f"Fatal error in main application: {e}", exc_info=True)
		raise
	finally:
		logger.info("Application closed")

if __name__ == "__main__":
	main()
