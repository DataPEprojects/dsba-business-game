from engine.parameters import Parameters
from entities.company import Company
from entities.product import PRODUCTS_CONFIG

class World:
    """Coordonne la simulation tour par tour."""
    def __init__(self):
        self.parameters = Parameters()
        self.turn = 1
        self.companies = [
            Company("test_comp_1 = player",is_player=True),
            Company("test_comp_2 = AI")
            # Company("test_comp_2")
        ]
    # outdated=> c'était l'acienne version pour test; j'aii séparé avec un .py dédié 
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
        Applique les budgets marketing décidés par les joueurs aux coûts réels.
        """
        for company in self.companies:
            # On parcourt toutes les décisions de vente enregistrées
            for country, products_decisions in company.sales_decisions.items():
                for product, decision in products_decisions.items():
                    
                    budget = decision.get("marketing", 0)
                    
                    if budget > 0:
                        # 1. On déduit du cash
                        company.cash -= budget
                        
                        # 2. On alimente TON dictionnaire de coûts
                        company.costs["marketing"] += budget

    def resolve_turn(self):
            """
            Logique de fin de tour V0.
            """
            print(f"--- RESOLVING TURN {self.turn} ---")
            
            # 1. Incrémenter le tour
            self.turn += 1
            
            # 2. (V0) On vérifie juste que le JSON charge, sinon on gère l'erreur
            try:
                # Juste pour tester que le fichier existe, on ne fait rien avec pour l'instant
                _ = self.parameters.get_turn(self.turn)
            except Exception as e:
                print(f"⚠️ Warning: Pas de config pour le tour {self.turn}. Fin du contenu demo ?")
                # Optionnel : self.turn -= 1 si tu veux bloquer