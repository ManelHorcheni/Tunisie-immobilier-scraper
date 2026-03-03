import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import random
from time import sleep
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import DatabaseManager
from utils.csv_manager import CSVManager
from loguru import logger

class BaseScraperAgent:
    """Classe de base pour tous les scrapers"""
    
    def __init__(self, agent_name, base_url, db_config=None, save_csv=True):
        self.agent_name = agent_name # Nom unique de l'agent
        self.base_url = base_url     # URL de base du site
        self.db = DatabaseManager(**(db_config or {}))        # Connexion DB
        self.csv_manager = CSVManager() if save_csv else None # Sauvegarde CSV
        self.save_csv = save_csv     # Flag pour sauvegarder en CSV
        
        # Configuration avancée de la session
        # Session HTTP avec headers réalistes
        self.session = requests.Session()
        self.session.headers.update({ 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }) # Simule un vrai navigateur
        
        # Statistiques de l'agent
        self.stats = {
            'pages': 0,   # Pages scrapées
            'found': 0,   # Annonces trouvées
            'new': 0,     # Nouvelles annonces
            'updated': 0, # Annonces mises à jour
            'errors': 0   # Erreurs rencontrées
        }
        
        # Configuration des logs (fichier par agent)
        logger.add(f"logs/{agent_name}_{{time}}.log", rotation="1 day")
    
    def get_page(self, url, retries=3):
        """Télécharger une page avec gestion d'erreurs et rotation d'user-agents"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36 Edg/90.0.818.66'
        ] # Liste de User-Agents pour rotation
        
        for attempt in range(retries):
            try:
                # Changer l'user-agent à chaque tentative
                self.session.headers.update({
                    'User-Agent': random.choice(user_agents)
                })
                
                # Délai aléatoire pour éviter la détection
                sleep(random.uniform(2, 5))
                
                # Requête HTTP avec timeout
                response = self.session.get(url, timeout=15)
                
                # Gestion des codes HTTP
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.warning(f"Page 404: {url}")
                    return None
                elif response.status_code == 403:
                    logger.error(f"Accès interdit (403) - Le site bloque peut-être les robots")
                    sleep(random.uniform(10, 20))  # Pause plus longue
                else:
                    logger.warning(f"Tentative {attempt+1}: Code {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout sur {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erreur de connexion sur {url}")
            except Exception as e:
                logger.error(f"Erreur téléchargement: {e}")
            
            # Pause avant nouvelle tentative
            if attempt < retries - 1:
                sleep(random.uniform(5, 15))
        
        self.stats['errors'] += 1
        return None
    
    def parse_listing(self, html):
        """À implémenter par chaque agent spécifique"""
        raise NotImplementedError
    
    def scrape(self, max_pages=None):
        """Méthode principale de scraping"""
        raise NotImplementedError
    
    def run(self, max_pages=None):
        """Exécuter le scraper avec logging et sauvegarde CSV"""
        start_time = datetime.now()
        logger.info(f"🚀 Démarrage de {self.agent_name}")
        
        try:
            # Appel de la méthode scrape (implémentée par l'enfant)
            results = self.scrape(max_pages)
            logger.info(f"✅ {self.agent_name} terminé: {len(results)} annonces")
            
            # Sauvegarde CSV des résultats
            if self.save_csv and self.csv_manager and results:
                self.csv_manager.save_agent_data(self.agent_name, results)
                
        except Exception as e:
            logger.error(f"❌ Erreur {self.agent_name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            results = []
        
        # Enregistrer les statistiques en db
        self.db.log_scraper_run(self.agent_name, {
            **self.stats,
            'status': 'completed' if self.stats['errors'] == 0 else 'completed_with_errors'
        })
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏱️  Temps d'exécution: {duration.total_seconds():.1f} secondes")
        
        return results, self.stats