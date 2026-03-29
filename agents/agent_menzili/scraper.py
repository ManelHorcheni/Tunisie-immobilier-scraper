#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║   MENZILI.TN SCRAPER                                                    ║
║   Site : https://www.menzili.tn/immo/vente-immobilier-tunisie           ║
║   Mêmes colonnes CSV que afariat (maisons / appartements / terrains)    ║
╚══════════════════════════════════════════════════════════════════════════╝

Structure HTML menzili :
  Listing : div.row.li-item-list > a[href*='/annonce/']
  Localisation listing : <p><i class="fa-map-marker"></i>\nDéléga, Gouvernorat</p>
  Page détail :
    - Fil d'Ariane : Maison|Appartement|Terrain / Gouvernorat / titre
    - Localisation : "Houmt Souk, Djerba-Houmt Souk, Médenine"
    - Date : "Déposée le: 07/11/24"
    - Prix : "700 000 DT"
    - Détails : Chambres / Salle de bain / Surf habitable / Surf terrain
    - Options : section texte libre (Climatisation, Piscine, Vue mer, etc.)
"""

import re
import os
import time
import random
import argparse
import pandas as pd
from datetime import datetime
from collections import Counter

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

# ═══════════════════════════════════════════════════════════════════════
# ⚙️  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

BASE_URL   = "https://www.menzili.tn"
SITE_NAME  = "menzili"
# URL de base : vente uniquement (pas de location)
LISTING_BASE = "/immo/vente-immobilier-tunisie"

OUTPUT_DIR = "."
PAUSE_MIN  = 1.5
PAUSE_MAX  = 3.0

GOVERNORATES = [
    'Tunis','Ariana','Ben Arous','Manouba','Nabeul','Zaghouan','Bizerte',
    'Béja','Jendouba','Kef','Siliana','Sousse','Monastir','Mahdia','Sfax',
    'Kairouan','Kasserine','Sidi Bouzid','Gabès','Médenine','Medenine',
    'Tataouine','Gafsa','Tozeur','Kébili',
]

# ═══════════════════════════════════════════════════════════════════════
# 🗺️  CODES POSTAUX TUNISIENS
# ═══════════════════════════════════════════════════════════════════════

CODE_POSTAL = {
    # Tunis
    "Tunis":"1000","Bab Bhar":"1000","Médina":"1008","Bab Souika":"1006",
    "El Omrane":"1005","El Omrane Supérieur":"1091","El Menzah":"1004",
    "Ettahrir":"1008","Ezzouhour":"1010","Jebel Jelloud":"1080",
    "Kabaria":"1018","La Goulette":"2060","La Marsa":"2070",
    "Le Bardo":"2000","Bardo":"2000","Le Kram":"2015",
    "Mutuelleville":"1082","Séjoumi":"1007","Sidi El Béchir":"1002",
    "Sidi Hassine":"1096","Carthage":"2016","Sidi Bou Said":"2026",
    "Gammarth":"2078","El Manar":"1004","Cité El Khadra":"1003",
    "Montplaisir":"1073","Lac":"1053","Berge du Lac":"1053",
    "Zahrouni":"2051","Cité Mahragène":"1082",
    # Ariana
    "Ariana":"2080","Ennasr":"2037","Cité Ennasr":"2037",
    "Raoued":"2083","Chotrana":"2086","Borj Louzir":"2073",
    "La Soukra":"2036","Soukra":"2036","Mnihla":"2094",
    "Kalâat el-Andalous":"2022","Menzah 6":"2091",
    # Ben Arous
    "Ben Arous":"2013","El Mourouj":"2074","Mourouj":"2074",
    "Hammam Lif":"2050","Hammam Chott":"2052",
    "Bou Mhel El Bassatine":"2097","Ezzahra":"2034",
    "Fouchana":"2082","Megrine":"2033","Mégrine":"2033",
    "Mohamedia":"2084","Rades":"2040","Radés":"2040","Mornag":"2090",
    # Manouba
    "Manouba":"2010","Mannouba":"2010","Den Den":"2011","Denden":"2011",
    "Oued Ellil":"2021","Jedaida":"7011","Tebourba":"1130","Mornaguia":"1110",
    # Nabeul
    "Nabeul":"8000","Hammamet":"8050","Yasmine Hammamet":"8057",
    "Kelibia":"8090","Korba":"8070","Menzel Temime":"8080",
    "Grombalia":"8030","Soliman":"8020","Beni Khalled":"8042",
    "Bou Argoub":"8025","El Haouaria":"8045","Takelsa":"8061",
    "Menzel Bouzelfa":"8010","Dar Chaabane El Fehri":"8011",
    "El Maamoura":"8013","Baraket Essahel":"8056",
    "Mrezgua":"8052","Mrezga":"8058","Beni Khiar":"8060",
    # Zaghouan
    "Zaghouan":"1100","Zriba":"1121","Djebel Oust":"1130",
    "Bir Mcherga":"1141","El Fahs":"1140","Nadhour":"1160",
    # Bizerte
    "Bizerte":"7000","Menzel Bourguiba":"7050","Mateur":"7030",
    "Ras Jebel":"7025","Ghar El Melh":"7023","Utique":"7020",
    "Tinja":"7012","Joumine":"7034","El Alia":"7041",
    "Ghezala":"7044","Menzel Jemil":"7080","Sejenane":"7040",
    # Béja
    "Béja":"9000","Beja":"9000","Nefza":"9020","Testour":"9040",
    "Téboursouk":"9060","Thibar":"9061","Amdoun":"9080",
    "Goubellat":"9030","Mejez El Bab":"9070",
    # Jendouba
    "Jendouba":"8100","Tabarka":"8110","Fernana":"8120",
    "Bou Salem":"8140","Ain Draham":"8130","Ghardimaou":"8160",
    # Kef
    "Le Kef":"7100","Kef":"7100","Dahmani":"7170",
    "Sakiet Sidi Youssef":"7115","Tajerouine":"7150",
    # Siliana
    "Siliana":"6100","Bou Arada":"6180","Gaafour":"6130",
    "El Krib":"6120","Makther":"6140","Rouhia":"6150",
    # Sousse
    "Sousse":"4000","Hammam Sousse":"4011","Kantaoui":"4089",
    "Akouda":"4022","Kalaa Kebira":"4060","Kalaa Sghira":"4021",
    "Sidi Bou Ali":"4040","M'Saken":"4070","Msaken":"4070",
    "Enfidha":"4030","Kondar":"4010","Sahloul":"4054",
    # Monastir
    "Monastir":"5000","Sahline":"5012","Ksar Hellal":"5070",
    "Jemmal":"5020","Jammel":"5020","Teboulba":"5080",
    "Bekalta":"5014","Bembla":"5011","Moknine":"5050",
    # Mahdia
    "Mahdia":"5100","El Jem":"5160","Ksour Essef":"5180",
    "Chebba":"5170","Hebira":"5111","Souassi":"5140",
    # Sfax
    "Sfax":"3000","Sakiet Ezzit":"3021","Sakiet Eddaïer":"3011",
    "Thyna":"3040","Agareb":"3030","El Amra":"3020",
    "El Hencha":"3010","Ghraiba":"3084","Jebeniana":"3080",
    "Kerkennah":"3070","La Skhira":"3041","Mahres":"3060",
    "Menzel Chaker":"3051",
    # Kairouan
    "Kairouan":"3100","El Alaa":"3110","Haffouz":"3130",
    "Hajeb El Ayoun":"3160","Oueslatia":"3120","Sbikha":"3114",
    # Kasserine
    "Kasserine":"1200","Sbeitla":"1250","Thala":"1210",
    "Feriana":"1240","Foussana":"1222","Sbiba":"1270",
    # Sidi Bouzid
    "Sidi Bouzid":"9100","Meknassy":"9140","Regueb":"9170",
    # Gabès
    "Gabès":"6000","Gabes":"6000","El Hamma":"6020",
    "Mareth":"6080","Matmata":"6015",
    # Médenine
    "Médenine":"4100","Medenine":"4100","Ben Guerdane":"4160",
    "Beni Khedache":"4110","Djerba":"4180","Jerba":"4180",
    "Djerba-Houmt Souk":"4180","Houmt Souk":"4180",
    "Djerba-Midoun":"4180","Midoun":"4116","Zarzis":"4170",
    "Ajim":"4135","Djerba-Ajim":"4135","El May":"4175",
    # Tataouine
    "Tataouine":"3200","Remada":"3240","Ghomrassen":"3220",
    # Gafsa
    "Gafsa":"2100","El Ksar":"2110","Métlaoui":"2130","Metlaoui":"2130",
    "Moulares":"2131","Redeyef":"2132",
    # Tozeur
    "Tozeur":"2200","Nefta":"2240","Hazoua":"2260",
    # Kébili
    "Kébili":"4200","Kebili":"4200","Douz":"4260","Souk Lahad":"4230",
}

def get_postal_code(location: str) -> str:
    if not location:
        return ""
    ll = location.lower().strip()
    for key, cp in CODE_POSTAL.items():
        if key.lower() == ll:
            return cp
    for key, cp in CODE_POSTAL.items():
        kl = key.lower()
        if kl in ll or ll in kl:
            return cp
    return ""

# ═══════════════════════════════════════════════════════════════════════
# 📋  COLONNES CSV (identiques à afariat)
# ═══════════════════════════════════════════════════════════════════════

COMMON_COLS = [
    'source','url_annonce','type_bien',
    'prix','date_insertion','gouvernorat','delegation',
    'localite','code_postal','superficie',
    'titre_foncier','vue_mer',
]

COLS = {
    'Maison/Villa': COMMON_COLS + [
        'etat','standing','nb_chambres','nb_salles_bain','dressing',
        'balcon','parking','piscine','chauffage_central','terrasse',
        'jardin','niveau','climatisation',
    ],
    'Appartement': COMMON_COLS + [
        'etat','standing','nb_chambres','nb_salles_bain','dressing',
        'balcon','parking','piscine','chauffage_central','jardin',
        'etage','ascenseur','syndic','climatisation',
    ],
    'Terrain': COMMON_COLS + [
        'terrain_viabilise','constructible','dimensions_terrain',
        'zone','facade','acces_route','acces_electricite',
        'acces_eau','vocation',
    ],
}

CSV_NAMES = {
    'Maison/Villa': f'{SITE_NAME}_maisons',
    'Appartement':  f'{SITE_NAME}_appartements',
    'Terrain':      f'{SITE_NAME}_terrains',
}

BOOL_FIELDS = [
    'titre_foncier','vue_mer','dressing','balcon','parking',
    'piscine','chauffage_central','terrasse','jardin','climatisation',
    'ascenseur','syndic','terrain_viabilise','constructible',
    'acces_route','acces_electricite','acces_eau',
]

# ═══════════════════════════════════════════════════════════════════════
# 🔢  REGEX
# ═══════════════════════════════════════════════════════════════════════

RE_PRIX    = re.compile(r'([\d\s]+)\s*DT', re.I)
RE_SURF    = re.compile(r'(\d+(?:[.,]\d+)?)\s*m[²2]?', re.I)
RE_CP      = re.compile(r'\b(\d{4})\b')
RE_DATE_FR = re.compile(r'(\d{2})/(\d{2})/(\d{2,4})')  # ex: 07/11/24

RE_SUITE_N = re.compile(r'(\d+|un|une|deux|trois|quatre|cinq)\s+suites?', re.I)
RE_SUITE_1 = re.compile(r'\bsuite[s]?\b', re.I)
RE_CHAMBRE = re.compile(
    r'(\d+|un|une|deux|trois|quatre|cinq)\s+(?:grandes?\s+)?chambres?\s*(?!\s*(?:de\s+)?bain)',
    re.I
)
RE_SDB_N   = re.compile(
    r'(\d+|une?|deux|trois)\s+(?:salles?\s+(?:de\s+)?(?:bain|eau)|sdb)\b',
    re.I
)
RE_SDB_1   = re.compile(r"\bsalle\s+(?:de\s+bain|d['']eau)\b", re.I)

RE_NIVEAUX = re.compile(r'\b(\d+)\s+niveaux?\b', re.I)
RE_R_PLUS  = re.compile(r'\bR\s*\+\s*(\d+)\b', re.I)
RE_ETAGE_N = re.compile(r'\b(\d+)\s*(?:e|er|ère|ème)?\s*étage\b', re.I)
RE_RDC     = re.compile(r'\b(?:rdc|rez[- ]de[- ]chaussée|plain[- ]pied)\b', re.I)

MOTS_CHIFFRES = {
    'un':1,'une':1,'deux':2,'trois':3,'quatre':4,'cinq':5,
    'six':6,'sept':7,'huit':8,'neuf':9,'dix':10,
}

def mot_to_int(s):
    s = str(s).strip().lower()
    if s in MOTS_CHIFFRES:
        return MOTS_CHIFFRES[s]
    m = re.search(r'\d+', s)
    return int(m.group()) if m else 0

# ═══════════════════════════════════════════════════════════════════════
# 🛠️  HELPERS
# ═══════════════════════════════════════════════════════════════════════

def clean(t) -> str:
    return re.sub(r'\s+', ' ', str(t or '')).strip()

def to_int(t) -> int:
    c = re.sub(r'[^\d]', '', str(t or ''))
    return int(c) if c else 0

def detect_bool(text: str, *keywords) -> str:
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text, re.I):
            return 'Oui'
    return 'Non'

def detect_type(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['terrain','hectare']):
        return 'Terrain'
    if any(w in t for w in ['maison','villa','dar','riad','ferme']):
        return 'Maison/Villa'
    if any(w in t for w in ['appartement','appartements','appart',
                             'studio','duplex','penthouse',
                             's+1','s+2','s+3','s+4','s+5']):
        return 'Appartement'
    return 'Autre'

def extract_gouvernorat(text: str) -> str:
    tl = text.lower()
    for g in GOVERNORATES:
        if g.lower() in tl:
            return g
    return ''

def parse_date(text: str) -> str:
    """Convertit DD/MM/YY ou DD/MM/YYYY en YYYY-MM-DD."""
    m = RE_DATE_FR.search(text or '')
    if m:
        j, mo, a = m.groups()
        if len(a) == 2:
            a = '20' + a
        return f"{a}-{mo}-{j}"
    return datetime.now().strftime('%Y-%m-%d')

def detect_etat(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['neuf','nouvelle construction','jamais habité',
                             'jamais occupé','livraison','nouvellement construit',
                             'en cours de construction','fin de construction']):
        return 'Neuf'
    if any(w in t for w in ['rénov','refait à neuf','remis à neuf','récemment rénové']):
        return 'Rénové'
    if any(w in t for w in ['bon état','très bon état','bien entretenu',
                             'parfait état','impeccable']):
        return 'Bon état'
    if any(w in t for w in ['à rénover','travaux','à rafraîchir','ancien']):
        return 'À rénover'
    return 'Non précisé'

def detect_standing(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ['luxe','prestige','ultra standing']):
        return 'Luxe'
    if any(w in t for w in ['haut standing','high standing','haut de gamme',
                             'grand standing','très haut standing']):
        return 'Haut standing'
    if any(w in t for w in ['moyen standing','standing moyen','confort']):
        return 'Moyen standing'
    if any(w in t for w in ['économique','economique','logement social']):
        return 'Économique'
    score = sum([
        'piscine'           in t,
        bool(re.search(r'\bplacard|dressing\b', t)),
        'chauffage central' in t,
        'climatisation'     in t or 'clim' in t,
        'ascenseur'         in t,
        'vue mer'           in t,
    ])
    if score >= 5: return 'Luxe'
    if score >= 3: return 'Haut standing'
    if score >= 2: return 'Moyen standing'
    return 'Non précisé'

def parse_suites_chambres_sdb(text: str):
    """1 suite = 1 chambre + 1 SDB + dressing automatique."""
    t = text.lower()
    nb_suites = sum(mot_to_int(m) for m in RE_SUITE_N.findall(t))
    if not nb_suites and RE_SUITE_1.search(t):
        nb_suites = 1

    nb_ch = 0
    for m in RE_CHAMBRE.finditer(t):
        nb_ch = max(nb_ch, mot_to_int(m.group(1)))

    sdb_vals = [mot_to_int(m) for m in RE_SDB_N.findall(t)]
    nb_sdb   = max(sdb_vals) if sdb_vals else (1 if RE_SDB_1.search(t) else 0)

    total_ch  = nb_ch  + nb_suites
    total_sdb = nb_sdb + nb_suites
    has_dress = bool(re.search(r'\b(?:dressing|placard[s]?)\b', t, re.I)) or nb_suites > 0
    return (total_ch or ''), (total_sdb or ''), has_dress

def parse_niveau(text: str) -> str:
    """RDC=1, R+1=2, R+2=3, 'X niveaux'=X"""
    t = text.lower()
    rp = RE_R_PLUS.search(t)
    if rp:
        return str(int(rp.group(1)) + 1)
    niv = RE_NIVEAUX.search(t)
    if niv:
        return niv.group(1)
    has_rdc   = bool(RE_RDC.search(t))
    etages    = [to_int(m.group(1)) for m in RE_ETAGE_N.finditer(t) if m.group(1)]
    max_etage = max(etages) if etages else 0
    if has_rdc and max_etage > 0:
        return str(max_etage + 1)
    if max_etage > 0:
        return str(max_etage + 1)
    if has_rdc:
        return '1'
    return ''

def parse_etage(text: str) -> str:
    """RDC=0, 1er étage=1, 2ème=2"""
    t = text.lower()
    if RE_RDC.search(t):
        return '0'
    m = RE_ETAGE_N.search(t)
    return m.group(1) if m else ''

def init_driver(headless=False):
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_experimental_option("excludeSwitches", ["enable-automation"])
    opts.add_experimental_option("useAutomationExtension", False)
    opts.add_argument("--start-maximized")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    )
    svc = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=svc, options=opts)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"}
    )
    return driver

# ═══════════════════════════════════════════════════════════════════════
# 🔗  COLLECTE DES LIENS
# ═══════════════════════════════════════════════════════════════════════

def collect_links(driver, max_pages: int) -> list:
    """
    Parcourt /immo/vente-immobilier-tunisie?page=N&tri=1
    Sélecteurs :
      - Liens : div.row.li-item-list a.li-item-list-title (ou a[href*='/annonce/'])
      - Type depuis le titre ou le fil d'Ariane dans l'URL
      - Exclusion locations : item-box-type contient "Louer"
    """
    seen   = set()
    result = []
    empty  = 0

    for page in range(1, max_pages + 1):
        if page == 1:
            url = f"{BASE_URL}{LISTING_BASE}?tri=1"
        else:
            url = f"{BASE_URL}{LISTING_BASE}?l=0&page={page}&tri=1"

        print(f'  Page {page:3d} → {url[:70]} ...', end='', flush=True)
        try:
            driver.get(url)
            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "div.row.li-item-list")
                    )
                )
            except Exception:
                pass
            time.sleep(random.uniform(2, 3))

            cards = driver.find_elements(By.CSS_SELECTOR, "div.row.li-item-list")
            found = 0

            for card in cards:
                # Vérifier que c'est une vente (pas une location)
                try:
                    type_op = card.find_element(
                        By.CSS_SELECTOR, "span.item-box-type"
                    ).text.strip().lower()
                    if 'louer' in type_op or 'location' in type_op:
                        continue
                except Exception:
                    pass

                # Récupérer le lien de l'annonce
                href = ''
                try:
                    link_el = card.find_element(
                        By.CSS_SELECTOR, "a.li-item-list-title"
                    )
                    href = link_el.get_attribute('href') or ''
                except Exception:
                    try:
                        link_el = card.find_element(
                            By.CSS_SELECTOR, "a[href*='/annonce/']"
                        )
                        href = link_el.get_attribute('href') or ''
                    except Exception:
                        continue

                if not href or href in seen:
                    continue
                seen.add(href)

                # Pré-détecter le type depuis le titre et l'URL
                title_txt = ''
                try:
                    title_txt = clean(link_el.text)
                except Exception:
                    pass
                tb = detect_type(f"{title_txt} {href}")
                if tb == 'Autre':
                    continue

                result.append((href, tb))
                found += 1

            print(f' ✅ {found}')
            empty = 0 if found else empty + 1
            if empty >= 3:
                print('  ⚠️  3 pages vides → arrêt.')
                break

        except Exception as e:
            print(f' ❌ {str(e)[:60]}')

        time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX))

    print(f'\n  📊 Total : {len(result)} liens')
    return result

# ═══════════════════════════════════════════════════════════════════════
# 📍  LOCALISATION depuis la page de détail
# ═══════════════════════════════════════════════════════════════════════

def parse_localisation_menzili(driver, body: str):
    """
    Sur menzili, la localisation est affichée sous le titre :
    "Houmt Souk, Djerba-Houmt Souk, Médenine"
    Format : localite, delegation, gouvernorat
    """
    gouvernorat = delegation = localite = code_postal = ''

    # 1. Fil d'Ariane : /immo/immobilier-GOUVERNORAT
    try:
        crumbs = driver.find_elements(
            By.CSS_SELECTOR, "ol.breadcrumb li a, div.breadcrumb a"
        )
        for crumb in crumbs:
            href = crumb.get_attribute('href') or ''
            txt  = clean(crumb.text)
            if '/immo/immobilier-' in href and txt:
                gouvernorat = txt
                break
    except Exception:
        pass

    # 2. Bloc de localisation sous le titre (texte brut)
    # Format dans la page : "Houmt Souk, Djerba-Houmt Souk, Médenine"
    try:
        loc_block = driver.find_element(
            By.XPATH,
            "//h1/following-sibling::*[contains(text(),',')][1]"
        )
        loc_text = clean(loc_block.text)
        parts = [p.strip() for p in loc_text.split(',') if p.strip()]
        if len(parts) >= 3:
            localite   = parts[0]
            delegation = parts[1]
            gouvernorat = gouvernorat or parts[2]
        elif len(parts) == 2:
            delegation  = parts[0]
            gouvernorat = gouvernorat or parts[1]
        elif len(parts) == 1:
            delegation  = parts[0]
    except Exception:
        pass

    # Fallback depuis le texte brut du body
    if not delegation:
        lines = body.split('\n')
        for line in lines[:20]:
            l = line.strip()
            if ',' in l and len(l) < 80:
                parts = [p.strip() for p in l.split(',')]
                # Si la dernière partie est un gouvernorat connu
                if parts and any(g.lower() in parts[-1].lower() for g in GOVERNORATES):
                    if len(parts) >= 3:
                        localite   = parts[0]
                        delegation = parts[1]
                        gouvernorat = gouvernorat or parts[-1]
                    elif len(parts) == 2:
                        delegation  = parts[0]
                        gouvernorat = gouvernorat or parts[1]
                    break

    if not gouvernorat:
        gouvernorat = extract_gouvernorat(body)

    # Nettoyer le gouvernorat (ex: "Médenine" → garder tel quel)
    gouvernorat = gouvernorat.strip()

    # Fallback localité → délégation
    if not localite and delegation:
        localite = delegation

    # Code postal
    for loc in [delegation, localite, gouvernorat]:
        cp = get_postal_code(loc)
        if cp:
            code_postal = cp
            break

    return gouvernorat, delegation, localite, code_postal

# ═══════════════════════════════════════════════════════════════════════
# 📄  EXTRACTION D'UNE ANNONCE
# ═══════════════════════════════════════════════════════════════════════

def extract_detail(driver, url: str) -> dict | None:
    try:
        driver.get(url)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, 'h1'))
            )
        except Exception:
            pass
        time.sleep(random.uniform(2, 3))

        body  = driver.find_element(By.TAG_NAME, 'body').text
        lines = body.split('\n')

        # ── Titre
        titre = ''
        try:
            titre = clean(driver.find_element(By.TAG_NAME, 'h1').text)
        except Exception:
            for l in lines[:5]:
                if l.strip() and len(l.strip()) > 5:
                    titre = l.strip()
                    break
        if not titre:
            return None

        # ── Type de bien depuis fil d'Ariane ou titre
        type_bien = 'Autre'
        try:
            # Fil d'Ariane : Maison / Appartement / Terrain
            crumbs = driver.find_elements(By.CSS_SELECTOR, "ol.breadcrumb li, .breadcrumb a")
            for crumb in crumbs:
                tb = detect_type(clean(crumb.text))
                if tb != 'Autre':
                    type_bien = tb
                    break
        except Exception:
            pass
        if type_bien == 'Autre':
            type_bien = detect_type(f"{titre} {url}")
        if type_bien == 'Autre':
            return None

        # ── Exclure les locaux commerciaux, bureaux, etc.
        EXCLUES = {'local commercial','bureau','bureaux','entrepôt','garage',
                   'place de parc','hôtel','hotel','fonds de commerce'}
        if any(ex in titre.lower() for ex in EXCLUES):
            return None

        # ── Initialiser item
        item = {c: '' for c in COLS[type_bien]}
        item['source']      = SITE_NAME
        item['url_annonce'] = url
        item['type_bien']   = type_bien

        # ── Prix
        # menzili affiche "700 000 DT" dans le body
        prix = 0
        for m in RE_PRIX.finditer(body):
            v = to_int(m.group(1))
            if v > 1000:
                prix = v
                break
        # Ignorer "Contactez l'annonceur"
        item['prix'] = prix if prix > 1000 else ''

        # ── Date de publication
        # Format : "Déposée le: 07/11/24"
        date_insertion = datetime.now().strftime('%Y-%m-%d')
        for line in lines:
            if 'éposée' in line or 'Déposée' in line:
                date_insertion = parse_date(line)
                break
        item['date_insertion'] = date_insertion

        # superficie initialisée à '' — sera remplie dans le bloc block-detail ci-dessous
        surf_hab = surf_terrain = ''

        # ── Description (utilisée pour suites/dressing et full text)
        desc = ''
        try:
            desc_el = driver.find_element(
                By.CSS_SELECTOR, "div.block-descr p[itemprop='text']"
            )
            desc = clean(desc_el.text)
        except Exception:
            try:
                desc_el = driver.find_element(
                    By.XPATH,
                    "//h3[contains(text(),'Description')]/following-sibling::p[1]"
                )
                desc = clean(desc_el.text)
            except Exception:
                pass
        full = f"{titre} {desc} {body}"

        # ── Chambres, SDB, Superficie, Niveau/Étage depuis div.block-detail
        # HTML réel : <div class="block-over"><span>Chambres : </span><strong>3 </strong></div>
        # On lit directement les éléments structurés via CSS/XPath
        nb_ch = nb_sdb = 0
        surf_hab = surf_terrain = niveaux_val = etage_val = ''

        try:
            detail_items = driver.find_elements(
                By.CSS_SELECTOR, "div.block-detail div.block-over"
            )
            for di in detail_items:
                txt = clean(di.text)   # ex: "Chambres : 3"
                # Extraire label et valeur
                m = re.match(r'^(.+?)\s*:\s*(.+)$', txt)
                if not m:
                    continue
                label = m.group(1).strip().lower()
                val   = m.group(2).strip()

                if 'chambre' in label:
                    nb_ch = to_int(val)
                elif 'salle de bain' in label or 'sdb' in label:
                    nb_sdb = to_int(val)
                elif 'surf habitable' in label or 'habitable' in label:
                    surf_hab = to_int(re.sub(r'[^\d]', '', val))
                elif 'surf terrain' in label or 'terrain' in label:
                    surf_terrain = to_int(re.sub(r'[^\d]', '', val))
                elif "nombre d'étage" in label or 'niveaux' in label or 'niveau' in label:
                    niveaux_val = to_int(val)
        except Exception:
            pass

        # ── Superficie
        item['superficie'] = surf_hab or surf_terrain or ''

        # ── Logique suites depuis description (ajoute chambres/SDB implicites)
        nb_ch_s, nb_sdb_s, has_dress = parse_suites_chambres_sdb(full)
        # Priorité : valeur structurée (block-detail) > déduction description
        if not nb_ch and nb_ch_s:
            nb_ch = int(nb_ch_s) if str(nb_ch_s).isdigit() else 0
        if not nb_sdb and nb_sdb_s:
            nb_sdb = int(nb_sdb_s) if str(nb_sdb_s).isdigit() else 0

        if type_bien != 'Terrain':
            item['nb_chambres']    = nb_ch or ''
            item['nb_salles_bain'] = nb_sdb or ''
            item['dressing']       = 'Oui' if has_dress else 'Non'

        # ── Options (section "### Options" dans la page)
        # Structure : texte libre listant les équipements séparés par des espaces
        # Ex: "Climatisation   Accès internet   Piscine   Terrasses   Jardin"
        options_text = ''
        try:
            opt_section = driver.find_element(
                By.XPATH,
                "//h3[contains(text(),'Options')]/following-sibling::p[1] | "
                "//h4[contains(text(),'Options')]/following-sibling::*[1]"
            )
            options_text = clean(opt_section.text).lower()
        except Exception:
            pass
        opt_full = f"{options_text} {full}".lower()

        # ── Localisation
        gouvernorat, delegation, localite, code_postal = parse_localisation_menzili(driver, body)
        item['gouvernorat'] = gouvernorat
        item['delegation']  = delegation
        item['localite']    = localite
        item['code_postal'] = code_postal

        # ── État & Standing
        item['etat']     = detect_etat(full)
        item['standing'] = detect_standing(full)

        # ── Niveau (Maison) / Étage (Appartement)
        # HTML: <span>Nombre d'étages : </span><strong>1 </strong>
        # niveaux_val est déjà extrait depuis block-detail ci-dessus
        if type_bien == 'Maison/Villa':
            if niveaux_val:
                item['niveau'] = str(niveaux_val)
            else:
                item['niveau'] = parse_niveau(full)
        elif type_bien == 'Appartement':
            if niveaux_val:
                # Pour appartement, "Nombre d'étages" = étage de l'appartement
                item['etage'] = str(niveaux_val)
            else:
                item['etage'] = parse_etage(full)

        # ── Booléens communs
        # Options menzili : Climatisation, Vue mer, Terrasses, Piscine, Jardin,
        #                   Place de parc, Garage, Meublé, Titre foncier, etc.
        item['balcon']            = detect_bool(opt_full, 'balcon')
        item['jardin']            = detect_bool(opt_full, 'jardin')
        item['piscine']           = detect_bool(opt_full, 'piscine')
        item['climatisation']     = detect_bool(opt_full, 'climatisation', 'clim')
        item['chauffage_central'] = detect_bool(opt_full, 'chauffage central', 'chauffage')
        item['parking']           = detect_bool(opt_full, 'place de parc', 'parking',
                                                'garage', 'place de parking')
        item['titre_foncier']     = detect_bool(opt_full, 'titre foncier', 'titre bleu',
                                                'titre individuel', 'titre rose')
        item['vue_mer']           = detect_bool(opt_full, 'vue mer', 'vue sur mer',
                                                'bord de mer', 'vue de mer')

        if type_bien == 'Maison/Villa':
            item['terrasse'] = detect_bool(opt_full, 'terrasse', 'terrasses')

        if type_bien == 'Appartement':
            item['ascenseur'] = detect_bool(opt_full, 'ascenseur')
            item['syndic']    = detect_bool(opt_full, 'syndic')

        # ── Terrain spécifique
        if type_bien == 'Terrain':
            # Superficie : surf_terrain depuis block-detail (déjà dans item['superficie'])
            if surf_terrain:
                item['superficie'] = surf_terrain

            item['terrain_viabilise'] = detect_bool(full, 'viabilisé', 'viabilise')
            item['constructible']     = detect_bool(full, 'constructible', 'construction')
            item['acces_route']       = detect_bool(full, 'accès route', 'piste', 'route',
                                                   'goudronné', 'accès par')
            item['acces_electricite'] = detect_bool(full, 'électricité', 'electricite',
                                                   'courant', 'transformateur')
            item['acces_eau']         = detect_bool(full, 'puits', 'eau')

            # Vocation depuis titre + description
            # Ex: "terrain agricole", "zone touristique", "terrain constructible"
            for kws, val in [
                (['résidentiel','habitation','lotissement'], 'Résidentielle'),
                (['commercial','commerce'],                  'Commerciale'),
                (['industriel','usine','entrepôt'],          'Industrielle'),
                (['agricole','agriculture','oliveraie',
                  'agriculteur','palmeraie'],                'Agricole'),
                (['touristique','hôtel','tourisme'],         'Touristique'),
            ]:
                if any(kw in full.lower() for kw in kws):
                    item['vocation'] = val
                    break

            # Zone (souvent mentionnée dans la description)
            for kws, val in [
                (['zone urbaine','urbain'],         'Urbaine'),
                (['zone touristique','touristique'],'Touristique'),
                (['zone agricole','agricole'],      'Agricole'),
                (['zone industrielle','industriel'],'Industrielle'),
                (['résidentiel','lotissement'],     'Résidentielle'),
            ]:
                if any(kw in full.lower() for kw in kws):
                    item['zone'] = val
                    break

            # Dimensions : "X m × Y m" ou "XxY" ou "X mètres × Y mètres"
            m = re.search(
                r'(\d+)\s*(?:m(?:ètres?)?)?\s*[xX×]\s*(\d+)\s*(?:m(?:ètres?)?)?',
                full
            )
            if m:
                item['dimensions_terrain'] = f"{m.group(1)}x{m.group(2)}"

            # Façade : "façade de X m" ou "X mètres linéaires" ou "façade : X"
            m = re.search(
                r'fa[çc]ade\s*(?:de|:|\s)\s*(\d+)|(\d+)\s*m[eè]tres?\s+lin[eé]aires?',
                full, re.I
            )
            if m:
                item['facade'] = m.group(1) or m.group(2)

        # Forcer booléens à Oui/Non
        for f in BOOL_FIELDS:
            if f in item and item[f] == '':
                item[f] = 'Non'

        return item

    except Exception as e:
        print(f'\n  ❌ {url[:60]} → {str(e)[:60]}')
        return None

# ═══════════════════════════════════════════════════════════════════════
# 💾  SCRAPER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class MenziliScraper:

    def __init__(self, output_dir=OUTPUT_DIR):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self._counts    = {t: 0 for t in CSV_NAMES}
        self._csv_paths = {
            t: os.path.join(output_dir, f'{CSV_NAMES[t]}.csv')
            for t in CSV_NAMES
        }

    def _init_csv(self):
        for t, path in self._csv_paths.items():
            pd.DataFrame(columns=COLS[t]).to_csv(
                path, index=False, encoding='utf-8-sig'
            )
            print(f'  📄 {os.path.basename(path)}')

    def _save(self, item):
        t = item['type_bien']
        if t not in self._csv_paths:
            return
        cols = COLS[t]
        df   = pd.DataFrame([item])
        for c in cols:
            if c not in df.columns:
                df[c] = ''
        df[cols].to_csv(
            self._csv_paths[t], mode='a', header=False,
            index=False, encoding='utf-8-sig'
        )
        self._counts[t] += 1

    def run(self, max_pages=50, headless=False):
        print('\n' + '═'*70)
        print('🏠  MENZILI.TN SCRAPER')
        print(f'   URL : {BASE_URL}{LISTING_BASE}')
        print('   Colonnes identiques à afariat (maisons / appartements / terrains)')
        print('═'*70)
        print('\n📄 CSV initialisés :')
        self._init_csv()

        driver = init_driver(headless=headless)
        try:
            print(f'\n📋 ÉTAPE 1 — COLLECTE ({max_pages} pages max)')
            links = collect_links(driver, max_pages)
            if not links:
                print('❌ Aucun lien trouvé.')
                return

            print('\n   Répartition :')
            for t, n in Counter(tb for _, tb in links).items():
                print(f'      {t}: {n}')

            total  = len(links)
            ok     = 0
            errors = 0
            print(f'\n🔍 ÉTAPE 2 — EXTRACTION ({total} annonces)')

            for i, (url, _) in enumerate(links, 1):
                pct = i / total * 100
                bar = '█' * int(pct/5) + '░' * (20 - int(pct/5))
                print(
                    f'\r  [{bar}] {i}/{total} ({pct:.0f}%) ✅{ok} ❌{errors}',
                    end='', flush=True
                )
                item = extract_detail(driver, url)
                if item:
                    self._save(item)
                    ok += 1
                else:
                    errors += 1
                time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX))

            print(f'\n  ✅ {ok} | ❌ {errors}')

        except KeyboardInterrupt:
            print('\n⚠️  Arrêt (Ctrl+C)')
        finally:
            driver.quit()

        print(f'\n{"═"*70}')
        print(f'✅ TERMINÉ — {sum(self._counts.values())} annonces')
        for t, path in self._csv_paths.items():
            n = self._counts[t]
            if n:
                print(f'   {n:5d}  →  {os.path.basename(path)}')
        print('═'*70 + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scraper menzili.tn — vente immobilière uniquement'
    )
    parser.add_argument('--pages',    type=int,  default=50,
                        help='Nombre de pages (défaut: 50, max ~1360)')
    parser.add_argument('--output',   type=str,  default='.',
                        help='Dossier de sortie')
    parser.add_argument('--headless', action='store_true',
                        help='Chrome sans fenêtre')
    args = parser.parse_args()
    MenziliScraper(args.output).run(args.pages, args.headless)