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

    def apply_player_action(self,company,action_data):
        """
        Here we will apply all the formulas, such as matrix prices ect...
        """
        pass

    def simulate_ai_turn(self, params):
        """
        Logic of AIs decisions
        """
        for c in self.companies:
            if not c.is_player:
                #AI logic to create
                pass