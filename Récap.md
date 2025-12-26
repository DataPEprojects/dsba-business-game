# Projet Market_py_project — Vue d'ensemble

Résumé rapide  
Jeu / simulation économique en tour par tour (Flask) — entreprises (joueur + IA) gèrent usines, lignes de production, pricing et ventes sur plusieurs pays.

---

## Arborescence principale (excl. venv & __pycache__)

- c:\Users\PE\Market_py_project/
  - main.py
  - engine/
  - entities/
  - templates/
  - static/
  - data/ (optionnel)
  - docs/ (optionnel)

---

## Dossiers — rôle bref

- engine/  
  Code du moteur de simulation : gestion des tours, paramètres, IA manager. Contient la logique métier qui orchestre Company, Factories et paramètres de chaque tour.

- entities/  
  Définitions des entités du jeu : Company (entreprise/joueur), Factories (usines) et toute logique locale aux entités (capacités, coûts, lignes).

- templates/  
  Templates Jinja2 pour l'interface web Flask (pages : index, factories, production, market, overview, gameover, ...).

- static/  
  Assets front-end (JS, CSS, images). Contrôle l'UI, requêtes AJAX vers les endpoints Flask.

- data/ (si présent)  
  JSON / données statiques (paramètres par tour, comportements IA préenregistrés, etc.).

- docs/ (optionnel)  
  Documentation additionnelle, guides, diagrammes.

---

## Fichiers clés — descriptions courtes

### Racine
- main.py  
  Application Flask : routes, endpoints AJAX, initialisation du monde (`World`), actions joueur (acheter usine, modifier lignes, définir ventes), résolution de tour via `world.resolve_turn()`.

### engine/
- engine/world.py  
  Moteur principal de simulation. Crée `World` qui :
  - initialise `Parameters`, `AIManager`, et `companies` (joueur + IA),
  - applique actions IA (buy factory, allocate lines, set prices),
  - calcule production (par usine/pays),
  - applique coûts de maintenance,
  - résout les ventes selon décision prix/pays,
  - gère historique des ventes et classement/ranking.

- engine/ai_manager.py  
  Définit `AIBehavior` (personnalités heuristiques : aggressive, balanced, conservative, premium, volume) et `AIManager` (génère plusieurs IA). Méthodes utiles : should_buy_factory, choose_country_for_factory, allocate_lines_by_country, choose_price, choose_sales_country.

- engine/parameters.py  
  (référencé) Charge / expose les paramètres de simulation par tour : produits, options de prix, pays et base_demand, événements globaux. World appelle `Parameters.get_turn(turn)`.

- engine/__init__.py  
  (probablement léger) Permet import package engine.

### entities/
- entities/factory.py  
  Classe `Factories` : représente une usine. Attributs :
    - id, country, config (depuis COUNTRY_CONFIG),
    - capacity, product_lines (dict),
    - properties : total_lines_used, free_space, maintenance_cost,
    - méthode modify_lines(product, qty) — ajout/retrait de lignes et retourne coût de l'opération.
  COUNTRY_CONFIG contient base_line_cost, efficiency_multiplier, max_capacity, maintenance_cost par pays.

- entities/company.py  
  Classe `Company` : représente entreprise/joueur. Attributs :
    - name, is_player, ai_behavior (optionnel), cash, profit, factories (dict pays -> [Factories,...]), stock (produit->qty), revenue, costs, sales_decisions.
  Méthodes importantes (utilisées par world.py / main.py) :
    - ensure_all_products(products) — initialise clés stock,
    - reset_all_past_inf() — remet revenue / costs à zéro chaque tour,
    - set_decision(product, field, value) / get_decision(product) — enregistrer/passer prix et pays de vente,
    - set_production_lines(country, product, qty) — applique ajustement des lignes en répartissant sur usines, débite/crédite cash selon `Factories.modify_lines`,
    - buy_factory(country, cost=..., factory_obj=None) — ajoute usine et débite si coût fourni.

### templates/ (exemples référencés dans main.py)
- index.html  
  Page d'accueil / dashboard (redirige ou affiche résumé).
- factories.html  
  Interface gestion des usines (acheter, voir capacités).
- production.html  
  Gestion et aperçu de production par pays/produit.
- market.html  
  Pricing & choix pays pour chaque produit ; affiche sales_history.
- turn_overview.html  
  Tableau récapitulatif des ventes du tour.
- gameover.html  
  Page de fin de partie / classement.

### static/
- js/   (ex : main.js)  
  AJAX pour endpoints (buy_factory, modify_lines_ajax, update_sales_ajax, resolve_turn).
- css/  (styles)
- images/ (optionnel)

### data/ (si présent)
- parameters.json (ou équivalent)  
  Paramètres par tour : products_meta (price_options), countries (base_demand par produit), global events, etc.
- ai_behaviors.json (optionnel)  
  Comportements pré-enregistrés pour IA (si utilisé au lieu de AIManager dynamique).

---

## Flux principal (très bref)
1. main.py initialise `world = World(total_turns, num_ais)`.
2. Sur action joueur (acheter usine, modifier lignes, set price) main.py modifie `Company` du joueur.
3. Quand on appuie sur "end turn" ou `/api/resolve_turn`, main.py appelle `world.resolve_turn()` :
   - world applique actions des IA (via AIManager / AIBehavior),
   - world calcule production (Factories.product_lines -> company.stock),
   - world applique coûts (maintenance),
   - world résout ventes (compare prix par pays, distribue demande, met à jour cash/revenue, sales_history),
   - world reset indicateurs et incrémente le tour.
4. Flask expose endpoints pour récupérer état (`/api/game_state`), récupérer ranking, sales_history, etc.

---

## Points d'attention / checklist rapide pour debug
- Company doit exposer : set_decision, get_decision, set_production_lines, buy_factory.
- Factories.modify_lines retourne le coût (positif si achat, négatif si vente) — Company doit gérer cash/rollback.
- AIBehavior.allocate_lines_by_country produit des cibles heuristiques ; Company doit appliquer sans dépasser capacity ni cash.
- Parameters.get_turn(turn) doit fournir la structure attendue par world._resolve_sales :
  - keys : "products_meta" (avec "price_options"), "countries" (avec "products" -> base_demand), "global" (event).
- Consistance COUNTRY_CONFIG passé à Factories (passer le dict complet, pas COUNTRY_CONFIG[country]).

---

Si tu veux, je peux :
- générer automatiquement ce fichier dans le repo (emplacement proposé en début),
- produire un diagramme simple des interactions (World ↔ Company ↔ Factories ↔ AIBehavior),
- lister tous les fichiers réellement présents dans ton workspace si tu me l'autorises à lire leur liste.


# Projet Market_py_project — Vue détaillée : engine

Cette section détaille le dossier `engine/` : rôle, fichiers et responsabilités précises de chaque module. L'objectif est d'avoir une référence rapide pour développer ou débugger le moteur de simulation.

## But global du dossier `engine/`
Le dossier `engine/` contient la logique centrale de la simulation tour-par-tour :
- orchestrer les tours (création d'usines IA, allocation des lignes, pricing),
- appliquer la production et les coûts,
- résoudre les ventes et produire l'historique des ventes,
- fournir les paramètres par tour (marchés, produits, prix).

## Fichiers principaux et responsabilités

### engine/world.py
Rôle : coeur du moteur de simulation. Coordonne les interactions entre `Parameters`, `AIManager`, `Company` et `Factories`.

Fonctions / méthodes clés :
- class World
  - __init__(self, total_turns=20, num_ais=5)
    - Initialise Parameters, AIManager, crée les compagnies (joueur + IA) et initialise l'état.
  - _initialize_companies(self)
    - Crée l'objet joueur (Company(is_player=True)) puis instancie les compagnies IA à partir de `AIManager.ais`. Assigne le comportement IA en tant qu'attribut de chaque Company (company.ai_behavior).
  - get_turn_data(self)
    - Délivre la configuration/paramètres du tour actuel via `Parameters.get_turn(turn)`.
  - _apply_ai_actions(self)
    - Pour chaque IA : éventuelle création d'usine, allocation de lignes (via ai.allocate_lines_by_country), choix de prix et pays (via ai.choose_price / choose_sales_country). Ne dépense pas d'argent sans vérification ; World/Company appliquent les modifications réelles.
  - _calculate_production(self)
    - Parcourt toutes les usines de chaque compagnie, calcule la production par produit = lines * base_output * efficiency_multiplier (dep. COUNTRY_CONFIG) et incrémente company.stock.
  - _apply_maintenance_costs(self)
    - Agrège maintenance_cost de chaque usine et débite company.cash ; consigne company.costs["maintenance"].
  - _resolve_sales(self)
    - Pour chaque produit : collecte offres (company, country, price, stock), groupe par pays, trie par prix et distribue la demande (base_demand) aux vendeurs au prix le plus bas, met à jour stock, cash, revenue et sales_history (liste d'événements de vente pour le tour).
  - resolve_turn(self)
    - Exécute séquentiellement : _apply_ai_actions → _calculate_production → _apply_maintenance_costs → _resolve_sales → reset indicateurs et incrément de turn.
  - get_ranking, is_game_over, get_company, get_all_companies
    - Fonctions utilitaires pour classement et accès aux compagnies.

Points d'attention :
- World attend que `Company` expose : set_decision, get_decision, set_production_lines, buy_factory (ou qu'on puisse manipuler company.factories directement).
- COUNTRY_CONFIG doit être passé correctement à `Factories` (le constructeur attend le dict complet).
- La logique d'IA dans AIBehavior produit des "cibles" ; Company doit appliquer ces cibles en respectant cash et capacités.

### engine/ai_manager.py
Rôle : définir les comportements IA heuristiques et fournir un ensemble d'IA.

Contenu / méthodes :
- class AIBehavior
  - __init__(self, name, personality) : définit expand_rate, price_position, product_focus, preferred_countries.
  - should_buy_factory(turn) : bool (tour 1 obligatoire, sinon probabiliste).
  - choose_country_for_factory() : renvoie un pays préféré.
  - allocate_lines_by_country(factories_owned) : renvoie une allocation cible {country: {product: qty}}. (Note : heuristique, ne tient pas compte du nombre d'usines ni du cash.)
  - choose_price(available_prices) : choisit un prix dans une liste selon price_position.
  - choose_sales_country(product) : heuristique par produit.
- class AIManager
  - __init__(num_ais=5) : crée self.ais (dict name -> AIBehavior).
  - _generate_ais, get_ai, get_all_ais

Remarques :
- Aléatoire via random ; pour reproductibilité, seed en amont (ex : main.py).
- `allocate_lines_by_country` fournit une cible simple : l'application doit adapter la répartition sur les usines réelles.

### engine/parameters.py
Rôle : fournisseur de données par tour (structure attendue par world.py).

Attendu :
- Méthode get_turn(turn) qui renvoie un dict contenant au minimum :
  - "products_meta" : pour chaque produit les "price_options" et autres méta (ex: {"A": {"price_options":[...], ...}, ...})
  - "countries" : mapping pays -> {"products": {product: {"base_demand": int}}, ...}
  - "global" : (événement global du tour, optionnel)
- Parameters s'occupe typiquement de charger un JSON/data et d'exposer get_turn.

### engine/__init__.py
- Permet l'import package engine. Souvent vide ou avec constantes partagées.

## Interactions importantes (flux simplifié)
- main.py initialise World(total_turns, num_ais) → world crée Companies et AIManager.
- Un tour : joueur définit décisions via routes Flask (main.py), puis lorsqu'on appelle world.resolve_turn():
  - World demande aux IA leurs décisions (ai_behavior), applique celles-ci via Company / Factories,
  - calcule production -> met à jour stock des compagnies,
  - applique maintenance -> retire cash,
  - résout ventes -> met à jour cash / revenue et sales_history,
  - reset des indicateurs pour le tour suivant.


# Projet Market_py_project — Vue détaillée : entities

Cette section décrit le dossier `entities/` : objets du domaine (usines, entreprises) et API attendue par le moteur.

## But global du dossier `entities/`
Contient les classes modélisant les objets persistants de la simulation :
- Factories : représentation d'une usine (capacité, lignes, coûts).
- Company : représentation d'une entreprise (joueur ou IA) — cash, usines, stocks, décisions.
Le moteur (engine/) appelle ces objets pour appliquer modifications concrètes (acheter usine, modifier lignes, enregistrer décisions).

## Fichiers principaux et responsabilités

### entities/factory.py
Rôle : représenter une usine, sa configuration par pays et gérer les lignes.

Structure et méthodes clés :
- COUNTRY_CONFIG (dict)
  - Contient la configuration par pays : base_line_cost, efficiency_multiplier, max_capacity, maintenance_cost.
  - Source unique de vérité pour coûts/efficacités.

- class Factories
  - __init__(self, country, config)
    - Initialise id (uuid), country, config = config[country], capacity (max_capacity), product_lines {}.
    - `config` attendu : le dict complet COUNTRY_CONFIG (on indexe ensuite par country).
  - property total_lines_used(self)
    - Somme des lignes allouées (utilisé pour calcul capacité utilisée).
  - property free_space(self)
    - capacity - total_lines_used.
  - property maintenance_cost(self)
    - Calcul des coûts de maintenance (souvent total_lines_used * config["maintenance_cost"]).
  - modify_lines(self, product, qty)
    - Ajuste product_lines[product] += qty.
    - Vérifie contraintes : pas de dépassement de capacité, pas de lignes négatives.
    - Retourne le "coût" de l'opération : qty * base_line_cost (positif si achat, négatif si suppression).
    - Doit lever ValueError si impossible (considéré par Company pour rollback).

Points d'attention / bonnes pratiques :
- Passer le dict complet COUNTRY_CONFIG au constructeur (Factories(country, COUNTRY_CONFIG)).
- modify_lines retourne un montant financier ; Company doit l'utiliser pour débiter/crediter cash et appliquer rollback si nécessaire.
- maintenance_cost calculé par usine ; aggregation faite côté Company/World.

### entities/company.py
Rôle : représenter une entreprise et exposer l'API que World/AIManager attend.

Attributs usuels :
- name, is_player (bool), ai_behavior (optionnel, objet AIBehavior)
- cash (float/int), profit, revenue
- factories : dict country -> list[Factories]
- stock : dict product -> qty
- costs : dict catégories (production, maintenance, marketing, transport, taxes)
- sales_decisions / sales_decisions_by_country : structure pour stocker pays/prix/marketing

Méthodes clés (attendues par engine/world.py) :
- __init__(..., ai_behavior=None)
  - Initialisation minimale ; configurer ai_behavior si fournie pour que World puisse appeler company.ai_behavior.
- ensure_all_products(self, products)
  - Initialise self.stock[p] = 0 pour chaque produit fourni.
- reset_all_past_inf(self)
  - Remet revenue et costs à zéro pour le nouveau tour.
- set_decision(self, product, field, value)
  - Enregistre la décision de vente d'un produit (field = "country" ou "price").
  - Structure simple : self.sales_decisions[product] = {"country": "", "price": 0}
- get_decision(self, product)
  - Retourne la décision courante (dict avec keys "country","price").
- set_production_lines(self, country, product, qty)
  - API utilisée par World après que l'IA rende une "cible" d'allocations.
  - Implémentation recommandée :
    - Calculer current_total dans le pays pour ce produit.
    - diff = qty - current_total.
    - Si diff > 0 : parcourir usines du pays et appeler f.modify_lines(product, add) jusqu'à combler diff ; vérifier cash avant appliquer définitivement ; rollback si insuffisant.
    - Si diff < 0 : retirer lignes progressivement ; appliquer remboursement éventuel (modify_lines retourne coût négatif).
    - Méthode doit être résistante (ne pas lever si utilisée par World en contexte IA) — mais lever ValueError pour actions utilisateur si souhaité.
- buy_factory(self, country, cost=0, factory_obj=None)
  - Ajouter une usine au dictionnaire factories ; si cost > 0 débiter self.cash.
  - Si factory_obj fourni, l'ajouter sans créer une nouvelle instance.
  - Doit implémenter vérification cash (lever ValueError si insuffisant).

Autres méthodes utiles possibles :
- set_sales_decision(country, product, field, value) — si tu utilises structure par pays.
- get_factories_summary() — retour rapide pour l'UI (nombre d'usines, capacité utilisée).
- compute_production_preview(country, product) — pour afficher à l'UI ce que produira l'usine.

Points d'attention / bonnes pratiques :
- Company applique la logique financière : débuter par vérifier cash puis appeler Factories.modify_lines, rollback en cas d'échec.
- Garder la logique physique (capacité, coûts, output) dans Factories ; Company orchestre et met à jour cash/costs/stock.
- Eviter duplication de config SETUP_COSTS : centraliser si possible (world.py + main.py partagent la même valeur).
- Si sales_decisions est structurée par pays, fournir des adaptateurs (set_decision+get_decision) pour compatibilité avec world._resolve_sales.

## Intégration avec engine/ (rappel)
- World s'appuie sur Company pour appliquer changements demandés par les IA :
  - company.ai_behavior fournit des cibles (World lit ai_behavior).
  - World appelle company.buy_factory(...) ou instancie Factories puis company.factories[...] append.
  - World appelle company.set_production_lines(country, product, qty) pour appliquer allocation.
  - World lit company.get_decision(product) pour résoudre ventes.
- Factories fournit le calcul de production réel (lines * 100 * efficiency_multiplier) — World utilise cette formule ou Company peut l'exposer via helper.

...existing code...

# Projet Market_py_project — Vue détaillée : static & templates

Cette section décrit brièvement les dossiers `static/` et `templates/` : rôle, fichiers clés et variables Jinja attendues.

## static/ — rôle bref
Contient les assets front-end (JS, CSS, images, bibliothèques). Organise la logique côté client (AJAX, interactions UI, mises à jour dynamiques).

Arborescence typique et fichiers importants :
- static/js/
  - main.js (ou app.js) : centralise les appels AJAX vers endpoints Flask (buy_factory, modify_lines_ajax, update_sales_ajax, resolve_turn, api/game_state). Gère écouteurs DOM, rafraîchissements partiels (sidebar, production), et affichage des notifications/flash.
  - helpers.js : utilitaires (formatage monnaie, build request payloads).
  - vendor/* : libs tierces (jQuery, Axios, Bootstrap JS) si présentes.
- static/css/
  - styles.css (ou app.css) : styles globaux de l'UI.
  - theme.css / responsive.css : adaptations affichage mobile.
  - vendor/* : bootstrap/fontawesome si utilisés.
- static/images/
  - logos, icônes, images de pays, etc.
- static/data/ (optionnel)
  - fixtures ou assets JSON côté client.

Bonnes pratiques / points d'attention :
- main.js doit respecter les endpoints définis dans main.py (POST/GET, payload JSON ou form).
- Prévoir gestion d'erreurs globale (toasts, console) et seed pour debug.
- Minifier / concaténer pour production.

## templates/ — rôle bref
Contient les templates Jinja2 utilisées par Flask pour rendre les pages. Doit exposer les variables nécessaires depuis main.py.

Fichiers/templates clés (exemples) :
- templates/base.html (layout principal)
  - Contient le header, footer, inclusion CSS/JS, blocs Jinja : block content, block scripts.
  - Variables utiles : sidebar data (player_cash, factory_count, current_turn), user flash messages.
- templates/partials/sidebar.html (inclus dans base)
  - Affiche cash, tour, boutons d'action rapides (end_turn).
  - Attendu : données retournées par get_sidebar_data(player).
- templates/index.html
  - Page d'accueil / dashboard (peut rediriger vers factories).
- templates/factories.html
  - UI pour acheter usines et lister factories du joueur.
  - Variables : player_factories (dict country -> list d'objets Factories), country_config (COUNTRY_CONFIG), setup_costs.
- templates/production.html
  - Gestion des lignes par pays/produit.
  - Variables : all_products, production_by_country, global_prod, global_maint.
  - Bind JS pour appeler modify_lines_ajax.
- templates/market.html
  - Choix pays/prix par produit et aperçu sales_history.
  - Variables : products_meta (price_options), all_markets, countries_data, global_event, player.
  - JS doit appeler update_sales_ajax pour sauvegarder choix.
- templates/turn_overview.html
  - Récapitulatif ventes du tour (matrix country×product).
  - Variables : sales_table, all_companies, ranking.
- templates/gameover.html
  - Classement final ; variables : ranking, player_rank.
- templates/components/*.html (optionnel)
  - Modals (confirm buy), tables, rows de factory — réutilisables.

Variables Jinja fréquemment attendues (exemples)
- player : objet Company (name, cash, factories, stock, revenue)
- sidebar data : player_cash, factory_count, current_turn
- turn_data : structure renvoyée par Parameters.get_turn (products_meta, countries, global)
- sales_history : liste d'événements de vente (country, product, company_name, price, quantity)
- ranking : liste dicts {rank, name, cash, is_player}


# Projet Market_py_project — Vue détaillée : main.py

Ce fichier est le point d'entrée Flask de l'application — il expose l'interface web, les endpoints utilisateur/AJAX et initialise le moteur (World). Ci‑dessous : rôle global, routes, helpers, payloads attendus, points de vigilance et suggestions.

## But global de main.py
- Initialiser le monde de jeu : world = World(total_turns=..., num_ais=...)
- Servir les pages (templates) et fournir les données nécessaires aux vues.
- Exposer les actions utilisateur (acheter usine, modifier lignes, définir prix/pays) via formulaires ou AJAX.
- Déclencher la résolution d'un tour (world.resolve_turn) et afficher les résultats.

## Initialisation
- world = World(total_turns=10, num_ais=5)  
  - crée Parameters, AIManager, Companies (joueur + IA) et sales_history vide.
- SETUP_COSTS : dict local des coûts d'implantation par pays (source unique recommandée).

## Helpers
- get_player()  
  - retourne l'objet Company du joueur (cherche c.is_player).
  - Doit gérer le cas où aucun joueur n'est présent (return None possible).
- get_sidebar_data(player)  
  - compile données pour la sidebar : nombre d'usines, cash, tour courant.
- calculate_global_stats(player)  
  - calcule maintenance totale et production par produit à partir des usines du joueur.

Ces helpers alimentent templates et endpoints AJAX.

## Routes d'affichage (render_template)
- "/" -> redirect vers "/factories"
- "/factories" -> factories.html  
  Variables fournies : country_config (COUNTRY_CONFIG), player_factories (player.factories), setup_costs, plus sidebar data.
- "/production" -> production.html  
  Variables : production_by_country (pré-calcul), all_products (depuis world.get_turn_data()["products_meta"]), global_maint, global_prod, sidebar.
- "/market" -> market.html  
  Variables : products_meta, countries_data, global_event, all_markets, player, sidebar.
- "/overview" -> turn_overview.html  
  Variables : sales_table (agrégat de world.sales_history), ranking, all_companies, sidebar.

Templates doivent s'attendre à ces variables (utiliser |tojson pour passer JS).

## Endpoints & AJAX (POST JSON ou form)
- "/buy_factory" (POST, form)
  - Payload: form field "country"
  - Logique : vérifie player.cash >= SETUP_COSTS[country], débite, crée Factories(country, COUNTRY_CONFIG) et l'ajoute à player.factories.
  - Retour : redirect vers view_factories + flash.
- "/modify_lines_ajax" (POST, JSON)
  - Payload JSON: { country, product, qty } (qty int positif pour ajout, négatif pour retrait)
  - Logique :
    - Identifie factory cible(s) dans player.factories[country]
    - Appelle Factories.modify_lines(product, qty) réparti (Company doit appliquer logique)
    - Vérifie et applique coût, rollback si cash insuffisant
    - Retour JSON :
      - new_lines, new_production, new_capacity_used, new_maintenance, new_cash, last_op_cost, global_maint, global_prod
  - Codes d'erreur : 400 pour payload invalide / pas de factory / cash insuffisant ; 500 pour erreur serveur.
- "/update_sales_ajax" (POST, JSON)
  - Payload JSON: { product, field, value }  (field = "country" ou "price")
  - Logique : validation (price → int), update via player.set_decision(product, field, value)
  - Retour JSON : {status:'saved', value}
- "/end_turn" (POST)
  - Appelé par bouton "fin de tour".
  - Logique : world.resolve_turn() → applique IA, production, maintenance, ventes, reset indicateurs et incrémente turn.
  - Effet : flash de confirmation puis redirect vers view_factories.
  - Attention : world.resolve_turn peut lever exceptions — encapsuler si besoin pour renvoyer erreur utilisateur.

## Contrats attendus / structures de données
- world.get_turn_data() doit renvoyer dict avec au moins :
  - "products_meta": { product: { "price_options": [...], ... }, ... }
  - "countries": { country: { "products": { product: {"base_demand": int}, ... } }, ... }
  - "global": événement (optionnel)
- Factories.modify_lines(product, qty) → retourne coût (qty * base_line_cost) ; l'appelant doit gérer rollback.
- Company doit exposer : set_decision(product, field, value), get_decision(product), set_production_lines(country, product, qty) ou buy_factory(country,...).

