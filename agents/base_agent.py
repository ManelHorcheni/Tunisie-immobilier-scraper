import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import random
from time import sleep
from datetime import datetime
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import DatabaseManager
from utils.csv_manager import CSVManager
from loguru import logger

class BaseScraperAgent:
    """Classe de base pour tous les scrapers"""
    
    def __init__(self, agent_name, base_url, db_config=None, save_csv=True, use_proxy=False):
        self.agent_name = agent_name
        self.base_url = base_url
        self.db = DatabaseManager(**(db_config or {}))
        self.csv_manager = CSVManager() if save_csv else None
        self.save_csv = save_csv
        self.use_proxy = use_proxy
        self.proxies = self._load_proxies() if use_proxy else None
        
        # Session HTTP avec headers réalistes
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Statistiques
        self.stats = {
            'pages': 0,
            'found': 0,
            'new': 0,
            'updated': 0,
            'errors': 0
        }
        
        # Configuration logging
        logger.add(f"logs/{agent_name}_{{time}}.log", rotation="1 day")
    
    def _load_proxies(self):
        """Charger une liste de proxys (à surcharger si besoin)"""
        return [
            {'http': 'http://proxy1:port', 'https': 'http://proxy1:port'},
            # À compléter avec de vrais proxys
        ]
    
    def get_page(self, url, retries=3, use_selenium=False):
        """Télécharger une page avec gestion d'erreurs"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Safari/605.1.15',
        ]
        
        for attempt in range(retries):
            try:
                # Rotation User-Agent
                self.session.headers.update({
                    'User-Agent': random.choice(user_agents)
                })
                
                # Délai aléatoire
                sleep(random.uniform(2, 5))
                
                # Proxy si activé
                proxies = random.choice(self.proxies) if self.proxies else None
                
                response = self.session.get(url, timeout=15, proxies=proxies)
                
                if response.status_code == 200:
                    return response.text
                elif response.status_code == 404:
                    logger.warning(f"Page 404: {url}")
                    return None
                elif response.status_code == 403:
                    logger.error(f"Accès interdit (403) - {url}")
                    sleep(random.uniform(10, 20))
                else:
                    logger.warning(f"Tentative {attempt+1}: Code {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout sur {url}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erreur de connexion sur {url}")
            except Exception as e:
                logger.error(f"Erreur: {e}")
            
            if attempt < retries - 1:
                sleep(random.uniform(5, 15))
        
        self.stats['errors'] += 1
        return None
    
    def extract_gouvernorat_delegation(self, location_text):
        """Extraire gouvernorat et délégation du texte (à surcharger)"""
        return None, None
    
    def extract_code_postal(self, text):
        """Extraire code postal du texte (à surcharger)"""
        return None
    
    def parse_listing(self, html):
        """À implémenter par chaque agent spécifique"""
        raise NotImplementedError
    
    def scrape(self, max_pages=None):
        """Méthode principale de scraping"""
        raise NotImplementedError
    
    def save_results(self, results):
        """Sauvegarder les résultats en base et CSV"""
        if not results:
            return
        
        for annonce in results:
            try:
                result = self.db.insert_annonce(annonce)
                if result == 'inserted':
                    self.stats['new'] += 1
                elif result == 'updated':
                    self.stats['updated'] += 1
                self.stats['found'] += 1
            except Exception as e:
                logger.error(f"Erreur insertion base: {e}")
                self.stats['errors'] += 1
        
        # Sauvegarde CSV
        if self.save_csv and self.csv_manager:
            self.csv_manager.save_agent_data(self.agent_name, results)
    
    def run(self, max_pages=None):
        """Exécuter le scraper complet"""
        start_time = datetime.now()
        logger.info(f"🚀 Démarrage de {self.agent_name}")
        
        try:
            results = self.scrape(max_pages)
            logger.success(f"✅ {self.agent_name} terminé: {len(results)} annonces")
            
            self.save_results(results)
                
        except Exception as e:
            logger.error(f"❌ Erreur {self.agent_name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            results = []
        
        # Enregistrer les statistiques
        try:
            self.db.log_scraper_run(self.agent_name, {
                **self.stats,
                'status': 'completed' if self.stats['errors'] == 0 else 'completed_with_errors'
            })
        except Exception as e:
            logger.error(f"Erreur sauvegarde stats: {e}")
        
        duration = datetime.now() - start_time
        logger.info(f"⏱️ Temps: {duration.total_seconds():.1f}s")
        
        return results, self.stats