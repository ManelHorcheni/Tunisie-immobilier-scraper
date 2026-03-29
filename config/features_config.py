"""
Configuration des features à extraire pour chaque type de bien
"""

# ============================================
# COLONNES COMMUNES À TOUS LES TYPES
# ============================================
COMMON_COLS = [
    # Identifiants
    'source_site',
    'code_annonce',
    'url_annonce',
    
    # Classification
    'nature',           # Vente / Location
    'type_bien',        # Maison, Appartement, Terrain
    
    # Localisation
    'gouvernorat',
    'delegation',
    'code_postal',
    
    # Caractéristiques de base
    'prix',
    'superficie_m2',
    'date_publication',
    
    # Documents
    'titre_foncier',    # Bleu / En cours / N/A
]

# ============================================
# CARACTÉRISTIQUES POUR MAISON
# ============================================
MAISON_COLS = [
    'etat',                 # Neuf, Rénové, Bon état, À rénover
    'standing',             # Économique, Moyen, Luxe
    'nb_chambres',
    'nb_sdb',
    'dressing',
    'balcon',
    'vue_mer',
    'parking',
    'piscine',
    'chauffage_central',
    'terrasse',
    'jardin',
    'niveau_maison',        # RDC, 1er, 2ème, etc.
    'climatisation',
]

# ============================================
# CARACTÉRISTIQUES POUR APPARTEMENT
# ============================================
APPARTEMENT_COLS = [
    'etat',                 # Neuf, Rénové, Bon état, À rénover
    'standing',             # Économique, Moyen, Luxe
    'nb_chambres',
    'nb_sdb',
    'dressing',
    'balcon',
    'vue_mer',
    'parking',
    'piscine',
    'chauffage_central',
    'jardin',
    'etage_appart',         # RDC, 1er, 2ème, etc.
    'ascenseur',
    'syndic',
    'climatisation',
]

# ============================================
# CARACTÉRISTIQUES POUR TERRAIN
# ============================================
TERRAIN_COLS = [
    'vue_mer',
    'terrain_viabilise',
    'constructible',
    'dimensions_terrain',   # L x l ou forme
    'zone',                  # Résidentielle, Industrielle, Agricole
    'facade',
    'acces_route',
    'acces_electricite',
    'acces_eau',
    'vocation',              # Habitat, Commerce, Mixte
]

# ============================================
# DICTIONNAIRE GLOBAL DES COLONNES PAR TYPE
# ============================================
SPECIFIC_COLS = {
    'Maison': MAISON_COLS,
    'Appartement': APPARTEMENT_COLS,
    'Terrain': TERRAIN_COLS,
}

# ============================================
# MAPPING DES TYPES DE BIENS DEPUIS LES SITES
# ============================================
PROPERTY_TYPE_MAPPING = {
    'tunisie_annonce': {
        'Maison': ['Maison', 'MAISON', 'maison', 'Villa', 'VILLA', 'villa', 'Dar', 'DAR', 'dar'],
        'Appartement': ['Appartement', 'APPARTEMENT', 'appart', 'App.', 'app.', 'Duplex', 'duplex'],
        'Terrain': ['Terrain', 'TERRAIN', 'terrain'],
    },
    'tayara': {
        'Maison': ['Maison', 'maison', 'Villa', 'villa'],
        'Appartement': ['Appartement', 'appartement'],
        'Terrain': ['Terrain', 'terrain'],
    },
    'mubawab': {
        'Maison': ['Maison', 'maison', 'Villa', 'villa'],
        'Appartement': ['Appartement', 'appartement'],
        'Terrain': ['Terrain', 'terrain'],
    }
}

# ============================================
# LISTE DES GOUVERNORATS TUNISIENS
# ============================================
GOVERNORATES = [
    'Tunis', 'Ariana', 'Ben Arous', 'Manouba',
    'Nabeul', 'Zaghouan', 'Bizerte', 'Béja',
    'Jendouba', 'Kef', 'Siliana', 'Sousse',
    'Monastir', 'Mahdia', 'Sfax', 'Kairouan',
    'Kasserine', 'Sidi Bouzid', 'Gabès', 'Medenine',
    'Tataouine', 'Gafsa', 'Tozeur', 'Kébili'
]

# ============================================
# MAPPING DES ZONES VERS GOUVERNORATS
# ============================================
ZONE_TO_GOUVERNORAT = {
    # Tunis
    'tunis': 'Tunis', 'menzah': 'Tunis', 'mutuelleville': 'Tunis',
    'lac': 'Tunis', 'berger du lac': 'Tunis', 'cité el khadhra': 'Tunis',
    'ennasr': 'Tunis', 'jardins de carthage': 'Tunis', 'carthage': 'Tunis',
    'la marsa': 'Tunis', 'sidi bou said': 'Tunis', 'aouina': 'Tunis',
    'bhar lazreg': 'Tunis',
    
    # Ariana
    'ariana': 'Ariana', 'ennasr 2': 'Ariana', 'chotrana': 'Ariana',
    'borj louzir': 'Ariana', 'raoued': 'Ariana',
    
    # Ben Arous
    'ben arous': 'Ben Arous', 'mourouj': 'Ben Arous', 'mégrine': 'Ben Arous',
    'ezzahra': 'Ben Arous', 'hammam lif': 'Ben Arous', 'radès': 'Ben Arous',
    
    # Nabeul / Cap Bon
    'nabeul': 'Nabeul', 'hammamet': 'Nabeul', 'beni khiar': 'Nabeul',
    'korba': 'Nabeul', 'kelibia': 'Nabeul', 'haouaria': 'Nabeul',
    'el haouaria': 'Nabeul', 'cap bon': 'Nabeul',
    
    # Sousse
    'sousse': 'Sousse', 'hammam sousse': 'Sousse', 'kantaoui': 'Sousse',
    
    # Sfax
    'sfax': 'Sfax', 'sakiet': 'Sfax', 'sprols': 'Sfax',
    
    # Monastir
    'monastir': 'Monastir', 'sahline': 'Monastir',
    
    # Bizerte
    'bizerte': 'Bizerte', 'menzel bourguiba': 'Bizerte',
    
    # Mahdia
    'mahdia': 'Mahdia',
}

# ============================================
# MAPPING DES CODES POSTAUX
# ============================================
CODE_POSTAL_MAP = {
    'Tunis': {
        'La Marsa': '2070',
        'Carthage': '2016',
        'El Menzah': '1004',
        'Mutuelleville': '1082',
        'Le Bardo': '2000',
        'La Goulette': '2060',
        'Le Kram': '2015',
        'Sidi Bou Said': '2026',
        'Bhar Lazreg': '2071',
        'Jardins de Carthage': '2016',
        'Aouina': '2080',
        'default': '1000'
    },
    'Ariana': {
        'Ennasr': '2037',
        'Raoued': '2083',
        'Chotrana': '2086',
        'Borj Louzir': '2073',
        'default': '2000'
    },
    'Ben Arous': {
        'El Mourouj': '2074',
        'Hammam Lif': '2050',
        'Megrine': '2033',
        'Ezzahra': '2034',
        'default': '3000'
    },
    'Manouba': {
        'La Manouba': '2010',
        'Den Den': '2011',
        'Oued Ellil': '2012',
        'default': '2010'
    },
    'Nabeul': {
        'Hammamet': '8050',
        'Nabeul': '8000',
        'Kelibia': '8090',
        'default': '8000'
    },
    'Sousse': {
        'Sousse': '4000',
        'Hammam Sousse': '4011',
        'Kantaoui': '4089',
        'default': '4000'
    },
    'Sfax': {
        'Sfax': '3000',
        'Sakiet Ezzit': '3021',
        'default': '3000'
    },
    'Monastir': {
        'Monastir': '5000',
        'Sahline': '5012',
        'default': '5000'
    },
    'Bizerte': {
        'Bizerte': '7000',
        'Menzel Bourguiba': '7050',
        'default': '7000'
    },
    'Mahdia': {
        'Mahdia': '5100',
        'default': '5100'
    },
    'Kairouan': {
        'Kairouan': '3100',
        'default': '3100'
    },
    'Gabès': {
        'Gabès': '6000',
        'default': '6000'
    },
    'Kasserine': {
        'Kasserine': '1200',
        'default': '1200'
    },
    'Gafsa': {
        'Gafsa': '2100',
        'default': '2100'
    },
    'Tozeur': {
        'Tozeur': '2200',
        'default': '2200'
    },
    'Kébili': {
        'Kébili': '4200',
        'default': '4200'
    },
    'Jendouba': {
        'Jendouba': '8100',
        'default': '8100'
    },
    'Béja': {
        'Béja': '9000',
        'default': '9000'
    },
    'Zaghouan': {
        'Zaghouan': '1100',
        'default': '1100'
    },
    'Sidi Bouzid': {
        'Sidi Bouzid': '9100',
        'default': '9100'
    },
    'Siliana': {
        'Siliana': '6100',
        'default': '6100'
    },
    'Medenine': {
        'Medenine': '4100',
        'default': '4100'
    },
    'Tataouine': {
        'Tataouine': '3200',
        'default': '3200'
    },
    'Kef': {
        'Kef': '7100',
        'default': '7100'
    }
}

# ============================================
# PATTERNS D'EXTRACTION
# ============================================
EXTRACTION_PATTERNS = {
    'superficie': [
        r'(\d+)\s*m[2²]', 
        r'(\d+)\s*m\.?$', 
        r'(\d+)\s*md',
        r'surface[:\s]*(\d+)\s*m', 
        r'(\d+)\s*m²',
        r'(\d+)\s*m2',
    ],
    'nb_chambres': [
        r'(\d+)\s*chambres?', 
        r'(\d+)\s*pi[eè]ces?',
        r'S\+(\d+)', 
        r'S(\d+)', 
        r'F(\d+)', 
        r'T(\d+)',
    ],
    'nb_sdb': [
        r'(\d+)\s*(salle de bain|sdb|salles de bains)',
        r'(\d+)\s*salle[s]?\s*de?\s*bains?',
    ],
    'etage': [
        (r'rdc|rez[-\s]de[-\s]chaussée', 'RDC'),
        (r'(\d+)[èe]r?\s*étage', r'\1er'),
        (r'(\d+)[èe]me?\s*étage', r'\1ème'),
        (r'(\d+)\s*(er|ème|eme)', r'\1ème'),
    ],
    'code_postal': [
        r'(\d{4})\s*$',
        r'cp[:\s]*(\d{4})',
        r'code postal[:\s]*(\d{4})',
    ],
    'standing': {
        'economique': ['économique', 'economique', 'standards'],
        'moyen': ['moyen', 'standing moyen', 'confort'],
        'luxe': ['luxe', 'de luxe', 'haut standing', 'prestige'],
    },
    'etat': {
        'neuf': ['neuf', 'nouveau', 'jamais habité', 'livraison'],
        'renove': ['rénové', 'renove', 'refait à neuf', 'récemment rénové'],
        'bon_etat': ['bon état', 'bon etat', 'bien entretenu', 'habitable'],
        'a_renover': ['à rénover', 'a renover', 'travaux', 'à rafraîchir'],
    },
    'titre_foncier': {
        'bleu': ['titre bleu', 'titre foncier bleu', 'bleu'],
        'vert': ['titre vert', 'titre foncier vert', 'vert'],
        'en_cours': ['en cours', 'en cours de', 'non disponible'],
    }
}