from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from engine.world import World
from entities.factory import Factories, COUNTRY_CONFIG

app = Flask(__name__)
app.secret_key = "super_secret_key" 

# 1. INITIALISATION DU MONDE
world = World()

# --- CONFIGURATION FIXE (Setup Costs) ---
# Note : Si ça devient dynamique un jour, on le bougera dans le JSON
SETUP_COSTS = {
    "USA": 10000,
    "China": 5000,
    "France": 8000
}

# --- HELPERS ---

def get_player():
    """Récupère l'objet Company du joueur humain."""
    for c in world.companies:
        if c.is_player:
            return c
    return None

def get_sidebar_data(player):
    """Données communes pour la sidebar (Cash, Tour, Usines)."""
    count = sum(len(factories) for factories in player.factories.values())
    return {
        "factory_count": count,
        "player_cash": player.cash,
        "current_turn": world.turn 
    }

def calculate_global_stats(player):
    """Calcule la maintenance totale et la production totale par produit."""
    total_maint = 0
    total_prod = {} 

    for f_list in player.factories.values():
        for f in f_list:
            total_maint += f.maintenance_cost
            
            efficiency = f.config["efficiency_multiplier"]
            for prod, lines in f.product_lines.items():
                output = lines * 100 * efficiency
                total_prod[prod] = total_prod.get(prod, 0) + int(output)

    return total_maint, total_prod

# --- ROUTES D'AFFICHAGE ---

@app.route("/")
def index():
    return redirect(url_for('view_factories'))

@app.route("/factories")
def view_factories():
    player = get_player()
    return render_template(
        "factories.html",
        country_config=COUNTRY_CONFIG,
        player_factories=player.factories,
        setup_costs=SETUP_COSTS,
        **get_sidebar_data(player)
    )

@app.route("/production")
def view_production():
    player = get_player()
    global_maint, global_prod = calculate_global_stats(player)
    
    # DYNAMIQUE : On charge les clés produits du tour actuel (ex: A, B, C...)
    current_params = world.get_turn_data()
    dynamic_products_list = list(current_params["products_meta"].keys())

    # NOUVEAU : Précalculer les lignes de production par pays et par produit
    production_by_country = {}
    for country, factories_list in player.factories.items():
        production_by_country[country] = {}
        for product in dynamic_products_list:
            total_lines = sum(f.product_lines.get(product, 0) for f in factories_list)
            production_by_country[country][product] = total_lines

    return render_template(
        "production.html",
        country_config=COUNTRY_CONFIG,
        player_factories=player.factories,
        all_products=dynamic_products_list, 
        global_maint=global_maint, 
        global_prod=global_prod,
        production_by_country=production_by_country,  # NOUVEAU
        **get_sidebar_data(player)
    )

@app.route('/market')
def market():
    player = get_player()
    
    # 1. Chargement du JSON du tour
    current_params = world.get_turn_data()
    
    # 2. Liste de TOUS les pays (Marchés potentiels)
    all_markets = list(current_params["countries"].keys())

    return render_template(
        'market.html', 
        player=player,
        all_markets=all_markets,
        products_meta=current_params["products_meta"], 
        countries_data=current_params["countries"],
        global_event=current_params["global"],
        **get_sidebar_data(player)
    )

# --- ACTIONS & AJAX ---

@app.route("/buy_factory", methods=["POST"])
def buy_factory():
    player = get_player()
    country = request.form.get("country")
    cost = SETUP_COSTS.get(country, 999999)

    if player.cash < cost:
        flash("Insufficient funds.", "error")
        return redirect(url_for('view_factories'))

    player.cash -= cost
    
    new_factory = Factories(country, COUNTRY_CONFIG)
    if country not in player.factories:
        player.factories[country] = [] 
    player.factories[country].append(new_factory) 
    
    flash(f"New factory established in {country}!", "success")
    return redirect(url_for('view_factories'))

@app.route('/modify_lines_ajax', methods=['POST'])
def modify_lines_ajax():
    """Gère l'ajout/retrait de lignes de production."""
    player = get_player()
    if not player:
        return jsonify({'error': 'Game not initialized'}), 400

    data = request.json
    country = data.get('country')
    product = data.get('product')
    
    try:
        qty = int(data.get('qty'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid quantity'}), 400

    factories_in_country = player.factories.get(country, [])
    if not factories_in_country:
        return jsonify({'error': 'No factory found in this country'}), 400
    
    cost = 0
    try:
        # Logique d'ajout (chercher de la place) ou de retrait (chercher des lignes)
        if qty > 0:
            target = next((f for f in factories_in_country if f.free_space >= qty), None)
            if not target: raise ValueError("Max capacity reached for this country!")
            cost = target.modify_lines(product, qty)
        else:
            target = next((f for f in factories_in_country if f.product_lines.get(product, 0) > 0), None)
            if not target: raise ValueError("No lines to remove.")
            cost = target.modify_lines(product, qty)

        # Vérif argent
        if cost > 0 and player.cash < cost:
            target.modify_lines(product, -qty) # Rollback
            return jsonify({'error': 'Not enough cash'}), 400
            
        player.cash -= cost

        # Recalculs pour le frontend
        country_lines = sum(f.product_lines.get(product, 0) for f in factories_in_country)
        country_maintenance = sum(f.maintenance_cost for f in factories_in_country)
        country_capacity_used = sum(f.total_lines_used for f in factories_in_country)
        country_prod = int(country_lines * 100 * COUNTRY_CONFIG[country]["efficiency_multiplier"])

        global_maint, global_prod_dict = calculate_global_stats(player)

        return jsonify({
            'new_lines': country_lines,
            'new_production': country_prod,
            'new_capacity_used': country_capacity_used,
            'new_maintenance': country_maintenance,
            'new_cash': player.cash,
            'last_op_cost': cost if qty > 0 else 0,
            'global_maint': global_maint,
            'global_prod': global_prod_dict
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'Server Error'}), 500

@app.route('/update_sales_ajax', methods=['POST'])
def update_sales_ajax():
    """Sauvegarde les choix Pays et Prix pour chaque produit."""
    player = get_player()
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    data = request.json
    product = data.get('product')
    field = data.get('field')  # 'country' ou 'price'
    value = data.get('value')
    
    # Validation
    if not product or not field:
        return jsonify({'error': 'Missing parameters'}), 400
    
    # Pour le prix, valider que c'est un nombre
    if field == 'price':
        try:
            value = int(value)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid price'}), 400
    
    # Init structure si vide
    if not hasattr(player, 'sales_decisions'):
        player.sales_decisions = {}
    
    # Update
    player.set_decision(product, field, value)

    return jsonify({'status': 'saved', 'value': value})

# --- ROUTE POUR AFFICHER LA PAGE OVERVIEW ---
@app.route("/overview")
def view_overview():
    player = get_player()
    ranking = world.get_ranking()
    
    # Préparer les données pour le tableau à double entrée
    current_params = world.get_turn_data()
    
    # Agréger les ventes par (country, product, company)
    sales_matrix = {}
    for sale in world.sales_history:
        key = (sale["country"], sale["product"])
        if key not in sales_matrix:
            base_demand = current_params["countries"][sale["country"]]["products"].get(sale["product"], {}).get("base_demand", 0)
            sales_matrix[key] = {
                "country": sale["country"],
                "product": sale["product"],
                "base_demand": base_demand,
                "sales": {}
            }
        company_name = sale["company_name"]
        sales_matrix[key]["sales"][company_name] = sales_matrix[key]["sales"].get(company_name, 0) + sale["quantity"]
    
    # Convertir en liste pour le template
    sales_table = list(sales_matrix.values())
    
    # Liste de toutes les entreprises
    all_companies = [c.name for c in world.companies]
    
    return render_template(
        "turn_overview.html",
        player=player,
        ranking=ranking,
        sales_table=sales_table,
        all_companies=all_companies,
        **get_sidebar_data(player)
    )

# --- ROUTE D'ACTION (Le bouton rouge) ---
@app.route("/end_turn", methods=["POST"])
def end_turn():
    # 1. On lance la résolution dans le moteur
    world.resolve_turn()
    
    # 2. Message de succès
    flash(f"Turn completed! Welcome to Turn {world.turn}.", "success")
    
    # 3. On redirige vers le début du cycle (les usines) pour le nouveau tour
    return redirect(url_for('view_factories'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)