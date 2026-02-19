###
# error_handler.py
# Centralized error handling and recovery utilities for OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Any, Callable, Optional, TypeVar
import logging
from functools import wraps

logger = logging.getLogger(__name__)

T = TypeVar('T')

def safe_execute(
    func: Callable[..., T],
    *args: Any,
    default: Optional[T] = None,
    error_msg: str = "Operation failed",
    log_level: str = "error",
    silent: bool = False
) -> Optional[T]:
	"""
	Führt eine Funktion sicher aus und loggt Fehler.
	
	Args:
		func: Zu execagutierende Funktion
		*args: Argumente für die Funktion
		default: Rückgabewert bei Fehler
		error_msg: Custom Fehlermeldung
		log_level: Logging-Level ('debug', 'warning', 'error')
		silent: Wenn True, keine Exception-Details loggen
	
	Returns:
		Funktionsergebnis oder default Value
	"""
	try:
		return func(*args)
	except Exception as e:
		if not silent:
			getattr(logger, log_level)(f"{error_msg}: {type(e).__name__}: {e}", exc_info=False)
		else:
			logger.debug(f"{error_msg}: {type(e).__name__}", exc_info=False)
		return default

def handle_exception(
    error_msg: str = "An error occurred",
    log_level: str = "error",
    notify_user: Optional[Callable[[str], None]] = None,
    silent: bool = False
) -> Callable:
	"""
	Decorator für robuste Exception-Behandlung mit optionaler User-Benachrichtigung.
	
	Args:
		error_msg: Fehlermeldung zum Loggen
		log_level: Logging-Level
		notify_user: Optional Callback zur User-Benachrichtigung (z.B. messagebox.showerror)
		silent: Wenn True, keine Details loggen
	
	Usage:
		@handle_exception("Failed to process image", notify_user=lambda msg: messagebox.showerror("Error", msg))
		def process_image(self, path):
			...
	"""
	def decorator(func: Callable) -> Callable:
		@wraps(func)
		def wrapper(*args: Any, **kwargs: Any) -> Any:
			try:
				return func(*args, **kwargs)
			except Exception as e:
				if not silent:
					getattr(logger, log_level)(
						f"{error_msg} in {func.__name__}: {type(e).__name__}: {e}",
						exc_info=False
					)
				else:
					logger.debug(f"{error_msg} in {func.__name__}: {type(e).__name__}", exc_info=False)
				
				if notify_user:
					notify_user(f"{error_msg}: {type(e).__name__}")
				
				return None
		return wrapper
	return decorator

def close_resource(resource: Any, resource_name: str = "resource") -> bool:
	"""
	Schließt eine Ressource sicher (File, Image, etc.)
	
	Returns:
		True wenn erfolgreich, False bei Fehler
	"""
	if resource is None:
		return True
	
	try:
		if hasattr(resource, 'close'):
			resource.close()
			logger.debug(f"Closed {resource_name}")
			return True
		return False
	except Exception as e:
		logger.warning(f"Error closing {resource_name}: {type(e).__name__}: {e}", exc_info=False)
		return False
