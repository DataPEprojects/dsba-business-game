from engine.parameters import Parameters
from entities.company import Company
from entities.product import PRODUCTS_CONFIG

class World:
    """Manages the turn-by-turn simulation and game state."""
    def __init__(self):
        self.parameters = Parameters()
        self.turn = 1
        self.companies = [
            Company("test_comp_1 = player",is_player=True),
            Company("test_comp_2 = AI")
        ]
    
    def get_turn_data(self):
        return self.parameters.get_turn(self.turn)
    
    def calculate_company_scores(self, company_actions, params):
        """
        Calculates a score for every market the company invested in.
        
        Args:
            company_actions (list): A list of dicts, e.g.:
                [
                    {"country": "China", "product": "A", "marketing": 20},
                    {"country": "USA",   "product": "B", "marketing": 15}
                ]
            params (dict): The full JSON configuration.

        Returns:
            dict: A nested dictionary of scores per [country][product]
                  Example: {"China": {"A": 24.0}, "USA": {"B": 16.8}}
        """
        scores = {}

        for action in company_actions:
            country = action["country"]
            product = action["product"]
            marketing = action["marketing"]

            # 1. Get the Integration Bonus from JSON
            # strictly following your structure: params["countries"][country]["integration_bonus"]
            country_data = params["countries"].get(country)
            
            if not country_data:
                continue # Skip invalid countries
                
            bonus = country_data["integration_bonus"]

            # 2. Compute the Score
            # Formula: Marketing * (1 + Integration Bonus)
            final_score = marketing * (1 + bonus)

            # 3. Store in the nested structure [country][product]
            if country not in scores:
                scores[country] = {}
            
            scores[country][product] = final_score

        return scores
    
    def _apply_marketing_costs(self):
        """
        Applies marketing budgets decided by players to actual costs.
        """
        for company in self.companies:
            # Process all recorded sales decisions
            for country, products_decisions in company.sales_decisions.items():
                for product, decision in products_decisions.items():
                    
                    budget = decision.get("marketing", 0)
                    
                    if budget > 0:
                        # Deduct from cash
                        company.cash -= budget
                        
                        # Track in costs dictionary
                        company.costs["marketing"] += budget

    def resolve_turn(self):
            """
            Executes end-of-turn logic (V0 implementation).
            """
            print(f"--- RESOLVING TURN {self.turn} ---")
            
            # Increment turn counter
            self.turn += 1
            
            # Verify that configuration exists for next turn
            try:
                # Check if turn configuration file exists
                _ = self.parameters.get_turn(self.turn)
            except Exception as e:
                print(f"⚠️ Warning: No configuration for turn {self.turn}. End of demo content?")