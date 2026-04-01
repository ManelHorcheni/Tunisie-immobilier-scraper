#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════╗
║   FUSION DES CSV IMMOBILIERS — PAR TYPE DE BIEN                        ║
║   Sources : afariat, menzili, diarkoum, behya.tn                       ║
║   Résultat : 3 fichiers fusionnés                                       ║
║     → tous_maisons.csv                                                  ║
║     → tous_appartements.csv                                             ║
║     → tous_terrains.csv                                                 ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import os
import pandas as pd

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURATION — modifier INPUT_DIR si les CSV sont ailleurs
# ═══════════════════════════════════════════════════════════════════════

INPUT_DIR  = "."          # dossier contenant tous les CSV sources
OUTPUT_DIR = "."          # dossier de sortie des fichiers fusionnés

# ═══════════════════════════════════════════════════════════════════════
# FICHIERS PAR TYPE
# ═══════════════════════════════════════════════════════════════════════

FICHIERS = {
    'maisons': [
        "afariat_maisons.csv",
        "menzili_maisons.csv",
        "diarkoum_maisons.csv",
        "behya.tn_maisons_final - behya.tn_maisons_final.csv",
    ],
    'appartements': [
        "afariat_appartements.csv",
        "menzili_appartements.csv",
        "diarkoum_appartements.csv",
        "behya.tn_appartements_final - behya.tn_appartements_final.csv",
    ],
    'terrains': [
        "afariat_terrains.csv",
        "menzili_terrains.csv",
        "diarkoum_terrains.csv",
        "behya.tn_terrains_final.csv",
    ],
}

OUTPUT_FILES = {
    'maisons':      "tous_maisons.csv",
    'appartements': "tous_appartements.csv",
    'terrains':     "tous_terrains.csv",
}

# ═══════════════════════════════════════════════════════════════════════
# COLONNES CIBLES PAR TYPE (ordre standard)
# ═══════════════════════════════════════════════════════════════════════

COMMON_COLS = [
    'source', 'url_annonce', 'type_bien',
    'prix', 'date_insertion', 'gouvernorat', 'delegation',
    'localite', 'code_postal', 'superficie',
    'titre_foncier', 'vue_mer',
]

COLS_MAISONS = COMMON_COLS + [
    'etat', 'standing', 'nb_chambres', 'nb_salles_bain', 'dressing',
    'balcon', 'parking', 'piscine', 'chauffage_central', 'terrasse',
    'jardin', 'niveau', 'climatisation',
]

COLS_APPARTEMENTS = COMMON_COLS + [
    'etat', 'standing', 'nb_chambres', 'nb_salles_bain', 'dressing',
    'balcon', 'parking', 'piscine', 'chauffage_central', 'jardin',
    'etage', 'ascenseur', 'syndic', 'climatisation',
]

COLS_TERRAINS = COMMON_COLS + [
    'terrain_viabilise', 'constructible', 'dimensions_terrain',
    'facade', 'acces_route', 'acces_electricite', 'acces_eau', 'vocation',
]

COLS_TARGET = {
    'maisons':      COLS_MAISONS,
    'appartements': COLS_APPARTEMENTS,
    'terrains':     COLS_TERRAINS,
}

# ═══════════════════════════════════════════════════════════════════════
# FUSION
# ═══════════════════════════════════════════════════════════════════════

def fusionner():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print('\n' + '═'*70)
    print('  FUSION DES CSV IMMOBILIERS')
    print('═'*70)

    for type_bien, fichiers in FICHIERS.items():
        print(f'\n📁 TYPE : {type_bien.upper()}')
        frames = []

        for nom in fichiers:
            path = os.path.join(INPUT_DIR, nom)
            if not os.path.exists(path):
                print(f'  ⚠️  Fichier absent : {nom}')
                continue
            try:
                # Essayer utf-8-sig puis latin-1 si erreur
                try:
                    df = pd.read_csv(path, encoding='utf-8-sig', low_memory=False)
                except UnicodeDecodeError:
                    df = pd.read_csv(path, encoding='latin-1', low_memory=False)

                n = len(df)
                print(f'  ✅ {nom:<60} {n:>6} lignes')
                frames.append(df)
            except Exception as e:
                print(f'  ❌ {nom} → {e}')

        if not frames:
            print(f'  ⚠️  Aucun fichier chargé pour {type_bien}, saut.')
            continue

        # Concaténer tous les dataframes
        df_all = pd.concat(frames, ignore_index=True, sort=False)

        # Aligner les colonnes sur les colonnes cibles
        cols = COLS_TARGET[type_bien]
        for c in cols:
            if c not in df_all.columns:
                df_all[c] = ''           # ajouter les colonnes manquantes
        df_all = df_all[cols]            # garder l'ordre standard

        # Supprimer les doublons basés sur url_annonce (même annonce scrappée 2x)
        before = len(df_all)
        df_all = df_all.drop_duplicates(subset=['url_annonce'], keep='first')
        dupes  = before - len(df_all)

        # Sauvegarder
        out_path = os.path.join(OUTPUT_DIR, OUTPUT_FILES[type_bien])
        df_all.to_csv(out_path, index=False, encoding='utf-8-sig')

        print(f'\n  → {OUTPUT_FILES[type_bien]}')
        print(f'     Total lignes    : {len(df_all):,}')
        if dupes:
            print(f'     Doublons retirés : {dupes:,}')
        print(f'     Colonnes         : {len(cols)}')

        # Répartition par source
        if 'source' in df_all.columns:
            print('     Répartition par source :')
            for src, cnt in df_all['source'].value_counts().items():
                print(f'       {src:<20} {cnt:>6} annonces')

    print('\n' + '═'*70)
    print('✅ FUSION TERMINÉE')
    print('═'*70 + '\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Fusion des CSV immobiliers par type de bien'
    )
    parser.add_argument('--input',  type=str, default='.',
                        help='Dossier contenant les CSV sources (défaut: .)')
    parser.add_argument('--output', type=str, default='.',
                        help='Dossier de sortie (défaut: .)')
    args = parser.parse_args()

    INPUT_DIR  = args.input
    OUTPUT_DIR = args.output

    fusionner()