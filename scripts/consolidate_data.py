#!/usr/bin/env python
"""
Script pour consolider les données de tous les agents
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.csv_manager import CSVManager
import pandas as pd
import glob # Pour trouver des fichiers avec des patterns
from datetime import datetime

def consolidate_all_data():
    """Consolider les données de tous les agents"""
    
    csv_manager = CSVManager()
    
    # Récupérer tous les fichiers CSV des agents
    agent_files = glob.glob("data/agents/*_latest.csv") 
    
    if not agent_files:
        print("❌ Aucun fichier agent trouvé")
        return
    
    # Chargement des données
    all_data = {}
    
    for file in agent_files:
        # Extrait "tunisie_annonce" de "data/agents/tunisie_annonce_latest.csv"
        agent_name = os.path.basename(file).replace('_latest.csv', '')
        df = pd.read_csv(file)
        all_data[agent_name] = df
        print(f"📊 {agent_name}: {len(df)} annonces")
    
    # Créer le dataset consolidé
    csv_manager.save_consolidated_dataset(all_data)
    
    # Créer un backup
    csv_manager.create_backup()
    
    return all_data

def generate_summary_report():
    """Générer un rapport sommaire des données"""
    
    latest_file = "data/exports/immobilier_tunisie_latest.csv"
    if not os.path.exists(latest_file):
        print("❌ Dataset consolidé non trouvé")
        return
    
    df = pd.read_csv(latest_file)
    
    # En-tête du rapport
    print("\n" + "="*60)
    print("📊 RAPPORT DES DONNÉES IMMOBILIÈRES")
    print("="*60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 Total annonces: {len(df)}")
    
    # Statistiques par source
    if 'source_agent' in df.columns:
        print("\n📌 Par source:")
        for source, count in df['source_agent'].value_counts().items():
            print(f"   • {source}: {count} annonces")

    # Statistiques des prix
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
        print(f"\n💰 Statistiques de prix:")
        print(f"   • Moyen: {df['price'].mean():,.0f} DT")
        print(f"   • Médian: {df['price'].median():,.0f} DT")
        print(f"   • Min: {df['price'].min():,.0f} DT")
        print(f"   • Max: {df['price'].max():,.0f} DT")
    
    # Top localisations
    if 'location' in df.columns:
        print("\n📍 Top 5 localisations:")
        for loc, count in df['location'].value_counts().head(5).items():
            print(f"   • {loc}: {count} annonces")
    
    # Types de biens
    if 'property_type' in df.columns:
        print("\n🏠 Types de biens:")
        for ptype, count in df['property_type'].value_counts().head(5).items():
            print(f"   • {ptype}: {count} annonces")
    
    # Sauvegarder le rapport
    report_file = f"data/exports/rapport_{datetime.now().strftime('%Y%m%d')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(str(df.describe()))
    
    print(f"\n✅ Rapport sauvegardé: {report_file}")

if __name__ == "__main__":
    print("🚀 Consolidation des données...")
    consolidate_all_data()
    generate_summary_report()