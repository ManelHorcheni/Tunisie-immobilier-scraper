import sys
import os
import time
import re
import random
from datetime import datetime

# Ajouter le chemin racine du projet au PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Imports Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

# Imports du projet
from agents.base_agent import BaseScraperAgent
from utils.csv_manager import CSVManager
from loguru import logger

class TayaraAgent(BaseScraperAgent):
    """Agent spécialisé pour Tayara.tn utilisant Selenium"""
    
    def __init__(self, db_config=None, save_csv=True, headless=False):
        super().__init__(
            agent_name="tayara",
            base_url="https://www.tayara.tn",
            db_config=db_config,
            save_csv=save_csv
        )
        self.headless = headless # Mode invisible si True
        self.driver = None       # Navigateur Selenium
        self.wait_time = 10      # Timeout d'attente
        
        # URLs à tester (car la structure change souvent)
        self.search_urls = [
            "/immobilier/vente/",
            "/annonces/immobilier/vente/",
            "/c/immobilier/vente/",
            "/fr/immobilier/vente/",
            "/properties/for-sale/",
            "/immobilier/",
            "/annonces/immobilier/"
        ]
        
        # Sélecteurs CSS multiples (pour s'adapter aux changements)
        self.listing_selectors = [
            "article",
            "div[class*='ad']",
            "div[class*='listing']",
            "div[class*='item']",
            "div[class*='card']",
            "div[data-testid*='ad']",
            "a[class*='ad']",
            "div[class*='result']",
            "div[class*='annonce']",
            "div[class*='property']"
        ]
        
        logger.info(f"✅ Agent Tayara initialisé (headless={headless})")
    
    def init_driver(self):
        """Initialiser le driver Selenium avec des options anti-détection"""
        try:
            chrome_options = Options()
            
            # Désactiver les flags d'automatisation
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)
            
            # Paramètres pour éviter la détection
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--start-maximized")
            
            # User agent réaliste (Chrome récent)
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            
            # Mode headless si demandé
            if self.headless:
                chrome_options.add_argument("--headless=new")
            
            # Désactiver les notifications
            chrome_options.add_argument("--disable-notifications")
            
            # Désactiver les extensions
            chrome_options.add_argument("--disable-extensions")
            
            # Initialiser le driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Supprimer les propriétés WebDriver
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            logger.info("✅ Driver Selenium initialisé avec succès")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation driver: {e}")
            raise
    
    def human_like_behavior(self):
        """Simuler un comportement humain réaliste"""
        try:
            # Scroll aléatoire (comme un humain)
            scroll_amount = random.randint(300, 800)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(1, 2))
            
            # Scroll vers le bas
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(0.5, 1.5))
            
            # Mouvement de souris simulé
            self.driver.execute_script("""
                var event = new MouseEvent('mousemove', {
                    view: window,
                    bubbles: true,
                    cancelable: true,
                    clientX: Math.random() * window.innerWidth,
                    clientY: Math.random() * window.innerHeight
                });
                document.dispatchEvent(event);
            """)
            time.sleep(random.uniform(0.5, 1))
            
        except Exception as e:
            logger.debug(f"Erreur simulation comportement: {e}")
    
    def find_working_url(self):
        """Trouver une URL qui fonctionne"""
        for test_url in self.search_urls:
            full_url = f"{self.base_url}{test_url}"
            logger.info(f"🔍 Test de l'URL: {full_url}")
            
            try:
                self.driver.get(full_url)
                time.sleep(random.uniform(3, 5))
                
                # Vérifier si la page contient des annonces
                page_source = self.driver.page_source.lower()
                
                # Indicateurs de présence d'annonces
                indicators = ['annonce', 'ad', 'listing', 'item', 'card', 'property']
                
                for indicator in indicators:
                    if indicator in page_source:
                        logger.info(f"✅ URL valide trouvée: {full_url} (indicateur: {indicator})")
                        return test_url # URL valide trouvée
                
                # Vérifier aussi le titre
                if "404" not in self.driver.title.lower() and "not found" not in self.driver.title.lower():
                    if len(self.driver.find_elements(By.CSS_SELECTOR, "body")) > 0:
                        logger.info(f"✅ URL accessible: {full_url}")
                        return test_url
                        
            except Exception as e:
                logger.warning(f"⚠️ Erreur avec {full_url}: {e}")
                continue
        
        return None
    
    def extract_annonces_from_page(self):
        """Extraire toutes les annonces de la page courante"""
        annonces = []
        
        # Attendre que la page charge
        time.sleep(random.uniform(2, 4))
        
        # Scroll progressif pour charger plus d'annonces
        for _ in range(3):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(1, 2))
        
        # Chercher les annonces avec différents sélecteurs
        found_listings = []
        for selector in self.listing_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if len(elements) > 3:  # Si on trouve au moins 3 éléments
                    found_listings = elements
                    logger.info(f"✅ Sélecteur '{selector}' a trouvé {len(elements)} éléments")
                    break
            except:
                continue
        
        if not found_listings:
            logger.warning("⚠️ Aucune annonce trouvée avec les sélecteurs standards")
            return []
        
        logger.info(f"📊 {len(found_listings)} annonces potentielles trouvées")
        
        # Parser chaque annonce
        for idx, listing in enumerate(found_listings[:30]):   # 3. Limiter à 30 annonces par page (performance)
            try:
                # Scroll vers l'élément
                self.driver.execute_script("arguments[0].scrollIntoView(true);", listing)
                time.sleep(random.uniform(0.3, 0.7))
                
                # Extraire les informations
                annonce = self.parse_listing_element(listing)
                
                if annonce:
                    annonces.append(annonce)
                    logger.debug(f"✅ Annonce #{idx+1} extraite: {annonce.get('title', '')[:30]}...")
                    
            except Exception as e:
                logger.debug(f"⚠️ Erreur parsing annonce #{idx+1}: {e}")
                continue
        
        return annonces
    
    def parse_listing_element(self, element):
        """Parser un élément d'annonce pour en extraire les informations"""
        try:
            # Titre - essayer plusieurs sélecteurs
            title = None
            title_selectors = ['h2', 'h3', 'h4', '.title', '[class*="title"]', 'a']
            
            for selector in title_selectors:
                try:
                    found = element.find_elements(By.CSS_SELECTOR, selector)
                    if found and found[0].text:
                        title = found[0].text.strip()
                        break
                except:
                    continue
            
            if not title:
                # Prendre le texte direct
                title = element.text.split('\n')[0] if element.text else "N/A"
            
            # Prix - chercher avec 4 sélecteurs
            price = None
            price_selectors = ['[class*="price"]', '[class*="amount"]', '[data-testid*="price"]', '.price']
            
            for selector in price_selectors:
                try:
                    found = element.find_elements(By.CSS_SELECTOR, selector)
                    if found and found[0].text:
                        price_text = found[0].text.strip()
                        # Extraire les chiffres
                        numbers = re.findall(r'[\d\s]+', price_text)
                        if numbers:
                            clean = re.sub(r'\s', '', numbers[0])
                            price = float(clean)
                            price_display = price_text
                        break
                except:
                    continue
            
            # Localisation - 4 sélecteurs
            location = None
            loc_selectors = ['[class*="location"]', '[class*="city"]', '[class*="place"]', '.location']
            
            for selector in loc_selectors:
                try:
                    found = element.find_elements(By.CSS_SELECTOR, selector)
                    if found and found[0].text:
                        location = found[0].text.strip()
                        break
                except:
                    continue
            
            # Lien - premier lien trouvé
            link = None
            try:
                links = element.find_elements(By.TAG_NAME, 'a')
                if links:
                    href = links[0].get_attribute('href')
                    if href and href.startswith('http'):
                        link = href
                    elif href:
                        link = f"{self.base_url}{href if href.startswith('/') else '/' + href}"
            except:
                pass
            
            # Image
            has_image = False
            try:
                imgs = element.find_elements(By.TAG_NAME, 'img')
                has_image = len(imgs) > 0
            except:
                pass
            
            # Type de bien - déduit du titre
            property_type = "Immobilier"
            if "appartement" in title.lower():
                property_type = "Appartement"
            elif "villa" in title.lower():
                property_type = "Villa"
            elif "terrain" in title.lower():
                property_type = "Terrain"
            elif "magasin" in title.lower() or "bureau" in title.lower():
                property_type = "Commercial"
            
            # Extraire ville et région
            city = None
            region = None
            if location:
                parts = location.split(',')
                city = parts[0].strip() if len(parts) > 0 else None
                region = parts[-1].strip() if len(parts) > 1 else None
            
            # Ne garder que si on a au moins un titre valide
            if title and title != "N/A" and len(title) > 3:
                return {
                    'source_site': self.agent_name,
                    'site_url': self.base_url,
                    'title': title,
                    'price_numeric': price,
                    'price_text': f"{price:,.0f} DT" if price else "Prix non spécifié",
                    'property_type': property_type,
                    'location': location or "Tunisie",
                    'city': city,
                    'region': region,
                    'link': link or self.base_url,
                    'publication_date': datetime.now(),
                    'with_photo': has_image,
                    'description': None,
                    'metadata': {
                        'extracted_with': 'selenium',
                        'timestamp': datetime.now().isoformat()
                    }
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Erreur parsing élément: {e}")
            return None
    
    def go_to_next_page(self, current_page):
        """Naviguer vers la page suivante"""
        try:
            # Essayer différents sélecteurs pour le bouton suivant
            next_selectors = [
                "a[rel='next']",
                "a:contains('Suivant')",
                "a:contains('Next')",
                ".pagination-next",
                "a[class*='next']",
                "button[class*='next']"
            ]
            
            for selector in next_selectors:
                try:
                    # Pour les sélecteurs avec :contains, on utilise XPath
                    if ':contains' in selector:
                        text = selector.split("'")[1] if "'" in selector else "Suivant"
                        next_btn = self.driver.find_elements(By.XPATH, f"//a[contains(text(), '{text}')]")
                    else:
                        next_btn = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    if next_btn:
                        logger.info(f"➡️ Bouton suivant trouvé avec {selector}")
                        self.human_like_behavior()
                        next_btn[0].click()
                        time.sleep(random.uniform(3, 5))
                        return True
                except:
                    continue
            
            # Si pas de bouton, essayer d'ajouter ?page= à l'URL
            current_url = self.driver.current_url
            if '?page=' in current_url:
                new_url = re.sub(r'page=\d+', f'page={current_page+1}', current_url)
            elif '&page=' in current_url:
                new_url = re.sub(r'page=\d+', f'page={current_page+1}', current_url)
            else:
                if '?' in current_url:
                    new_url = f"{current_url}&page={current_page+1}"
                else:
                    new_url = f"{current_url}?page={current_page+1}"
            
            logger.info(f"➡️ Tentative navigation directe: {new_url}")
            self.driver.get(new_url)
            time.sleep(random.uniform(3, 5))
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Impossible d'aller à la page suivante: {e}")
            return False
    
    def scrape(self, max_pages=10):
        """Méthode principale de scraping avec Selenium"""
        all_annonces = []
        current_page = 1
        
        try:
            # 1. Initialiser le driver
            self.init_driver()
            
            # 2. Trouver une URL qui fonctionne
            logger.info("🔍 Recherche d'une URL valide...")
            working_url = self.find_working_url()
            
            if not working_url:
                logger.error("❌ Aucune URL fonctionnelle trouvée")
                return []
            
            # 3. Aller à la première page
            first_url = f"{self.base_url}{working_url}"
            logger.info(f"🌐 Navigation vers {first_url}")
            self.driver.get(first_url)
            time.sleep(random.uniform(4, 6))
            
            # 4. Scraper les pages
            consecutive_empty = 0
            
            while current_page <= max_pages and consecutive_empty < 2:
                logger.info(f"📄 Scraping page {current_page}/{max_pages if max_pages else '∞'}")
                
                # Comportement humain
                self.human_like_behavior()
                
                # Extraire les annonces
                page_annonces = self.extract_annonces_from_page()
                
                if page_annonces:
                    logger.info(f"✅ {len(page_annonces)} annonces trouvées sur la page {current_page}")
                    
                    for annonce in page_annonces:
                        all_annonces.append(annonce)
                        
                        # Sauvegarde en base
                        try:
                            result = self.db.insert_annonce(annonce)
                            if result == 'inserted':
                                self.stats['new'] += 1
                            self.stats['found'] += 1
                        except Exception as e:
                            logger.error(f"Erreur insertion base: {e}")
                    
                    consecutive_empty = 0
                else:
                    logger.warning(f"⚠️ Aucune annonce sur la page {current_page}")
                    consecutive_empty += 1
                
                self.stats['pages'] += 1
                
                # Aller à la page suivante
                if current_page < max_pages:
                    if not self.go_to_next_page(current_page):
                        logger.info("🏁 Fin de la pagination")
                        break
                
                current_page += 1
                
                # Pause entre les pages
                time.sleep(random.uniform(5, 10))
            
            logger.info(f"🎉 Scraping terminé: {len(all_annonces)} annonces sur {self.stats['pages']} pages")
            
        except WebDriverException as e:
            logger.error(f"❌ Erreur WebDriver: {e}")
        except Exception as e:
            logger.error(f"❌ Erreur inattendue: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                self.driver.quit()
                logger.info("🛑 Driver fermé")
        
        return all_annonces
    
    def run(self, max_pages=5):
        """Exécuter le scraper avec logging"""
        start_time = datetime.now()
        logger.info(f"🚀 Démarrage de {self.agent_name} (Selenium)")
        
        try:
            results = self.scrape(max_pages)
            logger.info(f"✅ {self.agent_name} terminé: {len(results)} annonces")
            
            # Sauvegarde CSV
            if self.save_csv and self.csv_manager and results:
                self.csv_manager.save_agent_data(self.agent_name, results)
                
        except Exception as e:
            logger.error(f"❌ Erreur {self.agent_name}: {e}")
            import traceback
            traceback.print_exc()
            self.stats['errors'] += 1
            results = []
        
        # Enregistrer les stats
        try:
            self.db.log_scraper_run(self.agent_name, {
                **self.stats,
                'status': 'completed' if self.stats['errors'] == 0 else 'completed_with_errors'
            })
        except Exception as e:
            logger.error(f"Erreur sauvegarde stats: {e}")
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"⏱️  Temps d'exécution: {duration.total_seconds():.1f} secondes")
        
        return results, self.stats

# ============================================
# POINT D'ENTRÉE PRINCIPAL
# ============================================
if __name__ == "__main__":
    print("="*70)
    print("🕷️  AGENT TAYARA AVEC SELENIUM")
    print("="*70)
    
    # Vérifier les dépendances
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ Dépendances Selenium OK")
    except ImportError:
        print("❌ Installation nécessaire:")
        print("   pip install selenium webdriver-manager")
        sys.exit(1)
    
    print("\n📋 Configuration:")
    print("   • Mode: Headless = False (navigateur visible)")
    print("   • Pages max: 3")
    print("   • Sauvegarde CSV: Oui")
    print("   • Base de données: PostgreSQL")
    
    # Demander confirmation
    response = input("\n🚀 Lancer le scraping ? (o/n): ")
    if response.lower() != 'o':
        print("❌ Annulé")
        sys.exit(0)
    
    # Créer l'agent et exécuter
    agent = TayaraAgent(save_csv=True, headless=False)
    results, stats = agent.run(max_pages=3)
    
    # Afficher les résultats
    print("\n" + "="*70)
    print("📊 RÉSULTATS FINAUX")
    print("="*70)
    print(f"✅ Annonces trouvées: {len(results)}")
    print(f"📄 Pages scrapées: {stats.get('pages', 0)}")
    print(f"🆕 Nouvelles annonces: {stats.get('new', 0)}")
    print(f"❌ Erreurs: {stats.get('errors', 0)}")
    
    if results:
        print("\n📋 Aperçu des 3 premières annonces:")
        for i, annonce in enumerate(results[:3]):
            print(f"\n  {i+1}. {annonce.get('title', 'N/A')}")
            print(f"     💰 Prix: {annonce.get('price_text', 'N/A')}")
            print(f"     📍 Lieu: {annonce.get('location', 'N/A')}")
            print(f"     🔗 Lien: {annonce.get('link', 'N/A')[:50]}...")
    
    print("\n✨ Scraping terminé!")