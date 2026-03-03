import pandas as pd           # Manipulation de données et export CSV/Excel
import os                     # Gestion des chemins et dossiers
from datetime import datetime # Pour les timestamps dans les noms de fichiers
import json                   # Conversion des données complexes en JSON

class CSVManager:
    """Gestionnaire de fichiers CSV pour sauvegarder les données"""
    
    #  le gestionnaire avec un dossier de base (par défaut "data")
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir   # Dossier racine des données
        self._ensure_directories() # Crée l'arborescence
    
    def _ensure_directories(self):
        """Créer les dossiers nécessaires s'ils n'existent pas"""
        os.makedirs(self.base_dir, exist_ok=True)              # data/
        os.makedirs(f"{self.base_dir}/agents", exist_ok=True)  # data/agents/
        os.makedirs(f"{self.base_dir}/exports", exist_ok=True) # data/exports/
        os.makedirs(f"{self.base_dir}/backups", exist_ok=True) # data/backups/
    
    def save_agent_data(self, agent_name, data, format_type='csv'):
        """
        Sauvegarder les données d'un agent spécifique
        
        Args:
            agent_name: Nom de l'agent (tunisie_annonce, tayara, etc.)
            data: Liste de dictionnaires ou DataFrame
            format_type: 'csv' ou 'json'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S") # Ex: 20260225_143022
        
        # Convertir en DataFrame si nécessaire
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Les données doivent être une liste ou un DataFrame")
        
        if df.empty:
            print(f"⚠️ Aucune donnée à sauvegarder pour {agent_name}")
            return None
        
        # Nettoyer les données pour le CSV
        df = self._prepare_for_csv(df)
        
        # Sauvegarder au format CSV
        if format_type == 'csv':
            filename = f"{self.base_dir}/agents/{agent_name}_{timestamp}.csv"
            df.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"✅ Données {agent_name} sauvegardées: {filename} ({len(df)} lignes)")
            
            # Sauvegarder aussi une version "latest" pour accès facile
            latest_file = f"{self.base_dir}/agents/{agent_name}_latest.csv"
            df.to_csv(latest_file, index=False, encoding='utf-8-sig')
            
            return filename
        
        # Sauvegarder au format JSON
        elif format_type == 'json':
            filename = f"{self.base_dir}/agents/{agent_name}_{timestamp}.json"
            df.to_json(filename, orient='records', indent=2, force_ascii=False)
            print(f"✅ Données {agent_name} sauvegardées: {filename} ({len(df)} lignes)")
            return filename
    
    def save_consolidated_dataset(self, data_dict, format_type='csv'):
        """
        Sauvegarder un dataset consolidé de tous les agents
        
        Args:
            data_dict: Dictionnaire {agent_name: données}
            format_type: 'csv' ou 'json'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_dfs = []
        stats = {}
        
        # 1. Collecter tous les DataFrames
        for agent_name, data in data_dict.items():
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                continue
            
            if not df.empty:
                df['source_agent'] = agent_name # Ajoute la colonne source
                all_dfs.append(df)
                stats[agent_name] = len(df)
        
        if not all_dfs:
            print("⚠️ Aucune donnée à consolider")
            return None
        
        # 2. Concaténer tous les DataFrames
        consolidated_df = pd.concat(all_dfs, ignore_index=True, sort=False)
        
        # 3. Nettoyer les données
        consolidated_df = self._prepare_for_csv(consolidated_df)
        
        # 4. Sauvegarder le dataset consolidé
        if format_type == 'csv':
            filename = f"{self.base_dir}/exports/immobilier_tunisie_{timestamp}.csv"
            consolidated_df.to_csv(filename, index=False, encoding='utf-8-sig')
            
            # Version latest
            latest_file = f"{self.base_dir}/exports/immobilier_tunisie_latest.csv"
            consolidated_df.to_csv(latest_file, index=False, encoding='utf-8-sig')
        
        elif format_type == 'json':
            filename = f"{self.base_dir}/exports/immobilier_tunisie_{timestamp}.json"
            consolidated_df.to_json(filename, orient='records', indent=2, force_ascii=False)
        
        # 5. Sauvegarder les statistiques JSON
        stats_file = f"{self.base_dir}/exports/stats_{timestamp}.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'date': timestamp,
                'total_annonces': len(consolidated_df),
                'par_agent': stats,
                'colonnes': list(consolidated_df.columns)
            }, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Dataset consolidé sauvegardé: {filename}")
        print(f"📊 Total: {len(consolidated_df)} annonces")
        print(f"📊 Par agent: {stats}")
        
        return filename
    
    def _prepare_for_csv(self, df):
        """Préparer le DataFrame pour l'export CSV"""
        df = df.copy()
        
        # Convertir les listes/dicts en strings
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: 
                    json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
        
        # Remplacer les NaN par des chaînes vides
        df = df.fillna('')
        
        return df
    
    def create_backup(self):
        """Créer une sauvegarde de tous les CSV existants"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"{self.base_dir}/backups/backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        # Copier tous les fichiers CSV
        import shutil
        for root, dirs, files in os.walk(self.base_dir):
            if 'backups' in root: # Évite les backups de backups
                continue
            for file in files:
                if file.endswith('.csv') or file.endswith('.json'):
                    src = os.path.join(root, file)
                    dst = os.path.join(backup_dir, file)
                    shutil.copy2(src, dst)
        
        print(f"✅ Backup créé: {backup_dir}")
        return backup_dir
    
    def get_latest_dataset(self):
        """Récupérer le dernier dataset consolidé"""
        latest_file = f"{self.base_dir}/exports/immobilier_tunisie_latest.csv"
        if os.path.exists(latest_file):
            return pd.read_csv(latest_file)
        return None
    
    def export_for_analysis(self, df, name="analyse", formats=['csv', 'excel']):
        """Exporter pour analyse avec plusieurs formats"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{self.base_dir}/exports/{name}_{timestamp}"
        results = {}
        
        if 'csv' in formats:
            csv_file = f"{base_name}.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            results['csv'] = csv_file
        
        if 'excel' in formats:
            try:
                excel_file = f"{base_name}.xlsx"
                df.to_excel(excel_file, index=False, engine='openpyxl')
                results['excel'] = excel_file
            except:
                print("⚠️ Pour Excel, installez: pip install openpyxl")
        
        if 'json' in formats:
            json_file = f"{base_name}.json"
            df.to_json(json_file, orient='records', indent=2, force_ascii=False)
            results['json'] = json_file
        
        print(f"✅ Export {name} terminé: {results}")
        return results