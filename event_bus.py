###
# event_bus.py
# Publish-Subscribe event system for thread communication in OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Callable, Optional, Any, Dict, List
from enum import Enum
import logging
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

class EventType(Enum):
	"""Zentrale Event-Typen für die Anwendung"""
	
	# GIF Processing
	GIF_FRAME_LOADED = "gif:frame_loaded"
	GIF_FRAME_ERROR = "gif:frame_error"
	GIF_LOADING_STARTED = "gif:loading_started"
	
	# Texture Processing
	TEXTURE_GENERATED = "texture:generated"
	TEXTURE_ERROR = "texture:error"
	TEXTURE_GENERATION_STARTED = "texture:generation_started"
	
	# UI Events
	SETTINGS_CHANGED = "settings:changed"
	LANGUAGE_CHANGED = "ui:language_changed"
	THEME_CHANGED = "ui:theme_changed"
	
	# System Events
	ERROR_OCCURRED = "system:error"
	WARNING_OCCURRED = "system:warning"
	
	def __str__(self) -> str:
		return self.value

@dataclass
class Event:
	"""Datenklasse für Events"""
	event_type: EventType
	data: Any = None
	source: str = "system"
	timestamp: datetime = field(default_factory=datetime.now)

class EventBus:
	"""
	Zentrale Event-Bus für Publish-Subscribe Kommunikation.
	Ersetzt Queue-basierte Kommunikation durch flexibleres Event-System.
	
	Nutzung:
		bus = EventBus()
		
		# Subscriber registrieren
		def on_texture_generated(event: Event):
			print(f"Texture generated: {event.data}")
		bus.subscribe(EventType.TEXTURE_GENERATED, on_texture_generated)
		
		# Event publishen
		bus.publish(
			EventType.TEXTURE_GENERATED,
			data={'size': (2048, 2048)},
			source='image_processing'
		)
	"""
	
	def __init__(self):
		self._subscribers: Dict[str, List[Callable]] = {}
		self._event_history: List[Event] = []
		self._max_history = 100
		logger.info("EventBus initialized")
	
	def subscribe(self, event_type: EventType | str, callback: Callable[[Event], None]) -> Callable[[], None]:
		"""
		Subscribtet einen Callback für einen Event-Typ.
		
		Args:
			event_type: Zu überwachender Event-Typ
			callback: Funktion, die bei Event aufgerufen wird
		
		Returns:
			Unsubscribe-Funktion
		"""
		event_key = str(event_type)
		
		if event_key not in self._subscribers:
			self._subscribers[event_key] = []
		
		self._subscribers[event_key].append(callback)
		logger.debug(f"Subscribed to {event_key}")
		
		# Convenience: Return unsubscribe function
		def unsubscribe():
			self.unsubscribe(event_type, callback)
		
		return unsubscribe
	
	def unsubscribe(self, event_type: EventType | str, callback: Callable[[Event], None]) -> bool:
		"""
		Entfernt einen Subscriber.
		
		Returns:
			True wenn erfolgreich, False wenn nicht gefunden
		"""
		event_key = str(event_type)
		
		if event_key not in self._subscribers:
			return False
		
		try:
			self._subscribers[event_key].remove(callback)
			logger.debug(f"Unsubscribed from {event_key}")
			return True
		except ValueError:
			return False
	
	def publish(
		self,
		event_type: EventType | str,
		data: Any = None,
		source: str = "system"
	) -> None:
		"""
		Publishet einen Event an alle Subscriber.
		
		Args:
			event_type: Event-Typ
			data: Event-Daten
			source: Quelle des Events (zur Debugging)
		"""
		event_key = str(event_type)
		event = Event(
			event_type=event_type if isinstance(event_type, EventType) else EventType(event_type),
			data=data,
			source=source
		)
		
		# Log event
		logger.debug(f"Publishing event {event_key} from {source}")
		self._event_history.append(event)
		
		# Trim history
		if len(self._event_history) > self._max_history:
			self._event_history = self._event_history[-self._max_history:]
		
		# Call subscribers
		if event_key in self._subscribers:
			for callback in self._subscribers[event_key]:
				try:
					callback(event)
				except Exception as e:
					logger.error(f"Error in event subscriber: {type(e).__name__}: {e}", exc_info=False)
	
	def get_history(self, event_type: Optional[EventType | str] = None, limit: int = 10) -> List[Event]:
		"""
		Gibt Event-Verlauf zurück.
		
		Args:
			event_type: Optional eventtyp zum Filtern
			limit: Maximale Anzahl Events
		
		Returns:
			Liste von Events
		"""
		history = self._event_history[-limit:]
		
		if event_type:
			event_key = str(event_type)
			history = [e for e in history if str(e.event_type) == event_key]
		
		return history
	
	def clear_history(self) -> None:
		"""Löscht Event-Verlauf (für Tests)"""
		self._event_history.clear()
	
	def get_subscriber_count(self, event_type: Optional[EventType | str] = None) -> int:
		"""Gibt Anzahl der Subscriber zurück"""
		if event_type:
			event_key = str(event_type)
			return len(self._subscribers.get(event_key, []))
		else:
			return sum(len(subs) for subs in self._subscribers.values())
	
	def list_subscriptions(self) -> Dict[str, int]:
		"""Gibt Übersicht aller Subscriptions aus"""
		return {key: len(subs) for key, subs in self._subscribers.items() if subs}

# Global singleton instance
_event_bus_instance: Optional[EventBus] = None

def get_event_bus() -> EventBus:
	"""Gibt die globale EventBus-Instanz zurück"""
	global _event_bus_instance
	if _event_bus_instance is None:
		_event_bus_instance = EventBus()
	return _event_bus_instance

def reset_event_bus() -> None:
	"""Setzt den Event Bus zurück (für Tests)"""
	global _event_bus_instance
	_event_bus_instance = None
