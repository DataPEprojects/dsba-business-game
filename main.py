from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from engine.world import World
from entities.factory import Factories, COUNTRY_CONFIG
from entities.product import PRODUCTS_CONFIG

app = Flask(__name__)
app.secret_key = "super_secret_key" 

world = World()

# --- CONFIGURATION ---

SETUP_COSTS = {
    "USA": 10000,
    "China": 5000,
    "France": 8000
}

SALES_CONFIG = {
    "products_meta": {
        "A": {"base_demand": 1000, "price_range": [20, 100]},
        "B": {"base_demand": 800, "price_range": [50, 150]},
        "C": {"base_demand": 500, "price_range": [100, 300]}
    },
    "marketing_meta": {
        "cost_per_point": 100,
        "max_points": 50
    }
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
        "player_cash": player.cash
    }

def calculate_global_stats(player):
    total_maint = 0
    total_prod = {"A": 0, "B": 0, "C": 0}

    for f_list in player.factories.values():
        for f in f_list:
            # CORRECTION ICI : Pas de parenthèses car c'est une @property
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

    return render_template(
        "production.html",
        country_config=COUNTRY_CONFIG,
        player_factories=player.factories,
        all_products=["A", "B", "C"],
        global_maint=global_maint, 
        global_prod=global_prod,
        **get_sidebar_data(player)
    )
@app.route('/update_market_strategy', methods=['POST'])
def update_market_strategy():
    data = request.json
    player = world.companies[0]
    
    country = data['country']
    product = data['product']
    decision_type = data['type'] # 'price' ou 'marketing'
    value = data['value']
    
    # On s'assure que la structure existe dans le dictionnaire du joueur
    if country not in player.sales_decisions:
        player.sales_decisions[country] = {}
    if product not in player.sales_decisions[country]:
        player.sales_decisions[country][product] = {"price": 0, "marketing": 0}
        
    # On met à jour la valeur
    player.sales_decisions[country][product][decision_type] = value
    
    return jsonify({"status": "ok"})

@app.route('/market')
def market():
    player = world.companies[0]
    current_params = world.get_turn_data()
    
    # 1. Calcul de la production disponible
    local_production = {}

    for country_name, factories in player.factories.items():
        if len(factories) > 0:
            local_production[country_name] = {p: 0 for p in PRODUCTS_CONFIG.keys()}
            
            # On utilise COUNTRY_CONFIG (fixe) et pas current_params
            country_eff = COUNTRY_CONFIG[country_name]["efficiency_multiplier"]

            for f in factories:
                for prod_name, lines in f.product_lines.items():
                    qty = int(lines * 100 * country_eff)
                    local_production[country_name][prod_name] += qty

    # 2. On rend le template en utilisant ton helper pour la sidebar
    return render_template('market.html', 
                           player=player,
                           active_countries=local_production.keys(),
                           local_prod=local_production,
                           all_products=PRODUCTS_CONFIG.keys(),
                           products_meta=current_params["products_meta"],
                           marketing_meta=current_params["marketing_meta"],
                           global_event=current_params["global"],
                           **get_sidebar_data(player)  # <--- C'est ça qui corrige l'erreur
                           )

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
            target.modify_lines(product, -qty)
            return jsonify({'error': 'Not enough cash'}), 400
            
        player.cash -= cost

        # --- RECALCULS ---
        country_lines = sum(f.product_lines.get(product, 0) for f in factories_in_country)
        
        # CORRECTION ICI : Pas de parenthèses () pour total_lines_used ou maintenance_cost
        # car ce sont des @property dans factory.py
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

    if hasattr(player, 'set_sales_decision'):
        player.set_sales_decision(country, product, field, value)
    else:
        if not hasattr(player, 'sales_decisions'): player.sales_decisions = {}
        if country not in player.sales_decisions: player.sales_decisions[country] = {}
        if product not in player.sales_decisions[country]: player.sales_decisions[country][product] = {"price": 0, "marketing": 0}
        player.sales_decisions[country][product][field] = value

    return jsonify({'status': 'saved', 'value': value})

if __name__ == "__main__":
    app.run(debug=True, port=5000)