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
        # Sales decisions: sales_decisions[Country][Product] = {"price": 0, "marketing": 0}
        self.sales_decisions = {} 

    def get_decision(self, country, product):
        """Retrieves the current decision or returns a default value."""
        if country not in self.sales_decisions:
            self.sales_decisions[country] = {}
        
        if product not in self.sales_decisions[country]:
            self.sales_decisions[country][product] = {"price": 0, "marketing": 0}
            
        return self.sales_decisions[country][product]

    def set_decision(self, country, product, field, value):
        """Records a decision (price or marketing)."""
        # Initialize if necessary
        self.get_decision(country, product)
        
        # Save the value
        self.sales_decisions[country][product][field] = value
        
    def ensure_all_products(self,products):
        """Ensures all products exist in stock dictionary for dynamic product handling."""
        for p in products:
            self.stock.setdefault(p,0)

    def reset_all_past_inf(self):
        """Resets turn-specific indicators at the start of each turn."""
        self.revenue = 0
        # Initialize costs tracking for this turn
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}
