import pandas as pd
import os
from datetime import datetime
import json
import time

class CSVManager:
    """Gestionnaire de fichiers CSV pour sauvegarder les données"""
    
    def __init__(self, base_dir="data"):
        self.base_dir = base_dir
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Créer les dossiers nécessaires"""
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(f"{self.base_dir}/agents", exist_ok=True)
        os.makedirs(f"{self.base_dir}/exports", exist_ok=True)
        os.makedirs(f"{self.base_dir}/backups", exist_ok=True)
        os.makedirs(f"{self.base_dir}/by_type", exist_ok=True)
    
    def _safe_save(self, df, filepath, max_retries=3):
        """Sauvegarde sécurisée avec tentatives multiples"""
        for attempt in range(max_retries):
            try:
                df.to_csv(filepath, index=False, encoding='utf-8-sig')
                return True
            except PermissionError:
                if attempt < max_retries - 1:
                    print(f"⚠️ Permission denied, tentative {attempt+2}/{max_retries}")
                    time.sleep(2)
                else:
                    print(f"❌ Impossible d'écrire {filepath}")
                    return False
            except Exception as e:
                print(f"❌ Erreur: {e}")
                return False
        return False
    
    def save_agent_data(self, agent_name, data, format_type='csv'):
        """Sauvegarder les données d'un agent spécifique"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Conversion en DataFrame
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, pd.DataFrame):
            df = data
        else:
            raise ValueError("Les données doivent être une liste ou un DataFrame")
        
        if df.empty:
            print(f"⚠️ Aucune donnée à sauvegarder pour {agent_name}")
            return None
        
        # Nettoyage
        df = self._prepare_for_csv(df)
        
        # Sauvegarde avec horodatage
        filename = f"{self.base_dir}/agents/{agent_name}_{timestamp}.csv"
        success = self._safe_save(df, filename)
        
        if success:
            print(f"✅ Données {agent_name}: {filename} ({len(df)} lignes)")
            
            # Version latest
            latest_file = f"{self.base_dir}/agents/{agent_name}_latest.csv"
            self._safe_save(df, latest_file)
            
            return filename
        return None
    
    def save_consolidated_dataset(self, data_dict, format_type='csv'):
        """Sauvegarder un dataset consolidé de tous les agents"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        all_dfs = []
        stats = {}
        
        for agent_name, data in data_dict.items():
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                continue
            
            if not df.empty:
                df['source_agent'] = agent_name
                all_dfs.append(df)
                stats[agent_name] = len(df)
        
        if not all_dfs:
            print("⚠️ Aucune donnée à consolider")
            return None
        
        consolidated_df = pd.concat(all_dfs, ignore_index=True, sort=False)
        consolidated_df = self._prepare_for_csv(consolidated_df)
        
        filename = f"{self.base_dir}/exports/immobilier_tunisie_{timestamp}.csv"
        success = self._safe_save(consolidated_df, filename)
        
        if success:
            # Version latest
            latest_file = f"{self.base_dir}/exports/immobilier_tunisie_latest.csv"
            self._safe_save(consolidated_df, latest_file)
            
            # Statistiques
            stats_file = f"{self.base_dir}/exports/stats_{timestamp}.json"
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'date': timestamp,
                    'total_annonces': len(consolidated_df),
                    'par_agent': stats,
                    'colonnes': list(consolidated_df.columns)
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Dataset consolidé: {filename} ({len(consolidated_df)} annonces)")
            return filename
        return None
    
    def export_by_type(self, df=None):
        """Exporter les données par type de bien"""
        if df is None:
            df = self.get_latest_dataset()
            if df is None:
                print("❌ Aucun dataset trouvé")
                return
        
        if 'type_bien' not in df.columns:
            print("❌ Colonne 'type_bien' manquante")
            return
        
        print("\n📊 Export par type de bien...")
        
        for type_bien in df['type_bien'].unique():
            if pd.isna(type_bien):
                continue
            
            df_type = df[df['type_bien'] == type_bien]
            filename = f"{self.base_dir}/by_type/{type_bien.replace('/', '_')}.csv"
            df_type.to_csv(filename, index=False, encoding='utf-8-sig')
            print(f"   ✅ {type_bien}: {len(df_type)} annonces")
    
    def _prepare_for_csv(self, df):
        """Préparer le DataFrame pour l'export CSV"""
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda x: 
                    json.dumps(x, ensure_ascii=False) if isinstance(x, (list, dict)) else x)
        
        df = df.fillna('')
        return df
    
    def create_backup(self):
        """Créer une sauvegarde de tous les CSV"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"{self.base_dir}/backups/backup_{timestamp}"
        os.makedirs(backup_dir, exist_ok=True)
        
        import shutil
        copied = 0
        
        for root, dirs, files in os.walk(self.base_dir):
            if 'backups' in root:
                continue
            for file in files:
                if file.endswith(('.csv', '.json')):
                    try:
                        src = os.path.join(root, file)
                        dst = os.path.join(backup_dir, file)
                        shutil.copy2(src, dst)
                        copied += 1
                    except:
                        pass
        
        print(f"✅ Backup: {backup_dir} ({copied} fichiers)")
        return backup_dir
    
    def get_latest_dataset(self):
        """Récupérer le dernier dataset consolidé"""
        latest_file = f"{self.base_dir}/exports/immobilier_tunisie_latest.csv"
        if os.path.exists(latest_file):
            try:
                return pd.read_csv(latest_file)
            except:
                return None
        return None