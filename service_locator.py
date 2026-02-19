###
# service_locator.py
# Service locator for dependency management in OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Any, Dict, Optional, Type, TypeVar
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ServiceRegistry:
	"""
	Service Locator für einfaches Dependency Management.
	Ermöglicht zentrale Registrierung und Zugriff auf globale Services.
	
	Beispiel:
		registry.register('config', my_config_instance)
		config = registry.get('config')
	"""
	
	def __init__(self):
		self._services: Dict[str, Any] = {}
		self._singletons: Dict[str, Any] = {}
	
	def register(self, name: str, service: Any, singleton: bool = True) -> None:
		"""
		Registriert einen Service.
		
		Args:
			name: Eindeutiger Name des Services
			service: Service-Instanz oder Factory-Funktion
			singleton: Wenn True, wird die Instanz gecacht
		"""
		if name in self._services:
			logger.warning(f"Service '{name}' already registered, overwriting")
		
		self._services[name] = {
			'service': service,
			'singleton': singleton,
			'cached': False
		}
		logger.debug(f"Service '{name}' registered (singleton={singleton})")
	
	def get(self, name: str, default: Optional[T] = None) -> Optional[T]:
		"""
		Ruft einen registrierten Service ab.
		
		Args:
			name: Name des zu abzurufenden Services
			default: Fallback-Wert falls Service nicht existiert
		
		Returns:
			Service-Instanz oder default
		"""
		if name not in self._services:
			logger.warning(f"Service '{name}' not found")
			return default
		
		service_info = self._services[name]
		
		# Singleton-Caching
		if service_info['singleton']:
			if name in self._singletons:
				return self._singletons[name]  # type: ignore
		
		# Service aufrufen (falls Factory)
		service = service_info['service']
		if callable(service) and not isinstance(service, type):
			try:
				instance = service()
				if service_info['singleton']:
					self._singletons[name] = instance
				return instance  # type: ignore
			except Exception as e:
				logger.error(f"Error creating service '{name}': {type(e).__name__}: {e}", exc_info=False)
				return default
		else:
			# Ist bereits eine Instanz
			return service  # type: ignore
	
	def has(self, name: str) -> bool:
		"""Prüft, ob ein Service registriert ist"""
		return name in self._services
	
	def unregister(self, name: str) -> bool:
		"""Entfernt einen Service"""
		if name not in self._services:
			return False
		
		del self._services[name]
		if name in self._singletons:
			del self._singletons[name]
		
		logger.debug(f"Service '{name}' unregistered")
		return True
	
	def clear(self) -> None:
		"""Entfernt alle Services (für Tests)"""
		self._services.clear()
		self._singletons.clear()
		logger.debug("All services cleared")
	
	def list_services(self) -> list[str]:
		"""Gibt Liste aller registrierten Services zurück"""
		return list(self._services.keys())

# Global singleton instance
_registry_instance: Optional[ServiceRegistry] = None

def get_service_registry() -> ServiceRegistry:
	"""Gibt die globale ServiceRegistry-Instanz zurück"""
	global _registry_instance
	if _registry_instance is None:
		_registry_instance = ServiceRegistry()
	return _registry_instance

def register_service(name: str, service: Any, singleton: bool = True) -> None:
	"""Convenience-Funktion zum Registrieren eines Services"""
	get_service_registry().register(name, service, singleton)

def get_service(name: str, default: Optional[T] = None) -> Optional[T]:
	"""Convenience-Funktion zum Abrufen eines Services"""
	return get_service_registry().get(name, default)

def reset_registry() -> None:
	"""Setzt die Registry zurück (für Tests)"""
	global _registry_instance
	_registry_instance = None
