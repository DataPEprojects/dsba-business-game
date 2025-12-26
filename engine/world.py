from engine.parameters import Parameters
from entities.company import Company
from entities.factory import Factories, COUNTRY_CONFIG
from engine.AI_manager import AIManager

SETUP_COSTS = {
    "USA": 40000,
    "China": 25000,
    "France": 30000
}

class World:
    """Coordonne la simulation tour par tour."""
    def __init__(self, total_turns=20, num_ais=5):
        self.parameters = Parameters(total_turns=total_turns)
        self.turn = 1
        self.total_turns = total_turns 
        self.ai_manager = AIManager(num_ais=num_ais)
        self.companies = self._initialize_companies()
        self.sales_history = []
    
    def _initialize_companies(self):
        """Crée le joueur + les IA"""
        companies = []
        
        # Joueur humain
        player = Company("Player", is_player=True)
        companies.append(player)
        
        # IA
        for ai_name, ai_behavior in self.ai_manager.ais.items():
            company = Company(ai_name, is_player=False, ai_behavior=ai_behavior)
            companies.append(company)
        
        return companies
    
    def get_turn_data(self):
        """Renvoie les paramètres du tour actuel."""
        return self.parameters.get_turn(self.turn)
    
    def _apply_ai_actions(self):
        """Applique les actions des IA pour le tour courant."""
        turn_data = self.get_turn_data()
        
        for company in self.companies:
            if company.is_player:
                continue  # Le joueur agit via le front
            
            ai = company.ai_behavior
            
            # 1. Acheter une usine
            if ai.should_buy_factory(self.turn):
                country = ai.choose_country_for_factory()
                cost = SETUP_COSTS[country]
                
                if company.cash >= cost:
                    company.cash -= cost
                    new_factory = Factories(country, COUNTRY_CONFIG)
                    if country not in company.factories:
                        company.factories[country] = []
                    company.factories[country].append(new_factory)
            
            # 2. Allouer les lignes de production
            if company.factories:
                lines = ai.allocate_lines_by_country(company.factories)
                for country, products in lines.items():
                    if country in company.factories:
                        for product, qty in products.items():
                            company.set_production_lines(country, product, qty)
            
            # 3. Fixer prix et pays de vente
            for product in ["A", "B", "C"]:
                if product in turn_data["products_meta"]:
                    prices = turn_data["products_meta"][product]["price_options"]
                    chosen_price = ai.choose_price(prices)
                    sales_country = ai.choose_sales_country(product)
                    
                    company.set_decision(product, "country", sales_country)
                    company.set_decision(product, "price", chosen_price)
    
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
        """Résout les ventes selon la logique du prix le plus bas."""
        params = self.get_turn_data()
        self.sales_history = []
        
        for product in params["products_meta"].keys():
            offers = []
            
            for company in self.companies:
                decision = company.get_decision(product)
                country = decision.get("country", "")
                price = decision.get("price", 0)
                stock = company.stock.get(product, 0)
                
                if country and price > 0 and stock > 0:
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
            
            offers_by_country = {}
            for offer in offers:
                country = offer["country"]
                if country not in offers_by_country:
                    offers_by_country[country] = []
                offers_by_country[country].append(offer)
            
            for country, country_offers in offers_by_country.items():
                base_demand = country_offers[0]["base_demand"]
                country_offers.sort(key=lambda x: x["price"])
                
                remaining_demand = base_demand
                
                while remaining_demand > 0 and country_offers:
                    min_price = country_offers[0]["price"]
                    sellers_at_min_price = [o for o in country_offers if o["price"] == min_price]
                    
                    if not sellers_at_min_price:
                        break
                    
                    for seller in sellers_at_min_price:
                        if remaining_demand <= 0:
                            break
                        
                        qty_to_sell = min(1, seller["stock"], remaining_demand)
                        
                        if qty_to_sell > 0:
                            seller["company"].stock[product] -= qty_to_sell
                            revenue = qty_to_sell * seller["price"]
                            seller["company"].cash += revenue
                            seller["company"].revenue += revenue
                            
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
                    
                    country_offers = [o for o in country_offers if o["stock"] > 0]
    
    def get_ranking(self):
        """Retourne le classement des entreprises par cash décroissant."""
        ranked = sorted(self.companies, key=lambda c: c.cash, reverse=True)
        return [{"rank": i+1, "name": c.name, "cash": c.cash, "is_player": c.is_player} 
                for i, c in enumerate(ranked)]
    
    def resolve_turn(self):
        """Résout complètement le tour actuel."""
        print(f"--- RESOLVING TURN {self.turn} ---")
        
        # 1. Appliquer les actions IA
        self._apply_ai_actions()
        
        # 2. Calculer la production
        self._calculate_production()
        
        # 3. Appliquer les coûts de maintenance
        self._apply_maintenance_costs()
        
        # 4. Résoudre les ventes
        self._resolve_sales()
        
        # 5. Reset et passer au tour suivant
        for company in self.companies:
            if hasattr(company, 'reset_all_past_inf'):
                company.reset_all_past_inf()
        
        self.turn += 1
        
        print(f"Tour {self.turn - 1} résolu!")
        print(f"Classement: {self.get_ranking()}")
    
    def is_game_over(self):
        """Vérifie si la partie est terminée."""
        return self.turn > self.total_turns
    
    def get_company(self, name):
        """Récupère une compagnie par son nom."""
        return next((c for c in self.companies if c.name == name), None)
    
    def get_all_companies(self):
        """Retourne toutes les compagnies."""
        return self.companies