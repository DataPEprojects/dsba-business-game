class Company:
    """Représente une entreprise (joueur ou IA)."""
    def __init__(self, name, is_player=False):
        self.name = name
        self.is_player = is_player
        self.cash = 1000
        self.profit =0

        self.stock = {}
        self.revenue = 0
        self.costs = {}

    def ensure_all_products(self,products):
        """Pour avoir les stocks de manière dynamique (pour pouvoir en ajouter/modifier en toute sérénité)."""
        for p in products:
            self.stock.setdefault(p,0)

    def reset_all_past_inf(self):
        """Cette fonction reset les indicateurs uniques à chaque tours"""
        self.revenue = 0
        #liste élémentaire pour l'instant, à voir par la suite si nous en ajoutons
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}


    # servait à print l'état des entreprises, peut être réactivé si nécessaire
    # def __repr__(self):
    #     return f"<Company {self.name} | Cash={self.cash:.1f}>"
