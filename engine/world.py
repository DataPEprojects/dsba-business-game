import json
from engine.parameters import Parameters
from entities.company import Company
from entities.factory import Factories, COUNTRY_CONFIG

# Fixed setup costs for factory establishment
SETUP_COSTS = {
    "USA": 40000,
    "China": 25000,
    "France": 30000
}

class World:
    """Coordinates turn-by-turn simulation of the business game."""
    def __init__(self, total_turns=20):
        self.parameters = Parameters(total_turns=total_turns)
        self.turn = 1
        self.total_turns = total_turns 
        self.ai_behaviors = self._load_ai_behaviors()
        self.companies = self._initialize_companies()
        self.sales_history = []
        
    def _load_ai_behaviors(self):
        """Loads pre-recorded AI behaviors from JSON file."""
        with open("data/ai_behaviors.json", "r", encoding="utf-8-sig") as f:
            return json.load(f)
    
    def _initialize_companies(self):
        """Creates the player and 5 AI companies."""
        companies = [Company("Player", is_player=True)]
        
        for ai_name in self.ai_behaviors.keys():
            companies.append(Company(ai_name, is_player=False))
        
        # Initialize stock for all products
        all_products = list(self.parameters.get_turn(1)["products_meta"].keys())
        for company in companies:
            company.ensure_all_products(all_products)
            
        return companies
    
    def get_turn_data(self):
        """Returns parameters for the current turn."""
        return self.parameters.get_turn(self.turn)
    
    def _apply_ai_actions(self, turn_number):
        """Applies pre-recorded AI actions for the given turn."""
        for company in self.companies:
            if company.is_player:
                continue
            
            ai_name = company.name
            turn_data = self.ai_behaviors[ai_name]["turns"].get(str(turn_number))
            
            if not turn_data:
                continue
            
            # Purchase factories
            for country in turn_data["buy_factories"]:
                cost = SETUP_COSTS[country]
                if company.cash >= cost:
                    company.cash -= cost
                    new_factory = Factories(country, COUNTRY_CONFIG)
                    if country not in company.factories:
                        company.factories[country] = []
                    company.factories[country].append(new_factory)
            
            # Allocate production lines
            for country, products in turn_data["production_lines"].items():
                if country not in company.factories:
                    continue
                    
                for product, target_lines in products.items():
                    factories_list = company.factories[country]
                    current_lines = sum(f.product_lines.get(product, 0) for f in factories_list)
                    diff = target_lines - current_lines
                    
                    if diff > 0:
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
                                        factory.modify_lines(product, -can_add)
                                        break
                                except:
                                    pass
                    elif diff < 0:
                        for factory in factories_list:
                            if diff >= 0:
                                break
                            current_in_factory = factory.product_lines.get(product, 0)
                            can_remove = min(abs(diff), current_in_factory)
                            if can_remove > 0:
                                try:
                                    cost = factory.modify_lines(product, -can_remove)
                                    company.cash -= cost
                                    diff += can_remove
                                except:
                                    pass
            
            # Set sales decisions (country + price)
            sales = turn_data.get("sales", {})
            for product, decision in sales.items():
                country = decision.get("country", "")
                price = decision.get("price", 0)
                if country:
                    company.set_decision(product, "country", country)
                if price > 0:
                    company.set_decision(product, "price", price)
    
    def _calculate_production(self):
        """Calculates production and adds to inventory stock."""
        for company in self.companies:
            for country, factories_list in company.factories.items():
                efficiency = COUNTRY_CONFIG[country]["efficiency_multiplier"]
                
                for factory in factories_list:
                    for product, lines in factory.product_lines.items():
                        production = int(lines * 100 * efficiency)
                        company.stock[product] = company.stock.get(product, 0) + production
    
    def _apply_maintenance_costs(self):
        """Deducts maintenance costs from all factories."""
        for company in self.companies:
            total_maintenance = 0
            for factories_list in company.factories.values():
                for factory in factories_list:
                    total_maintenance += factory.maintenance_cost
            
            company.cash -= total_maintenance
            company.costs["maintenance"] = total_maintenance
    
    def _resolve_sales(self):
        """Resolves sales using lowest-price-first logic. Each product can only be sold in ONE country."""
        params = self.get_turn_data()
        self.sales_history = []
        
        # For each product, resolve sales in the country where it's sold
        for product in params["products_meta"].keys():
            
            # Collect all offers for this product (company, country, price, stock)
            offers = []
            for company in self.companies:
                decision = company.get_decision(product)
                country = decision.get("country", "")
                price = decision.get("price", 0)
                stock = company.stock.get(product, 0)
                
                # Product must have assigned country, price > 0, and stock available
                if country and price > 0 and stock > 0:
                    # Check that country exists and has demand
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
            
            # Group offers by country (one product sold by multiple companies in different countries)
            # But each company only sells its product in ONE country
            offers_by_country = {}
            for offer in offers:
                country = offer["country"]
                if country not in offers_by_country:
                    offers_by_country[country] = []
                offers_by_country[country].append(offer)
            
            # For each country where the product is sold
            for country, country_offers in offers_by_country.items():
                base_demand = country_offers[0]["base_demand"]
                
                # Sort by ascending price
                country_offers.sort(key=lambda x: x["price"])
                
                remaining_demand = base_demand
                
                # Sales algorithm
                while remaining_demand > 0 and country_offers:
                    # Find minimum price
                    min_price = country_offers[0]["price"]
                    sellers_at_min_price = [o for o in country_offers if o["price"] == min_price]
                    
                    if not sellers_at_min_price:
                        break
                    
                    # Alternating sales for sellers at the same price
                    for seller in sellers_at_min_price:
                        if remaining_demand <= 0:
                            break
                        
                        qty_to_sell = min(1, seller["stock"], remaining_demand)
                        
                        if qty_to_sell > 0:
                            # Execute sale
                            seller["company"].stock[product] -= qty_to_sell
                            revenue = qty_to_sell * seller["price"]
                            seller["company"].cash += revenue
                            seller["company"].revenue += revenue
                            
                            # Track sale in history
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
                    
                    # Remove sellers with no stock left
                    country_offers = [o for o in country_offers if o["stock"] > 0]
    
    def get_ranking(self):
        """Returns company ranking sorted by cash (descending)."""
        ranked = sorted(self.companies, key=lambda c: c.cash, reverse=True)
        return [{"rank": i+1, "name": c.name, "cash": c.cash, "is_player": c.is_player} 
                for i, c in enumerate(ranked)]
    
    def resolve_turn(self):
        """Resolves the current turn completely."""
        print(f"--- RESOLVING TURN {self.turn} ---")
        
        # Advance to next turn
        self.turn += 1
        
        # Apply AI actions for this turn
        self._apply_ai_actions(self.turn)
        
        # Calculate production and add to stock
        self._calculate_production()
        
        # Apply maintenance costs
        self._apply_maintenance_costs()
        
        # Resolve sales
        self._resolve_sales()
        
        # Reset indicators for next turn
        for company in self.companies:
            company.reset_all_past_inf()
        
        print(f"Turn {self.turn} resolved!")
        print(f"Ranking: {self.get_ranking()}")



