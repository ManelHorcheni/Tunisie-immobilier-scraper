#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔═══════════════════════════════════════════════════════════════════════╗
║   AFARIAT.TN SCRAPER — VERSION FINALE CORRIGÉE                      ║
║   ✅ Délégation & Localité depuis fil d'Ariane + champ Adresse      ║
║   ✅ Code postal : CP annonce > délégation > localité (dict ~300)    ║
║   ✅ Niveau → entier (1=RDC, 2=R+1, 3=R+2…)                        ║
║   ✅ Étage appartement → entier (0=RDC, 1=1er, 2=2ème…)            ║
║   ✅ Standing déduit mots-clés + score équipements                   ║
║   ✅ Suite = 1 chambre + 1 SDB + dressing automatique               ║
╚═══════════════════════════════════════════════════════════════════════╝
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
# 🗺️  CODES POSTAUX TUNISIENS (~300 délégations/localités)
# ═══════════════════════════════════════════════════════════════════════

CODE_POSTAL_TUNISIE = {
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
    "Zahrouni":"2051","Cité Mahragène":"1082","Mohamed V":"1023",
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
    "Mohamedia":"2084","Rades":"2040","Radés":"2040",
    "Mornag":"2090","Mhamdia":"1145",
    # Manouba
    "Manouba":"2010","Mannouba":"2010","Den Den":"2011","Denden":"2011",
    "Oued Ellil":"2021","Douar Hicher":"2086",
    "Jedaida":"7011","Tebourba":"1130","El Battan":"2013",
    "Borj El Amri":"2083","Mornaguia":"1110",
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
    "Ennadhour":"1160",
    # Bizerte
    "Bizerte":"7000","Menzel Bourguiba":"7050","Mateur":"7030",
    "Ras Jebel":"7025","Ras Djebel":"7070","Ghar El Melh":"7023",
    "Utique":"7020","Tinja":"7012","Joumine":"7034",
    "El Alia":"7041","Ghezala":"7044","Menzel Jemil":"7080",
    "Sejenane":"7040",
    # Béja
    "Béja":"9000","Beja":"9000","Nefza":"9020","Testour":"9040",
    "Téboursouk":"9060","Thibar":"9061","Amdoun":"9080",
    "Goubellat":"9030","Mejez El Bab":"9070",
    # Jendouba
    "Jendouba":"8100","Tabarka":"8110","Fernana":"8120",
    "Bou Salem":"8140","Ain Draham":"8130","Ain Drahem":"8130",
    "Ghardimaou":"8160","Oued Meliz":"8145","Bousalem":"8170",
    # Kef
    "Le Kef":"7100","Kef":"7100","Dahmani":"7170",
    "Sakiet Sidi Youssef":"7115","Tajerouine":"7150",
    "Kalaa Khasbah":"7122","Tejerouin":"7150",
    # Siliana
    "Siliana":"6100","Bou Arada":"6180","Gaafour":"6130",
    "El Krib":"6120","Makther":"6140","Makthar":"6140","Rouhia":"6150",
    # Sousse
    "Sousse":"4000","Hammam Sousse":"4011","Kantaoui":"4089",
    "Akouda":"4022","Kalaa Kebira":"4060","Kalla Kebira":"4060",
    "Kalaa Sghira":"4021","Sidi Bou Ali":"4040",
    "Sidi El Héni":"4041","M'Saken":"4070","Msaken":"4070",
    "Enfidha":"4030","Kondar":"4010","Sahloul":"4054",
    # Monastir
    "Monastir":"5000","Sahline":"5012","Ksar Hellal":"5070",
    "Jemmal":"5020","Jammel":"5020","Teboulba":"5080",
    "Bekalta":"5014","Bembla":"5011","Ksibet El Médiouni":"5013",
    "Ouerdanine":"5040","Sayada":"5025","Zeramdine":"5010","Moknine":"5050",
    # Mahdia
    "Mahdia":"5100","El Jem":"5160","El Jamm":"5160",
    "Ksour Essef":"5180","Chebba":"5170","Hebira":"5111","Souassi":"5140",
    # Sfax
    "Sfax":"3000","Sakiet Ezzit":"3021","Sakiet Eddaïer":"3011",
    "Sakiet Eddaier":"3011","Thyna":"3040","Agareb":"3030",
    "Bir Ali Ben Khalifa":"3060","El Amra":"3020",
    "El Hencha":"3010","Ghraiba":"3084","Jebeniana":"3080",
    "Jbeniyana":"3080","Kerkennah":"3070","Karkena":"3070",
    "La Skhira":"3041","Mahres":"3060","Menzel Chaker":"3051",
    "El Aguereb":"3030","El Mahres":"3060",
    # Kairouan
    "Kairouan":"3100","El Alaa":"3110","Haffouz":"3130",
    "Hajeb El Ayoun":"3160","Nasrallah":"3124",
    "Oueslatia":"3120","Sbikha":"3114","Bouhajla":"3180","Cherarda":"3116",
    # Kasserine
    "Kasserine":"1200","Sbeitla":"1250","Thala":"1210",
    "Feriana":"1240","Foussana":"1222","Haïdra":"1230","Sbiba":"1270",
    # Sidi Bouzid
    "Sidi Bouzid":"9100","Meknassy":"9140","Meknasi":"9140",
    "Menzel Bouzaiane":"9141","Regueb":"9170","Souk Jedid":"9131",
    "Bir El Hfay":"9113","Jilma":"9110",
    # Gabès
    "Gabès":"6000","Gabes":"6000","El Hamma":"6020",
    "Mareth":"6080","Matmata":"6015","Nouvelle Matmata":"6016",
    # Medenine
    "Medenine":"4100","Ben Guerdane":"4160","Benguerden":"4160",
    "Beni Khedache":"4110","Djerba":"4180","Jerba":"4180",
    "Djerba Midoun":"4116","Midoun":"4116","Zarzis":"4170",
    "Ajim":"4135","El May":"4175",
    # Tataouine
    "Tataouine":"3200","Tataouin":"3200","Remada":"3240","Ghomrassen":"3220",
    # Gafsa
    "Gafsa":"2100","El Ksar":"2110","Métlaoui":"2130","Metlaoui":"2130",
    "Moulares":"2131","Redeyef":"2132","El Guettar":"2180",
    # Tozeur
    "Tozeur":"2200","Touzeur":"2200","Nefta":"2240","Hazoua":"2260","Dguech":"2260",
    # Kébili
    "Kébili":"4200","Kebili":"4200","Douz":"4260","Souk Lahad":"4230",
}

def get_postal_code(location: str) -> str:
    """CP par délégation/localité : exact insensible à la casse puis partiel."""
    if not location:
        return ""
    ll = location.lower().strip()
    for key, cp in CODE_POSTAL_TUNISIE.items():
        if key.lower() == ll:
            return cp
    for key, cp in CODE_POSTAL_TUNISIE.items():
        kl = key.lower()
        if kl in ll or ll in kl:
            return cp
    return ""

# ═══════════════════════════════════════════════════════════════════════
# ⚙️  CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════

BASE_URL   = "https://afariat.com"
SITE_NAME  = "afariat"
OUTPUT_DIR = "."
PAUSE_MIN  = 1.5
PAUSE_MAX  = 3.0

LISTING_URLS = [
    "/categorie/Immobilier/Maison",
    "/categorie/Immobilier/Appartements",
    "/categorie/Immobilier/Terrain",
    "/immobilier",
]

GOVERNORATES = [
    'Tunis','Ariana','Ben Arous','Manouba','Nabeul','Zaghouan','Bizerte',
    'Béja','Jendouba','Kef','Siliana','Sousse','Monastir','Mahdia','Sfax',
    'Kairouan','Kasserine','Sidi Bouzid','Gabès','Medenine','Tataouine',
    'Gafsa','Tozeur','Kébili',
]

# ═══════════════════════════════════════════════════════════════════════
# 📋  COLONNES
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

RE_PRIX    = re.compile(r'(\d[\d\s]*?)\s*DT', re.I)
RE_SURF    = re.compile(r'(\d+(?:[.,]\d+)?)\s*m[²2]', re.I)
RE_CP      = re.compile(r'\b(\d{4})\b')

MOIS_FR = {
    'janvier':1,'février':2,'mars':3,'avril':4,'mai':5,'juin':6,
    'juillet':7,'août':8,'septembre':9,'octobre':10,'novembre':11,'décembre':12,
}

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

def detect_bool(text, *keywords) -> str:
    for kw in keywords:
        if re.search(r'\b' + re.escape(kw) + r'\b', text, re.I):
            return 'Oui'
    return 'Non'

def detect_type(text) -> str:
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

def extract_gouvernorat(text) -> str:
    tl = text.lower()
    for g in GOVERNORATES:
        if g.lower() in tl:
            return g
    return ''

def extract_cp(text) -> str:
    """Premier CP valide (4 chiffres 1000-9999) trouvé dans le texte."""
    for m in RE_CP.finditer(text or ''):
        cp = m.group(1)
        if 1000 <= int(cp) <= 9999:
            return cp
    return ''

def parse_date_fr(text) -> str:
    text = text.lower().strip()
    for mois_fr, mois_num in MOIS_FR.items():
        if mois_fr in text:
            m = re.search(r'(\d{1,2})\s+' + mois_fr + r'\s+(\d{4})', text)
            if m:
                jour, annee = m.groups()
                return f"{annee}-{mois_num:02d}-{int(jour):02d}"
    return ''

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
# 🔍  ÉTAT & STANDING
# ═══════════════════════════════════════════════════════════════════════

def detect_etat(text) -> str:
    t = text.lower()
    if any(w in t for w in ['neuf','nouvelle construction','jamais habité',
                             'jamais occupé','livraison','nouvellement construit']):
        return 'Neuf'
    if any(w in t for w in ['rénov','refait à neuf','remis à neuf','récemment rénové']):
        return 'Rénové'
    if any(w in t for w in ['bon état','très bon état','bien entretenu',
                             'parfait état','impeccable']):
        return 'Bon état'
    if any(w in t for w in ['à rénover','travaux','à rafraîchir','ancien']):
        return 'À rénover'
    return 'Non précisé'

def detect_standing(text) -> str:
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

# ═══════════════════════════════════════════════════════════════════════
# 🛏️  SUITES → chambres + SDB + dressing
# ═══════════════════════════════════════════════════════════════════════

def parse_suites_chambres_sdb(text):
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

# ═══════════════════════════════════════════════════════════════════════
# 🏢  NIVEAU (entier) et ÉTAGE (entier)
# ═══════════════════════════════════════════════════════════════════════

def parse_niveau(text, critere_val='') -> str:
    """
    Retourne le nombre de niveaux sous forme d'entier :
      RDC seul          → 1
      R+1               → 2
      R+2               → 3
      "2 niveaux"       → 2
      RDC + 1er étage   → 2
    """
    if critere_val:
        n = to_int(critere_val)
        if n:
            return str(n)
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

def parse_etage(text) -> str:
    """
    Retourne l'étage de l'appartement sous forme d'entier :
      RDC / rez-de-chaussée → 0
      1er étage             → 1
      2ème étage            → 2
    """
    t = text.lower()
    if RE_RDC.search(t):
        return '0'
    m = RE_ETAGE_N.search(t)
    if m:
        return m.group(1)
    return ''

# ═══════════════════════════════════════════════════════════════════════
# 📍  LOCALISATION — correction principale
# ═══════════════════════════════════════════════════════════════════════

def parse_localisation(driver, body: str):
    """
    Retourne (gouvernorat, delegation, localite, code_postal).

    Stratégie :
    1. Fil d'Ariane CSS (/ville/ → délégation, /annonces- → gouvernorat)
    2. Champ "Adresse" dans le texte brut → localité + CP direct
    3. Fallback gouvernorat depuis le body
    4. CP depuis dictionnaire si absent
    """
    gouvernorat = delegation = localite = code_postal = ''

    # ── 1. Fil d'Ariane ──────────────────────────────────────────────
    try:
        for lnk in driver.find_elements(By.CSS_SELECTOR, "a[href*='/ville/']"):
            txt = clean(lnk.text)
            if txt and txt.lower() not in ('', 'immobilier', 'accueil'):
                delegation = txt
                break
    except Exception:
        pass

    try:
        for lnk in driver.find_elements(By.CSS_SELECTOR, "a[href*='/annonces-']"):
            txt = clean(lnk.text)
            if txt in GOVERNORATES:
                gouvernorat = txt
                break
    except Exception:
        pass

    # ── 2. Champ "Adresse" via XPath CSS (plus fiable que texte brut)
    # HTML: <p><small>Adresse</small></p> + <small class="fw-bold">Valeur</small>
    adresse_raw = ''
    try:
        addr_xpaths = [
            "//p[.//small[normalize-space(text())='Adresse']]/following-sibling::small[contains(@class,'fw-bold')]",
            "//small[normalize-space(text())='Adresse']/parent::p/following-sibling::small",
            "//div[contains(@class,'col-10')][.//small[normalize-space(text())='Adresse']]//small[contains(@class,'fw-bold')]",
        ]
        for xp in addr_xpaths:
            els = driver.find_elements(By.XPATH, xp)
            if els:
                adresse_raw = clean(els[0].text)
                break
    except Exception:
        pass

    # Fallback : chercher dans le texte brut
    if not adresse_raw:
        body_lines = body.split('\n')
        for i, line in enumerate(body_lines):
            if line.strip() == 'Adresse' and i + 1 < len(body_lines):
                adresse_raw = body_lines[i + 1].strip()
                break

    if adresse_raw:
        # CP 4 chiffres directement dans l'adresse
        cp = extract_cp(adresse_raw)
        if cp:
            code_postal = cp

        # Décomposer les parties de l'adresse
        parts = [p.strip() for p in re.split(r'[,;]', adresse_raw) if p.strip()]
        gov_lower   = [g.lower() for g in GOVERNORATES]
        deleg_lower = delegation.lower()
        quartier    = []

        for part in parts:
            if re.fullmatch(r'\d{4}', part):
                continue
            if part.lower() in gov_lower:
                if not gouvernorat:
                    gouvernorat = part
                continue
            if deleg_lower and part.lower() == deleg_lower:
                continue
            if part.lower() in ('immobilier', 'tunisie', 'tunisie immobilier'):
                continue
            quartier.append(part)

        localite = ', '.join(quartier)

    # ── 3. Fallback gouvernorat depuis le body ─────────────────────────
    if not gouvernorat:
        gouvernorat = extract_gouvernorat(body)

    # ── 4. Fallback localité → délégation si vide ──────────────────────
    # Si aucune localité précise trouvée, utiliser la délégation
    if not localite and delegation:
        localite = delegation

    # ── 5. CP depuis dictionnaire ───────────────────────────────────────
    if not code_postal:
        for loc in [delegation, localite, gouvernorat]:
            cp = get_postal_code(loc)
            if cp:
                code_postal = cp
                break

    return gouvernorat, delegation, localite, code_postal

# ═══════════════════════════════════════════════════════════════════════
# 🔍  LECTURE D'UN CRITÈRE STRUCTURÉ (XPath)
# ═══════════════════════════════════════════════════════════════════════

def get_critere_val(driver, label: str) -> str:
    """
    Lit la valeur d'un critère structuré dans le bloc Critères.
    Structure HTML afariat :
      <div class="col-10">
        <p class="text-muted m-0"><small>LABEL</small></p>
        <small class="fw-bold">VALEUR</small>
        <!-- ou <a><small class="fw-bold">VALEUR</small></a> -->
      </div>
    """
    xpaths = [
        # Cas standard : <p><small>label</small></p> + <small fw-bold>
        f"//p[.//small[normalize-space(text())='{label}']]/following-sibling::small[contains(@class,'fw-bold')]",
        # Via lien <a>
        f"//p[.//small[normalize-space(text())='{label}']]/following-sibling::a//small",
        # div.col-10 parent
        f"//div[contains(@class,'col-10')][.//small[normalize-space(text())='{label}']]//small[contains(@class,'fw-bold')]",
        f"//div[contains(@class,'col-10')][.//small[normalize-space(text())='{label}']]//a/small",
    ]
    for xp in xpaths:
        try:
            els = driver.find_elements(By.XPATH, xp)
            for el in els:
                val = clean(el.text)
                if val:
                    return val
        except Exception:
            pass
    return ''


# ═══════════════════════════════════════════════════════════════════════
# 🔗  COLLECTE DES LIENS
# ═══════════════════════════════════════════════════════════════════════

def collect_links(driver, max_pages: int) -> list:
    seen   = set()
    result = []

    for base_listing in LISTING_URLS:
        url  = BASE_URL + base_listing
        page = 1

        while page <= max_pages:
            label = base_listing.split('/')[-1]
            print(f'  [{label}] p{page} ...', end='', flush=True)
            try:
                driver.get(url)
                time.sleep(random.uniform(2, 3))

                anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/annonce']")
                found   = 0
                for a in anchors:
                    href = a.get_attribute('href') or ''
                    if not re.search(r'/annonce[^s]', href):
                        continue
                    if 'Immobilier' not in href:
                        continue
                    if href in seen:
                        continue
                    try:
                        card_text = a.find_element(
                            By.XPATH, "ancestor::div[contains(@class,'card')][1]"
                        ).text
                    except Exception:
                        card_text = a.text or ''

                    if any(w in card_text.lower() for w in ['location','à louer','louer']):
                        continue

                    tb = detect_type(card_text) or detect_type(href)
                    if tb == 'Autre':
                        continue

                    seen.add(href)
                    result.append((href, tb))
                    found += 1

                print(f' ✅ {found}')

                # Pagination
                next_url = None
                try:
                    nxt = driver.find_element(
                        By.CSS_SELECTOR, "a[aria-label='Next'], a[rel='next']"
                    )
                    next_url = nxt.get_attribute('href')
                except Exception:
                    pass
                if not next_url:
                    try:
                        nxt = driver.find_element(
                            By.XPATH,
                            f"//a[contains(@class,'page-link') and normalize-space(text())='{page+1}']"
                        )
                        next_url = nxt.get_attribute('href')
                    except Exception:
                        pass
                if not next_url:
                    next_url = (
                        BASE_URL + base_listing + "?page=2" if page == 1
                        else re.sub(r'page=\d+', f'page={page+1}', url)
                    )

                if found == 0 and page > 1:
                    break

                url   = next_url
                page += 1

            except Exception as e:
                print(f' ❌ {str(e)[:60]}')
                break

    print(f'\n  📊 Total : {len(result)} liens')
    return result

# ═══════════════════════════════════════════════════════════════════════
# 📄  EXTRACTION D'UNE ANNONCE
# ═══════════════════════════════════════════════════════════════════════

EXCLUES_CAT = {
    'bureaux et locaux commerciaux','bureaux','local commercial',
    'entrepôt','hangar','usine','hôtel','hotel','fonds de commerce',
}

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
            for line in lines[:5]:
                l = line.strip()
                if l and 'DT' not in l and len(l) > 5:
                    titre = l
                    break
        if not titre:
            return None

        # ── Nature → Vente uniquement
        nature = ''
        for i, line in enumerate(lines):
            if "Nature de l'opération" in line and i + 1 < len(lines):
                nature = lines[i + 1].strip()
                break
        if 'location' in nature.lower():
            return None
        if not nature and re.search(r'\bà louer\b|\bpar mois\b|\b/mois\b', body, re.I):
            return None

        # ── Catégorie
        categorie = ''
        for i, line in enumerate(lines):
            if line.strip() == 'Catégorie' and i + 1 < len(lines):
                categorie = lines[i + 1].strip()
                break
        if any(ex in categorie.lower() for ex in EXCLUES_CAT):
            return None

        # ── Type de bien
        type_bien = detect_type(f"{titre} {categorie}")
        if type_bien == 'Autre':
            return None

        # ── Initialiser
        item = {c: '' for c in COLS[type_bien]}
        item['source']      = SITE_NAME
        item['url_annonce'] = url
        item['type_bien']   = type_bien

        # ── Prix
        prix = 0
        try:
            pe = driver.find_element(
                By.XPATH,
                "//*[contains(@class,'text-primary') or contains(@class,'fw-bolder')]"
            )
            m = RE_PRIX.search(pe.text)
            if m:
                prix = to_int(m.group(1))
        except Exception:
            pass
        if not prix:
            for m in RE_PRIX.finditer(body):
                v = to_int(m.group(1))
                if v > 1000:
                    prix = v
                    break
        item['prix'] = prix

        # ── Date de publication
        # HTML: <b>Publiée</b>: 6 décembre 2025
        # body text: "Publiée :" puis date sur ligne suivante OU même ligne
        date_insertion = datetime.now().strftime('%Y-%m-%d')
        for i, line in enumerate(lines):
            if 'Publi' in line and ('e' in line.lower()):
                stripped = line.strip()
                if not ('Publiée' in stripped or 'Publie' in stripped):
                    continue
                # Cas 1 : date sur la même ligne après ":"
                after = re.sub(r'.*Publi[eé]e\s*:?\s*', '', stripped, flags=re.I).strip()
                parsed = parse_date_fr(after)
                if parsed:
                    date_insertion = parsed
                    break
                # Cas 2 : date sur la ligne suivante
                if i + 1 < len(lines):
                    parsed = parse_date_fr(lines[i + 1].strip())
                    if parsed:
                        date_insertion = parsed
                break
        item['date_insertion'] = date_insertion

        # ── Superficie
        for m in RE_SURF.finditer(body):
            v = to_int(m.group(1))
            if v > 0:
                item['superficie'] = v
                break

        # ── Description
        desc = ''
        try:
            for p in driver.find_elements(By.TAG_NAME, 'p'):
                txt = clean(p.text)
                if len(txt) > 80 and 'DT' not in txt and 'Afariat' not in txt:
                    desc = txt
                    break
        except Exception:
            pass
        full = f"{titre} {desc} {body}"

        # ── Localisation (correction principale)
        gouvernorat, delegation, localite, code_postal = parse_localisation(driver, body)
        item['gouvernorat'] = gouvernorat
        item['delegation']  = delegation
        item['localite']    = localite
        item['code_postal'] = code_postal

        # ── État & Standing
        item['etat']     = detect_etat(full)
        item['standing'] = detect_standing(full)

        # ── Chambres / SDB / Dressing
        nb_ch, nb_sdb, has_dress = parse_suites_chambres_sdb(full)
        item['nb_chambres']    = nb_ch
        item['nb_salles_bain'] = nb_sdb
        item['dressing']       = 'Oui' if has_dress else 'Non'

        # ── Niveau (Maison) → entier | Étage (Appartement) → entier
        if type_bien == 'Maison/Villa':
            # Priorité : critère structuré "Nombre de niveaux" via XPath
            niv_critere = get_critere_val(driver, 'Nombre de niveaux')
            # Fallback texte brut
            if not niv_critere:
                for i, line in enumerate(lines):
                    if 'Nombre de niveaux' in line and i + 1 < len(lines):
                        niv_critere = lines[i + 1].strip()
                        break
            item['niveau'] = parse_niveau(full, niv_critere)

        elif type_bien == 'Appartement':
            # Priorité : critère structuré "Etage" via XPath
            # HTML: <small>Etage</small> + <small class="fw-bold">2</small>
            etage_critere = get_critere_val(driver, 'Etage')
            if etage_critere:
                # Valeur directe depuis le critère (ex: "2", "RDC", "1")
                if re.fullmatch(r'\d+', etage_critere.strip()):
                    item['etage'] = etage_critere.strip()
                elif re.search(r'rdc|rez', etage_critere, re.I):
                    item['etage'] = '0'
                else:
                    item['etage'] = etage_critere.strip()
            else:
                # Fallback : déduire depuis le texte
                item['etage'] = parse_etage(full)

        # ── Booléens communs
        item['balcon']            = detect_bool(full, 'balcon')
        item['jardin']            = detect_bool(full, 'jardin')
        item['piscine']           = detect_bool(full, 'piscine')
        item['climatisation']     = detect_bool(full, 'climatisation', 'clim')
        item['chauffage_central'] = detect_bool(full, 'chauffage central')
        item['parking']           = detect_bool(full, 'parking', 'place de parking',
                                                'places de parking', 'portail électrique')
        item['titre_foncier']     = detect_bool(full, 'titre foncier', 'titre bleu',
                                                'titre individuel', 'titre rose')
        item['vue_mer']           = detect_bool(full, 'vue mer', 'vue sur mer', 'bord de mer')

        if type_bien == 'Maison/Villa':
            item['terrasse'] = detect_bool(full, 'terrasse')

        if type_bien == 'Appartement':
            # Ascenseur : critère structuré "Ascenceur" (avec faute d'orthographe du site)
            # HTML: <small>Ascenceur</small> + <small class="fw-bold">non</small> ou "oui"
            asc_val = get_critere_val(driver, 'Ascenceur') or get_critere_val(driver, 'Ascenseur')
            if asc_val:
                item['ascenseur'] = 'Oui' if 'oui' in asc_val.lower() else 'Non'
            else:
                item['ascenseur'] = detect_bool(full, 'ascenseur')
            item['syndic'] = detect_bool(full, 'syndic')

        # ── Terrain spécifique
        if type_bien == 'Terrain':
            item['terrain_viabilise'] = detect_bool(full, 'viabilisé','viabilise')
            item['constructible']     = detect_bool(full, 'constructible')
            item['acces_route']       = detect_bool(full, 'accès route','route','goudronné')
            item['acces_electricite'] = detect_bool(full, 'électricité','electricite','courant')
            item['acces_eau']         = detect_bool(full, 'eau')

            for kws, val in [
                (['résidentiel','habitation'], 'Résidentielle'),
                (['commercial','commerce'],    'Commerciale'),
                (['industriel','usine'],       'Industrielle'),
                (['agricole','agriculture'],   'Agricole'),
                (['touristique'],              'Touristique'),
            ]:
                if any(kw in full.lower() for kw in kws):
                    item['vocation'] = val
                    break

            for kws, val in [
                (['zone urbaine','urbain'],    'Urbaine'),
                (['agricole'],                 'Agricole'),
                (['touristique'],              'Touristique'),
                (['industriel'],               'Industrielle'),
            ]:
                if any(kw in full.lower() for kw in kws):
                    item['zone'] = val
                    break

            m = re.search(r'(\d+)\s*[xX×]\s*(\d+)', full)
            if m:
                item['dimensions_terrain'] = f"{m.group(1)}x{m.group(2)}"
            m = re.search(r'fa[çc]ade\s*:?\s*(\d+)', full, re.I)
            if m:
                item['facade'] = m.group(1)

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

class AfariatScraper:

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

    def run(self, max_pages=20, headless=False):
        print('\n' + '═'*70)
        print('🏠  AFARIAT.TN SCRAPER — VERSION FINALE CORRIGÉE')
        print("   ✅ Délégation & Localité : fil d'Ariane + champ Adresse")
        print("   ✅ Code postal : CP annonce > délégation > dict (~300 villes)")
        print("   ✅ Niveau → entier (1=RDC, 2=R+1…) | Étage → entier (0=RDC)")
        print("   ✅ Standing déduit mots-clés + score équipements")
        print("   ✅ Suite = 1 chambre + 1 SDB + dressing automatique")
        print('═'*70)
        self._init_csv()

        driver = init_driver(headless=headless)
        try:
            print('\n📋 ÉTAPE 1 — COLLECTE')
            links = collect_links(driver, max_pages)
            if not links:
                print('❌ Aucun lien trouvé.')
                return

            print('\n   Répartition :')
            for t, n in Counter(tb for _, tb in links).items():
                print(f'      {t}: {n}')

            total = len(links)
            ok = errors = 0
            print(f'\n🔍 ÉTAPE 2 — EXTRACTION ({total} annonces)')

            for i, (url, _) in enumerate(links, 1):
                pct = i / total * 100
                bar = '█' * int(pct/5) + '░' * (20 - int(pct/5))
                print(f'\r  [{bar}] {i}/{total} ({pct:.0f}%) ✅{ok} ❌{errors}',
                      end='', flush=True)
                item = extract_detail(driver, url)
                if item:
                    self._save(item)
                    ok += 1
                else:
                    errors += 1
                time.sleep(random.uniform(PAUSE_MIN, PAUSE_MAX))

            print(f'\n  ✅ {ok} | ❌ {errors}')

        except KeyboardInterrupt:
            print('\n⚠️  Arrêt')
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--pages',    type=int,  default=20)
    parser.add_argument('--output',   type=str,  default='.')
    parser.add_argument('--headless', action='store_true')
    args = parser.parse_args()
    AfariatScraper(args.output).run(args.pages, args.headless)