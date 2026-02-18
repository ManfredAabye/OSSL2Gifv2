# Dateien und Strukturinformationen

Zuletzt aktualisiert: 18. Februar 2026

## 📁 Projektstruktur

```bash
PyOSSL2Gif/
├── Haupt-Anwendung
│   ├── start.py              # Startskript der Anwendung
│   ├── main.py               # Hauptklasse (ModernApp)
│   ├── gui_layout.py         # GUI-Layout und Widgets
│   ├── events.py             # Event-Handler
│   ├── image_processing.py   # Bildverarbeitung und Effekte
│   ├── file_ops.py           # Datei-I/O
│   ├── threading_utils.py    # Thread-Management
│   └── tooltip.py            # Tooltip-Klasse
│
├── Konfiguration & Daten
│   ├── config.py             # Konfigurations-Management
│   ├── config.json           # Gespeicherte Einstellungen
│   └── translations.py       # Mehrsprachigkeit (10 Sprachen)
│
├── Dokumentation
│   ├── README.md             # Hauptdokumentation
│   ├── DEPENDENCIES.md       # Abhängigkeiten-Changelog
│   └── DateienStruktur.md    # Diese Datei
│
├── Abhängigkeiten & Tools
│   ├── requirements.txt      # Python-Pakete
│   └── update_dependencies.py # Automatisches Update-Tool
│
├── Tests
│   ├── test_file_ops.py      # Unit-Tests für file_ops.py
│   └── test_image_processing.py # Unit-Tests für image_processing.py
│
└── Ressourcen
    └── Icon.ico              # Anwendungs-Icon
```

---

## 📄 Detaillierte Dateibeschreibungen

### Kern-Module

#### config.py

**Zweck:** Laden und Speichern von Benutzereinstellungen  
**Funktionen:**

- Liest/Schreibt `config.json`
- Speichert Theme, Sprache, Texturgrößen, etc.
- Stellt Standardwerte bereit

#### config.json

**Zweck:** JSON-Datei mit gespeicherten Benutzereinstellungen  
**Inhalt:** Theme, Sprache, Texturbreite/-höhe, Hintergrundfarbe, Export-Format, Borderless-Modus, Max-Frames, Effekt-Einstellungen

#### events.py

**Zweck:** Event-Handler für alle Benutzeraktionen  
**Funktionen:**

- Hinzufügen/Entfernen von Frames
- Ändern von Einstellungen
- Auslösen von Vorschau-Updates
- Sprachwechsel
- Farbauswahl (Hintergrundfarbe)
- Delegiert Bildverarbeitung an `image_processing.py`

#### file_ops.py

**Zweck:** Datei-Input/Output-Operationen  
**Funktionen:**

- GIF laden (mit Frame-Extraktion)
- Textur speichern (PNG, JPG, BMP)
- LSL-Skript exportieren
- Bilder zu GIF kombinieren
- Keine GUI-Logik

#### gui_layout.py

**Zweck:** Komplettes GUI-Layout  
**Funktionen:**

- Erstellt alle Tkinter-Widgets
- Definiert Layout-Struktur
- Nutzt ttkbootstrap für modernes Design
- Keine Event-Handler-Implementierung

#### image_processing.py

**Zweck:** Bildverarbeitung und Effekte  
**Funktionen:**

- Effekte: Graustufen, Schärfe, Weichzeichnen, Transparenz, Farbintensität
- Vorschau-Generierung (GIF + Textur)
- Hintergrundfarbe-Compositing
- Thread-basierte Verarbeitung
- Keine GUI- oder Event-Logik

#### main.py

**Zweck:** Hauptklasse und Anwendungslogik  
**Funktionen:**

- `ModernApp`-Klasse (erbt von `tk.Tk`)
- Initialisiert GUI-Komponenten
- Verbindet alle Module
- Verwaltet Anwendungszustand
- Startet nicht direkt (siehe `start.py`)

#### start.py

**Zweck:** Anwendungs-Einstiegspunkt  
**Funktionen:**

- Startet die Anwendung
- Initialisiert `ModernApp` aus `main.py`
- Ruft Tkinter-Hauptschleife auf
- Kann Umgebungsprüfungen enthalten

#### threading_utils.py

**Zweck:** Thread-Management für Hintergrundaufgaben  
**Funktionen:**

- Queue-basierte Kommunikation
- Worker-Threads für zeitintensive Operationen
- Hält GUI reaktionsfähig während Bildverarbeitung
- Thread-sichere UI-Updates

**Hinweis:** In der alten Dokumentation als `threading.py` bezeichnet, tatsächlicher Dateiname ist aber `threading_utils.py`

#### tooltip.py

**Zweck:** Tooltip-Funktionalität  
**Funktionen:**

- `ToolTip`-Klasse für Hilfetexte
- Zeigt kontextsensitive Hilfe beim Hovern
- Mehrsprachige Unterstützung

#### translations.py

**Zweck:** Mehrsprachigkeits-System  
**Funktionen:**

- Übersetzungen für 10 Sprachen:
  - Deutsch (de), Englisch (en), Französisch (fr)
  - Spanisch (es), Italienisch (it), Russisch (ru)
  - Niederländisch (nl), Schwedisch (se)
  - Polnisch (pl), Portugiesisch (pt)
- `tr()`-Funktion für Übersetzungsabfragen

---

### Dokumentation

#### README.md

**Zweck:** Hauptdokumentation für Benutzer und Entwickler  
**Inhalt:**

- Installation und Systemanforderungen
- Vollständiges Tutorial (11 Schritte)
- Beispiel-Workflow (Second Life Feueranimation)
- Wartung & Update-Anleitungen
- Entwickler-Dokumentation (Module, Threading, Erweiterungen)
- Performance-Metriken
- Tipps & Best Practices

#### DEPENDENCIES.md

**Zweck:** Changelog und Dokumentation für Abhängigkeiten  
**Inhalt:**

- Versionshistorie aller Python-Pakete
- Update-Notizen (Pillow 11.3.0 → 12.1.1, pyinstaller 6.16.0 → 6.19.0)
- Kompatibilitätsprobleme
- Test-Checkliste nach Updates
- Rollback-Anleitungen
- Wichtige Versionshinweise

#### DateienStruktur.md

**Zweck:** Diese Datei - Übersicht über Projektstruktur  
**Inhalt:**

- Dateibaumstruktur
- Detaillierte Beschreibung jeder Datei
- Zweck und Funktionen der Module
- Abhängigkeiten zwischen Modulen

---

### Abhängigkeiten & Tools

#### requirements.txt

**Zweck:** Liste der benötigten Python-Pakete  
**Inhalt:**

- Pillow==12.1.1 (Bildverarbeitung)
- ttkbootstrap==1.20.1 (GUI-Framework)
- pyinstaller==6.19.0 (Build-Tool, optional)
- Detaillierte Kommentare zu jeder Abhängigkeit
- Update-Anleitungen inline

#### update_dependencies.py

**Zweck:** Automatisches Update-Tool für Abhängigkeiten  
**Funktionen:**

- Prüft alle Pakete auf verfügbare Updates
- Zeigt Versions-Vergleich (installiert vs. verfügbar)
- Interaktive Installation mit Bestätigung
- Aktualisiert `requirements.txt` automatisch
- Formatierte Ausgabe mit Emojis und Farben

**Verwendung:**

```bash
python update_dependencies.py
```

---

### Tests

#### test_file_ops.py

**Zweck:** Unit-Tests für `file_ops.py`  
**Funktionen:**

- Testet GIF-Laden
- Testet Textur-Speichern
- Testet LSL-Export
- Testet Bilder-zu-GIF-Konvertierung

#### test_image_processing.py

**Zweck:** Unit-Tests für `image_processing.py`  
**Funktionen:**

- Testet alle Effekte (Graustufen, Schärfe, Weichzeichnen, Transparenz, Farbintensität)
- Testet Alpha-Compositing mit Hintergrundfarben
- Testet Thread-Sicherheit
- Testet Fehlerbehandlung

**Tests ausführen:**

```bash
python -m pytest test_*.py
```

---

### Ressourcen

#### Icon.ico

**Zweck:** Anwendungs-Icon  
**Format:** ICO (Windows-Icon-Format)  
**Verwendung:**

- Fenster-Icon der Anwendung
- Taskleisten-Icon
- Build mit pyinstaller (`.exe`)

---

### Generierte Dateien (nicht im Repository)

#### **pycache**/

**Zweck:** Python-Bytecode-Cache  
**Inhalt:** `.pyc`-Dateien (kompilierte Python-Module)  
**Hinweis:** Automatisch von Python generiert, sollte nicht versioniert werden (in `.gitignore`)

---

## 🔄 Abhängigkeiten zwischen Modulen

```bash
start.py
    └── main.py (ModernApp)
        ├── gui_layout.py (erstellt UI)
        ├── events.py (Event-Handler)
        │   ├── image_processing.py (Bildverarbeitung)
        │   └── file_ops.py (Datei-I/O)
        ├── threading_utils.py (Thread-Management)
        ├── translations.py (Übersetzungen)
        ├── tooltip.py (Tooltips)
        └── config.py (Einstellungen)
            └── config.json (Daten)
```

---

## 📋 Entwickler-Hinweise

### Neue Dateien hinzufügen

Wenn neue Dateien zum Projekt hinzugefügt werden, bitte diese Datei (`DateienStruktur.md`) aktualisieren.

### Modul-Konventionen

- **Keine zirkulären Imports:** Module sollten klare Hierarchien haben
- **Separation of Concerns:** GUI, Logik, und Daten getrennt halten
- **Thread-Safety:** Alle UI-Updates im Hauptthread (verwende `root.after()`)
- **Typ-Annotationen:** Wo möglich für bessere Wartbarkeit

### Testing

Für jedes neue Modul sollten entsprechende Unit-Tests erstellt werden.

### Code-Style

- Python 3.13+ Features verwenden
- PEP 8 Style Guide befolgen
- Docstrings für alle Funktionen/Klassen
- Kommentare in Deutsch für Benutzernähe

---

## 📊 Statistiken

- **Gesamt-Dateien:** 20 (ohne `__pycache__`)
- **Python-Module:** 11
- **Dokumentation:** 3
- **Tests:** 2
- **Konfiguration:** 2
- **Ressourcen:** 1
- **Tools:** 1

---

## 🔧 Wartung

Diese Datei wurde zuletzt am **18. Februar 2026** aktualisiert.

Bei Änderungen an der Projektstruktur bitte:

1. Diese Datei aktualisieren
2. README.md entsprechend anpassen (falls nötig)
3. Imports in betroffenen Modulen prüfen
