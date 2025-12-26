import random

class MarketGenerator:
    def __init__(self,total_turns=20):
        self.total_turns = total_turns
        self.base_config = {
            "products": {
                "A": {"base_price": 18, "base_demand": {"France": 1200, "USA": 2000, "China": 1800}},
                "B": {"base_price": 100, "base_demand": {"France": 400, "USA": 500, "China": 200}},
                "C": {"base_price": 230, "base_demand": {"France": 100, "USA": 150, "China": 50}}
            },
            "countries": {
                "France": {"integration_bonus": 0.10},
                "USA": {"integration_bonus": 0.12},
                "China": {"integration_bonus": 0.20}
            }
        }

    def get_turn_data(self, turn):
        """Génère les données du tour dynamiquement."""
        multiplier, event = self._get_climate(turn)
        
        data = {
            "global": {"event": event, "economic_index": round(multiplier, 2)},
            "products_meta": {},
            "marketing_meta": {"budget_marketing": [0, 1000, 2000, 5000, 10000]},
            "countries": {},
            "transport_matrix": self._generate_transport_matrix(),
            "tax_matrix": self._generate_tax_matrix()
        }

        # Génération Prix et Demande
        for prod, info in self.base_config["products"].items():
            center_price = int(info["base_price"] * multiplier)
            spread = 3 if prod == "A" else 5
            price_range = [center_price - spread + i for i in range(spread * 2 + 1)]
            
            data["products_meta"][prod] = {
                "description": f"Product {prod}",
                "price_options": price_range,
                "price_range": price_range
            }

            for country in ["France", "USA", "China"]:
                base_dem = info["base_demand"][country]
                final_demand = int(base_dem * multiplier * random.uniform(0.95, 1.05))
                
                if country not in data["countries"]:
                    data["countries"][country] = {
                        "products": {},
                        "integration_bonus": self.base_config["countries"][country]["integration_bonus"]
                    }
                
                data["countries"][country]["products"][prod] = {"base_demand": final_demand}

        return data
    
    def _get_climate(self, turn):
        """Détermine le climat économique selon le tour avec randomness."""
        # Phase 1: Early stability (turns 1-2)
        if turn <= 2:
            base_multiplier = 1.0 + (turn * 0.02)
            event = "Stability"
        
        # Phase 2: Growth period (turns 3 to 60% of game)
        elif turn <= int(self.total_turns * 0.6):
            progress = (turn - 2) / (int(self.total_turns * 0.6) - 2)
            base_multiplier = 1.0 + (progress * 0.15)
            # Random event: 30% chance of boom, 20% chance of dip
            rand = random.random()
            if rand < 0.3:
                base_multiplier *= random.uniform(1.05, 1.15)
                event = "Boom"
            elif rand < 0.5:
                base_multiplier *= random.uniform(0.92, 0.98)
                event = "Dip"
            else:
                event = "Growth"
        
        # Phase 3: Crisis period (60% to 80% of game)
        elif turn <= int(self.total_turns * 0.8):
            base_multiplier = random.uniform(0.65, 0.85)
            event = "Recession"
        
        # Phase 4: Recovery (80% to end)
        else:
            progress = (turn - int(self.total_turns * 0.8)) / (self.total_turns - int(self.total_turns * 0.8))
            base_multiplier = 0.7 + (progress * 0.35)
            base_multiplier *= random.uniform(0.98, 1.05)
            event = "Recovery"
        
        return round(base_multiplier, 2), event

    def _generate_transport_matrix(self):
        """Génère la matrice de transport."""
        return {
            "France": {"France": 0.00, "USA": 0.05, "China": 0.25},
            "USA": {"France": 0.05, "USA": 0.00, "China": 0.20},
            "China": {"France": 0.25, "USA": 0.20, "China": 0.00}
        }

    def _generate_tax_matrix(self):
        """Génère la matrice de taxes."""
        return {
            "France": {"France": 0.05, "USA": 0.08, "China": 0.15},
            "USA": {"France": 0.08, "USA": 0.04, "China": 0.12},
            "China": {"France": 0.10, "USA": 0.12, "China": 0.05}
        }