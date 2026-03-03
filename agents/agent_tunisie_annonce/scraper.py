import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from agents.base_agent import BaseScraperAgent
from bs4 import BeautifulSoup
import re
from datetime import datetime
from loguru import logger

class TunisieAnnonceAgent(BaseScraperAgent):
    """Agent spécialisé pour Tunisie Annonce"""
    
    def __init__(self, db_config=None, save_csv=True):
        super().__init__( # Appelle le constructeur de la classe parente
            agent_name="tunisie_annonce", # Nom unique
            base_url="http://www.tunisie-annonce.com", # URL de base
            db_config=db_config,
            save_csv=save_csv
        )
        # L'URL spécifique pour les annonces immobilières
        #rech_cod_rub=101 : Rubrique "Immobilier"
        #rech_cod_typ=10102 : Type "Vente"
        self.search_url = "/AnnoncesImmobilier.asp?rech_cod_rub=101&rech_cod_typ=10102"
    
    def parse_listing(self, listing_html):
        """Parser une annonce individuelle"""
        try:
            cols = listing_html.find_all('td') # Récupère toutes les colonnes
            if len(cols) < 10 or not cols[1].find('a'): # Vérification validité
                return None
            
            # 1. Titre (colonne 5)
            title = cols[5].find('a').text.strip() if cols[5].find('a') else "N/A"
            
            # 2. Prix (colonne 7) - avec nettoyage
            price_raw = cols[7].text.strip() if cols[7].text else "N/A"
            price_clean = re.sub(r'[^\d]', '', price_raw) # Garde uniquement les chiffres
            price_numeric = float(price_clean) if price_clean else None
            
            # 3. Type de bien (colonne 3)
            property_type = cols[3].text.strip() if cols[3].text else "N/A"
            
            # 4. Localisation (colonne 1) - avec lien
            location = cols[1].find('a').text.strip() if cols[1].find('a') else "N/A"
            
            # 5. Extraction ville/région
            location_parts = location.split()
            city = location_parts[-1] if location_parts else None
            region = location_parts[0] if location_parts else None
            
            # 6. Date (colonne 9) - format DD/MM/YYYY
            date_raw = cols[9].text.strip() if len(cols) > 9 and cols[9].text else "N/A"
            try:
                pub_date = datetime.strptime(date_raw, "%d/%m/%Y")
            except:
                pub_date = None
            
            # 7. Lien (dans la même colonne que le titre)
            link_tag = cols[5].find('a')
            link = f"{self.base_url}/{link_tag['href']}" if link_tag and link_tag.get('href') else "N/A"
            
            # 8. Présence de photo (icône appareil photo)
            with_photo = 'icon_camera' in str(cols[5])
            
            # 9. Construction de l'objet annonce normalisé
            annonce = {
                'source_site': self.agent_name,
                'site_url': self.base_url,
                'title': title,
                'description': None,
                'price_numeric': price_numeric,
                'price_text': price_raw,
                'property_type': property_type,
                'location': location,
                'city': city,
                'region': region,
                'surface': None,
                'rooms': None,
                'bedrooms': None,
                'bathrooms': None,
                'floor': None,
                'total_floors': None,
                'furnished': False,
                'new_building': False,
                'with_photo': with_photo,
                'photo_urls': [],
                'publication_date': pub_date,
                'agent_name': None,
                'phone': None,
                'email': None,
                'link': link,
                'metadata': {
                    'raw_preview': str(cols)[:200]  # Pour debug
                }
            }
            
            return annonce
            
        except Exception as e:
            logger.error(f"Erreur parsing: {e}")
            return None
    
    def get_total_pages(self, soup):
        """Extraire le nombre total de pages depuis la pagination"""
        try:
            # Chercher le lien "Dernière page" ou le numéro de dernière page
            pagination = soup.find('table', class_='TableauPagination')
            if pagination:
                links = pagination.find_all('a')
                last_page = 1
                for link in links:
                    text = link.text.strip()
                    if text.isdigit() and int(text) > last_page:
                        last_page = int(text)
                logger.info(f"📊 Nombre total de pages détecté: {last_page}")
                return last_page
        except Exception as e:
            logger.error(f"Erreur récupération nombre de pages: {e}")
        return None
    
    def scrape(self, max_pages=None):
        """Scraper toutes les pages jusqu'à la fin"""
        all_data = []
        page = 1
        total_pages = None
        consecutive_empty = 0
        max_consecutive_empty = 3  # Arrêter après 3 pages vides consécutives
        
        # 1. Détection du nombre total de pages
        first_url = f"{self.base_url}{self.search_url}&rech_page_num=1"
        first_html = self.get_page(first_url)
        if first_html:
            first_soup = BeautifulSoup(first_html, 'html.parser')
            total_pages = self.get_total_pages(first_soup)

        # 2. Boucle de scraping
        while True:
            # Construire l'URL avec le paramètre de page
            if '?' in self.search_url:
                url = f"{self.base_url}{self.search_url}&rech_page_num={page}"
            else:
                url = f"{self.base_url}{self.search_url}?page={page}"
            
            logger.info(f"📄 Scraping page {page}" + (f"/{total_pages}" if total_pages else ""))
            
            html = self.get_page(url)
            if not html:
                logger.warning(f"⚠️ Page {page} vide ou inaccessible")
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    logger.info(f"🛑 Arrêt après {consecutive_empty} pages vides consécutives")
                    break
                page += 1
                continue
            
            # Recherche des annonces avec plusieurs sélecteurs
            soup = BeautifulSoup(html, 'html.parser')
            
            # Vérifier différents sélecteurs possibles
            listings = soup.find_all('tr', class_='Tableau1')
            if not listings:
                listings = soup.find_all('tr', attrs={'class': re.compile(r'Tableau\d')})
            if not listings:
                listings = soup.find_all('tr', bgcolor='#FFFFFF')  # Autre pattern possible
            
            if not listings:
                logger.warning(f"⚠️ Aucune annonce trouvée sur la page {page}")
                consecutive_empty += 1
                if consecutive_empty >= max_consecutive_empty:
                    break
                page += 1
                continue
            
            # Réinitialiser le compteur de pages vides
            consecutive_empty = 0
            
            logger.info(f"✅ {len(listings)} annonces trouvées sur la page {page}")
            
            page_data = []
            # Parsing des annonces de la page
            for listing in listings:
                parsed = self.parse_listing(listing)
                if parsed:
                    page_data.append(parsed)
                    
                    # Insertion en base et mise à jour des stats
                    result = self.db.insert_annonce(parsed)
                    if result == 'inserted':
                        self.stats['new'] += 1
                    elif result == 'updated':
                        self.stats['updated'] += 1
                    
                    self.stats['found'] += 1
            
            all_data.extend(page_data)
            self.stats['pages'] += 1
            
            # Vérifier s'il y a un lien "Suivant" ou "Page suivante"
            next_link = soup.find('a', string=re.compile(r'Suivante|Suivant|>|»'))
            if not next_link and page >= (total_pages or float('inf')):
                logger.info(f"🏁 Dernière page atteinte (page {page})")
                break
            
            page += 1
            
            # Respecter une pause plus longue entre les pages pour éviter le blocage
            import time
            time.sleep(2)  # Pause de 2 secondes entre les pages
        
        logger.info(f"✅ {self.agent_name}: {len(all_data)} annonces trouvées au total")
        return all_data

if __name__ == "__main__":
    # Test en local
    agent = TunisieAnnonceAgent(save_csv=True)
    results, stats = agent.run(max_pages=None)  # None = toutes les pages
    print(f"Résultats: {len(results)} annonces")
    print(f"Statistiques: {stats}")