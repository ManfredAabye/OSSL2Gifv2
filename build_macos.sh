#!/bin/bash
# Erstellt eine eigenständige macOS-App aus OSSL2Gifv2 mit allen Abhängigkeiten
# macOS 12 (Monterey) und neuer

set -e  # Skript beenden bei Fehlern

# --- Farben für Ausgaben (macOS-kompatibel) ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Konfiguration ---
PROJECT_DIR="OSSL2Gifv2"
MAIN_SCRIPT="start.py"
APP_NAME="OSSL2Gif"
ICON_FILE="icon.icns"  # macOS verwendet .icns, nicht .ico!
VENV_DIR=".venv_build"
DEPLOYMENT_TARGET="10.15"  # Mindest-macOS-Version (Catalina für breitere Kompatibilität)

# --- Header ---
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OSSL2Gifv2 Builder für macOS${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "Ziel-macOS: ab Version 12 (Monterey)"
echo -e "Mindest-Kompatibilität: ${DEPLOYMENT_TARGET}+"

# --- 1. Prüfe macOS-Version ---
echo -e "\n${YELLOW}[1/7] Prüfe macOS-Version...${NC}"
MACOS_VERSION=$(sw_vers -productVersion)
echo "macOS Version: $MACOS_VERSION"

MACOS_MAJOR=$(echo "$MACOS_VERSION" | cut -d. -f1)
if [ "$MACOS_MAJOR" -lt 12 ]; then
    echo -e "${YELLOW}⚠️  Warnung: Du verwendest macOS $MACOS_VERSION. Offiziell wird ab 12 unterstützt.${NC}"
    read -p "Trotzdem fortfahren? (j/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Jj]$ ]]; then
        exit 1
    fi
fi

# --- 2. Repository klonen oder aktualisieren ---
echo -e "\n${YELLOW}[2/7] Repository wird vorbereitet...${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo "Klone Repository von GitHub..."
    git clone https://github.com/ManfredAabye/OSSL2Gifv2.git "$PROJECT_DIR"
    cd "$PROJECT_DIR"
else
    cd "$PROJECT_DIR"
    echo "Verzeichnis vorhanden. Aktualisiere mit 'git pull'..."
    git pull
fi

echo -e "${GREEN}✓ Repository bereit in $(pwd)${NC}"

# --- 3. Python und Abhängigkeiten prüfen ---
echo -e "\n${YELLOW}[3/7] Prüfe Python-Umgebung...${NC}"

# Prüfe ob Python 3 vorhanden
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 nicht gefunden!${NC}"
    echo "Bitte installiere Python 3.13 von: https://www.python.org/downloads/"
    echo "Wichtig: 'Add Python to PATH' bei der Installation auswählen!"
    exit 1
fi

PY_VERSION=$(python3 --version)
echo "Verwende: $PY_VERSION"

# Prüfe ob tkinter verfügbar ist (wichtig für GUI)
echo "Prüfe tkinter..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo -e "${RED}✗ tkinter nicht gefunden!${NC}"
    echo "Auf macOS muss tkinter separat installiert werden:"
    echo "  brew install python-tk@3.13"
    echo "Oder: python3 -m pip install tk"
    exit 1
fi
echo -e "${GREEN}✓ tkinter verfügbar${NC}"

# --- 4. Virtuelle Build-Umgebung erstellen ---
echo -e "\n${YELLOW}[4/7] Erstelle virtuelle Build-Umgebung...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
echo -e "${GREEN}✓ Virtuelle Umgebung aktiviert${NC}"

# --- 5. Abhängigkeiten installieren ---
echo -e "\n${YELLOW}[5/7] Installiere Abhängigkeiten...${NC}"
pip install --upgrade pip

# Installiere aus requirements.txt
if [ -f "requirements.txt" ]; then
    echo "Installiere Pakete aus requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠️  requirements.txt nicht gefunden. Installiere Standardpakete...${NC}"
    pip install pillow ttkbootstrap
fi

# PyInstaller für macOS optimiert installieren
echo "Installiere PyInstaller..."
pip install pyinstaller

# Zeige installierte Pakete
echo -e "\nInstallierte Pakete:"
pip list | grep -E "Pillow|ttkbootstrap|pyinstaller"

# --- 6. Icon konvertieren (falls nötig) ---
echo -e "\n${YELLOW}[6/7] Bereite Icon vor...${NC}"

# Falls ein .ico existiert, konvertiere es zu .icns (benötigt 'iconutil' und 'sips')
if [ -f "icon.ico" ] && [ ! -f "$ICON_FILE" ]; then
    echo "Konvertiere icon.ico zu macOS .icns Format..."
    
    # Temporäres Verzeichnis für Iconsets
    ICONSET="OSSLLogo.iconset"
    mkdir -p "$ICONSET"
    
    # Benötigt 'convert' von ImageMagick? Versuche es mit sips (macOS built-in)
    if command -v sips &> /dev/null; then
        # Verschiedene Größen für macOS Icons erstellen
        for size in 16 32 64 128 256 512 1024; do
            sips -z $size $size icon.ico --out "$ICONSET/icon_${size}x${size}.png" 2>/dev/null || \
            echo "  - Größe ${size}x${size} übersprungen"
        done
        
        # Mit iconutil in .icns konvertieren
        iconutil -c icns "$ICONSET" -o "$ICON_FILE"
        rm -rf "$ICONSET"
        echo -e "${GREEN}✓ Icon konvertiert: $ICON_FILE${NC}"
    else
        echo -e "${YELLOW}⚠️  Konvertierung nicht möglich. Verwende Standard-Icon.${NC}"
        echo "Tipp: Installiere ImageMagick mit 'brew install imagemagick' für Icon-Konvertierung"
    fi
fi

if [ ! -f "$ICON_FILE" ]; then
    echo -e "${YELLOW}⚠️  Kein Icon gefunden. Baue ohne App-Icon.${NC}"
fi

# --- 7. Bereinigung alter Builds ---
echo "Entferne alte Build-Artefakte..."
rm -rf build dist *.spec

# --- 8. PyInstaller Build mit macOS-spezifischen Optionen ---
echo -e "\n${YELLOW}[7/7] Baue macOS-App mit PyInstaller...${NC}"

# Basis-Befehl für macOS
PYI_CMD="pyinstaller --noconfirm --onefile --windowed"

# macOS-spezifische Optionen
PYI_CMD="$PYI_CMD --name $APP_NAME"
PYI_CMD="$PYI_CMD --osx-bundle-identifier com.ossl2gif.app"
PYI_CMD="$PYI_CMD --target-architecture universal2"  # Universal Binary (Intel + Apple Silicon)
PYI_CMD="$PYI_CMD --codesign-identity -"  # Ad-hoc Signierung (optional)

# Mindest-macOS-Version setzen
export MACOSX_DEPLOYMENT_TARGET="$DEPLOYMENT_TARGET"

# Icon hinzufügen, falls vorhanden
if [ -f "$ICON_FILE" ]; then
    PYI_CMD="$PYI_CMD --icon=$ICON_FILE"
    echo "Icon wird eingebunden: $ICON_FILE"
fi

# Versteckte Importe für ttkbootstrap (falls nötig)
PYI_CMD="$PYI_CMD --hidden-import ttkbootstrap"

# Ausführen
echo "Führe Build aus:"
echo "$PYI_CMD $MAIN_SCRIPT"
$PYI_CMD "$MAIN_SCRIPT"

# --- 9. Nachbearbeitung und Erfolgsprüfung ---
echo -e "\n${YELLOW}[8/8] Finalisiere App...${NC}"

APP_PATH="dist/$APP_NAME"
if [ -f "$APP_PATH" ]; then
    # Berechtigungen setzen
    chmod +x "$APP_PATH"
    
    # AppBundle erstellen (optional - für richtige macOS App)
    echo "Erstelle macOS App-Bundle..."
    APP_BUNDLE="dist/${APP_NAME}.app"
    mkdir -p "$APP_BUNDLE/Contents/MacOS"
    mkdir -p "$APP_BUNDLE/Contents/Resources"
    
    # Binary ins Bundle verschieben
    mv "$APP_PATH" "$APP_BUNDLE/Contents/MacOS/"
    
    # Plist erstellen
    cat > "$APP_BUNDLE/Contents/Info.plist" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>$APP_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>com.ossl2gif.app</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>2.0.3</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>$DEPLOYMENT_TARGET</string>
    <key>NSHighResolutionCapable</key>
    <true/>
EOF

    # Icon ins Bundle kopieren
    if [ -f "$ICON_FILE" ]; then
        cp "$ICON_FILE" "$APP_BUNDLE/Contents/Resources/"
        echo "    <key>CFBundleIconFile</key>" >> "$APP_BUNDLE/Contents/Info.plist"
        echo "    <string>$(basename "$ICON_FILE")</string>" >> "$APP_BUNDLE/Contents/Info.plist"
    fi
    
    echo "</dict>" >> "$APP_BUNDLE/Contents/Info.plist"
    echo "</plist>" >> "$APP_BUNDLE/Contents/Info.plist"
    
    # Zusätzliche Dateien kopieren
    if [ -f "README.md" ]; then
        cp "README.md" "$APP_BUNDLE/Contents/Resources/"
    fi
    
    # --- 10. Erfolgsmeldung ---
    echo -e "\n${GREEN}✅ BUILD ERFOLGREICH!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo "Die macOS-App wurde erstellt:"
    echo "  📁 $(pwd)/dist/${APP_NAME}.app"
    echo ""
    echo "App-Informationen:"
    echo "  • Größe: $(du -h "$APP_BUNDLE" | cut -f1)"
    echo "  • Binary: $(file "$APP_BUNDLE/Contents/MacOS/$APP_NAME" | grep -o 'Mach-O.*')"
    echo "  • macOS-Version: ab $DEPLOYMENT_TARGET"
    echo ""
    echo "Zum Ausführen:"
    echo "  • Doppelklick auf ${APP_NAME}.app im Finder"
    echo "  • Oder Terminal: open dist/${APP_NAME}.app"
    echo ""
    echo -e "${YELLOW}⚠️  Wichtig für macOS:${NC}"
    echo "  • Beim ersten Start erscheint eine Sicherheitswarnung"
    echo "  • Gehe zu: Systemeinstellungen → Datenschutz & Sicherheit"
    echo "  • Klicke auf 'Trotzdem öffnen'"
    echo -e "${GREEN}========================================${NC}"
    
    # Erstelle ein einfaches Start-Skript
    cat > "dist/start.command" << EOF
#!/bin/bash
cd "\$(dirname "\$0")"
open "${APP_NAME}.app"
EOF
    chmod +x "dist/start.command"
    
else
    echo -e "${RED}❌ FEHLER: Build fehlgeschlagen!${NC}"
    echo "Überprüfe die PyInstaller-Ausgabe auf Fehlermeldungen."
    exit 1
fi

# --- 11. Aufräumen ---
echo -e "\n${BLUE}Build-Prozess abgeschlossen.${NC}"
