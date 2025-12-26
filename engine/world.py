import json
from engine.parameters import Parameters
from entities.company import Company
from entities.factory import Factories, COUNTRY_CONFIG

# --- CONFIGURATION FIXE (Setup Costs) ---
SETUP_COSTS = {
    "USA": 40000,
    "China": 25000,
    "France": 30000
}

class World:
    """Coordonne la simulation tour par tour."""
    def __init__(self, total_turns=20):
        self.parameters = Parameters(total_turns=total_turns)
        self.turn = 1
        self.total_turns = total_turns 
        self.ai_behaviors = self._load_ai_behaviors()
        self.companies = self._initialize_companies()
        self.sales_history = []  # Historique des ventes du dernier tour
        
    def _load_ai_behaviors(self):
        """Charge les comportements pré-enregistrés des IA."""
        with open("data/ai_behaviors.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    
    def _initialize_companies(self):
        """Crée le joueur et les 5 IA."""
        companies = [Company("Player", is_player=True)]
        
        for ai_name in self.ai_behaviors.keys():
            companies.append(Company(ai_name, is_player=False))
        
        # Initialiser les stocks pour tous les produits
        all_products = list(self.parameters.get_turn(1)["products_meta"].keys())
        for company in companies:
            company.ensure_all_products(all_products)
            
        return companies
    
    def get_turn_data(self):
        """Renvoie les paramètres du tour actuel."""
        return self.parameters.get_turn(self.turn)
    
    def _apply_ai_actions(self, turn_number):
        """Applique les actions pré-enregistrées des IA pour le tour donné."""
        for company in self.companies:
            if company.is_player:
                continue  # Le joueur a déjà fait ses choix via le front
            
            ai_name = company.name
            turn_data = self.ai_behaviors[ai_name]["turns"].get(str(turn_number))
            
            if not turn_data:
                continue
            
            # 1. Acheter des usines
            for country in turn_data["buy_factories"]:
                cost = SETUP_COSTS[country]
                if company.cash >= cost:
                    company.cash -= cost
                    new_factory = Factories(country, COUNTRY_CONFIG)
                    if country not in company.factories:
                        company.factories[country] = []
                    company.factories[country].append(new_factory)
            
            # 2. Allouer les lignes de production
            for country, products in turn_data["production_lines"].items():
                if country not in company.factories:
                    continue
                    
                for product, target_lines in products.items():
                    factories_list = company.factories[country]
                    current_lines = sum(f.product_lines.get(product, 0) for f in factories_list)
                    diff = target_lines - current_lines
                    
                    if diff > 0:  # Acheter des lignes
                        for factory in factories_list:
                            if diff <= 0:
                                break
                            can_add = min(diff, factory.free_space)
                            if can_add > 0:
                                try:
                                    cost = factory.modify_lines(product, can_add)
                                    if company.cash >= cost:
                                        company.cash -= cost
                                        diff -= can_add
                                    else:
                                        factory.modify_lines(product, -can_add)  # Rollback
                                        break
                                except:
                                    pass
                    elif diff < 0:  # Vendre des lignes
                        for factory in factories_list:
                            if diff >= 0:
                                break
                            current_in_factory = factory.product_lines.get(product, 0)
                            can_remove = min(abs(diff), current_in_factory)
                            if can_remove > 0:
                                try:
                                    cost = factory.modify_lines(product, -can_remove)
                                    company.cash -= cost  # cost sera négatif (remboursement)
                                    diff += can_remove
                                except:
                                    pass
            
            # 3. Définir les décisions de vente (pays + prix)
            sales = turn_data.get("sales", {})
            for product, decision in sales.items():
                country = decision.get("country", "")
                price = decision.get("price", 0)
                if country:
                    company.set_decision(product, "country", country)
                if price > 0:
                    company.set_decision(product, "price", price)
    
    def _calculate_production(self):
        """Calcule la production et l'ajoute aux stocks."""
        for company in self.companies:
            for country, factories_list in company.factories.items():
                efficiency = COUNTRY_CONFIG[country]["efficiency_multiplier"]
                
                for factory in factories_list:
                    for product, lines in factory.product_lines.items():
                        production = int(lines * 100 * efficiency)
                        company.stock[product] = company.stock.get(product, 0) + production
    
    def _apply_maintenance_costs(self):
        """Déduit les coûts de maintenance de toutes les usines."""
        for company in self.companies:
            total_maintenance = 0
            for factories_list in company.factories.values():
                for factory in factories_list:
                    total_maintenance += factory.maintenance_cost
            
            company.cash -= total_maintenance
            company.costs["maintenance"] = total_maintenance
    
    def _resolve_sales(self):
        """Résout les ventes selon la logique du prix le plus bas.
        NOUVELLE LOGIQUE : Chaque produit ne peut être vendu que dans UN SEUL pays."""
        params = self.get_turn_data()
        self.sales_history = []  # Reset l'historique pour ce tour
        
        # Pour chaque produit, résoudre les ventes dans le pays où il est commercialisé
        for product in params["products_meta"].keys():
            
            # Collecter toutes les offres pour ce produit (company, pays, prix, stock)
            offers = []
            for company in self.companies:
                decision = company.get_decision(product)
                country = decision.get("country", "")
                price = decision.get("price", 0)
                stock = company.stock.get(product, 0)
                
                # Le produit doit avoir un pays assigné, un prix > 0 et du stock
                if country and price > 0 and stock > 0:
                    # Vérifier que ce pays existe et qu'il y a de la demande
                    if country in params["countries"]:
                        base_demand = params["countries"][country]["products"].get(product, {}).get("base_demand", 0)
                        if base_demand > 0:
                            offers.append({
                                "company": company,
                                "country": country,
                                "price": price,
                                "stock": stock,
                                "base_demand": base_demand
                            })
            
            if not offers:
                continue
            
            # Grouper les offres par pays (un produit peut être vendu par plusieurs entreprises dans différents pays)
            # Mais chaque entreprise ne vend son produit que dans UN pays
            offers_by_country = {}
            for offer in offers:
                country = offer["country"]
                if country not in offers_by_country:
                    offers_by_country[country] = []
                offers_by_country[country].append(offer)
            
            # Pour chaque pays où le produit est commercialisé
            for country, country_offers in offers_by_country.items():
                base_demand = country_offers[0]["base_demand"]  # Même demande pour tous
                
                # Trier par prix croissant
                country_offers.sort(key=lambda x: x["price"])
                
                remaining_demand = base_demand
                
                # Algorithme de vente
                while remaining_demand > 0 and country_offers:
                    # Trouver le prix minimum
                    min_price = country_offers[0]["price"]
                    sellers_at_min_price = [o for o in country_offers if o["price"] == min_price]
                    
                    if not sellers_at_min_price:
                        break
                    
                    # Vente alternée pour les vendeurs au même prix
                    for seller in sellers_at_min_price:
                        if remaining_demand <= 0:
                            break
                        
                        qty_to_sell = min(1, seller["stock"], remaining_demand)
                        
                        if qty_to_sell > 0:
                            # Vendre
                            seller["company"].stock[product] -= qty_to_sell
                            revenue = qty_to_sell * seller["price"]
                            seller["company"].cash += revenue
                            seller["company"].revenue += revenue
                            
                            # Tracker la vente
                            self.sales_history.append({
                                "country": country,
                                "product": product,
                                "company_name": seller["company"].name,
                                "is_player": seller["company"].is_player,
                                "price": seller["price"],
                                "quantity": qty_to_sell
                            })
                            
                            seller["stock"] -= qty_to_sell
                            remaining_demand -= qty_to_sell
                    
                    # Retirer les vendeurs sans stock
                    country_offers = [o for o in country_offers if o["stock"] > 0]
    
    def get_ranking(self):
        """Retourne le classement des entreprises par cash décroissant."""
        ranked = sorted(self.companies, key=lambda c: c.cash, reverse=True)
        return [{"rank": i+1, "name": c.name, "cash": c.cash, "is_player": c.is_player} 
                for i, c in enumerate(ranked)]
    
    def resolve_turn(self):
        """Résout complètement le tour actuel."""
        print(f"--- RESOLVING TURN {self.turn} ---")
        
        # Passer au tour suivant
        self.turn += 1
        
        # 1. Appliquer les actions IA pour ce tour
        self._apply_ai_actions(self.turn)
        
        # 2. Calculer la production -> stock
        self._calculate_production()
        
        # 3. Appliquer les coûts de maintenance
        self._apply_maintenance_costs()
        
        # 4. Résoudre les ventes
        self._resolve_sales()
        
        # 5. Reset des indicateurs pour le prochain tour
        for company in self.companies:
            company.reset_all_past_inf()
        
        print(f"Tour {self.turn} résolu!")
        print(f"Classement: {self.get_ranking()}")



