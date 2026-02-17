###
# config.py
# This file handles the configuration for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###
import json
import os
import sys

if getattr(sys, 'frozen', False):
    # Im PyInstaller-Bundle: Schreibe config.json ins aktuelle Arbeitsverzeichnis (neben die EXE)
    CONFIG_FILE = os.path.join(os.getcwd(), 'config.json')
else:
    # Im normalen Python: Schreibe ins Quellverzeichnis
    CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config.json')

def save_config(data):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)
