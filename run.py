#!/usr/bin/env python
"""
Script principal pour lancer tous les composants
"""
import subprocess
import sys
import os
from pathlib import Path

def main():
    print("="*60)
    print("🏠 PROJET IMMOBILIER MULTI-AGENTS")
    print("="*60)
    
    # Vérifier l'environnement
    if not os.path.exists('venv'):
        print("❌ Environnement virtuel non trouvé")
        print("Exécutez d'abord: python -m venv venv")
        return
    
    print("\n📦 Composants disponibles:")
    print("1. 🔧 Initialiser la base de données")
    print("2. 🕷️  Lancer le scraper Tunisie Annonce")
    print("3. 🕷️  Lancer le scraper Tayara")
    print("4. 🌐 Lancer l'API Flask")
    print("5. 📊 Lancer le dashboard")
    print("6. 🚀 Tout lancer")
    print("7. ❌ Quitter")
    
    choice = input("\n📌 Votre choix (1-7): ")
    
    if choice == '1':
        print("\n🔧 Initialisation de la base...")
        subprocess.run([sys.executable, "database/models.py"])
    
    elif choice == '2':
        print("\n🕷️  Lancement scraper Tunisie Annonce...")
        subprocess.run([sys.executable, "agents/agent_tunisie_annonce/scraper.py"])
    
    elif choice == '3':
        print("\n🕷️  Lancement scraper Tayara...")
        subprocess.run([sys.executable, "agents/agent_tayara/scraper.py"])
    
    elif choice == '4':
        print("\n🌐 Lancement API Flask...")
        subprocess.run([sys.executable, "api/app.py"])
    
    elif choice == '5':
        print("\n📊 Lancement dashboard...")
        subprocess.run([sys.executable, "dashboard.py"])
    
    elif choice == '6':
        print("\n🚀 Lancement de tous les composants...")
        print("📌 Démarrer l'API dans un terminal séparé")
        print("📌 Démarrer le dashboard dans un autre terminal")
    
    elif choice == '7':
        print("\n👋 Au revoir!")
        return

if __name__ == "__main__":
    main()