
# OSSL2Gif – GIF zu Textur Konverter (Version 2.0.8)

Mit OSSL2Gif 2.0.8 wandelst du animierte GIFs komfortabel in Texturen für Second Life/OpenSim um – jetzt mit vielen neuen Features und moderner Oberfläche!

## Was ist neu in 2.0.8?

- **Einzelne Bilder entfernen:** Über den neuen "Entfernen"-Button kannst du gezielt einzelne Frames aus der GIF-Liste löschen.
- **Max. Bilder:** Die maximale Bildanzahl ist einstellbar. Überschüssige Bilder werden automatisch entfernt.
- **Threading:** Hinzufügen und Entfernen von Frames läuft im Hintergrund – die Oberfläche bleibt immer reaktionsschnell.
- **Mehrsprachigkeit:** Die Oberfläche ist in vielen Sprachen verfügbar (Deutsch, Englisch, Französisch, Spanisch, Italienisch, Russisch, Niederländisch, Schwedisch, Polnisch, Portugiesisch).
- **Modernes UI:** Optional mit `ttkbootstrap` für ein frisches, anpassbares Design.
- **Fehlerbehebungen:** Viele Bugs und UX-Probleme wurden beseitigt.
- **Konfigurationsspeicherung:** Alle Einstellungen werden automatisch gespeichert und beim nächsten Start wiederhergestellt.

## Unterstützte Betriebssysteme

- **Windows 10/11** (empfohlen)
- **Linux** (Ubuntu, Fedora, etc.)
- **macOS** (ab macOS 12)

OSSL2Gif ist plattformübergreifend und läuft überall dort, wo Python 3.13 und tkinter verfügbar sind.

## Voraussetzungen

- **Python 3.13**  
  Download: <https://www.python.org/downloads/>  
  Während der Installation: Haken setzen bei „Add Python to PATH“
- **pip** (meist mit Python installiert)
- **tkinter** (bei Python fast immer schon dabei)
- **Pillow** (für die Bildverarbeitung)
- **ttkbootstrap** (für ein modernes Aussehen)

## Installation – Schritt für Schritt

1. **Python installieren**
   - Lade Python 3.13 von [python.org](https://www.python.org/downloads/) herunter und installiere es.
   - Achte darauf, dass „Add Python to PATH“ aktiviert ist.

2. **Prüfen, ob Python und pip funktionieren**
   - Öffne die Eingabeaufforderung (Windows-Taste, dann „cmd“ eingeben und Enter).
   - Prüfe die Versionen:

     ```bash
     python --version
     pip --version
     ```

   - Beide Befehle sollten eine Versionsnummer anzeigen.

3. **Benötigte Pakete installieren**
   - Wechsle in den Ordner, in dem sich die Dateien befinden (z.B. `PyOSSL2Gif`).
   - Installiere alle Abhängigkeiten:

     ```bash
     pip install -r requirements.txt
     ```

## Wartung & Updates

### Abhängigkeiten aktualisieren

Um von Bugfixes und neuen Features zu profitieren, sollten die Abhängigkeiten regelmäßig aktualisiert werden:

1. **Alle Pakete auf neueste Versionen aktualisieren:**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Nur ein bestimmtes Paket aktualisieren:**
   ```bash
   pip install --upgrade Pillow
   ```

3. **Installierte Versionen prüfen:**
   ```bash
   pip list
   ```

4. **Nach veralteten Paketen suchen:**
   ```bash
   pip list --outdated
   ```

### Wichtige Hinweise zu Updates

- **Pillow**: Hauptbibliothek für Bildverarbeitung. Updates bringen oft Performance-Verbesserungen für RGBA-Operationen.
- **ttkbootstrap**: UI-Framework. Updates können neue Themes und Widgets enthalten.
- **pyinstaller**: Nur relevant, wenn `.exe`-Dateien erstellt werden sollen.

### Kompatibilitätstest nach Updates

Nach größeren Updates solltest du die Anwendung testen:

1. Anwendung starten: `python start.py`
2. GIF laden und alle Effekte testen
3. Textur mit verschiedenen Hintergrundfarben speichern
4. LSL-Export prüfen

Bei Problemen kannst du auf eine vorherige Version zurück:
```bash
pip install Pillow==11.3.0
```

## Starten

- Im Ordner mit der Datei `start.py` folgenden Befehl ausführen:

  ```bash
  python start.py
  ```

## Bedienung – Komplettes Tutorial von A bis Z

### Schritt 1: Anwendung starten

Führe `python start.py` aus. Die Hauptoberfläche erscheint mit zwei Hauptbereichen:

- **Links:** GIF-Vorschau mit Wiedergabesteuerung
- **Rechts:** Textur-Vorschau mit dem finalen Texture-Sheet

![Screenshot: Hauptoberfläche](docs/screenshots/01_hauptoberflaeche.png)

### Schritt 2: GIF-Datei laden

1. Klicke auf **"GIF laden"** (obere Buttonleiste)
2. Wähle eine animierte GIF-Datei aus (z.B. `beispiel-animation.gif`)
3. Die Frames werden automatisch geladen und in der GIF-Vorschau angezeigt
4. Die Textur-Vorschau zeigt die Anordnung aller Frames in einem Grid

![Screenshot: GIF geladen](docs/screenshots/02_gif_geladen.png)

**Tipp:** Die Statusleiste unten zeigt die Anzahl der geladenen Frames an.

### Schritt 3: Animation abspielen

Teste die Animation mit den Media-Steuerelementen:

- **⏮ Zurück:** Ein Frame zurück
- **▶ Play:** Animation abspielen
- **⏸ Pause:** Animation pausieren
- **⏹ Stop:** Animation stoppen und zum ersten Frame zurückkehren
- **⏭ Vor:** Ein Frame vorwärts

**Abspielrate anpassen:**

- Nutze den Slider "Abspielrate" (10-500%)
- 100% = normale Geschwindigkeit
- 50% = halbe Geschwindigkeit
- 200% = doppelte Geschwindigkeit

![Screenshot: Media-Steuerung](docs/screenshots/03_media_steuerung.png)

### Schritt 4: Effekte anwenden

#### GIF-Effekte (linke Seite)

Diese Effekte gelten nur für die GIF-Vorschau:

- **Graustufen:** Wandelt die Farben in Graustufen um
- **Schärfen:** Macht das Bild schärfer (Slider: 0-5)
- **Weichzeichnen:** Wendet Gaussian Blur an (Slider: 0-10 Pixel)
- **Transparenz:** Passt die Deckkraft an (Slider: 0-1)
- **Farbintensität:** Verstärkt oder reduziert die Farbsättigung (Slider: 0-1)

#### Textur-Effekte (rechte Seite)

Diese Effekte werden auf die finale Textur angewendet:

- Dieselben Optionen wie bei GIF-Effekten
- Änderungen werden sofort in der Textur-Vorschau angezeigt

![Screenshot: Effekte-Panel](docs/screenshots/04_effekte.png)

**Beispiel:** Für ein Schwarzweiß-Textur Sheet: Aktiviere "Graustufen" im Textur-Effekte-Panel.

### Schritt 5: Hintergrundfarbe festlegen

1. Im Bereich "Textur-Einstellungen" findest du das **"Hintergrundfarbe"**-Feld
2. **Linksklick** auf das Farbfeld → Farbauswahl-Dialog öffnet sich
   - Wähle eine Farbe
   - Stelle die Transparenz ein (0 = vollständig transparent, 255 = undurchsichtig)
3. **Rechtsklick** auf das Farbfeld → Setzt sofort 100% Transparenz
4. Die Vorschau zeigt ein Schachbrettmuster für Transparenzbereiche

![Screenshot: Hintergrundfarbe](docs/screenshots/05_hintergrundfarbe.png)

**Tipp:** Für transparente Texturen nutze die Standard-Einstellung (vollständig transparent).

### Schritt 6: Frames verwalten

#### Frames hinzufügen

1. Wähle mit der Spinbox einen Frame (0 bis N-1)
2. Klicke auf **"Bild hinzufügen"**
3. Der ausgewählte Frame wird am Ende der Liste hinzugefügt

#### Frames entfernen

1. Wähle den zu entfernenden Frame in der Spinbox
2. Klicke auf **"Entfernen"**
3. Der Frame wird aus der Liste gelöscht

#### Max. Bilder begrenzen

- Nutze die Spinbox "Max. Bilder" (1-256)
- Überschüssige Frames werden automatisch entfernt
- Nützlich, um große Animationen zu kürzen

![Screenshot: Frame-Verwaltung](docs/screenshots/06_frame_verwaltung.png)

### Schritt 7: Textur-Größe anpassen

1. Im Bereich "Bildgröße" findest du zwei Eingabefelder:
   - **Breite** (Standard: 2048)
   - **Höhe** (Standard: 2048)
2. Oder nutze die **Preset-Combobox**:
   - 512×512 (klein)
   - 1024×1024 (mittel)
   - 2048×2048 (groß, empfohlen)
   - 4096×4096 (sehr groß)

**Wichtig für Second Life/OpenSim:**

- Max. Texturgröße: 1024×1024 (normaler Account)
- Premium-Accounts: bis 2048×2048 möglich
- Wähle die Größe passend zu deinen Upload-Rechten

![Screenshot: Größen-Einstellung](docs/screenshots/07_groesse.png)

### Schritt 9: Textur speichern

1. Klicke auf **"Textur speichern"**
2. Wähle das Exportformat:
   - **PNG:** Unterstützt Transparenz (empfohlen)
   - **JPG:** Kompakter, keine Transparenz
   - **BMP:** Unkomprimiert
3. Gib einen Dateinamen ein (automatisch vorgeschlagen: `name;columns;rows;speed.png`)
4. Speichern → Fertig!

**Dateinamen-Format:**

```bash
beispiel;4;3;100.png
```

- `beispiel`: Name der Animation
- `4`: Anzahl Spalten (Tiles X)
- `3`: Anzahl Zeilen (Tiles Y)
- `100`: Geschwindigkeit (FPS-Info für LSL)

![Screenshot: Speichern-Dialog](docs/screenshots/08_speichern.png)

### Schritt 10: LSL-Skript exportieren

1. Klicke auf **"LSL exportieren"**
2. Ein LSL-Skript wird generiert mit all deinen Einstellungen
3. Speichere das Skript als `.lsl`-Datei
4. Importiere es in Second Life/OpenSim

**LSL-Skript nutzen:**

```lsl
// Das Skript liest automatisch:
// - Texturname aus dem Inventar
// - Spalten/Zeilen aus dem Dateinamen
// - Geschwindigkeit aus dem Dateinamen
```

![Screenshot: LSL-Export](docs/screenshots/09_lsl_export.png)

### Schritt 11: Bilder zu GIF kombinieren (Bonus)

Du kannst auch einzelne Bilder zu einem GIF kombinieren:

1. Klicke auf **"Bilder zu GIF"**
2. Wähle eine ZIP-Datei mit Bildern oder einen Ordner
3. Die Bilder werden automatisch zu einem GIF kombiniert
4. Speichere das resultierende GIF

**Unterstützte Formate:** PNG, JPG, JPEG, BMP, GIF

---

## Beispiel-Workflow: Feueranimation für Second Life

### Szenario

Du hast eine `fire-animation.gif` mit 20 Frames und möchtest daraus eine Textur für ein flammenloderndes Objekt in Second Life erstellen.

### Ablauf

1. **Start:** `python start.py`
2. **Laden:** GIF laden → `fire-animation.gif` auswählen
3. **Prüfen:** Animation mit Play-Button testen
4. **Anpassen:**
   - Textur-Effekte → Farbintensität auf 1.2 erhöhen (lebendigere Flammen)
   - Hintergrundfarbe → Vollständig transparent lassen
5. **Optimieren:**
   - Max. Bilder → auf 16 reduzieren (für bessere Performance in SL)
   - Größe → 1024×1024 wählen (passt für Standard-Account)
6. **Speichern:**
   - Textur speichern als `fire;4;4;50.png`
   - LSL exportieren als `fire-animation.lsl`
7. **In Second Life:**
   - Textur hochladen
   - In ein Prim einfügen
   - LSL-Skript ins Inventar des Prims ziehen
   - Fertig! Die Flammen animieren sich automatisch

---

## Tipps & Best Practices

### Performance-Optimierung

- **Große GIFs:** Reduziere die Anzahl der Frames mit "Max. Bilder"
- **Threading:** Alle rechenintensiven Operationen laufen im Hintergrund
- **Abspielrate:** Bei niedrigen Werten (< 50%) kann es zu Verzögerungen kommen

### Second Life/OpenSim Tipps

- **Texturgröße:** Standard-Accounts sind auf 1024×1024 limitiert
- **Transparenz:** Nutze PNG-Format für transparente Bereiche
- **Animation:** Die Geschwindigkeit im Dateinamen ist ein Hinweis für LSL (nicht bindend)
- **Upload-Kosten:** Größere Texturen kosten mehr L$ beim Upload

### Qualität vs. Dateigröße

- **PNG:** Beste Qualität, größere Dateien, Transparenz unterstützt
- **JPG:** Kleinere Dateien, keine Transparenz, leichter Qualitätsverlust
- **BMP:** Sehr große Dateien, nur für spezielle Zwecke

### Fehlerbehebung

- **GIF lädt nicht:** Prüfe, ob die Datei beschädigt ist
- **Textur ist schwarz:** Hintergrundfarbe auf transparent setzen
- **Performance-Probleme:** Reduziere die Anzahl der Frames oder wähle kleinere Texturgröße
- **Effekte wirken nicht:** Stelle sicher, dass die Checkbox aktiviert ist

---

## Entwickler-Dokumentation

### Projektstruktur

```bash
PyOSSL2Gif/
├── start.py              # Einstiegspunkt der Anwendung
├── main.py               # Hauptklasse ModernApp
├── gui_layout.py         # GUI-Layout und Widget-Erstellung
├── image_processing.py   # Bildverarbeitung und Threading
├── file_ops.py           # Datei-I/O (Laden, Speichern, Export)
├── events.py             # Event-Handler für Benutzeraktionen
├── translations.py       # Mehrsprachigkeits-Unterstützung
├── tooltip.py            # ToolTip-Klasse für Hilfe-Tooltips
├── threading_utils.py    # Queue-Management für Threading
├── config.py             # Konfigurationsverwaltung
├── config.json           # Gespeicherte Einstellungen
└── requirements.txt      # Python-Abhängigkeiten
```

### Haupt-Module im Detail

#### `main.py` – Hauptanwendung

**Zweck:** Zentrale Koordination der Anwendung

**Wichtige Klasse:** `ModernApp`

- Erbt von `tk.Tk` (Tkinter Hauptfenster)
- Initialisiert alle GUI-Komponenten
- Verwaltet den Anwendungszustand (GIF-Frames, Einstellungen)
- Koordiniert zwischen GUI, Events und Bildverarbeitung

**Zentrale Methoden:**

```python
def __init__(self):
    # Initialisiert das Hauptfenster
    # Lädt gespeicherte Konfiguration
    # Erstellt GUI-Layout

def _bind_effects_panel_events(self):
    # Bindet alle Effekt-Slider an Event-Handler
    # Ermöglicht Echtzeit-Updates

def start_animation(self):
    # Startet die GIF-Animation
    # Nutzt threading für flüssige Wiedergabe

def save_config(self):
    # Speichert alle Einstellungen in config.json
    # Wird beim Beenden aufgerufen
```

**Threading-Implementierung:**

- Alle Media-Funktionen (Play, Stop, Step) nutzen Threads
- Verhindert UI-Blocking während der Bildverarbeitung

---

#### `gui_layout.py` – GUI-Erstellung

**Zweck:** Baut die gesamte Benutzeroberfläche auf

**Hauptfunktion:** `create_modern_layout(self)`

- Erstellt alle Panels, Buttons, Slider, Labels
- Nutzt `ttk` für moderne Widgets
- Optional: `ttkbootstrap` für erweiterte Themes

**Layout-Struktur:**

```bash
┌─────────────────────────────────────────────┐
│  [Menü] [Buttons: Laden, Speichern, etc.]  │
├──────────────────┬──────────────────────────┤
│   GIF-Vorschau   │   Textur-Vorschau        │
│   ┌────────────┐ │   ┌────────────────────┐ │
│   │  Canvas    │ │   │  Canvas            │ │
│   └────────────┘ │   └────────────────────┘ │
│   Media-Controls │   Textur-Einstellungen   │
├──────────────────┴──────────────────────────┤
│   GIF-Effekte    │   Textur-Effekte         │
└──────────────────┴──────────────────────────┘
```

**Widget-Typen:**

- `ttk.Frame`: Container für Gruppierungen
- `ttk.LabelFrame`: Gruppierungen mit Titel
- `ttk.Button`: Aktions-Buttons
- `ttk.Scale`: Slider für Werte
- `ttk.Checkbutton`: Ein/Aus-Schalter
- `tk.Canvas`: Bildanzeige (GIF/Textur)

**Besonderheiten:**

- Alle Widgets werden als `self.widget_name` gespeichert
- Tooltips werden über `ToolTip`-Klasse hinzugefügt
- Mehrsprachigkeit durch `tr()`-Funktion

---

#### `image_processing.py` – Bildverarbeitung

**Zweck:** Alle Bildmanipulationen und Threading

**Threading-Architektur:**

```python
# Worker-Thread für GIF-Vorschau
def _process_gif_frame_worker(self, current_frame, ...):
    # Läuft im Hintergrund
    # Verarbeitet einen Frame
    # Legt Ergebnis in gif_queue

# Queue-Checker (UI-Thread)
def _check_gif_queue(self):
    # Prüft periodisch die Queue
    # Aktualisiert Canvas mit fertigen Frames
    # Bleibt im UI-Thread (thread-safe)
```

**Effekt-Pipeline:**

```python
def apply_effects(self, img, prefix):
    # 1. Graustufen (optional)
    if grayscale: img = convert_grayscale(img)
    
    # 2. Schärfen (optional)
    if sharpen: img = enhance_sharpness(img)
    
    # 3. Weichzeichnen (optional)
    if blur: img = apply_gaussian_blur(img)
    
    # 4. Transparenz (optional)
    if transparency: img = adjust_alpha(img)
    
    # 5. Farbintensität (optional)
    if colorintensity: img = adjust_saturation(img)
    
    return img
```

**Textur-Sheet-Generierung:**

```python
def _process_texture_worker(self):
    # Berechnet Grid-Layout (tiles_x, tiles_y)
    tiles_x = ceil(sqrt(frame_count))
    tiles_y = ceil(frame_count / tiles_x)
    
    # Erstellt leeres Sheet mit Hintergrundfarbe
    sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
    
    # Fügt jeden Frame ein
    for idx, frame in enumerate(frames):
        x = (idx % tiles_x) * tile_w
        y = (idx // tiles_x) * tile_h
        sheet.paste(resized_frame, (x, y))
    
    return sheet
```

**Wichtige Funktionen:**

- `show_gif_frame()`: Zeigt einzelnen GIF-Frame
- `show_texture()`: Generiert und zeigt Textur-Sheet
- `apply_effects()`: Wendet alle aktivierten Effekte an
- `_apply_bg_to_image()`: Composite für Hintergrundfarbe

---

#### `file_ops.py` – Dateiverwaltung

**Zweck:** Laden, Speichern, Import/Export

**GIF-Laden:**

```python
def load_gif(self):
    # 1. Datei-Dialog öffnen
    file = filedialog.askopenfilename(...)
    
    # 2. Frames extrahieren
    frames = []
    gif = Image.open(file)
    while True:
        frames.append(gif.copy())
        gif.seek(len(frames))
    
    # 3. Im Speicher halten
    self.gif_frames = frames
    self.frame_count = len(frames)
    
    # 4. Datei schließen (Frames bleiben im RAM)
    gif.close()
```

**Textur-Speichern:**

```python
def save_texture(self):
    # 1. Regeneriere Textur mit aktuellen Einstellungen
    sheet = generate_texture_sheet(frames, bg_color)
    
    # 2. Hintergrundfarbe einbetten (alpha_composite)
    if bg_color not transparent:
        sheet = Image.alpha_composite(background, sheet)
    
    # 3. Format-Konvertierung
    if format == "JPG": sheet = sheet.convert("RGB")
    
    # 4. Speichern
    sheet.save(filename, format)
```

**LSL-Export:**

- Generiert LSL-Skript basierend auf Textur-Metadaten
- Liest automatisch Grid-Layout und Geschwindigkeit
- Nutzt Template mit Platzhaltern

---

#### `events.py` – Event-Handler

**Zweck:** Verarbeitet alle Benutzeraktionen

**Event-Flow:**

```bash
Benutzeraktion (Click, Slider)
    ↓
Event-Handler in events.py
    ↓
Datenverarbeitung (ggf. in Thread)
    ↓
GUI-Update (show_gif_frame/show_texture)
    ↓
Canvas wird aktualisiert
```

**Wichtige Handler:**

- `choose_bg_color()`: Öffnet Farbauswahl-Dialog
- `set_transparent_bg()`: Setzt Transparenz auf 100%
- `add_selected_frame_to_texture()`: Fügt Frame hinzu (threaded)
- `remove_selected_frame_from_texture()`: Entfernt Frame (threaded)
- `on_maxframes_changed()`: Reagiert auf Max-Bilder-Änderung
- `update_previews()`: Aktualisiert beide Canvas-Bereiche

**Threading-Pattern:**

```python
def some_action(self):
    def do_work():
        # Schwere Arbeit hier
        result = process_data()
        # GUI-Update im Main-Thread
        self.root.after(0, lambda: update_ui(result))
    
    threading.Thread(target=do_work, daemon=True).start()
```

---

#### `translations.py` – Mehrsprachigkeit

**Zweck:** Unterstützt 10 Sprachen

**Struktur:**

```python
translations = {
    'de': {
        'load_btn': 'GIF laden',
        'save_texture': 'Textur speichern',
        ...
    },
    'en': {
        'load_btn': 'Load GIF',
        'save_texture': 'Save Texture',
        ...
    },
    ...
}

def tr(key, lang='de'):
    return translations.get(lang, {}).get(key, key)
```

**Unterstützte Sprachen:**

- Deutsch (de), Englisch (en), Französisch (fr)
- Spanisch (es), Italienisch (it), Russisch (ru)
- Niederländisch (nl), Schwedisch (se)
- Polnisch (pl), Portugiesisch (pt)

---

#### `config.py` – Konfiguration

**Zweck:** Speichert und lädt Einstellungen

**Gespeicherte Daten (config.json):**

```json
{
  "lang": "de",
  "width": 2048,
  "height": 2048,
  "bg_color": "#00000000",
  "framerate": 10,
  "export_format": "PNG",
  "maxframes": 196,
  "theme": "superhero"
}
```

**Auto-Speicherung:**

- Beim Beenden der Anwendung: `save_config()`
- Beim Start: `load_config()` stellt alles wieder her

---

### Erweitern der Anwendung

#### Neuen Effekt hinzufügen

1. **In `gui_layout.py`:** Widget hinzufügen

```python
self.new_effect_var = tk.BooleanVar(value=False)
new_effect_check = ttk.Checkbutton(frame, 
    text="Neuer Effekt", 
    variable=self.new_effect_var)
```

1. **In `main.py`:** Event-Binding

```python
self.new_effect_var.trace_add('write', 
    lambda *args: self._apply_gif_effect())
```

1. **In `image_processing.py`:** Effekt implementieren

```python
def apply_effects(self, img, prefix):
    # ... bestehende Effekte ...
    
    if self.__dict__[f'{prefix}_new_effect'].get():
        img = apply_new_effect(img)
    
    return img
```

#### Neues Dateiformat unterstützen

In `file_ops.py` anpassen:

```python
def save_texture(self):
    # Format hinzufügen
    filetypes.append(("WebP", "*.webp"))
    
    # Konvertierung implementieren
    if fmt == "WEBP":
        img.save(file, format="WEBP", quality=95)
```

---

### Testing

**Manuelle Tests:**

1. Laden verschiedener GIF-Formate
2. Alle Effekte einzeln und kombiniert testen
3. Performance-Test mit großen GIFs (100+ Frames)
4. Speichern in allen Formaten
5. LSL-Export prüfen

**Test-Dateien:**

- `test_image_processing.py`: Unit-Tests für Bildverarbeitung
- `test_file_ops.py`: Tests für Datei-Operationen

**Ausführen:**

```bash
python -m pytest test_*.py
```

---

### Performance-Metriken

**Typische Verarbeitungszeiten (Intel i5, 16GB RAM):**

- GIF laden (50 Frames, 512×512): ~0.5s
- Textur generieren (50 Frames, 2048×2048): ~2s
- Effekt anwenden (Graustufen): ~0.1s pro Frame
- Textur speichern (PNG, 2048×2048): ~1s

**Optimierungen:**

- Threading verhindert UI-Blocking
- Frames bleiben im RAM (kein Nachladen)
- Queue-basierte Kommunikation zwischen Threads
- PIL/Pillow nutzt optimierte C-Implementierungen

---

## Changelog (Auszug)

- Version 2.0.3: Einzelbild-Entfernung, max. Bilder, Threading, Borderless-Verbesserung, modernes UI, Bugfixes
Version 2.0.4: Logging-System hinzugefügt.

- Version 2.0.5: Type Hints zu den wichtigsten Funktionen hinzugefügt.

- Version 2.0.6: Custom Exceptions - sehr hilfreich für bessere Fehlerbehandlung hinzugefügt.


- Version 2.0.7: Randlos funktioniert nicht immer. Es sollte den Rand auf der Rechten Seite und den Unteren Rand die Transparent oder Einfarbig sein können entfernen indem die Textur entsprechende Pixel nach Rechts und unten über den Rand hinaus Skaliert so das sie nach dem speichern Eliminiert sind.

- Version 2.0.8: Randlos ist jetzt anders gelöst und alle borderless Funktionen wurden entfernt.

---


