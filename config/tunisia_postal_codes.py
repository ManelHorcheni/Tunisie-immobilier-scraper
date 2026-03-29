#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fichier de codes postaux tunisiens par délégation
Basé sur la liste officielle des bureaux de poste
"""

# Dictionnaire complet des codes postaux par délégation
CODE_POSTAL_TUNISIE = {
    # ==================== ARIANA ====================
    "Carthage": "2035",
    "Cité Ennasr": "2001",
    "Borj Baccouch": "2027",
    "Soukra": "2036",
    "Ariana": "2080",
    "Ariana Géant": "2002",
    "Menzah 6": "2091",
    "Cité La Gazelle": "2083",
    
    # ==================== BEJA ====================
    "Mjaz Elbab": "9070",
    "Teboursouk": "9040",
    "Beja": "9000",
    "Dougga": "9032",
    
    # ==================== BEN AROUS ====================
    "Rades Medina": "2098",
    "Mhamdia": "1145",
    "Hammam Lif": "2050",
    "Radés": "2040",
    "Ezzahra": "2034",
    "Ben Arous": "2013",
    "Errisala": "2044",
    "Ezzahra El Habib": "2065",
    "Nouvelle Médina": "2063",
    "Mourouj 1": "2074",
    "Mourouj 3": "2068",
    "Megrine Riadh": "2014",
    "Mornag": "2090",
    "Megrine": "2033",
    
    # ==================== BIZERTE ====================
    "Bizerte": "7000",
    "Ras Djebel": "7070",
    "Bizerte bab mater": "7061",
    "Menzel Bourguiba": "7050",
    "MZL Bourguiba Ennajah": "7072",
    "Mateur": "7030",
    "Menzel Jemil": "7080",
    
    # ==================== GABES ====================
    "gabès hached": "6001",
    "Gabes B-Bhar": "6000",
    "Cite El Amel": "6033",
    "El Hamma": "6020",
    "Mareth": "6080",
    
    # ==================== GAFSA ====================
    "Gafsa": "2100",
    "Gafsa Cité Ennour": "2123",
    "Gafsa Intilaka": "2117",
    "Metlaoui": "2130",
    "El Guettar": "2180",
    "Errdayef": "2120",
    "Gafsa gare": "2111",
    
    # ==================== JENDOUBA ====================
    "Ain Drahem": "8130",
    "Bousalem": "8170",
    "Tabarka": "8110",
    "Jendouba": "8100",
    "Ghardimaou": "8160",
    
    # ==================== KAIROUAN ====================
    "bouhajla": "3180",
    "Kaiouran Okba": "3140",
    "Kairouan Sud": "3131",
    "Kairouan": "3100",
    "Oueslatia": "3120",
    "Hajeb Laayoune": "3160",
    "Cité Hajjem": "3129",
    "Cherarda": "3116",
    "Cite ennasr kairouan": "3182",
    "Cité Ibn Jazzar": "3199",
    "Haffouz": "3130",
    
    # ==================== KASSERINE ====================
    "Sbiba": "1270",
    "Feryana": "1240",
    "Tela": "1210",
    "Kasserine": "1200",
    "Sbeitla": "1250",
    
    # ==================== KEBILI ====================
    "Douz": "4260",
    "Kebili": "4200",
    "Kébili Biez": "4280",
    "souk lahad": "4230",
    
    # ==================== KEF ====================
    "Dahmani": "7170",
    "Kef": "7100",
    "Tejerouin": "7150",
    "Kef Ouest": "7117",
    
    # ==================== MAHDIA ====================
    "Hekaima": "5131",
    "Mahdia Republique": "5150",
    "Chebba": "5170",
    "Mahdia": "5100",
    "mahdia hiboun": "5111",
    "Ksour Essef": "5180",
    "Souassi": "5140",
    "El Jamm": "5160",
    
    # ==================== MANNOUBA ====================
    "Tebourba": "1130",
    "Mornaguia": "1110",
    "Denden": "2011",
    "Mannouba": "2010",
    "Oued Ellil": "2021",
    
    # ==================== MEDENINE ====================
    "El May": "4175",
    "Ajim": "4135",
    "Mouensa": "4144",
    "Midoun": "4116",
    "Zarzis": "4170",
    "Medenine": "4100",
    "Jerba": "4180",
    "Jerba Aéroport": "4120",
    "Cedouikech": "4145",
    "Akrou": "4176",
    "Benguerden": "4160",
    "Souihel": "4173",
    
    # ==================== MONASTIR ====================
    "Ksar Hellal": "5070",
    "Moknine": "5050",
    "Jammel": "5020",
    "Monastir": "5000",
    "Ksar Hlel Riadh": "5016",
    "Monastir République": "5060",
    "Teboulba": "5080",
    
    # ==================== NABEUL ====================
    "Kelibia": "8090",
    "yasmine hammamet": "8057",
    "nabeul thameur": "8062",
    "Béni Khiar": "8060",
    "Korba": "8070",
    "Mrezga": "8058",
    "Soliman": "8020",
    "Grombalia": "8030",
    "Dar Chaaban Fehri": "8011",
    "Hammamet": "8050",
    "Menzel Temim": "8080",
    "Nabeul": "8000",
    
    # ==================== SFAX ====================
    "merkez chihya": "3041",
    "Merkez Bouacida": "3031",
    "Cité El Habib": "3052",
    "Sidi Abbes": "3062",
    "Sfax Jadida": "3027",
    "merkez el alia": "3051",
    "Sfax 15 Novembre": "3089",
    "Cité Khayri": "3079",
    "Cité Bahri": "3064",
    "Esskhira": "3050",
    "Sfax": "3000",
    "Karkena": "3070",
    "Sfax Hached": "3069",
    "El Boustène": "3099",
    "tyna": "3083",
    "El Aguereb": "3030",
    "Sakiet Ezzit": "3021",
    "Jbeniyana": "3080",
    "El Hencha": "3010",
    "Sfax Maghreb Arabe": "3049",
    "El Mahres": "3060",
    "Sakiet Eddaier": "3011",
    
    # ==================== SIDI BOUZID ====================
    "Benaoun": "9120",
    "Bir El Hfay": "9113",
    "Jilma": "9110",
    "Meknasi": "9140",
    "Ergueb": "9170",
    "Sidi Bou Zid": "9100",
    
    # ==================== SILIANA ====================
    "Makthar": "6140",
    "Bouarada": "6180",
    "Siliana": "6100",
    "Rouhia": "6150",
    
    # ==================== SOUSSE ====================
    "Enfidha": "4030",
    "Sousse Khzema": "4051",
    "Hammam Sousse": "4011",
    "Hammam sousse plage": "4083",
    "Kalla Kebira": "4060",
    "Sousse": "4000",
    "sahloul": "4054",
    "Sousse Corniche": "4059",
    "Hammam Sousse Gharbi": "4017",
    "Msaken": "4070",
    "Sousse Ibn Khaldoun": "4061",
    "sousse erriadh": "4023",
    "kantaoui": "4089",
    
    # ==================== TATAOUINE ====================
    "Tataouine mahrajène": "3234",
    "tataouine Ettahrir": "3263",
    "Ghomrassen": "3220",
    "Tataouin": "3200",
    
    # ==================== TOZEUR ====================
    "Nefta": "2240",
    "Dguech": "2260",
    "Touzeur": "2200",
    "tozeur chokrasti": "2210",
    
    # ==================== TUNIS ====================
    "Zahrouni": "2051",
    "Cité Mahragéne": "1082",
    "Sidi Hassine": "1095",
    "Mohamed V": "1023",
    "Tunis RP": "1000",
    "Tunis Republique": "1001",
    "Monplaisir": "1073",
    "El Manar II": "2092",
    "Berge du Lac": "1053",
    "Tunis Thameur": "1069",
    "Carthage": "2016",
    "Marsa Safsaf": "2078",
    "Tunis Belvedère": "1002",
    "Bardo": "2000",
    "Tunis Hached": "1049",
    "Cite El Mhiri": "2045",
    "Cité Rommana": "1068",
    "Cite Ezzouhour": "2052",
    "Bab Menara": "1008",
    "Bab El Khadhra": "1075",
    "Tunis Aéroport": "2079",
    "El Menzah": "1004",
    "Bab Souika": "1006",
    "Cite El Khadra": "1003",
    
    # ==================== ZAGHOUAN ====================
    "El Fahs": "1140",
    "Bir Mcherga": "1141",
    "Zaghouan": "1100",
    "Jbel El West": "1111",
    "hammam zriba": "1152",
    "Ennadhour": "1160",
}


def get_postal_code(delegation: str, gouvernorat: str = "") -> str:
    """
    Retourne le code postal pour une délégation donnée
    Priorité: recherche exacte > recherche partielle > par défaut selon gouvernorat
    """
    if not delegation:
        return ""
    
    # Recherche exacte (insensible à la casse)
    delegation_lower = delegation.lower()
    for key, cp in CODE_POSTAL_TUNISIE.items():
        if key.lower() == delegation_lower:
            return cp
    
    # Recherche partielle (contient la délégation)
    for key, cp in CODE_POSTAL_TUNISIE.items():
        if key.lower() in delegation_lower or delegation_lower in key.lower():
            return cp
    
    # Codes postaux par défaut par gouvernorat
    default_codes = {
        "Tunis": "1000",
        "Ariana": "2080",
        "Ben Arous": "2013",
        "Manouba": "2010",
        "Nabeul": "8000",
        "Zaghouan": "1100",
        "Bizerte": "7000",
        "Béja": "9000",
        "Jendouba": "8100",
        "Kef": "7100",
        "Siliana": "6100",
        "Sousse": "4000",
        "Monastir": "5000",
        "Mahdia": "5100",
        "Sfax": "3000",
        "Kairouan": "3100",
        "Kasserine": "1200",
        "Sidi Bouzid": "9100",
        "Gabès": "6000",
        "Medenine": "4100",
        "Tataouine": "3200",
        "Gafsa": "2100",
        "Tozeur": "2200",
        "Kébili": "4200",
    }
    
    if gouvernorat in default_codes:
        return default_codes[gouvernorat]
    
    return ""


def get_all_delegations() -> list:
    """Retourne toutes les délégations disponibles"""
    return list(CODE_POSTAL_TUNISIE.keys())


def get_delegations_by_governorate(gouvernorat: str) -> list:
    """Retourne les délégations d'un gouvernorat spécifique"""
    # Mapping gouvernorat -> délégations (simplifié)
    governorate_map = {
        "Ariana": ["Carthage", "Cité Ennasr", "Borj Baccouch", "Soukra", "Ariana", "Menzah 6", "Cité La Gazelle"],
        "Beja": ["Mjaz Elbab", "Teboursouk", "Beja", "Dougga"],
        "Ben Arous": ["Rades Medina", "Mhamdia", "Hammam Lif", "Radés", "Ezzahra", "Ben Arous", "Errisala", 
                      "Ezzahra El Habib", "Nouvelle Médina", "Mourouj 1", "Mourouj 3", "Megrine Riadh", "Mornag", "Megrine"],
        "Bizerte": ["Bizerte", "Ras Djebel", "Menzel Bourguiba", "Mateur", "Menzel Jemil"],
        "Gabès": ["El Hamma", "Mareth"],
        "Gafsa": ["Gafsa", "Metlaoui", "El Guettar", "Errdayef"],
        "Jendouba": ["Ain Drahem", "Bousalem", "Tabarka", "Jendouba", "Ghardimaou"],
        "Kairouan": ["Kairouan", "Oueslatia", "Hajeb Laayoune", "Haffouz"],
        "Kasserine": ["Kasserine", "Sbeitla", "Sbiba", "Feryana", "Tela"],
        "Kebili": ["Douz", "Kebili"],
        "Kef": ["Kef", "Dahmani", "Tejerouin"],
        "Mahdia": ["Mahdia", "Chebba", "Ksour Essef", "El Jamm"],
        "Manouba": ["Mannouba", "Tebourba", "Mornaguia", "Denden", "Oued Ellil"],
        "Medenine": ["Medenine", "Zarzis", "Jerba", "Midoun", "Ajim", "Benguerden"],
        "Monastir": ["Monastir", "Ksar Hellal", "Moknine", "Jammel", "Teboulba"],
        "Nabeul": ["Nabeul", "Hammamet", "Kelibia", "Korba", "Béni Khiar", "Soliman", "Grombalia", "Dar Chaaban Fehri", "Menzel Temim"],
        "Sfax": ["Sfax", "Sakiet Ezzit", "Sakiet Eddaier", "El Mahres", "Karkena", "El Hencha", "Agareb"],
        "Sidi Bouzid": ["Sidi Bou Zid", "Meknasi", "Ergueb", "Jilma"],
        "Siliana": ["Siliana", "Makthar", "Bouarada", "Rouhia"],
        "Sousse": ["Sousse", "Hammam Sousse", "Msaken", "Kalla Kebira", "Enfidha", "kantaoui"],
        "Tataouine": ["Tataouin", "Ghomrassen"],
        "Tozeur": ["Touzeur", "Nefta", "Dguech"],
        "Tunis": ["Tunis RP", "El Menzah", "Bardo", "Carthage", "La Marsa", "Sidi Bou Said", "Berge du Lac", "Mutuelleville"],
        "Zaghouan": ["Zaghouan", "El Fahs", "Bir Mcherga", "Ennadhour"],
    }
    
    return governorate_map.get(gouvernorat, [])


if __name__ == "__main__":
    # Test
    print("="*60)
    print("📮 TEST DES CODES POSTAUX")
    print("="*60)
    
    test_delegations = [
        "Hammamet", "La Marsa", "Sousse", "Sfax", "Kairouan", "Tunis RP",
        "El Menzah", "Bardo", "Carthage", "Nabeul"
    ]
    
    for d in test_delegations:
        cp = get_postal_code(d)
        print(f"   {d}: {cp}")
    
    print("\n" + "="*60)
    print(f"📊 Total délégations: {len(CODE_POSTAL_TUNISIE)}")
    print("="*60)