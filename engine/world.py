from engine.parameters import Parameters
from entities.company import Company

class World:
    """Coordonne la simulation tour par tour."""
    def __init__(self):
        self.parameters = Parameters()
        self.turn = 1
        self.companies = [
            Company("A"),
            Company("B"),
            Company("C")
        ]

    def run(self, n_turns=2):
        for i in range(1, n_turns + 1):
            print(f"\n=== Tour {i} ===")
            params = self.parameters.get_turn(i)
            self.simulate_turn(params)

    def simulate_turn(self, params):
        print("Événement global :", params["global"]["event"])
        for c in self.companies:
            print(f"{c.name}  (cash: {c.cash:.1f})")
