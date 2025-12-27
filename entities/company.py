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
        # Sales decisions structure: sales_decisions[Product] = {"country": "...", "price": 0}
        # Each product can only be sold in ONE country
        self.sales_decisions = {} 

    def get_decision(self, product):
        """Gets current decision for a product or returns default values."""
        if product not in self.sales_decisions:
            self.sales_decisions[product] = {"country": "", "price": 0}
            
        return self.sales_decisions[product]

    def set_decision(self, product, field, value):
        """Records a decision (country or price) for a product."""
        # Initialisation si nécessaire
        self.get_decision(product)
        
        # Enregistrement
        self.sales_decisions[product][field] = value
        
    def ensure_all_products(self,products):
        """Initializes stock for all products dynamically."""
        for p in products:
            self.stock.setdefault(p,0)

    def reset_all_past_inf(self):
        """Resets turn-specific indicators (revenue and costs)."""
        self.revenue = 0
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}


    # For debugging: prints company status (can be reactivated if needed)
    # def __repr__(self):
    #     return f"<Company {self.name} | Cash={self.cash:.1f}>"
