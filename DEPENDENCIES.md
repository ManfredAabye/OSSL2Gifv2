# Changelog - PyOSSL2Gif Abhängigkeiten

Alle wichtigen Änderungen an den Abhängigkeiten werden in dieser Datei dokumentiert.

## [2026-02-18] - Dependency Update

### Aktualisiert

- **Pillow**: 11.3.0 → 12.1.1
  - Verbesserte Performance bei RGBA-Operationen
  - Neue Filter und Optimierungen
  - Bugfixes für `alpha_composite()`
  - Vollständige Python 3.13 Unterstützung
  
- **pyinstaller**: 6.16.0 → 6.19.0
  - Verbesserte Python 3.13 Unterstützung
  - Kleinere Executable-Größen
  - Bugfixes für Windows 11

### Unverändert

- **ttkbootstrap**: 1.20.1 (bereits aktuell)

### Hinzugefügt

- `update_dependencies.py`: Automatisches Update-Script
- Detaillierte Kommentare in `requirements.txt`
- Wartungs-Sektion in README.md

---

## [Bisherige Versionen]

### Initiale Abhängigkeiten

- Pillow (Bildverarbeitung)
- ttkbootstrap (GUI-Framework)
- pyinstaller (Build-Tool)
- tkinter (Standardbibliothek)

---

## Update-Prozess

### Regelmäßige Prüfung (empfohlen: monatlich)

1. Update-Script ausführen:

   ```bash
   python update_dependencies.py
   ```

2. Oder manuell prüfen:

   ```bash
   pip list --outdated
   ```

3. Updates installieren:

   ```bash
   pip install --upgrade -r requirements.txt
   ```

### Nach größeren Updates testen

- [ ] Anwendung startet ohne Fehler
- [ ] GIF-Laden funktioniert
- [ ] Alle Effekte (Graustufen, Schärfen, Weichzeichnen, etc.)
- [ ] Hintergrundfarbe wird korrekt angezeigt
- [ ] Textur-Speicherung (PNG, JPG, BMP)
- [ ] LSL-Export funktioniert
- [ ] Animation läuft flüssig

---

## Bekannte Kompatibilitätsprobleme

### Pillow 12.x

- ✅ Keine Breaking Changes für unsere Verwendung
- ✅ RGBA-Operationen funktionieren wie erwartet
- ✅ `alpha_composite()` Performance verbessert

### ttkbootstrap 1.20.x

- ✅ Stabil mit allen verwendeten Themes

### pyinstaller 6.19.x

- ✅ Windows 11 kompatibel
- ✅ Python 3.13 vollständig unterstützt

---

## Wichtige Versionshinweise

### Pillow

- **Mindestversion**: 10.0.0 (für `alpha_composite()`)
- **Empfohlen**: 12.1.1+ (beste Performance)

### ttkbootstrap

- **Mindestversion**: 1.10.0 (für verwendete Widgets)
- **Empfohlen**: 1.20.1+ (stabile Themes)

### Python

- **Mindestversion**: 3.10
- **Empfohlen**: 3.13+ (beste Performance)
