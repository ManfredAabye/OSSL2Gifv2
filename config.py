###
# config.py
# This file handles the configuration for the OSSL2Gif application.
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###
import json
import os
import sys
import logging

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    # Im PyInstaller-Bundle: Schreibe config.json ins aktuelle Arbeitsverzeichnis (neben die EXE)
    CONFIG_FILE = os.path.join(os.getcwd(), 'config.json')
else:
    # Im normalen Python: Schreibe ins Quellverzeichnis
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def save_config(self):
    """Speichert die Konfiguration der App-Instanz (self) in die config.json."""
    # self.get_config() muss ein dict liefern
    data = self.get_config() if hasattr(self, 'get_config') else None
    if data is not None:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.debug(f"Configuration saved to {CONFIG_FILE}")
    else:
        logger.warning("Cannot save config: get_config() returned None")

def load_config():
    if not os.path.exists(CONFIG_FILE):
        logger.debug(f"Config file not found: {CONFIG_FILE}")
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = json.load(f)
        logger.debug(f"Configuration loaded from {CONFIG_FILE}: {list(config.keys())}")
        return config
