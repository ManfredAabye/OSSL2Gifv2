#!/usr/bin/env python3
"""
Update-Script für PyOSSL2Gif Abhängigkeiten
============================================

Dieses Script prüft automatisch, ob Updates für die verwendeten Bibliotheken
verfügbar sind und bietet optionale Installation an.

Verwendung:
    python update_dependencies.py

"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, shell=False):
    """Führt einen Shell-Befehl aus und gibt Ausgabe zurück."""
    try:
        result = subprocess.run(
            cmd,
            shell=shell,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Fehler bei Befehl: {' '.join(cmd)}")
        print(f"   {e.stderr}")
        return None


def get_installed_version(package):
    """Holt die installierte Version eines Pakets."""
    output = run_command([sys.executable, "-m", "pip", "show", package])
    if output:
        for line in output.split('\n'):
            if line.startswith('Version:'):
                return line.split(':', 1)[1].strip()
    return None


def get_latest_version(package):
    """Holt die neueste verfügbare Version eines Pakets."""
    output = run_command([sys.executable, "-m", "pip", "index", "versions", package])
    if output:
        for line in output.split('\n'):
            if line.startswith(package):
                # Format: "packagename (version)"
                return line.split('(')[1].split(')')[0].strip()
    return None


def check_updates():
    """Prüft alle Abhängigkeiten auf Updates."""
    packages = [
        ("Pillow", "Bildverarbeitung"),
        ("ttkbootstrap", "GUI-Framework"),
        ("pyinstaller", "Build-Tool")
    ]
    
    print("=" * 70)
    print("📦 PyOSSL2Gif - Abhängigkeiten-Prüfung")
    print("=" * 70)
    print()
    
    updates_available = []
    
    for package, description in packages:
        print(f"🔍 Prüfe {package} ({description})...")
        
        installed = get_installed_version(package)
        if not installed:
            print(f"   ⚠️  Nicht installiert!")
            updates_available.append((package, None, "nicht installiert"))
            continue
        
        latest = get_latest_version(package)
        if not latest:
            print(f"   ⚠️  Konnte neueste Version nicht ermitteln")
            continue
        
        if installed != latest:
            print(f"   📦 Installiert: {installed}")
            print(f"   ✨ Verfügbar:   {latest}")
            print(f"   🔼 Update verfügbar!")
            updates_available.append((package, installed, latest))
        else:
            print(f"   ✅ Aktuell: {installed}")
        
        print()
    
    return updates_available


def update_requirements_file(updates):
    """Aktualisiert die requirements.txt mit neuen Versionen."""
    req_file = Path(__file__).parent / "requirements.txt"
    
    if not req_file.exists():
        print("❌ requirements.txt nicht gefunden!")
        return False
    
    content = req_file.read_text(encoding='utf-8')
    
    for package, old_version, new_version in updates:
        if old_version and old_version != "nicht installiert":
            # Ersetze alte Version mit neuer
            old_line = f"{package}=={old_version}"
            new_line = f"{package}=={new_version}"
            content = content.replace(old_line, new_line)
    
    req_file.write_text(content, encoding='utf-8')
    print(f"✅ requirements.txt aktualisiert!")
    return True


def install_updates(packages_to_update):
    """Installiert Updates für die angegebenen Pakete."""
    print("\n" + "=" * 70)
    print("📥 Installiere Updates...")
    print("=" * 70)
    print()
    
    for package, _, version in packages_to_update:
        print(f"⬇️  Installiere {package}=={version}...")
        cmd = [sys.executable, "-m", "pip", "install", f"{package}=={version}"]
        result = run_command(cmd)
        
        if result is not None:
            print(f"   ✅ {package} erfolgreich aktualisiert!")
        else:
            print(f"   ❌ Fehler beim Update von {package}")
        print()


def main():
    """Hauptfunktion."""
    print("\n")
    
    # Prüfe auf Updates
    updates = check_updates()
    
    if not updates:
        print("=" * 70)
        print("✅ Alle Abhängigkeiten sind aktuell!")
        print("=" * 70)
        return
    
    # Zeige Zusammenfassung
    print("=" * 70)
    print(f"📋 Zusammenfassung: {len(updates)} Update(s) verfügbar")
    print("=" * 70)
    for package, old, new in updates:
        if old and old != "nicht installiert":
            print(f"   • {package}: {old} → {new}")
        else:
            print(f"   • {package}: {new} (neu installieren)")
    print()
    
    # Frage Benutzer
    response = input("Möchten Sie die Updates installieren? (j/n): ").lower().strip()
    
    if response in ['j', 'ja', 'y', 'yes']:
        install_updates(updates)
        
        # Aktualisiere requirements.txt
        response = input("requirements.txt mit neuen Versionen aktualisieren? (j/n): ").lower().strip()
        if response in ['j', 'ja', 'y', 'yes']:
            update_requirements_file(updates)
        
        print("\n" + "=" * 70)
        print("✅ Update-Prozess abgeschlossen!")
        print("=" * 70)
        print("\n💡 Tipp: Teste die Anwendung jetzt:")
        print("   python start.py")
        print()
    else:
        print("\n❌ Update abgebrochen.")
        print("💡 Um später zu aktualisieren:")
        print("   pip install --upgrade -r requirements.txt")
        print()


if __name__ == "__main__":
    main()
