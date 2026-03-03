import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from dash import Dash, html, dcc, Input, Output, callback
import dash
import numpy as np
from datetime import datetime, timedelta

# ============================================
# INITIALISATION
# ============================================
app = Dash(__name__, title="ImmoMulti - Dashboard Tunisie")

API_BASE_URL = "http://localhost:5000"

# Style global
COLORS = {
    'tunisie_annonce': '#3498db',
    'tayara': '#e74c3c',
    'mubawab': '#2ecc71',
    'background': '#f8fafc',
    'text': '#1e293b',
    'card': '#ffffff'
}

# ============================================
# FONCTIONS DE RÉCUPÉRATION
# ============================================
def fetch_data():
    """Récupère les données depuis l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/annonces?per_page=1000", timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Vérifier la structure des données
        if isinstance(data, dict) and 'annonces' in data:
            df = pd.DataFrame(data['annonces'])
            print(f"✅ Données récupérées: {len(df)} annonces")
            return df
        elif isinstance(data, list):
            df = pd.DataFrame(data)
            print(f"✅ Données récupérées (liste): {len(df)} annonces")
            return df
        else:
            print(f"⚠️ Structure de données inattendue: {type(data)}")
            return pd.DataFrame()
            
    except requests.exceptions.ConnectionError:
        print("❌ Impossible de se connecter à l'API. Vérifiez que l'API tourne sur http://localhost:5000")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Erreur API: {e}")
        return pd.DataFrame()

def preprocess_data(df):
    """Nettoie les données"""
    if df.empty:
        return df
    
    # Nettoyer les noms de colonnes
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Convertir le prix en numérique
    if 'price' in df.columns:
        df['price'] = pd.to_numeric(df['price'], errors='coerce')
    elif 'price_numeric' in df.columns:
        df['price'] = pd.to_numeric(df['price_numeric'], errors='coerce')
    
    # Convertir la date
    if 'publication_date' in df.columns:
        df['publication_date'] = pd.to_datetime(df['publication_date'], errors='coerce')
    elif 'scrape_date' in df.columns:
        df['publication_date'] = pd.to_datetime(df['scrape_date'], errors='coerce')
    else:
        df['publication_date'] = datetime.now()
    
    # Ajouter une colonne source si elle n'existe pas
    if 'source_site' not in df.columns:
        df['source_site'] = 'inconnu'
    
    # Ajouter une colonne location si elle n'existe pas
    if 'location' not in df.columns:
        df['location'] = 'Non spécifié'
    
    # Ajouter une colonne property_type si elle n'existe pas
    if 'property_type' not in df.columns:
        df['property_type'] = 'Non spécifié'
    
    return df

# Chargement initial
df = preprocess_data(fetch_data())

# ============================================
# LAYOUT
# ============================================
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("🏠 ImmoMulti - Dashboard Immobilier Tunisie", 
               style={'color': COLORS['text'], 'marginBottom': '5px'}),
        html.P("Agrégation multi-sites | Tunisie Annonce + Tayara.tn", 
              style={'color': '#64748b', 'fontSize': '16px'}),
        html.Div(id='api-status', style={'color': '#27ae60', 'fontSize': '14px'}),
    ], style={'textAlign': 'center', 'padding': '30px 0'}),
    
    html.Div(id='error-message', style={'textAlign': 'center', 'color': '#dc2626'}),
    
    # KPI Cards
    html.Div([
        html.Div([
            html.H4("📊 Total annonces", style={'color': '#64748b', 'marginBottom': '5px'}),
            html.H2(id='kpi-total', children="0", 
                   style={'color': COLORS['text'], 'margin': '0', 'fontSize': '32px'}),
        ], style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 
                 'display': 'inline-block', 'margin': '1%', 'textAlign': 'center', 'padding': '20px'}),
        
        html.Div([
            html.H4("🏷️ Types de biens", style={'color': '#64748b', 'marginBottom': '5px'}),
            html.H2(id='kpi-types', children="0", 
                   style={'color': COLORS['text'], 'margin': '0', 'fontSize': '32px'}),
        ], style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 
                 'display': 'inline-block', 'margin': '1%', 'textAlign': 'center', 'padding': '20px'}),
        
        html.Div([
            html.H4("📍 Localisations", style={'color': '#64748b', 'marginBottom': '5px'}),
            html.H2(id='kpi-locations', children="0", 
                   style={'color': COLORS['text'], 'margin': '0', 'fontSize': '32px'}),
        ], style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 
                 'display': 'inline-block', 'margin': '1%', 'textAlign': 'center', 'padding': '20px'}),
        
        html.Div([
            html.H4("💰 Prix moyen", style={'color': '#64748b', 'marginBottom': '5px'}),
            html.H2(id='kpi-prix-moyen', children="0 DT", 
                   style={'color': COLORS['text'], 'margin': '0', 'fontSize': '32px'}),
        ], style={'backgroundColor': COLORS['card'], 'borderRadius': '12px', 
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'width': '22%', 
                 'display': 'inline-block', 'margin': '1%', 'textAlign': 'center', 'padding': '20px'}),
    ], style={'marginBottom': '30px'}),
    
    # Filtre source
    html.Div([
        html.Div([
            html.Label("📌 Filtrer par source:", style={'fontWeight': '600', 'marginRight': '10px'}),
            dcc.Dropdown(
                id='filter-source',
                options=[
                    {'label': '🌐 Tous les sites', 'value': 'all'},
                    {'label': '📰 Tunisie Annonce', 'value': 'tunisie_annonce'},
                    {'label': '🛒 Tayara.tn', 'value': 'tayara'},
                ],
                value='all',
                clearable=False,
                style={'width': '300px', 'display': 'inline-block'}
            )
        ], style={'textAlign': 'center', 'padding': '10px'}),
    ], style={'backgroundColor': COLORS['card'], 'padding': '20px', 
             'borderRadius': '12px', 'marginBottom': '20px'}),
    
    # Graphiques
    html.Div([
        html.Div([
            html.H3("📈 Distribution des prix", style={'color': COLORS['text']}),
            dcc.Graph(id='chart-prix-distribution')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%',
                 'backgroundColor': COLORS['card'], 'padding': '15px', 'borderRadius': '12px',
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3("🥧 Répartition par site", style={'color': COLORS['text']}),
            dcc.Graph(id='chart-repartition-site')
        ], style={'width': '48%', 'display': 'inline-block',
                 'backgroundColor': COLORS['card'], 'padding': '15px', 'borderRadius': '12px',
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    ], style={'marginBottom': '20px'}),
    
    html.Div([
        html.Div([
            html.H3("📊 Top 10 localisations", style={'color': COLORS['text']}),
            dcc.Graph(id='chart-top-locations')
        ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '2%',
                 'backgroundColor': COLORS['card'], 'padding': '15px', 'borderRadius': '12px',
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
        
        html.Div([
            html.H3("📅 Évolution temporelle", style={'color': COLORS['text']}),
            dcc.Graph(id='chart-evolution')
        ], style={'width': '48%', 'display': 'inline-block',
                 'backgroundColor': COLORS['card'], 'padding': '15px', 'borderRadius': '12px',
                 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    ]),
    
    # Tableau récapitulatif
    html.Div([
        html.H3("📋 Dernières annonces", style={'color': COLORS['text']}),
        html.Div(id='table-recent', style={'marginTop': '10px'})
    ], style={'marginTop': '30px', 'backgroundColor': COLORS['card'], 
             'padding': '20px', 'borderRadius': '12px',
             'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Stockage des données
    dcc.Interval(id='interval-component', interval=30*1000, n_intervals=0),  # Refresh toutes les 30s
    dcc.Store(id='data-store', data=df.to_dict('records') if not df.empty else [])
], style={'fontFamily': 'Arial, sans-serif', 'padding': '20px', 
         'backgroundColor': COLORS['background'], 'maxWidth': '1400px', 
         'margin': '0 auto'})

# ============================================
# CALLBACKS
# ============================================

@callback(
    [Output('data-store', 'data'),
     Output('api-status', 'children'),
     Output('error-message', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def refresh_data(n_intervals):
    """Actualise les données périodiquement"""
    new_df = fetch_data()
    processed_df = preprocess_data(new_df)
    
    if processed_df.empty:
        return [], "⚠️ API non disponible", html.Div(
            "❌ Impossible de se connecter à l'API. Vérifiez que l'API Flask tourne sur http://localhost:5000",
            style={'color': '#dc2626', 'backgroundColor': '#fee2e2', 'padding': '10px', 'borderRadius': '8px'}
        )
    
    return processed_df.to_dict('records'), "✅ Connecté à l'API", ""

@callback(
    [Output('kpi-total', 'children'),
     Output('kpi-types', 'children'),
     Output('kpi-locations', 'children'),
     Output('kpi-prix-moyen', 'children'),
     Output('chart-prix-distribution', 'figure'),
     Output('chart-repartition-site', 'figure'),
     Output('chart-top-locations', 'figure'),
     Output('chart-evolution', 'figure'),
     Output('table-recent', 'children')],
    [Input('data-store', 'data'),
     Input('filter-source', 'value')]
)
def update_dashboard(data, source):
    """Met à jour tous les composants du dashboard"""
    
    # Créer un DataFrame à partir des données
    if data and len(data) > 0:
        df = pd.DataFrame(data)
        df = preprocess_data(df)  # Re-nettoyer au cas où
    else:
        df = pd.DataFrame()
    
    # Appliquer le filtre source
    if source != 'all' and not df.empty and 'source_site' in df.columns:
        df = df[df['source_site'] == source]
    
    # ===== KPI =====
    if df.empty:
        total = "0"
        types = "0"
        locations = "0"
        prix_moyen = "0 DT"
    else:
        total = str(len(df))
        types = str(len(df['property_type'].unique())) if 'property_type' in df.columns else "0"
        locations = str(len(df['location'].unique())) if 'location' in df.columns else "0"
        
        if 'price' in df.columns and not df['price'].isna().all():
            prix_moyen = f"{df['price'].mean():,.0f} DT"
        else:
            prix_moyen = "N/A"
    
    # ===== GRAPHIQUE 1: Distribution des prix =====
    if not df.empty and 'price' in df.columns and not df['price'].isna().all():
        fig1 = px.histogram(
            df, 
            x='price',
            nbins=20,
            title=f"Distribution des prix ({len(df)} annonces)",
            color_discrete_sequence=['#3498db'],
            labels={'price': 'Prix (DT)', 'count': 'Nombre'}
        )
        fig1.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            margin=dict(l=40, r=40, t=50, b=40)
        )
    else:
        fig1 = go.Figure()
        fig1.add_annotation(
            text="Aucune donnée de prix disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig1.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    
    # ===== GRAPHIQUE 2: Répartition par site =====
    if not df.empty and 'source_site' in df.columns:
        site_counts = df['source_site'].value_counts()
        fig2 = px.pie(
            values=site_counts.values,
            names=site_counts.index,
            title="Annonces par site",
            color_discrete_map=COLORS
        )
        fig2.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    else:
        fig2 = go.Figure()
        fig2.add_annotation(
            text="Aucune donnée de source disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig2.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    
    # ===== GRAPHIQUE 3: Top localisations =====
    if not df.empty and 'location' in df.columns:
        top_locs = df['location'].value_counts().head(10)
        fig3 = px.bar(
            x=top_locs.values,
            y=top_locs.index,
            orientation='h',
            title="Top 10 localisations",
            labels={'x': "Nombre d'annonces", 'y': ''},
            color_discrete_sequence=['#3498db']
        )
        fig3.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40),
            yaxis={'categoryorder':'total ascending'}
        )
    else:
        fig3 = go.Figure()
        fig3.add_annotation(
            text="Aucune donnée de localisation disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig3.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    
    # ===== GRAPHIQUE 4: Évolution temporelle =====
    if not df.empty and 'publication_date' in df.columns:
        df['date'] = pd.to_datetime(df['publication_date']).dt.date
        daily = df.groupby('date').size().reset_index(name='count')
        daily = daily.sort_values('date')
        
        fig4 = px.line(
            daily,
            x='date',
            y='count',
            title="Évolution quotidienne",
            markers=True,
            labels={'date': 'Date', 'count': "Nombre d'annonces"}
        )
        fig4.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    else:
        fig4 = go.Figure()
        fig4.add_annotation(
            text="Aucune donnée temporelle disponible",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        fig4.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=40, r=40, t=50, b=40)
        )
    
    # ===== TABLEAU DES ANNONCES RÉCENTES =====
    if not df.empty:
        recent = df.head(10)
        table_rows = []
        for idx, row in recent.iterrows():
            # Titre tronqué
            title = str(row.get('title', ''))[:40] + "..." if len(str(row.get('title', ''))) > 40 else str(row.get('title', ''))
            
            # Prix formaté
            price = row.get('price', 'N/A')
            if pd.notna(price) and price != 'N/A':
                try:
                    price = f"{float(price):,.0f} DT"
                except:
                    price = str(price)
            else:
                price = "N/A"
            
            # Date formatée
            date = row.get('publication_date', '')
            if pd.notna(date):
                date = str(date)[:10] if len(str(date)) > 10 else str(date)
            else:
                date = "N/A"
            
            table_rows.append(html.Tr([
                html.Td(title, style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                html.Td(price, style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                html.Td(row.get('source_site', 'N/A'), style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                html.Td(row.get('location', 'N/A'), style={'padding': '8px', 'borderBottom': '1px solid #ddd'}),
                html.Td(date, style={'padding': '8px', 'borderBottom': '1px solid #ddd'})
            ]))
        
        table = html.Table([
            html.Thead(html.Tr([
                html.Th("Titre", style={'padding': '8px', 'backgroundColor': '#f0f0f0'}),
                html.Th("Prix", style={'padding': '8px', 'backgroundColor': '#f0f0f0'}),
                html.Th("Source", style={'padding': '8px', 'backgroundColor': '#f0f0f0'}),
                html.Th("Localisation", style={'padding': '8px', 'backgroundColor': '#f0f0f0'}),
                html.Th("Date", style={'padding': '8px', 'backgroundColor': '#f0f0f0'})
            ])),
            html.Tbody(table_rows)
        ], style={'width': '100%', 'borderCollapse': 'collapse'})
    else:
        table = html.Div("Aucune annonce disponible", style={'textAlign': 'center', 'padding': '20px'})
    
    return total, types, locations, prix_moyen, fig1, fig2, fig3, fig4, table

# ============================================
# LANCEMENT
# ============================================
if __name__ == '__main__':
    print("="*60)
    print("🚀 DASHBOARD MULTI-AGENTS DÉMARRÉ")
    print("="*60)
    print("🌐 http://127.0.0.1:8050")
    print("📊 Sources: Tunisie Annonce, Tayara.tn")
    print("📡 API cible: http://localhost:5000")
    print("="*60)
    app.run(debug=True, port=8050)