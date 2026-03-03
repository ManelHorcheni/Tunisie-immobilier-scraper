"""
Script d'analyse des données pour Jupyter Notebook ou script Python
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def load_latest_data():
    """Charger le dernier dataset consolidé"""
    latest_file = "data/exports/immobilier_tunisie_latest.csv"
    if os.path.exists(latest_file):
        df = pd.read_csv(latest_file)
        print(f"✅ Données chargées: {len(df)} annonces")
        return df
    else:
        print("❌ Fichier non trouvé")
        return None

def analyse_prix_par_localisation(df):
    """Analyser les prix par localisation"""
    if 'price' not in df.columns or 'location' not in df.columns:
        return
    
    # Nettoyer les prix
    df['price_clean'] = pd.to_numeric(df['price'], errors='coerce')
    
    # Top 10 localisations avec le plus d'annonces
    top_locs = df['location'].value_counts().head(10).index
    df_top = df[df['location'].isin(top_locs)]
    
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_top, x='location', y='price_clean')
    plt.xticks(rotation=45)
    plt.title('Distribution des prix par localisation (Top 10)')
    plt.tight_layout()
    plt.savefig('data/exports/prix_par_localisation.png')
    plt.show()

def analyse_par_source(df):
    """Analyser les données par source"""
    if 'source_agent' not in df.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Nombre d'annonces par source
    source_counts = df['source_agent'].value_counts()
    axes[0].pie(source_counts.values, labels=source_counts.index, autopct='%1.1f%%')
    axes[0].set_title('Répartition par source')
    
    # Prix moyen par source
    if 'price' in df.columns:
        df['price_clean'] = pd.to_numeric(df['price'], errors='coerce')
        prix_moyen = df.groupby('source_agent')['price_clean'].mean().sort_values()
        axes[1].barh(prix_moyen.index, prix_moyen.values)
        axes[1].set_title('Prix moyen par source (DT)')
        axes[1].set_xlabel('Prix moyen (DT)')
    
    plt.tight_layout()
    plt.savefig('data/exports/analyse_par_source.png')
    plt.show()

def exporter_statistics(df):
    """Exporter les statistiques détaillées"""
    stats = {
        'total_annonces': len(df),
        'prix_moyen': df['price_clean'].mean() if 'price_clean' in df.columns else None,
        'prix_median': df['price_clean'].median() if 'price_clean' in df.columns else None,
        'nb_localisations': df['location'].nunique() if 'location' in df.columns else None,
        'nb_types': df['property_type'].nunique() if 'property_type' in df.columns else None,
    }
    
    # Statistiques par source
    if 'source_agent' in df.columns:
        stats['par_source'] = df['source_agent'].value_counts().to_dict()
    
    # Exporter en JSON
    import json
    with open('data/exports/statistiques.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print("✅ Statistiques exportées dans data/exports/statistiques.json")

if __name__ == "__main__":
    df = load_latest_data()
    if df is not None:
        print("\n📊 Analyse des données...")
        analyse_prix_par_localisation(df)
        analyse_par_source(df)
        exporter_statistics(df)