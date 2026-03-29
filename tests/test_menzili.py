import sys
import os
print("="*50)
print("🔍 TEST DE L'AGENT MENZILI")
print("="*50)

# Afficher le chemin courant
print(f"📁 Dossier courant: {os.getcwd()}")

# Tester l'import du module base_agent
try:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    print(f"📂 Path ajouté: {os.path.dirname(os.path.dirname(os.path.abspath(__file__)))}")
    
    from agents.base_agent import BaseScraperAgent
    print("✅ BaseScraperAgent importé avec succès")
except Exception as e:
    print(f"❌ Erreur import BaseScraperAgent: {e}")

# Tester l'import des modules de config
try:
    from config.features_config import GOVERNORATES
    print(f"✅ features_config importé - {len(GOVERNORATES)} gouvernorats trouvés")
except Exception as e:
    print(f"❌ Erreur import features_config: {e}")

# Tester l'import du scraper
try:
    from agents.agent_menzili.scraper import MenziliAgent
    print("✅ MenziliAgent importé avec succès")
except Exception as e:
    print(f"❌ Erreur import MenziliAgent: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("📋 VÉRIFICATION DE LA STRUCTURE")
print("="*50)

# Lister les fichiers dans agents/agent_menzili/
menzili_dir = os.path.join("agents", "agent_menzili")
if os.path.exists(menzili_dir):
    print(f"✅ Dossier {menzili_dir} trouvé")
    files = os.listdir(menzili_dir)
    print(f"📄 Fichiers: {files}")
else:
    print(f"❌ Dossier {menzili_dir} non trouvé")

# Vérifier le fichier scraper.py
scraper_file = os.path.join(menzili_dir, "scraper.py")
if os.path.exists(scraper_file):
    print(f"✅ Fichier scraper.py trouvé")
else:
    print(f"❌ Fichier scraper.py manquant")