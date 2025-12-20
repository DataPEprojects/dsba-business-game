class Company:
    def __init__(self, name, is_player=False):
        self.name = name
        self.is_player = is_player
        self.factories = {} 
        self.cash = 100000
        self.profit =0
        self.stock = {}
        self.revenue = 0
        self.costs = {}        
        # --- AJOUT POUR LES VENTES ---
        # Structure : self.sales_decisions[Pays][Produit] = {"price": 0, "marketing": 0}
        self.sales_decisions = {} 

    def get_decision(self, country, product):
        """Récupère la décision actuelle ou renvoie une valeur par défaut"""
        if country not in self.sales_decisions:
            self.sales_decisions[country] = {}
        
        if product not in self.sales_decisions[country]:
            self.sales_decisions[country][product] = {"price": 0, "marketing": 0}
            
        return self.sales_decisions[country][product]

    def set_decision(self, country, product, field, value):
        """Enregistre une décision (price ou marketing)"""
        # Initialisation si nécessaire
        self.get_decision(country, product)
        
        # Enregistrement
        self.sales_decisions[country][product][field] = value
        
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
