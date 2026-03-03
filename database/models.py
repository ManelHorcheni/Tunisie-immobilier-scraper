import psycopg2               # Pilote PostgreSQL pour Python
from psycopg2 import sql      # Pour construire des requêtes SQL dynamiques
from datetime import datetime # Pour les timestamps
import logging                # Pour les logs
import json                   # Pour convertir dict → JSON string

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
        self.init_database() # Crée les tables si elles n'existent pas
    
    def get_connection(self):
        """Établir une connexion à la base"""
        return psycopg2.connect(**self.conn_params)
    
    # CRÉATION DES TABLES
    def init_database(self):
        """Initialiser les tables si elles n'existent pas"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Table principale des annonces (avec colonnes TEXT pour éviter les problèmes JSON)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS annonces (
                    id SERIAL PRIMARY KEY,
                    source_site VARCHAR(50) NOT NULL,
                    site_url VARCHAR(255),
                    title TEXT,
                    description TEXT,
                    price NUMERIC,
                    price_text VARCHAR(50),
                    property_type VARCHAR(100),
                    location VARCHAR(255),
                    city VARCHAR(100),
                    region VARCHAR(100),
                    surface NUMERIC,
                    rooms INTEGER,
                    bedrooms INTEGER,
                    bathrooms INTEGER,
                    floor INTEGER,
                    total_floors INTEGER,
                    furnished BOOLEAN DEFAULT FALSE,
                    new_building BOOLEAN DEFAULT FALSE,
                    with_photo BOOLEAN DEFAULT FALSE,
                    photo_urls TEXT,
                    publication_date TIMESTAMP,
                    scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    agent_name VARCHAR(100),
                    phone VARCHAR(50),
                    email VARCHAR(100),
                    link TEXT UNIQUE,
                    status VARCHAR(20) DEFAULT 'active',
                    views INTEGER DEFAULT 0,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour les recherches fréquentes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_source ON annonces(source_site)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_location ON annonces(location)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_price ON annonces(price)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_date ON annonces(publication_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON annonces(property_type)")
            
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
                    total_annonces INTEGER DEFAULT 0,
                    nouvelles_annonces INTEGER DEFAULT 0,
                    prix_moyen NUMERIC,
                    prix_min NUMERIC,
                    prix_max NUMERIC,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(stat_date, source_site)
                )
            """)
            
            conn.commit()
            logging.info("✅ Base de données initialisée avec succès")
            
        except Exception as e:
            logging.error(f"❌ Erreur initialisation DB: {e}")
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
            
            # Vérifier si l'annonce existe déjà (par lien)
            cursor.execute("SELECT id FROM annonces WHERE link = %s", (annonce_data['link'],))
            existing = cursor.fetchone()
            
            # Convertir les dictionnaires en chaînes JSON
            metadata_str = json.dumps(annonce_data.get('metadata', {})) if annonce_data.get('metadata') else None
            photo_urls_str = json.dumps(annonce_data.get('photo_urls', [])) if annonce_data.get('photo_urls') else None
            
            if existing:
                # Mise à jour : l'annonce existe déjà
                query = """
                    UPDATE annonces SET
                        title = COALESCE(%s, title),
                        price = COALESCE(%s, price),
                        price_text = COALESCE(%s, price_text),
                        property_type = COALESCE(%s, property_type),
                        location = COALESCE(%s, location),
                        city = COALESCE(%s, city),
                        region = COALESCE(%s, region),
                        publication_date = COALESCE(%s, publication_date),
                        with_photo = COALESCE(%s, with_photo),
                        photo_urls = COALESCE(%s, photo_urls),
                        metadata = COALESCE(%s, metadata),
                        updated_at = CURRENT_TIMESTAMP
                    WHERE link = %s
                """
                cursor.execute(query, (
                    annonce_data.get('title'),
                    annonce_data.get('price_numeric'),
                    annonce_data.get('price_text'),
                    annonce_data.get('property_type'),
                    annonce_data.get('location'),
                    annonce_data.get('city'),
                    annonce_data.get('region'),
                    annonce_data.get('publication_date'),
                    annonce_data.get('with_photo', False),
                    photo_urls_str,
                    metadata_str,
                    annonce_data['link']
                ))
                result = 'updated'
            else:
                # Insertion
                query = """
                    INSERT INTO annonces (
                        source_site, site_url, title, description, price, price_text,
                        property_type, location, city, region, surface, rooms,
                        bedrooms, bathrooms, furnished, new_building, with_photo,
                        photo_urls, publication_date, agent_name, phone, email,
                        link, metadata
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                             %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(query, (
                    annonce_data.get('source_site'),
                    annonce_data.get('site_url'),
                    annonce_data.get('title'),
                    annonce_data.get('description'),
                    annonce_data.get('price_numeric'),
                    annonce_data.get('price_text'),
                    annonce_data.get('property_type'),
                    annonce_data.get('location'),
                    annonce_data.get('city'),
                    annonce_data.get('region'),
                    annonce_data.get('surface'),
                    annonce_data.get('rooms'),
                    annonce_data.get('bedrooms'),
                    annonce_data.get('bathrooms'),
                    annonce_data.get('furnished', False),
                    annonce_data.get('new_building', False),
                    annonce_data.get('with_photo', False),
                    photo_urls_str,
                    annonce_data.get('publication_date'),
                    annonce_data.get('agent_name'),
                    annonce_data.get('phone'),
                    annonce_data.get('email'),
                    annonce_data.get('link'),
                    metadata_str
                ))
                result = 'inserted'
            
            conn.commit()
            return result
            
        except Exception as e:
            logging.error(f"❌ Erreur insertion: {e}")
            logging.error(f"Donnée problématique: {annonce_data.get('link')}")
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
            
            # Convertir les stats en JSON string si nécessaire
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
            cursor.execute("""
                SELECT source_site, COUNT(*) 
                FROM annonces 
                GROUP BY source_site
            """)
            par_source = cursor.fetchall()
            
            # Statistiques des prix
            cursor.execute("""
                SELECT 
                    AVG(price) as prix_moyen,
                    MIN(price) as prix_min,
                    MAX(price) as prix_max
                FROM annonces 
                WHERE price IS NOT NULL
            """)
            prix_stats = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return {
                'total': total,
                'par_source': dict(par_source),
                'prix_moyen': prix_stats[0],
                'prix_min': prix_stats[1],
                'prix_max': prix_stats[2]
            }
        except Exception as e:
            logging.error(f"❌ Erreur stats: {e}")
            return {}