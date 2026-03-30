#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DIARKOUM.TN SCRAPER - VERSION FINALE
Modifications v3 :
  - Suppression colonne 'zone' (terrains)
  - titre_foncier : détection enrichie (bleu, individuel, en cours, collectif, ...)
  - Pagination complète : max_pages=2000 par défaut (couvre ~8320 annonces)
"""

import re
import os
import time
import random
import argparse
import requests
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

BASE_URL      = "https://diarkoum.tn"
SITE_NAME     = "diarkoum"
LISTING_URL   = f"{BASE_URL}/annonces.php?type_recherche=1"
LOADMORE_URL  = f"{BASE_URL}/loadmore.php"

OUTPUT_DIR = "."
PAUSE_MIN  = 1.5
PAUSE_MAX  = 3.0

GOVERNORATES = [
    'Tunis','Ariana','Ben Arous','Manouba','Nabeul','Zaghouan','Bizerte',
    'Beja','Jendouba','Kef','Siliana','Sousse','Monastir','Mahdia','Sfax',
    'Kairouan','Kasserine','Sidi Bouzid','Gabes','Medenine',
    'Tataouine','Gafsa','Tozeur','Kebili',
]

REGION_GOV = {
    'Tunis 1': 'Tunis', 'Tunis 2': 'Tunis',
    'Nabeul 1': 'Nabeul', 'Nabeul 2': 'Nabeul',
    'Sfax 1': 'Sfax', 'Sfax 2': 'Sfax',
    'Gabes': 'Gabes', 'Medenine': 'Medenine',
}

CODE_POSTAL = {
    "Tunis":"1000","La Goulette":"2060","La Marsa":"2070",
    "Le Bardo":"2000","Bardo":"2000","Le Kram":"2015",
    "Carthage":"2016","Sidi Bou Said":"2026","Gammarth":"2078",
    "El Manar":"1004","Cite El Khadra":"1003","El Aouina":"2045",
    "Ariana":"2080","Ennasr":"2037","La Soukra":"2036","Soukra":"2036",
    "Ben Arous":"2013","El Mourouj":"2074","Mourouj":"2074",
    "Hammam Lif":"2050","Ezzahra":"2034","Megrine":"2033","Rades":"2040",
    "Manouba":"2010","Den Den":"2011",
    "Nabeul":"8000","Hammamet":"8050","Kelibia":"8090","Korba":"8070",
    "Grombalia":"8030","Soliman":"8020",
    "Zaghouan":"1100","Bizerte":"7000","Mateur":"7030",
    "Beja":"9000","Jendouba":"8100","Tabarka":"8110",
    "Kef":"7100","Siliana":"6100",
    "Sousse":"4000","Hammam Sousse":"4011","Akouda":"4022",
    "Monastir":"5000","Jemmal":"5020","Moknine":"5050","Skanes":"5000",
    "Mahdia":"5100","El Jem":"5160","Ksour Essef":"5180",
    "Sfax":"3000","Kairouan":"3100","Kasserine":"1200","Sbeitla":"1250",
    "Sidi Bouzid":"9100","Gabes":"6000","Medenine":"4100",
    "Ben Guerdane":"4160","Djerba":"4180","Zarzis":"4170",
    "Tataouine":"3200","Gafsa":"2100","Tozeur":"2200",
    "Kebili":"4200","Douz":"4260",
}

def get_postal_code(location):
    if not location:
        return ""
    ll = location.lower().strip()
    for key, cp in CODE_POSTAL.items():
        if key.lower() == ll:
            return cp
    for key, cp in CODE_POSTAL.items():
        if key.lower() in ll or ll in key.lower():
            return cp
    return ""

# ═══════════════════════════════════════════════════════════════════════
# COLONNES CSV — zone supprimée des terrains
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
        # 'zone' SUPPRIME
        'terrain_viabilise','constructible','dimensions_terrain',
        'facade','acces_route','acces_electricite','acces_eau','vocation',
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

EXCLUES_TITRE = {
    'loft','immeuble','bureaux','commerce','fonds de commerce',
    'hotel','garage','local',
}

# ═══════════════════════════════════════════════════════════════════════
# REGEX
# ═══════════════════════════════════════════════════════════════════════

RE_PRIX    = re.compile(r'([\d\s.,]+)\s*dt', re.I)
RE_SURF    = re.compile(r'(\d+(?:[.,]\d+)?)\s*m[²2]?', re.I)
RE_DATE    = re.compile(r'(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})')
RE_DATE_AJOUTE = re.compile(
    r'(?:ajout[eé]\s+le\s*:?\s*|publi[eé]e?\s+le\s*:?\s*)(\d{1,2})[/\-](\d{1,2})[/\-](\d{2,4})',
    re.I
)
RE_SUITE_N = re.compile(r'(\d+|un|une|deux|trois|quatre|cinq)\s+suites?', re.I)
RE_SUITE_1 = re.compile(r'\bsuite[s]?\b', re.I)
RE_CHAMBRE = re.compile(
    r'(\d+|un|une|deux|trois|quatre|cinq)\s+(?:grandes?\s+)?chambres?\s*(?!\s*(?:de\s+)?bain)',
    re.I
)
RE_SDB_N   = re.compile(
    r'(\d+|une?|deux|trois)\s+(?:salles?\s+(?:de\s+)?(?:bain|eau)|sdb)\b', re.I
)
RE_SDB_1   = re.compile(r"salle\s+(?:de\s+bain|d['']eau)", re.I)
RE_NIVEAUX = re.compile(r'\b(\d+)\s+niveaux?\b', re.I)
RE_R_PLUS  = re.compile(r'\bR\s*\+\s*(\d+)\b', re.I)
RE_ETAGE_N = re.compile(r'(\d+)\s*(?:e|er|ème|ere)?\s*étage', re.I)
RE_RDC     = re.compile(r'rdc|rez.de.chaussée|plain.pied', re.I)
RE_DIMENSIONS = re.compile(
    r'(\d+(?:[,.]\d+)?)\s*[mM]?\s*[xX×]\s*(\d+(?:[,.]\d+)?)\s*[mM]?'
)
RE_FACADE = re.compile(
    r'(?:fa[cç]ade\s*(?:de|:|\s)\s*(\d+(?:[,.]\d+)?)'
    r'|(\d+(?:[,.]\d+)?)\s*m[eè]tres?\s+(?:lin[eé]aires?|de\s+fa[cç]ade)'
    r'|(\d+(?:[,.]\d+)?)\s*ml\b)',
    re.I
)

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

def clean(t):
    return re.sub(r'\s+', ' ', str(t or '')).strip()

def to_int(t):
    c = re.sub(r'[^\d]', '', str(t or ''))
    return int(c) if c else 0

def detect_bool(text, *keywords):
    for kw in keywords:
        if re.search(re.escape(kw), text, re.I):
            return 'Oui'
    return 'Non'

# ═══════════════════════════════════════════════════════════════════════
# FIX TITRE FONCIER — Détection enrichie avec type
# Retourne : 'Titre Bleu', 'Titre Individuel', 'Titre Collectif',
#            'Titre En Cours', 'Oui' (générique), ou 'Non'
# ═══════════════════════════════════════════════════════════════════════

def detect_titre_foncier(text):
    t = text.lower()
    # Titre bleu (= titre individuel enregistré)
    if re.search(r'titre\s+bleu', t):
        return 'Titre Bleu'
    # Titre individuel
    if re.search(r'titre\s+individuel', t):
        return 'Titre Individuel'
    # Titre collectif / indivis
    if re.search(r'titre\s+collectif|titre\s+indivis|indivision', t):
        return 'Titre Collectif'
    # Titre en cours d'immatriculation
    if re.search(r'titre\s+en\s+cours|immatriculation\s+en\s+cours|en\s+cours\s+d\'immatriculation', t):
        return 'Titre En Cours'
    # Titre rose (= réquisition d'immatriculation)
    if re.search(r'titre\s+rose', t):
        return 'Titre Rose'
    # Titre foncier générique
    if re.search(r'titre\s+foncier|papier\s+l[eé]gal|dossier\s+juridique\s+complet', t):
        return 'Oui'
    return 'Non'


def detect_type(text):
    t = text.lower()
    for ex in EXCLUES_TITRE:
        if ex in t:
            return 'Exclu'
    if any(w in t for w in ['terrain','hectare','agricole']):
        return 'Terrain'
    if any(w in t for w in ['maison','villa','dar','riad','ferme','duplex maison']):
        return 'Maison/Villa'
    if any(w in t for w in ['appartement','appart','studio','duplex',
                             'penthouse','s+1','s+2','s+3','s+4','s+5']):
        return 'Appartement'
    return 'Autre'

def extract_gouvernorat(text):
    tl = text.lower()
    for g in GOVERNORATES:
        if g.lower() in tl:
            return g
    return ''

def clean_gouvernorat(raw):
    raw = re.sub(r'^(Acheter|Louer|Vacances)\s*[>&;gt]+\s*', '', raw, flags=re.I).strip()
    # Nettoyage &gt; HTML entity
    raw = re.sub(r'&gt;', '>', raw)
    raw = re.sub(r'>\s*', '', raw).strip()
    return REGION_GOV.get(raw, raw)

def parse_date(text):
    m = RE_DATE_AJOUTE.search(text or '')
    if m:
        j, mo, a = m.groups()
        if len(a) == 2: a = '20' + a
        return f"{a}-{mo.zfill(2)}-{j.zfill(2)}"
    m = RE_DATE.search(text or '')
    if m:
        j, mo, a = m.groups()
        if len(a) == 2: a = '20' + a
        return f"{a}-{mo.zfill(2)}-{j.zfill(2)}"
    return ''

def detect_etat(text):
    t = text.lower()
    if any(w in t for w in ['neuf','nouvelle construction','jamais habité',
                             'livraison','nouvellement construit']):
        return 'Neuf'
    if any(w in t for w in ['rénov','refait à neuf','remis à neuf']):
        return 'Rénové'
    if any(w in t for w in ['bon état','très bon état','bien entretenu']):
        return 'Bon état'
    if any(w in t for w in ['à rénover','travaux','à rafraîchir','ancien']):
        return 'À rénover'
    return 'Non précisé'

def detect_standing(text):
    t = text.lower()
    if any(w in t for w in ['luxe','prestige','ultra standing']):
        return 'Luxe'
    if any(w in t for w in ['haut standing','high standing','haut de gamme','grand standing']):
        return 'Haut standing'
    if any(w in t for w in ['moyen standing','confort']):
        return 'Moyen standing'
    if any(w in t for w in ['économique','economique','logement social']):
        return 'Économique'
    score = sum([
        'piscine' in t,
        bool(re.search(r'placard|dressing', t)),
        'chauffage central' in t,
        'climatisation' in t or 'clim' in t,
        'ascenseur' in t,
        'vue mer' in t,
    ])
    if score >= 5: return 'Luxe'
    if score >= 3: return 'Haut standing'
    if score >= 2: return 'Moyen standing'
    return 'Non précisé'

def parse_suites_chambres_sdb(text):
    t = text.lower()
    nb_suites = sum(mot_to_int(m) for m in RE_SUITE_N.findall(t))
    if not nb_suites and RE_SUITE_1.search(t):
        nb_suites = 1
    nb_ch = 0
    for m in RE_CHAMBRE.finditer(t):
        nb_ch = max(nb_ch, mot_to_int(m.group(1)))
    sdb_vals = [mot_to_int(m) for m in RE_SDB_N.findall(t)]
    nb_sdb = max(sdb_vals) if sdb_vals else (1 if RE_SDB_1.search(t) else 0)
    total_ch  = nb_ch + nb_suites
    total_sdb = nb_sdb + nb_suites
    has_dress = bool(re.search(r'dressing|placard', t, re.I)) or nb_suites > 0
    return (total_ch or ''), (total_sdb or ''), has_dress

def parse_niveau(text):
    t = text.lower()
    rp = RE_R_PLUS.search(t)
    if rp: return str(int(rp.group(1)) + 1)
    niv = RE_NIVEAUX.search(t)
    if niv: return niv.group(1)
    has_rdc = bool(RE_RDC.search(t))
    etages  = [to_int(m.group(1)) for m in RE_ETAGE_N.finditer(t) if m.group(1)]
    mx = max(etages) if etages else 0
    if has_rdc and mx > 0: return str(mx + 1)
    if mx > 0: return str(mx + 1)
    if has_rdc: return '1'
    return ''

def parse_etage(text):
    t = text.lower()
    if RE_RDC.search(t): return '0'
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
# COLLECTE DES LIENS
# ═══════════════════════════════════════════════════════════════════════

def collect_links(driver, max_pages):
    seen   = set()
    result = []

    print(f'  Page  1 → {LISTING_URL} ...', end='', flush=True)
    try:
        driver.get(LISTING_URL)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.gallery-image"))
            )
        except Exception:
            pass
        time.sleep(random.uniform(2, 3))

        found = _scrape_cards_from_driver(driver, seen, result)
        print(f' OK {found}')

        cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
            ),
            'Referer': LISTING_URL,
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
    except Exception as e:
        print(f' ERREUR {e}')
        cookies = {}
        headers = {}

    sess = requests.Session()
    sess.headers.update(headers)
    for name, val in cookies.items():
        sess.cookies.set(name, val)

    empty_pages = 0
    for page in range(2, max_pages + 1):
        if page % 50 == 0:
            print(f'\n  Page {page:4d} — {len(result)} liens collectés', end='')
        print('.', end='', flush=True)

        try:
            resp = sess.post(LOADMORE_URL, data={'page': str(page)}, timeout=20)
            if resp.status_code != 200 or not resp.text.strip():
                empty_pages += 1
                if empty_pages >= 3:
                    print(f'\n  ARRET: 3 pages vides à la page {page}')
                    break
                continue

            found = _scrape_cards_from_html(resp.text, seen, result)

            if found == 0:
                empty_pages += 1
                if empty_pages >= 3:
                    print(f'\n  ARRET: 3 pages vides à la page {page}')
                    break
            else:
                empty_pages = 0

            time.sleep(random.uniform(0.3, 0.8))

        except Exception as e:
            print(f'\n  ERREUR page {page}: {str(e)[:60]}')
            break

    print(f'\n  Total collecté : {len(result)} liens')
    return result


def _scrape_cards_from_driver(driver, seen, result):
    found = 0
    cards = driver.find_elements(By.CSS_SELECTOR, "div.gallery-image")
    for card in cards:
        try:
            link_el = card.find_element(By.CSS_SELECTOR, "a[href*='details.php']")
            href = link_el.get_attribute('href') or ''
        except Exception:
            continue
        if not href or href in seen:
            continue
        card_text = clean(card.text)
        tb = detect_type(card_text)
        if tb == 'Autre':
            try:
                titre_el = card.find_element(By.CSS_SELECTOR, "div.font-bold")
                tb = detect_type(titre_el.text)
            except Exception:
                pass
        if tb in ('Exclu', 'Autre'):
            continue
        seen.add(href)
        result.append((href, tb))
        found += 1
    return found


def _scrape_cards_from_html(html, seen, result):
    found = 0
    for href_m in re.finditer(
        r'href="((?:https://diarkoum\.tn/)?details\.php\?id_annonce=(\d+))"',
        html, re.I
    ):
        href = href_m.group(1)
        if not href.startswith('http'):
            href = BASE_URL + '/' + href.lstrip('/')
        if href in seen:
            continue
        start = max(0, href_m.start() - 500)
        end   = min(len(html), href_m.end() + 500)
        ctx   = re.sub(r'<[^>]+>', ' ', html[start:end])
        ctx   = re.sub(r'\s+', ' ', ctx)
        tb = detect_type(ctx)
        if tb in ('Exclu', 'Autre'):
            continue
        seen.add(href)
        result.append((href, tb))
        found += 1
    return found


# ═══════════════════════════════════════════════════════════════════════
# EXTRACTION D'UNE ANNONCE
# ═══════════════════════════════════════════════════════════════════════

def extract_detail(driver, url):
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

        # Titre
        titre = ''
        try:
            titre = clean(driver.find_element(By.TAG_NAME, 'h1').text)
        except Exception:
            for l in lines[:5]:
                if l.strip() and len(l.strip()) > 5:
                    titre = l.strip(); break
        if not titre:
            return None

        # Type
        type_bien = detect_type(titre)
        if type_bien in ('Exclu', 'Autre'):
            try:
                crumbs = driver.find_elements(By.CSS_SELECTOR, ".breadcrumb a")
                for c in crumbs:
                    tb = detect_type(clean(c.text))
                    if tb not in ('Autre', 'Exclu'):
                        type_bien = tb; break
            except Exception:
                pass
        if type_bien in ('Exclu', 'Autre'):
            return None

        item = {c: '' for c in COLS[type_bien]}
        item['source']      = SITE_NAME
        item['url_annonce'] = url
        item['type_bien']   = type_bien

        # Prix
        prix = 0
        try:
            val_el = driver.find_element(By.CSS_SELECTOR, "div.price div.value")
            raw_prix = re.sub(r'[^\d]', '', clean(val_el.text))
            if raw_prix:
                prix = int(raw_prix)
        except Exception:
            pass
        if not prix:
            for m in RE_PRIX.finditer(body):
                raw = re.sub(r'[\s.]', '', m.group(1))
                v   = to_int(raw)
                if v > 1000:
                    prix = v; break
        item['prix'] = prix or ''

        # Date
        date_insertion = ''
        try:
            spans = driver.find_elements(By.XPATH, "//span[contains(., 'Ajout')]")
            for sp in spans:
                d = parse_date(clean(sp.text))
                if d:
                    date_insertion = d; break
        except Exception:
            pass
        if not date_insertion:
            for line in lines:
                if 'ajout' in line.lower() or 'publi' in line.lower():
                    d = parse_date(line)
                    if d:
                        date_insertion = d; break
        if not date_insertion:
            date_insertion = datetime.now().strftime('%Y-%m-%d')
        item['date_insertion'] = date_insertion

        # Info-blocks (superficie, chambres, SDB, étage)
        superficie    = ''
        nb_ch_struct  = 0
        nb_sdb_struct = 0
        etage_struct  = ''
        try:
            info_blocks = driver.find_elements(By.CSS_SELECTOR, "div.info-block")
            for block in info_blocks:
                try:
                    val_txt   = clean(block.find_element(By.CSS_SELECTOR, "div.info-value").text)
                    label_txt = clean(block.find_element(By.CSS_SELECTOR, "div.info-text").text).lower()
                    val_num   = to_int(re.sub(r'[^\d]', '', val_txt.split()[0] if val_txt else ''))
                    if 'surface' in label_txt:
                        superficie = val_num
                    elif 'chambre' in label_txt:
                        nb_ch_struct = val_num
                    elif 'salle' in label_txt or 'bain' in label_txt:
                        nb_sdb_struct = val_num
                    elif 'étage' in label_txt or 'etage' in label_txt:
                        etage_struct = str(val_num)
                except Exception:
                    pass
        except Exception:
            pass
        item['superficie'] = superficie

        # Description
        desc = ''
        try:
            for sel in ["div.readmore_db p", "div.readmore_db", "div.presentation-text p"]:
                els = driver.find_elements(By.CSS_SELECTOR, sel)
                for el in els:
                    txt = clean(el.text)
                    if len(txt) > 80:
                        desc = txt; break
                if desc: break
        except Exception:
            pass
        full = f"{titre} {desc} {body}"

        # Chambres / SDB
        nb_ch_s, nb_sdb_s, has_dress = parse_suites_chambres_sdb(desc + ' ' + titre)
        nb_ch  = nb_ch_struct  or (int(str(nb_ch_s))  if str(nb_ch_s).isdigit()  else 0)
        nb_sdb = nb_sdb_struct or (int(str(nb_sdb_s)) if str(nb_sdb_s).isdigit() else 0)
        if not nb_ch:
            m = re.search(r'(\d+)\s+chambres?', titre, re.I)
            if m: nb_ch = to_int(m.group(1))
        if not superficie:
            m = RE_SURF.search(titre)
            if m:
                v = to_int(m.group(1))
                if v > 0: item['superficie'] = v

        if type_bien != 'Terrain':
            item['nb_chambres']    = nb_ch or ''
            item['nb_salles_bain'] = nb_sdb or ''
            item['dressing']       = 'Oui' if has_dress else 'Non'

        # Localisation
        gouvernorat = delegation = localite = code_postal = ''
        try:
            crumbs = driver.find_elements(By.CSS_SELECTOR, "nav.breadcrumb a, .breadcrumb a")
            crumb_texts = []
            for c in crumbs:
                t_clean = clean(c.text)
                if t_clean and t_clean.lower() not in ('accueil',):
                    crumb_texts.append(t_clean)
            if len(crumb_texts) >= 2:
                gouvernorat = clean_gouvernorat(crumb_texts[0])
                delegation  = crumb_texts[1].strip()
            elif len(crumb_texts) == 1:
                gouvernorat = clean_gouvernorat(crumb_texts[0])
        except Exception:
            pass
        if not gouvernorat:
            gouvernorat = extract_gouvernorat(body)
        gouvernorat = REGION_GOV.get(gouvernorat, gouvernorat)
        if not delegation:
            m = re.search(r'(?:à|a)\s+([A-ZÀ-Ü][a-zà-ü]+(?:\s+[A-ZÀ-Ü][a-zà-ü]+)?)', titre)
            if m: delegation = m.group(1).strip()
        localite = delegation

        item['gouvernorat'] = gouvernorat
        item['delegation']  = delegation
        item['localite']    = localite
        for loc in [delegation, localite, gouvernorat]:
            cp = get_postal_code(loc)
            if cp:
                code_postal = cp; break
        item['code_postal'] = code_postal

        # Etat & Standing
        item['etat']     = detect_etat(full)
        item['standing'] = detect_standing(full)

        # Niveau / Etage
        if type_bien == 'Maison/Villa':
            item['niveau'] = parse_niveau(full)
        elif type_bien == 'Appartement':
            item['etage'] = etage_struct or parse_etage(full)

        # Options
        opt_full = full.lower()

        item['balcon']            = detect_bool(opt_full, 'balcon')
        item['jardin']            = detect_bool(opt_full, 'jardin')
        item['piscine']           = detect_bool(opt_full, 'piscine')
        item['climatisation']     = detect_bool(opt_full, 'climatisation', 'clim')
        item['chauffage_central'] = detect_bool(opt_full, 'chauffage central', 'chauffage centrale')
        item['parking']           = detect_bool(opt_full, 'parking', 'place de parking',
                                                'place de parc', 'garage')
        item['vue_mer']           = detect_bool(opt_full,
                                                'vue mer', 'vue sur mer', 'bord de mer',
                                                'face à la mer', 'vue panoramique sur la mer')

        # TITRE FONCIER — valeur qualitative
        item['titre_foncier'] = detect_titre_foncier(full)

        if type_bien == 'Maison/Villa':
            item['terrasse'] = detect_bool(opt_full, 'terrasse')
        if type_bien == 'Appartement':
            item['ascenseur'] = detect_bool(opt_full, 'ascenseur')
            item['syndic']    = detect_bool(opt_full, 'syndic')

        # Terrain
        if type_bien == 'Terrain':
            item['terrain_viabilise'] = detect_bool(full, 'viabilisé', 'viabilise')
            item['constructible']     = detect_bool(full, 'constructible', 'construction')
            item['acces_route']       = detect_bool(full, 'accès route', 'route', 'piste', 'goudronné')
            item['acces_electricite'] = detect_bool(full, 'électricité', 'electricite', 'courant')
            item['acces_eau']         = detect_bool(full, 'puits', 'eau')

            for kws, val in [
                (['résidentiel','habitation','lotissement'], 'Résidentielle'),
                (['commercial','commerce'],                  'Commerciale'),
                (['industriel','usine'],                     'Industrielle'),
                (['agricole','agriculture','oliveraie'],     'Agricole'),
                (['touristique'],                            'Touristique'),
            ]:
                if any(kw in full.lower() for kw in kws):
                    item['vocation'] = val; break

            m = RE_DIMENSIONS.search(full)
            if m:
                d1 = m.group(1).replace(',', '.')
                d2 = m.group(2).replace(',', '.')
                item['dimensions_terrain'] = f"{d1}x{d2}"

            m = RE_FACADE.search(full)
            if m:
                val_f = m.group(1) or m.group(2) or m.group(3) or ''
                item['facade'] = val_f.replace(',', '.')

        # Forcer booléens
        for f in BOOL_FIELDS:
            if f in item and item[f] == '':
                item[f] = 'Non'
        # titre_foncier n'est plus un booléen simple, pas dans BOOL_FIELDS

        return item

    except Exception as e:
        print(f'\n  ERREUR {url[:60]} : {str(e)[:60]}')
        return None


# ═══════════════════════════════════════════════════════════════════════
# SCRAPER PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class DiarkoumScraper:

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
            print(f'  CSV : {os.path.basename(path)}')

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

    def run(self, max_pages=2000, headless=False):
        print('\n' + '='*70)
        print('DIARKOUM.TN SCRAPER - VERSION FINALE')
        print(f'URL    : {LISTING_URL}')
        print(f'Pages  : jusqu\'a {max_pages} (~{max_pages*9} annonces)')
        print('Attend : ~8320 annonces (1593 maisons + 1372 apparts + 5054 terrains)')
        print('='*70)
        print('\nCSV initialises :')
        self._init_csv()

        driver = init_driver(headless=headless)
        try:
            print(f'\nETAPE 1 - COLLECTE (max {max_pages} pages)')
            links = collect_links(driver, max_pages)
            if not links:
                print('Aucun lien trouve.')
                return

            print('\n   Repartition :')
            for t, n in Counter(tb for _, tb in links).items():
                print(f'      {t}: {n}')

            total  = len(links)
            ok     = 0
            errors = 0
            print(f'\nETAPE 2 - EXTRACTION ({total} annonces)')

            for i, (url, _) in enumerate(links, 1):
                pct = i / total * 100
                bar = '#' * int(pct/5) + '.' * (20 - int(pct/5))
                print(
                    f'\r  [{bar}] {i}/{total} ({pct:.0f}%) OK:{ok} ERR:{errors}',
                    end='', flush=True
                )
                item = extract_detail(driver, url)
                if item:
                    self._save(item)
                    ok += 1
                else:
                    errors += 1
                time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX))

            print(f'\n  OK: {ok} | ERREURS: {errors}')

        except KeyboardInterrupt:
            print('\nArret (Ctrl+C) — donnees partielles sauvegardees')
        finally:
            driver.quit()

        print(f'\n{"="*70}')
        print(f'TERMINE — {sum(self._counts.values())} annonces sauvegardees')
        for t, path in self._csv_paths.items():
            n = self._counts[t]
            if n:
                print(f'   {n:5d}  ->  {os.path.basename(path)}')
        print('='*70 + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scraper diarkoum.tn — vente immobiliere uniquement'
    )
    parser.add_argument('--pages',    type=int,  default=2000,
                        help='Pages max (defaut: 2000 = toutes les annonces)')
    parser.add_argument('--output',   type=str,  default='.',
                        help='Dossier de sortie')
    parser.add_argument('--headless', action='store_true',
                        help='Chrome sans fenetre')
    args = parser.parse_args()
    DiarkoumScraper(args.output).run(args.pages, args.headless)