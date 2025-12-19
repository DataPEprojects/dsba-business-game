from engine.parameters import Parameters
from entities.company import Company
from entities.product import PRODUCTS_CONFIG

class World:
    """Coordonne la simulation tour par tour."""
    def __init__(self):
        self.parameters = Parameters()
        self.turn = 1
        self.companies = [
            Company("test_comp_1",is_player=True),
            # Company("test_comp_2"),
            # Company("test_comp_2")
        ]

    def run(self, n_turns=2):
        for i in range(1, n_turns + 1):
            print(f"\n=== Tour {i} ===")
            params = self.parameters.get_turn(i)
            self.simulate_turn(params)

    def simulate_turn(self, params):
        print("Événement global :", params["global"]["event"])
        for c in self.companies:
            if c.is_player:
                self.player_turn(c)
            else:
                self.AI_turn(c)
            print(f"{c.name}  (cash: {c.cash:.1f})")
    
    def player_turn(self,company):
        print(f"Hello CEO de {company}")
        action = input("Test = veux tu achter / vendre ?")
        print(f"Vous avez choisi de :{action}")

    def AI_turn(self,company):
        print(f"Le CEO de {company} ne fait rien, il doit être malade")