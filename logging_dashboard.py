###
# logging_dashboard.py
# Real-time logging dashboard for OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import tkinter as tk
from tkinter import ttk
from typing import Any, Optional, List, Callable
import logging
from datetime import datetime
from collections import deque

class LoggerHandler(logging.Handler):
	"""Custom logging handler for GUI dashboard"""
	
	def __init__(self, capacity: int = 100):
		super().__init__()
		self.log_queue: deque[str] = deque(maxlen=capacity)
		self.callbacks: List[Callable[[str], None]] = []
	
	def emit(self, record: logging.LogRecord) -> None:
		"""
		Emit a log record.
		
		Args:
			record: Log record to emit
		"""
		try:
			msg = self.format(record)
			timestamp = datetime.now().strftime("%H:%M:%S")
			colored_msg = f"[{timestamp}] [{record.levelname:7}] {msg}"
			self.log_queue.append(colored_msg)
			
			# Call all registered callbacks
			for callback in self.callbacks:
				try:
					callback(colored_msg)
				except Exception:
					pass  # Ignore callback errors
		except Exception:
			self.handleError(record)
	
	def register_callback(self, callback: Callable[[str], None]) -> None:
		"""Register a callback to be called when logs are emitted"""
		self.callbacks.append(callback)
	
	def get_logs(self) -> list[str]:
		"""Gets all buffered logs"""
		return list(self.log_queue)

class LoggingDashboard:
	"""
	Real-time logging dashboard for monitoring OSSL2Gif errors and warnings.
	Shows error history, filtering, and search capabilities.
	"""
	
	def __init__(self, parent_app: Any):
		"""
		Args:
			parent_app: Reference to ModernApp instance
		"""
		self.parent_app = parent_app
		self.lang = parent_app.lang if hasattr(parent_app, 'lang') else 'de'
		
		# Setup custom handler
		self.handler = LoggerHandler(capacity=200)
		self.handler.setFormatter(logging.Formatter('%(message)s'))
		
		# Add handler to root logger
		root_logger = logging.getLogger()
		root_logger.addHandler(self.handler)
		
		# UI State
		self.window: Optional[tk.Toplevel] = None
		self.text_widget: Optional[tk.Text] = None
		self.filter_var: Optional[tk.StringVar] = None
		self.level_var: Optional[tk.StringVar] = None
	
	def show(self) -> None:
		"""Opens the logging dashboard"""
		if self.window is not None and self.window.winfo_exists():
			self.window.lift()
			self.window.focus()
			return
		
		# Create toplevel window
		self.window = tk.Toplevel(self.parent_app.root)
		self.window.title("OSSL2Gif Logging Dashboard" if self.lang == 'en' else "OSSL2Gif Log-Übersicht")
		self.window.geometry("700x500")
		
		# Toolbar
		toolbar = ttk.Frame(self.window)
		toolbar.pack(fill=tk.X, padx=5, pady=5)
		
		# Filter level
		ttk.Label(toolbar, text="Level:" if self.lang == 'en' else "Stufe:").pack(side=tk.LEFT, padx=5)
		self.level_var = tk.StringVar(value="ALL")
		level_combo = ttk.Combobox(
			toolbar,
			textvariable=self.level_var,
			values=["ALL", "ERROR", "WARNING", "INFO", "DEBUG"],
			state='readonly',
			width=10
		)
		level_combo.pack(side=tk.LEFT, padx=5)
		level_combo.bind('<<ComboboxSelected>>', lambda e: self._update_display())
		
		# Search
		ttk.Label(toolbar, text="Search:" if self.lang == 'en' else "Suche:").pack(side=tk.LEFT, padx=5)
		self.filter_var = tk.StringVar()
		search_entry = ttk.Entry(toolbar, textvariable=self.filter_var, width=30)
		search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
		search_entry.bind('<KeyRelease>', lambda e: self._update_display())
		
		# Clear button
		ttk.Button(toolbar, text="Löschen" if self.lang == 'de' else "Clear", command=self._clear_logs).pack(side=tk.LEFT, padx=5)
		
		# Text widget with scrollbar
		frame = ttk.Frame(self.window)
		frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
		
		scrollbar = ttk.Scrollbar(frame)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
		
		self.text_widget = tk.Text(
			frame,
			height=25,
			width=80,
			font=("Courier", 9),
			yscrollcommand=scrollbar.set,
			bg="#1e1e1e",
			fg="#d4d4d4"
		)
		self.text_widget.pack(fill=tk.BOTH, expand=True)
		scrollbar.config(command=self.text_widget.yview)
		
		# Configure color tags
		self._setup_colors()
		
		# Register callback for real-time updates
		self.handler.register_callback(self._on_log_emitted)
		
		# Initial display
		self._update_display()
	
	def _setup_colors(self) -> None:
		"""Setup text colors for different log levels"""
		if self.text_widget:
			self.text_widget.tag_configure("ERROR", foreground="#ff6b6b")
			self.text_widget.tag_configure("WARNING", foreground="#ffa500")
			self.text_widget.tag_configure("INFO", foreground="#4ec9b0")
			self.text_widget.tag_configure("DEBUG", foreground="#858585")
	
	def _on_log_emitted(self, log_msg: str) -> None:
		"""Callback when a log is emitted"""
		if self.text_widget and self.text_widget.winfo_exists():
			# Extract level
			level = "INFO"
			if "ERROR" in log_msg:
				level = "ERROR"
			elif "WARNING" in log_msg:
				level = "WARNING"
			elif "DEBUG" in log_msg:
				level = "DEBUG"
			
			# Check filter
			if not self._matches_filter(log_msg):
				return
			
			# Append to text
			self.text_widget.config(state=tk.NORMAL)
			self.text_widget.insert(tk.END, log_msg + "\n", level)
			self.text_widget.see(tk.END)
			self.text_widget.config(state=tk.DISABLED)
	
	def _update_display(self) -> None:
		"""Refresh the display with filtered logs"""
		if not self.text_widget:
			return
		
		self.text_widget.config(state=tk.NORMAL)
		self.text_widget.delete(1.0, tk.END)
		
		# Get all logs and filter
		for log_msg in self.handler.get_logs():
			if self._matches_filter(log_msg):
				# Extract level
				level = "INFO"
				if "ERROR" in log_msg:
					level = "ERROR"
				elif "WARNING" in log_msg:
					level = "WARNING"
				elif "DEBUG" in log_msg:
					level = "DEBUG"
				
				self.text_widget.insert(tk.END, log_msg + "\n", level)
		
		self.text_widget.see(tk.END)
		self.text_widget.config(state=tk.DISABLED)
	
	def _matches_filter(self, log_msg: str) -> bool:
		"""Check if log message matches current filters"""
		if not self.level_var or not self.filter_var:
			return True
		
		# Check level filter
		level_filter = self.level_var.get()
		if level_filter != "ALL" and level_filter not in log_msg:
			return False
		
		# Check search filter
		search = self.filter_var.get().lower()
		if search and search not in log_msg.lower():
			return False
		
		return True
	
	def _clear_logs(self) -> None:
		"""Clear all logs"""
		self.handler.log_queue.clear()
		self._update_display()
	
	def get_recent_errors(self, limit: int = 10) -> List[str]:
		"""Get recent error logs"""
		errors = [
			log for log in self.handler.get_logs()
			if "ERROR" in log
		]
		return errors[-limit:]
