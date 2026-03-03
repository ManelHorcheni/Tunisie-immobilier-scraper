#!/usr/bin/env python
"""
Script pour lancer tous les agents (Requests + Selenium)
"""
import sys
import os
import time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.agent_tunisie_annonce.scraper import TunisieAnnonceAgent
from agents.agent_tayara.scraper import TayaraSeleniumAgent  # Nouvel agent
from utils.csv_manager import CSVManager
import pandas as pd

def run_all_agents(max_pages_per_agent=5):
    """Lancer tous les agents et consolider les résultats"""
    
    print("="*60)
    print("🚀 LANCEMENT DE TOUS LES AGENTS")
    print("="*60)
    start_time = datetime.now()
    
    csv_manager = CSVManager()
    all_results = {}
    all_stats = {}
    
    # Agent Tunisie Annonce (Requests)
    print(f"\n Lancement de Tunisie Annonce (Requests)...")
    try:
        agent = TunisieAnnonceAgent(save_csv=True)
        results, stats = agent.run(max_pages=max_pages_per_agent)
        all_results['tunisie_annonce'] = results
        all_stats['Tunisie Annonce'] = stats
        print(f"✅ Tunisie Annonce: {len(results)} annonces")
    except Exception as e:
        print(f"❌ Erreur Tunisie Annonce: {e}")
    
    # Pause de 10 secondes entre les agents
    time.sleep(10)
    
    # Agent Tayara (Selenium)
    print(f"\n Lancement de Tayara (Selenium)...")
    try:
        agent = TayaraSeleniumAgent(save_csv=True, headless=False)
        results, stats = agent.run(max_pages=max_pages_per_agent)
        all_results['tayara'] = results
        all_stats['Tayara'] = stats
        print(f"✅ Tayara: {len(results)} annonces")
    except Exception as e:
        print(f"❌ Erreur Tayara: {e}")
    
    # Consolider les données
    print("\n" + "="*60)
    print("📊 CONSOLIDATION DES DONNÉES")
    print("="*60)
    
    # Convertir les résultats en DataFrames
    dfs = {}
    for agent_key, results in all_results.items():
        if results and len(results) > 0:
            dfs[agent_key] = pd.DataFrame(results)
            print(f"📊 {agent_key}: {len(results)} annonces")
    
    if dfs:
        csv_manager.save_consolidated_dataset(dfs)
        csv_manager.create_backup()
    
    # Afficher les statistiques
    print("\n📈 STATISTIQUES D'EXÉCUTION")
    print("-" * 40)
    for agent_name, stats in all_stats.items():
        print(f"\n{agent_name}:")
        print(f"   • Pages: {stats.get('pages', 0)}")
        print(f"   • Annonces: {stats.get('found', 0)}")
        print(f"   • Nouvelles: {stats.get('new', 0)}")
        print(f"   • Erreurs: {stats.get('errors', 0)}")
    
    # Temps d'exécution
    end_time = datetime.now()
    duration = end_time - start_time
    print(f"\n⏱️  Temps total: {duration.total_seconds():.1f} secondes")
    
    return all_results, all_stats

if __name__ == "__main__":
    run_all_agents(max_pages_per_agent=3)