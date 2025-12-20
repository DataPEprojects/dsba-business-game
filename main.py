from flask import Flask, render_template, request, redirect, url_for, flash
from engine.world import World
from entities.factory import Factories, COUNTRY_CONFIG

app = Flask(__name__)
app.secret_key = "super_secret_key" # Nécessaire pour utiliser 'flash' (messages d'erreur/succès)

# Initialisation du monde
world = World()

# Configuration des coûts d'ouverture d'usine (Hardcodé pour l'exemple)
SETUP_COSTS = {
    "USA": 10000,
    "China": 5000,
    "France": 8000
}

def get_player():
    """Récupère le premier joueur humain trouvé."""
    for c in world.companies:
        if c.is_player:
            return c
    return None

# --- ROUTES D'AFFICHAGE ---

@app.route("/")
def index():
    return redirect(url_for('factories_dashboard'))

@app.route("/factories")
def factories_dashboard():
    player = get_player()
    
    # On passe toutes les infos nécessaires au template dashboard.html
    return render_template(
        "dashboard.html",
        country_config=COUNTRY_CONFIG,
        player_factories=player.factories, # Doit être un dict {Pays: ObjetFactory}
        all_products=["A", "B", "C"],      # Liste de tes produits
        setup_costs=SETUP_COSTS,
        player_cash=player.cash
    )

# --- ROUTES D'ACTION (POST) ---

@app.route("/buy_factory", methods=["POST"])
def buy_factory():
    player = get_player()
    country = request.form.get("country")
    cost = SETUP_COSTS.get(country, 999999)

    # 1. Vérif : A-t-il déjà l'usine ?
    if country in player.factories:
        flash(f"Usine déjà présente en {country} !", "error")
        return redirect(url_for('factories_dashboard'))

    # 2. Vérif : A-t-il l'argent ?
    if player.cash < cost:
        flash("Fonds insuffisants pour ouvrir cette usine.", "error")
        return redirect(url_for('factories_dashboard'))

    # 3. Action : Paiement et Création
    player.cash -= cost
    new_factory = Factories(country)
    player.factories[country] = new_factory # Assure-toi que player.factories est un dict !
    
    flash(f"Usine ouverte en {country} pour {cost}€.", "success")
    return redirect(url_for('factories_dashboard'))


@app.route("/modify_lines", methods=["POST"])
def modify_lines():
    player = get_player()
    country = request.form.get("country")
    product = request.form.get("product")
    try:
        qty = int(request.form.get("qty"))
    except ValueError:
        return redirect(url_for('factories_dashboard'))

    # Récupération de l'usine
    factory = player.factories.get(country)
    if not factory:
        return redirect(url_for('factories_dashboard'))

    try:
        # Calcul du coût via la méthode de la classe Factory
        cost = factory.modify_lines(product, qty)
        
        # Application du coût au joueur
        # Note: Si cost est positif, on paie. Si on supprime des lignes, cost est négatif (remboursement ?)
        # À toi de décider si on rembourse ou non. Ici, on paie l'installation.
        if qty > 0:
            if player.cash >= cost:
                player.cash -= cost
            else:
                # Annuler l'ajout si pas de sous (rollback manuel simple)
                factory.modify_lines(product, -qty) 
                flash("Pas assez d'argent pour ajouter cette ligne.", "error")
        
    except ValueError as e:
        flash(str(e), "error")

    return redirect(url_for('factories_dashboard'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)