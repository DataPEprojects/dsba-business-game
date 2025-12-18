class Company:
    """Représente une entreprise (joueur ou IA)."""
    def __init__(self, name):
        self.name = name
        self.cash = 1000
        self.profit = 0

    def __repr__(self):
        return f"<Company {self.name} | Cash={self.cash:.1f}>"
