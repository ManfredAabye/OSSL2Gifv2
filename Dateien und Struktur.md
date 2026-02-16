# Dateien und Strukturinformationen

Name: Dateien und Struktur.md

Config.py:
Enthält laden und speichern von Benutzereinstellungen.

events.py:
Beinhaltet Event-Handler für Benutzeraktionen (z. B. das Hinzufügen von Frames, das Ändern von Einstellungen, das Auslösen von Vorschau-Updates und das Wechseln der Sprache). Die eigentliche Bildverarbeitung findet hier nicht statt, sondern wird an image_processing.py delegiert.

file_ops.py:
Enthält Funktionen zum Laden und Speichern von GIFs und Texturen sowie zum Exportieren von LSL-Skripten. Keine GUI-Logik.

gui_layout.py:
Definiert die Benutzeroberfläche mit tkinter, insbesondere das Layout und die Erstellung aller Widgets. Hier werden keine Event-Handler oder Bildverarbeitungsfunktionen implementiert.

image_processing.py:
Stellt alle Funktionen zur Bildverarbeitung bereit (Effekte wie Graustufen, Schärfe, Weichzeichnen, Vorschau-Generierung). Keine GUI- oder Event-Logik.

main.py:
Enthält die Hauptklasse (ModernApp), die die GUI initialisiert, die Hauptlogik bündelt und die verschiedenen Module miteinander verbindet. Startet aber nicht direkt die Anwendung.

start.py:
Startskript, das die Anwendung startet, indem es die Hauptklasse aus main.py initialisiert und die Tkinter-Hauptschleife aufruft. Kann auch Umgebungsprüfungen enthalten.

tooltip.py:
Enthält die Klasse für Tooltips, die in der GUI verwendet werden, um Hilfetexte anzuzeigen.

translations.py:
Beinhaltet die Übersetzungen für die mehrsprachige Benutzeroberfläche (Texte für Deutsch, Englisch, Französisch, Spanisch usw.).

---
