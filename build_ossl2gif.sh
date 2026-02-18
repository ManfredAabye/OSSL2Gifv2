#!/bin/bash
# Build-Skript für OSSL2Gifv2 (Version 2.0.3)
# Erstellt eine eigenständige Linux-ELF aus dem Quellcode von GitHub.

set -e  # Skript beenden bei Fehlern

# --- Farben für Ausgaben ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# --- Konfiguration ---
PROJECT_DIR="OSSL2Gifv2"
MAIN_SCRIPT="start.py"
OUTPUT_NAME="OSSL2Gif"
ICON_FILE="icon.ico" # Optional, falls vorhanden
VENV_DIR=".venv_build" # Separate Build-Umgebung

# --- Header ---
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  OSSL2Gifv2 Builder für Linux${NC}"
echo -e "${BLUE}========================================${NC}"

# --- 1. Repository klonen oder aktualisieren ---
echo -e "\n${YELLOW}[1/7] Repository wird vorbereitet...${NC}"
if [ -d "$PROJECT_DIR" ]; then
    echo "Verzeichnis $PROJECT_DIR existiert bereits. Aktualisiere mit 'git pull'..."
    cd "$PROJECT_DIR"
    git pull
    cd ..
else
    echo "Klone Repository von GitHub..."
    git clone https://github.com/ManfredAabye/OSSL2Gifv2.git "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
echo -e "${GREEN}✓ Repository bereit in $(pwd)${NC}"

# --- 2. Python und Abhängigkeiten prüfen ---
echo -e "\n${YELLOW}[2/7] Prüfe Python-Umgebung...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 nicht gefunden. Bitte installiere Python 3.13.${NC}"
    exit 1
fi

PY_VERSION=$(python3 --version)
echo "Verwende: $PY_VERSION"
if [[ ! "$PY_VERSION" == *"3.13"* ]]; then
    echo -e "${YELLOW}⚠️  Warnung: OSSL2Gifv2 wurde primär für Python 3.13 entwickelt. Du verwendest $PY_VERSION${NC}"
fi

# --- 3. Virtuelle Build-Umgebung erstellen ---
echo -e "\n${YELLOW}[3/7] Erstelle virtuelle Build-Umgebung '${VENV_DIR}'...${NC}"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo -e "${GREEN}✓ Virtuelle Umgebung aktiviert.${NC}"

# --- 4. Abhängigkeiten installieren ---
echo -e "\n${YELLOW}[4/7] Installiere Abhängigkeiten...${NC}"
pip install --upgrade pip

# Installiere aus requirements.txt, falls vorhanden
if [ -f "requirements.txt" ]; then
    echo "Installiere Pakete aus requirements.txt..."
    pip install -r requirements.txt
else
    echo -e "${YELLOW}⚠️  requirements.txt nicht gefunden. Installiere Standardpakete...${NC}"
    pip install pillow ttkbootstrap
fi

# PyInstaller für den Build-Prozess installieren
echo "Installiere PyInstaller..."
pip install pyinstaller

# Zeige installierte Pakete
echo -e "\nInstallierte Pakete:"
pip list | grep -E "Pillow|ttkbootstrap|pyinstaller"

# --- 5. Build-Vorbereitung ---
echo -e "\n${YELLOW}[5/7] Bereite Build vor...${NC}"

# Prüfe, ob die Hauptdatei existiert
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}✗ Hauptdatei '$MAIN_SCRIPT' nicht gefunden!${NC}"
    exit 1
fi

# Entferne alte Build-Artefakte
rm -rf build dist *.spec

# --- 6. PyInstaller Build ausführen ---
echo -e "\n${YELLOW}[6/7] Baue OSSL2Gif mit PyInstaller (onefile)...${NC}"

# Baue den PyInstaller-Befehl
PYI_CMD="pyinstaller --noconfirm --onefile --windowed --name $OUTPUT_NAME"

# Füge Icon hinzu, falls vorhanden
if [ -f "$ICON_FILE" ]; then
    PYI_CMD="$PYI_CMD --icon=$ICON_FILE"
    echo "Icon '$ICON_FILE' wird eingebunden."
else
    echo -e "${YELLOW}⚠️  Icon-Datei '$ICON_FILE' nicht gefunden. Baue ohne Icon.${NC}"
fi

# Füge versteckte Importe hinzu (falls nötig, z.B. für ttkbootstrap)
# PYI_CMD="$PYI_CMD --hidden-import ttkbootstrap"

# Starte den Build
echo "Führe aus: $PYI_CMD $MAIN_SCRIPT"
$PYI_CMD "$MAIN_SCRIPT"

# --- 7. Erfolgsprüfung und Ausgabe ---
echo -e "\n${YELLOW}[7/7] Prüfe Build-Ergebnis...${NC}"

if [ -f "dist/$OUTPUT_NAME" ]; then
    # Berechtigungen setzen
    chmod +x "dist/$OUTPUT_NAME"

    # Zusätzliche Dateien kopieren
    if [ -f "$ICON_FILE" ]; then
        cp -f "$ICON_FILE" dist/
        echo "Icon wurde nach dist/ kopiert."
    fi

    # Kopiere README oder andere wichtige Dateien
    if [ -f "README.md" ]; then
        cp -f "README.md" dist/
    fi

    # Zeige Erfolgsmeldung mit Details
    echo -e "\n${GREEN}✅ BUILD ERFOLGREICH!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo "Die ausführbare Datei befindet sich in:"
    echo "  $(pwd)/dist/$OUTPUT_NAME"
    echo ""
    echo "Datei-Informationen:"
    echo "  Größe: $(du -h dist/$OUTPUT_NAME | cut -f1)"
    echo "  Berechtigungen: $(ls -l dist/$OUTPUT_NAME | awk '{print $1}')"
    echo ""
    echo "Zum Ausführen:"
    echo "  ./dist/$OUTPUT_NAME"
    echo -e "${GREEN}========================================${NC}"
else
    echo -e "${RED}❌ FEHLER: Build fehlgeschlagen!${NC}"
    echo "Überprüfe die PyInstaller-Ausgabe oben auf Fehlermeldungen."
    exit 1
fi

# Vorschlag: Erstelle ein Shell-Skript zum einfachen Starten
cat > dist/start.sh << 'EOF'
#!/bin/bash
# Starter für OSSL2Gif
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
"$SCRIPT_DIR/OSSL2Gif"
EOF
chmod +x dist/start.sh
echo "Zusätzlich wurde 'dist/start.sh' erstellt (nützlich für Starter/Shortcuts)."

echo -e "\n${BLUE}Build-Prozess abgeschlossen.${NC}"
