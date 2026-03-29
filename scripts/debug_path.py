import sys
import os

print("="*60)
print("🔍 DIAGNOSTIC COMPLET DES CHEMINS")
print("="*60)

# 1. Dossier courant
print(f"\n📁 Dossier courant: {os.getcwd()}")

# 2. Contenu du dossier courant
print("\n📋 Contenu du dossier courant:")
for item in os.listdir('.'):
    print(f"   - {item}")

# 3. Chemin absolu du script
script_path = os.path.abspath(__file__)
print(f"\n📄 Chemin du script: {script_path}")

# 4. Tenter différents chemins
print("\n🔄 Test de différents chemins:")

chemins_a_tester = [
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    os.path.dirname(os.path.abspath(__file__)),
    "C:\\Users\\Thinkpad\\Desktop\\TunisieImmoMultiAgents",
]

for i, chemin in enumerate(chemins_a_tester):
    print(f"\nChemin {i+1}: {chemin}")
    if os.path.exists(chemin):
        print(f"   ✅ Existe")
        sys.path.insert(0, chemin)
        try:
            from agents.base_agent import BaseScraperAgent
            print(f"   ✅ IMPORT RÉUSSI avec ce chemin !")
            break
        except ImportError as e:
            print(f"   ❌ Import échoué: {e}")
    else:
        print(f"   ❌ N'existe pas")

print("\n" + "="*60)
input("Appuyez sur Entrée pour quitter...")