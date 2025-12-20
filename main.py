from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from engine.world import World
from entities.factory import Factories, COUNTRY_CONFIG
from entities.product import PRODUCTS_CONFIG

app = Flask(__name__)
app.secret_key = "super_secret_key" 

# On instancie le monde, qui charge tes JSONs via Parameters
world = World()

# --- CONFIGURATION FIXE (Ce qui n'est pas dans le JSON tour par tour) ---

# Si les coûts de setup sont fixes, on les garde ici. 
# S'ils changent par tour, il faudra les déplacer dans le JSON aussi.
SETUP_COSTS = {
    "USA": 10000,
    "China": 5000,
    "France": 8000
}

# --- HELPERS ---

def get_player():
    for c in world.companies:
        if c.is_player:
            return c
    return None

def get_sidebar_data(player):
    count = sum(len(factories) for factories in player.factories.values())
    return {
        "factory_count": count,
        "player_cash": player.cash,
        "current_turn": world.turn 
    }

def calculate_global_stats(player):
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

# --- ROUTES ---

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
    
    # DYNAMIQUE : On récupère la liste des produits depuis le JSON du tour actuel
    current_params = world.get_turn_data()
    dynamic_products_list = list(current_params["products_meta"].keys())

    return render_template(
        "production.html",
        country_config=COUNTRY_CONFIG,
        player_factories=player.factories,
        all_products=dynamic_products_list, # Plus de hardcode ["A", "B", "C"]
        global_maint=global_maint, 
        global_prod=global_prod,
        **get_sidebar_data(player)
    )

@app.route('/market')
def market():
    player = get_player()
    
    # 1. Chargement des données du tour
    current_params = world.get_turn_data()
    
    # 2. Où est-ce qu'on produit ? (Sources)
    # On a besoin de savoir où on a des usines pour calculer les routes
    production_sources = {}
    for country_name, factories in player.factories.items():
        if len(factories) > 0:
            production_sources[country_name] = True

    # 3. On prépare TOUS les marchés (Destinations)
    # On prend les clés de "countries" dans le JSON (France, USA, China...)
    all_markets = list(current_params["countries"].keys())

    return render_template(
        'market.html', 
        player=player,
        # La liste de tous les pays où on peut vendre (Destination)
        all_markets=all_markets, 
        # Là où on produit (Origine)
        production_sources=production_sources.keys(),
        # Les matrices pour le calcul en direct JS
        transport_matrix=current_params["transport_matrix"],
        tax_matrix=current_params["tax_matrix"],
        # Le reste...
        products_meta=current_params["products_meta"], 
        marketing_meta=current_params["marketing_meta"],
        global_event=current_params["global"],
        **get_sidebar_data(player)
    )

@app.route('/update_market_strategy', methods=['POST'])
def update_market_strategy():
    data = request.json
    player = get_player()
    
    country = data['country']
    product = data['product']
    decision_type = data['type'] # 'price' ou 'marketing'
    value = data['value']
    
    # Init structure si besoin
    if country not in player.sales_decisions:
        player.sales_decisions[country] = {}
    if product not in player.sales_decisions[country]:
        player.sales_decisions[country][product] = {"price": 0, "marketing": 0}
        
    player.sales_decisions[country][product][decision_type] = value
    
    return jsonify({"status": "ok"})

# --- ACTIONS (POST) ---

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
        if qty > 0:
            target = next((f for f in factories_in_country if f.free_space >= qty), None)
            if not target: raise ValueError("Max capacity reached for this country!")
            cost = target.modify_lines(product, qty)
        else:
            target = next((f for f in factories_in_country if f.product_lines.get(product, 0) > 0), None)
            if not target: raise ValueError("No lines to remove.")
            cost = target.modify_lines(product, qty)

        if cost > 0 and player.cash < cost:
            target.modify_lines(product, -qty) # Rollback
            return jsonify({'error': 'Not enough cash'}), 400
            
        player.cash -= cost

        # --- RECALCULS ---
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
    player = get_player()
    if not player:
        return jsonify({'error': 'Player not found'}), 400

    data = request.json
    country = data.get('country')
    product = data.get('product')
    field = data.get('field') 
    
    try:
        value = int(data.get('value'))
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid value'}), 400

    # Sauvegarde flexible
    if not hasattr(player, 'sales_decisions'): player.sales_decisions = {}
    if country not in player.sales_decisions: player.sales_decisions[country] = {}
    if product not in player.sales_decisions[country]: player.sales_decisions[country][product] = {"price": 0, "marketing": 0}
    player.sales_decisions[country][product][field] = value

    return jsonify({'status': 'saved', 'value': value})

if __name__ == "__main__":
    app.run(debug=True, port=5000)