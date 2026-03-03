from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import sys
import os
from datetime import datetime, timedelta
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import DatabaseManager
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)

db = DatabaseManager()

def get_db_connection():
    """Obtenir une connexion avec cursor dict"""
    conn = psycopg2.connect(**db.conn_params)
    conn.cursor_factory = RealDictCursor
    return conn

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil de l'API"""
    return jsonify({
        "api_name": "API Immobilière Tunisie Multi-Agents",
        "version": "2.0",
        "description": "Agrégation de plusieurs sites d'annonces immobilières",
        "agents": ["tunisie_annonce", "tayara", "mubawab"],
        "endpoints": {
            "/": "GET - Cette page",
            "/annonces": "GET - Toutes les annonces",
            "/annonces/<int:id>": "GET - Annonce par ID",
            "/stats": "GET - Statistiques globales",
            "/stats/agents": "GET - Stats par agent",
            "/search": "GET - Recherche avancée",
            "/recent": "GET - Annonces récentes",
            "/scrape/<agent>": "POST - Lancer un agent spécifique",
            "/scrape/all": "POST - Lancer tous les agents"
        }
    })

@app.route('/annonces', methods=['GET'])
def get_annonces():
    """Récupérer toutes les annonces avec pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    source = request.args.get('source', None)
    
    offset = (page - 1) * per_page
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = "SELECT * FROM annonces WHERE 1=1"
    params = []
    
    if source:
        query += " AND source_site = %s"
        params.append(source)
    
    query += " ORDER BY publication_date DESC NULLS LAST LIMIT %s OFFSET %s"
    params.extend([per_page, offset])
    
    cur.execute(query, params)
    annonces = cur.fetchall()
    
    # Total count
    cur.execute("SELECT COUNT(*) FROM annonces" + 
                (" WHERE source_site = %s" if source else ""), 
                ([source] if source else []))
    total = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return jsonify({
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page,
        "annonces": annonces
    })

@app.route('/annonces/<int:id>', methods=['GET'])
def get_annonce(id):
    """Récupérer une annonce par son ID"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM annonces WHERE id = %s", (id,))
    annonce = cur.fetchone()
    cur.close()
    conn.close()
    
    if annonce:
        return jsonify(annonce)
    return jsonify({"error": "Annonce non trouvée"}), 404

@app.route('/stats', methods=['GET'])
def get_stats():
    """Statistiques globales"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Total par source
    cur.execute("""
        SELECT source_site, COUNT(*) as total 
        FROM annonces 
        GROUP BY source_site 
        ORDER BY total DESC
    """)
    par_source = cur.fetchall()
    
    # Prix moyen par source
    cur.execute("""
        SELECT source_site, 
               AVG(price) as prix_moyen,
               MIN(price) as prix_min,
               MAX(price) as prix_max
        FROM annonces 
        WHERE price IS NOT NULL 
        GROUP BY source_site
    """)
    prix_par_source = cur.fetchall()
    
    # Top localisations
    cur.execute("""
        SELECT location, COUNT(*) as total 
        FROM annonces 
        WHERE location != 'N/A'
        GROUP BY location 
        ORDER BY total DESC 
        LIMIT 10
    """)
    top_locations = cur.fetchall()
    
    # Types de biens
    cur.execute("""
        SELECT property_type, COUNT(*) as total 
        FROM annonces 
        WHERE property_type != 'N/A'
        GROUP BY property_type 
        ORDER BY total DESC
    """)
    types_biens = cur.fetchall()
    
    # Statistiques temporelles
    cur.execute("""
        SELECT 
            DATE_TRUNC('day', scrape_date) as jour,
            COUNT(*) as nouvelles
        FROM annonces 
        WHERE scrape_date > NOW() - INTERVAL '7 days'
        GROUP BY DATE_TRUNC('day', scrape_date)
        ORDER BY jour DESC
    """)
    dernieres_24h = cur.fetchall()
    
    # Total général
    cur.execute("SELECT COUNT(*) FROM annonces")
    total = cur.fetchone()['count']
    
    cur.close()
    conn.close()
    
    return jsonify({
        "total_annonces": total,
        "par_source": par_source,
        "prix_par_source": prix_par_source,
        "top_localisations": top_locations,
        "types_biens": types_biens,
        "evolution_7j": dernieres_24h,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/stats/agents', methods=['GET'])
def get_agent_stats():
    """Statistiques des agents scraper"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            agent_name,
            COUNT(*) as executions,
            AVG(items_found) as avg_items,
            SUM(items_new) as total_new,
            SUM(items_updated) as total_updated,
            SUM(errors) as total_errors,
            MAX(end_time) as last_run
        FROM scraper_logs
        GROUP BY agent_name
        ORDER BY last_run DESC
    """)
    stats = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return jsonify(stats)

@app.route('/search', methods=['GET'])
def search():
    """Recherche avancée"""
    # Paramètres de recherche
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    location = request.args.get('location')
    property_type = request.args.get('type')
    source = request.args.get('source')
    keywords = request.args.get('q')
    
    query = "SELECT * FROM annonces WHERE 1=1"
    params = []
    
    if min_price:
        query += " AND price >= %s"
        params.append(min_price)
    
    if max_price:
        query += " AND price <= %s"
        params.append(max_price)
    
    if location:
        query += " AND location ILIKE %s"
        params.append(f"%{location}%")
    
    if property_type:
        query += " AND property_type = %s"
        params.append(property_type)
    
    if source:
        query += " AND source_site = %s"
        params.append(source)
    
    if keywords:
        query += " AND title ILIKE %s"
        params.append(f"%{keywords}%")
    
    query += " ORDER BY publication_date DESC LIMIT 100"
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify({
        "total": len(results),
        "results": results
    })

@app.route('/recent', methods=['GET'])
def recent():
    """Annonces récentes"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT * FROM annonces 
        WHERE scrape_date > NOW() - INTERVAL '24 hours'
        ORDER BY scrape_date DESC
        LIMIT 50
    """)
    recent = cur.fetchall()
    cur.close()
    conn.close()
    
    return jsonify(recent)

@app.route('/scrape/<agent>', methods=['POST'])
def run_agent(agent):
    """Lancer un agent spécifique"""
    try:
        if agent == "tunisie_annonce":
            from agents.agent_tunisie_annonce.scraper import TunisieAnnonceAgent
            agent_instance = TunisieAnnonceAgent()
        elif agent == "tayara":
            from agents.agent_tayara.scraper import TayaraAgent
            agent_instance = TayaraAgent()
        else:
            return jsonify({"error": f"Agent {agent} non trouvé"}), 404
        
        # Lancer en arrière-plan (simplifié)
        stats = agent_instance.run(max_pages=3)
        
        return jsonify({
            "message": f"Agent {agent} démarré",
            "stats": stats
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/scrape/all', methods=['POST'])
def run_all_agents():
    """Lancer tous les agents"""
    results = {}
    errors = []
    
    agents_to_run = [
        ('tunisie_annonce', 'TunisieAnnonceAgent'),
        ('tayara', 'TayaraAgent')
    ]
    
    for agent_name, agent_class in agents_to_run:
        try:
            module = __import__(f'agents.agent_{agent_name}.scraper', fromlist=[agent_class])
            AgentClass = getattr(module, agent_class)
            agent = AgentClass()
            stats = agent.run(max_pages=2)
            results[agent_name] = stats
        except Exception as e:
            errors.append({agent_name: str(e)})
    
    return jsonify({
        "message": "Tous les agents exécutés",
        "results": results,
        "errors": errors if errors else None
    })

if __name__ == '__main__':
    print("="*60)
    print("🚀 API IMMOBILIÈRE MULTI-AGENTS DÉMARRÉE")
    print("="*60)
    print("🌐 http://127.0.0.1:5000")
    print("📊 Agents disponibles: tunisie_annonce, tayara")
    print("="*60)
    app.run(debug=True, port=5000)