import random

class AIBehavior:
    def __init__(self, name, personality):
        self.name = name
        self.personality = personality
        
        if personality == "aggressive":
            self.expand_rate = 0.85
            self.price_position = "low"
            self.product_focus = {"A": 0.7, "B": 0.2, "C": 0.1}
            self.preferred_countries = ["China", "USA"]
        elif personality == "balanced":
            self.expand_rate = 0.5
            self.price_position = "middle"
            self.product_focus = {"A": 0.35, "B": 0.35, "C": 0.3}
            self.preferred_countries = ["France", "USA", "China"]
        elif personality == "conservative":
            self.expand_rate = 0.3
            self.price_position = "high"
            self.product_focus = {"A": 0.1, "B": 0.3, "C": 0.6}
            self.preferred_countries = ["France"]
        elif personality == "premium":
            self.expand_rate = 0.4
            self.price_position = "high"
            self.product_focus = {"C": 0.7, "B": 0.2, "A": 0.1}
            self.preferred_countries = ["France", "USA"]
        else:  # volume
            self.expand_rate = 0.95
            self.price_position = "very_low"
            self.product_focus = {"A": 0.8, "B": 0.15, "C": 0.05}
            self.preferred_countries = ["China"]
    
    def should_buy_factory(self, turn):
        """Turn 1 obligatoire, après c'est probabiliste"""
        return turn == 1 or random.random() < self.expand_rate
    
    def choose_country_for_factory(self):
        return random.choice(self.preferred_countries)
    
    def allocate_lines_by_country(self, factories_owned):
        """Allouer les lignes par usine et produit"""
        allocation = {}
        capacity_per_factory = 20
        
        for country in factories_owned.keys():
            allocation[country] = {}
            remaining = capacity_per_factory
            
            for product in ["A", "B", "C"]:
                qty = int(capacity_per_factory * self.product_focus.get(product, 0))
                qty = min(qty, remaining)
                if qty > 0:
                    allocation[country][product] = qty
                    remaining -= qty
        
        return allocation
    
    def choose_price(self, available_prices):
        """Choisir un prix parmi les options du marché"""
        sorted_prices = sorted(available_prices)
        n = len(sorted_prices)
        
        if self.price_position == "very_low":
            return sorted_prices[0]
        elif self.price_position == "low":
            return sorted_prices[max(0, n // 4)]
        elif self.price_position == "middle":
            return sorted_prices[n // 2]
        elif self.price_position == "high":
            return sorted_prices[min(n-1, 3*n // 4)]
        else:  # premium
            return sorted_prices[-1]
    
    def choose_sales_country(self, product):
        """Choisir le pays pour vendre ce produit"""
        if product == "C":
            return random.choice(["USA", "France"])
        elif product == "A":
            return random.choice(self.preferred_countries)
        else:
            return random.choice(self.preferred_countries)


class AIManager:
    PERSONALITIES = ["aggressive", "balanced", "conservative", "premium", "volume"]
    
    def __init__(self, num_ais=5):
        # Cap à 10 max, pas de négatif
        self.num_ais = max(0, min(int(num_ais), 10))
        self.ais = self._generate_ais()
    
    def _generate_ais(self):
        """Génère jusqu'à 10 IA.
        - 0..4: noms fixes + personnalités cyclées
        - 5..9: noms fixes + personnalités aléatoires
        """
        import random
        ais = {}
        base_names = [
            "AI_Alpha", "AI_Beta", "AI_Gamma", "AI_Delta", "AI_Epsilon",
            "AI_Zeta", "AI_Eta", "AI_Theta", "AI_Iota", "AI_Kappa"
        ]
        
        for i in range(self.num_ais):
            name = base_names[i]
            if i < 5:
                personality = self.PERSONALITIES[i % len(self.PERSONALITIES)]
            else:
                personality = random.choice(self.PERSONALITIES)
            ais[name] = AIBehavior(name, personality)
        
        return ais
    
    def get_ai(self, name):
        return self.ais.get(name)
    
    def get_all_ais(self):
        return list(self.ais.values())