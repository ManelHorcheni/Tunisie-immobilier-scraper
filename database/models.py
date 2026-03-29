import psycopg2
from psycopg2 import sql
from datetime import datetime
import logging
import json

# Configuration du logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseManager:
    """Gestionnaire de base de données pour tous les agents"""
    
    def __init__(self, dbname="immo_tunisie_multi", user="postgres", 
                 password="admin", host="localhost", port="5432"):
        self.conn_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.init_database()
    
    def get_connection(self):
        """Établir une connexion à la base"""
        try:
            conn = psycopg2.connect(**self.conn_params)
            return conn
        except Exception as e:
            logging.error(f"❌ Erreur de connexion: {e}")
            raise
    
    def init_database(self):
        """Initialiser les tables avec le schéma complet des features"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Table principale des annonces
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS annonces (
                    id SERIAL PRIMARY KEY,
                    
                    -- Identifiants
                    source_site VARCHAR(50) NOT NULL,
                    code_annonce VARCHAR(100),
                    url_annonce TEXT UNIQUE,
                    
                    -- Classification
                    nature VARCHAR(50),
                    type_bien VARCHAR(100),
                    
                    -- Localisation
                    gouvernorat VARCHAR(100),
                    delegation VARCHAR(100),
                    localite VARCHAR(100),
                    code_postal VARCHAR(10),
                    
                    -- Caractéristiques de base
                    prix NUMERIC,
                    superficie_m2 NUMERIC,
                    date_publication TIMESTAMP,
                    titre_foncier VARCHAR(100),
                    
                    -- Champs Maison & Appartement
                    etat VARCHAR(50),
                    standing VARCHAR(50),
                    nb_chambres INTEGER,
                    nb_sdb INTEGER,
                    dressing BOOLEAN DEFAULT FALSE,
                    balcon BOOLEAN DEFAULT FALSE,
                    vue_mer BOOLEAN DEFAULT FALSE,
                    parking BOOLEAN DEFAULT FALSE,
                    piscine BOOLEAN DEFAULT FALSE,
                    chauffage_central BOOLEAN DEFAULT FALSE,
                    climatisation BOOLEAN DEFAULT FALSE,
                    jardin BOOLEAN DEFAULT FALSE,
                    
                    -- Champs spécifiques Maison
                    terrasse BOOLEAN DEFAULT FALSE,
                    niveau_maison VARCHAR(50),
                    
                    -- Champs spécifiques Appartement
                    etage_appart VARCHAR(50),
                    ascenseur BOOLEAN DEFAULT FALSE,
                    syndic BOOLEAN DEFAULT FALSE,
                    
                    -- Champs spécifiques Terrain
                    terrain_viabilise BOOLEAN DEFAULT FALSE,
                    constructible BOOLEAN DEFAULT FALSE,
                    dimensions_terrain VARCHAR(100),
                    zone VARCHAR(100),
                    facade BOOLEAN DEFAULT FALSE,
                    acces_route BOOLEAN DEFAULT FALSE,
                    acces_electricite BOOLEAN DEFAULT FALSE,
                    acces_eau BOOLEAN DEFAULT FALSE,
                    vocation VARCHAR(100),
                    
                    -- Métadonnées
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    
                    -- Dates de scraping
                    scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour optimiser les recherches
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON annonces(source_site)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type_bien ON annonces(type_bien)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_gouvernorat ON annonces(gouvernorat)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_prix ON annonces(prix)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON annonces(date_publication)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_code_postal ON annonces(code_postal)")
            
            # Table pour les logs des scrapers
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraper_logs (
                    id SERIAL PRIMARY KEY,
                    agent_name VARCHAR(50) NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    pages_scraped INTEGER DEFAULT 0,
                    items_found INTEGER DEFAULT 0,
                    items_new INTEGER DEFAULT 0,
                    items_updated INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    status VARCHAR(20) DEFAULT 'running',
                    error_message TEXT,
                    details TEXT
                )
            """)
            
            # Table pour les statistiques quotidiennes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS daily_stats (
                    id SERIAL PRIMARY KEY,
                    stat_date DATE DEFAULT CURRENT_DATE,
                    source_site VARCHAR(50),
                    type_bien VARCHAR(100),
                    total_annonces INTEGER DEFAULT 0,
                    nouvelles_annonces INTEGER DEFAULT 0,
                    prix_moyen NUMERIC,
                    prix_min NUMERIC,
                    prix_max NUMERIC,
                    superficie_moyenne NUMERIC,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stat_date, source_site, type_bien)
                )
            """)
            
            conn.commit()
            logging.info("✅ Base de données initialisée avec succès")
            
        except Exception as e:
            logging.error(f"❌ Erreur initialisation DB: {e}")
            raise
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def insert_annonce(self, annonce_data):
        """Insérer ou mettre à jour une annonce"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Vérifier si l'annonce existe déjà
            url_annonce = annonce_data.get('url_annonce')
            if not url_annonce:
                logging.error("❌ url_annonce manquant")
                return 'error'
            
            cursor.execute("SELECT id FROM annonces WHERE url_annonce = %s", (url_annonce,))
            existing = cursor.fetchone()
            
            # Convertir les métadonnées en JSON
            metadata_str = json.dumps(annonce_data.get('metadata', {})) if annonce_data.get('metadata') else None
            
            # Préparer les colonnes et valeurs
            columns = []
            values = []
            placeholders = []
            
            for key, value in annonce_data.items():
                if key not in ['metadata'] and value is not None:
                    columns.append(key)
                    placeholders.append('%s')
                    values.append(value)
            
            if existing:
                # Mise à jour
                set_clauses = [f"{col} = %s" for col in columns]
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                query = f"UPDATE annonces SET {', '.join(set_clauses)} WHERE url_annonce = %s"
                values.append(url_annonce)
                cursor.execute(query, values)
                result = 'updated'
            else:
                # Insertion
                columns.append('metadata')
                placeholders.append('%s')
                values.append(metadata_str)
                
                query = f"INSERT INTO annonces ({', '.join(columns)}) VALUES ({', '.join(placeholders)})"
                cursor.execute(query, values)
                result = 'inserted'
            
            conn.commit()
            return result
            
        except Exception as e:
            logging.error(f"❌ Erreur insertion: {e}")
            import traceback
            traceback.print_exc()
            return 'error'
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def log_scraper_run(self, agent_name, stats):
        """Enregistrer une exécution du scraper"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            details_str = json.dumps(stats.get('details', {})) if stats.get('details') else None
            
            cursor.execute("""
                INSERT INTO scraper_logs (
                    agent_name, end_time, pages_scraped, items_found,
                    items_new, items_updated, errors, status, details
                ) VALUES (%s, CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s)
            """, (
                agent_name,
                stats.get('pages', 0),
                stats.get('found', 0),
                stats.get('new', 0),
                stats.get('updated', 0),
                stats.get('errors', 0),
                stats.get('status', 'completed'),
                details_str
            ))
            
            conn.commit()
            logging.info(f"✅ Log enregistré pour {agent_name}")
            
        except Exception as e:
            logging.error(f"❌ Erreur log: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    def get_stats(self):
        """Récupérer des statistiques générales"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Total général
            cursor.execute("SELECT COUNT(*) FROM annonces")
            total = cursor.fetchone()[0]
            
            # Répartition par source
            cursor.execute("SELECT source_site, COUNT(*) FROM annonces GROUP BY source_site")
            par_source = dict(cursor.fetchall())
            
            # Répartition par type de bien
            cursor.execute("SELECT type_bien, COUNT(*) FROM annonces WHERE type_bien IS NOT NULL GROUP BY type_bien")
            par_type = dict(cursor.fetchall())
            
            # Statistiques des prix
            cursor.execute("""
                SELECT 
                    AVG(prix) as prix_moyen,
                    MIN(prix) as prix_min,
                    MAX(prix) as prix_max
                FROM annonces 
                WHERE prix IS NOT NULL
            """)
            prix_stats = cursor.fetchone()
            
            # Statistiques des superficies
            cursor.execute("""
                SELECT 
                    AVG(superficie_m2) as superficie_moyenne,
                    MIN(superficie_m2) as superficie_min,
                    MAX(superficie_m2) as superficie_max
                FROM annonces 
                WHERE superficie_m2 IS NOT NULL
            """)
            superficie_stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'total': total,
                'par_source': par_source,
                'par_type': par_type,
                'prix_moyen': prix_stats[0] if prix_stats else None,
                'prix_min': prix_stats[1] if prix_stats else None,
                'prix_max': prix_stats[2] if prix_stats else None,
                'superficie_moyenne': superficie_stats[0] if superficie_stats else None,
                'superficie_min': superficie_stats[1] if superficie_stats else None,
                'superficie_max': superficie_stats[2] if superficie_stats else None,
            }
        except Exception as e:
            logging.error(f"❌ Erreur stats: {e}")
            return {}
    
    def get_annonces_by_type(self, type_bien, limit=100):
        """Récupérer les annonces d'un type spécifique"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM annonces 
                WHERE type_bien = %s 
                ORDER BY date_publication DESC
                LIMIT %s
            """, (type_bien, limit))
            
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            
            result = [dict(zip(columns, row)) for row in rows]
            
            cursor.close()
            conn.close()
            
            return result
        except Exception as e:
            logging.error(f"❌ Erreur get_annonces_by_type: {e}")
            return []


if __name__ == "__main__":
    print("="*60)
    print("🚀 INITIALISATION DE LA BASE DE DONNÉES")
    print("="*60)
    
    db = DatabaseManager()
    print("✅ Base de données prête!")