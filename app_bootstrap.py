###
# app_bootstrap.py
# Application bootstrap and dependency setup for OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

import logging
from config_manager import get_config, ConfigManager
from service_locator import register_service, get_service_registry
from logging_config import get_logger

logger = get_logger(__name__)

def bootstrap_services() -> None:
	"""
	Initialisiert und registriert alle Anwendungs-Services.
	Sollte einmal beim Programmstart aufgerufen werden.
	"""
	registry = get_service_registry()
	
	try:
		# === Core Services ===
		# ConfigManager - zentrale Konfiguration
		config = get_config()
		register_service('config', config, singleton=True)
		logger.info("ConfigManager registered")
		
		# Logger - zentral verwalteter Logger
		register_service('logger', logger, singleton=True)
		logger.info("Logger registered")
		
		# === Message Bus für Thread-Kommunikation ===
		# (Queue-basierte Kommunikation existiert bereits, kann später zentralisiert werden)
		
		logger.info(f"Bootstrap complete. Registered services: {registry.list_services()}")
		
	except Exception as e:
		logger.error(f"Error during bootstrap: {type(e).__name__}: {e}", exc_info=True)
		raise

def get_app_config() -> ConfigManager:
	"""Convenience-Funktion zum Abrufen des Config-Services"""
	from service_locator import get_service
	config = get_service('config')
	if config is None:
		# Fallback: Direct instantiation wenn Service nicht registriert
		config = get_config()
	return config

def shutdown_services() -> None:
	"""
	Sauberer Shutdown aller Services.
	Sollte beim Programmende aufgerufen werden.
	"""
	try:
		# Shutdown Worker Pool
		from worker_pool import shutdown_worker_pool
		shutdown_worker_pool()
		
		# Shutdown Service Registry
		registry = get_service_registry()
		registry.clear()
		logger.info("Services shutdown complete")
	except Exception as e:
		logger.error(f"Error during shutdown: {type(e).__name__}: {e}", exc_info=True)
