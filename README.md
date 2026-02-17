
# OSSL2Gif – GIF zu Textur Konverter (Version 2.0.0)

Mit OSSL2Gif 2.0.0 wandelst du animierte GIFs komfortabel in Texturen für Second Life/OpenSim um – jetzt mit vielen neuen Features und moderner Oberfläche!

## Was ist neu in 2.0.0?

- **Einzelne Bilder entfernen:** Über den neuen "Entfernen"-Button kannst du gezielt einzelne Frames aus der GIF-Liste löschen.
- **Max. Bilder:** Die maximale Bildanzahl ist einstellbar. Überschüssige Bilder werden automatisch entfernt.
- **Threading:** Hinzufügen und Entfernen von Frames läuft im Hintergrund – die Oberfläche bleibt immer reaktionsschnell.
- **Borderless-Optimierung:** Randlose Texturen werden robuster und ohne leere Pixel erzeugt.
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
- **Optional:** Für ein modernes Aussehen `ttkbootstrap`

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

## Starten

- Im Ordner mit der Datei `start.py` folgenden Befehl ausführen:

  ```bash
  python start.py
  ```

## Bedienung (Kurzüberblick)

1. **GIF laden:** Klicke auf „GIF laden“ und wähle eine animierte GIF-Datei aus.
2. **Vorschau:** Das GIF und die spätere Textur werden angezeigt.
3. **Effekte:** Graustufen, Schärfe, Weichzeichnen, Transparenz und Farbintensität einstellbar.
4. **Bildgröße:** Zielgröße der Textur anpassen.
5. **Randlos:** Entfernt überflüssige transparente Ränder (Borderless).
6. **Play/Pause:** Animation abspielen oder anhalten.
7. **Bild hinzufügen:** Einzelne GIF-Frames zur Textur hinzufügen (über die Spinbox und den Button).
8. **Bild entfernen:** Mit dem "Entfernen"-Button gezielt ein Bild aus der Liste löschen.
9. **Max. Bilder:** Die maximale Bildanzahl ist über die Spinbox einstellbar.
10. **Sprache:** Sprache im Dropdown-Menü wählen.
11. **Speichern:** GIF oder Textur als Datei speichern.
12. **LSL exportieren:** LSL-Skript für Second Life/OpenSim erzeugen.

## Tipps & Hinweise

- Für ein modernes Aussehen installiere `ttkbootstrap` (siehe oben).
- Die Benutzeroberfläche ist mehrsprachig (Deutsch, Englisch, Französisch, Spanisch, u.v.m.).
- Die Buttons "Bild hinzufügen" und "Entfernen" arbeiten jetzt immer in Einzelschritten.
- Die maximale Bildanzahl ("Max. Bilder") kann jederzeit angepasst werden.
- Bei Problemen: Stelle sicher, dass du Python 3.13 verwendest und alle Pakete installiert sind.

---

## Changelog (Auszug)

- 2.0.0: Einzelbild-Entfernung, max. Bilder, Threading, Borderless-Verbesserung, modernes UI, Bugfixes
- 1.x: Grundfunktionen (GIF laden, speichern, Effekte, Export)

---
