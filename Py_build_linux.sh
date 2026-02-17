#!/bin/bash
# Erstellt eine eigenständige ELF aus PyOSSL2Gif/start.py mit allen Abhängigkeiten
# Voraussetzung: Python, pip und pyinstaller müssen installiert sein

# Virtuelle Umgebung aktivieren (falls vorhanden)
if [ -f .venv/bin/activate ]; then
    source .venv/bin/activate
fi

# PyInstaller installieren, falls nicht vorhanden
if ! python3 -m pip show pyinstaller > /dev/null 2>&1; then
    python3 -m pip install pyinstaller
fi

# ELF bauen (onefile, ohne Konsole, Icon optional)
# pyinstaller --noconfirm --onefile --windowed --name OSSL2Gif PyOSSL2Gif/start.py
pyinstaller --noconfirm --onefile --windowed --name OSSL2Gif --icon=icon.ico PyOSSL2Gif/start.py

# Icon ins dist-Ordner kopieren (optional)
if [ -f icon.ico ]; then
    cp -f icon.ico dist/icon.ico
fi

# Hinweis für den Nutzer
if [ -f dist/OSSL2Gif ]; then
    echo
    echo "Fertig! Die ELF befindet sich in dist/OSSL2Gif"
    [ -f dist/icon.ico ] && echo "Icon wurde nach dist kopiert."
else
    echo "Fehler beim Erstellen der ELF!"
fi