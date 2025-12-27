import uuid

COUNTRY_CONFIG = {
    "USA": {
        "base_line_cost": 130,      # Expensive lines
        "efficiency_multiplier": 1.5, # Best production (+50%)
        "max_capacity": 20,
        "maintenance_cost": 400,     # High maintenance
    },
    "China": {
        "base_line_cost": 80,        # Cheapest lines
        "efficiency_multiplier": 0.9, # Slower production (-10%)
        "max_capacity": 20,
        "maintenance_cost": 100,     # Low maintenance
    },
    "France": {
        "base_line_cost": 100,       # Balanced
        "efficiency_multiplier": 1.2, # Good production (+20%)
        "max_capacity": 20,
        "maintenance_cost": 300,     # Balanced maintenance
    },
}



class Factories:
    def __init__(self, country, config):
        self.id = str(uuid.uuid4())[:8] # Ex: "a1b2c3d4"
        self.country = country
        self.config = config[country]
        self.capacity = self.config["max_capacity"]
        # Track lines per product: {'A': 5, 'B': 0}
        self.product_lines = {} 
    
    @property
    def total_lines_used(self):
        return sum(self.product_lines.values())

    @property
    def free_space(self):
        return self.capacity - self.total_lines_used

    @property
    def maintenance_cost(self):
        return self.total_lines_used * self.config["maintenance_cost"]

    def modify_lines(self, product, qty):
        current = self.product_lines.get(product, 0)
        
        # Check constraints
        if qty > 0 and self.free_space < qty:
            raise ValueError("Not enough capacity")
        if qty < 0 and current + qty < 0:
            raise ValueError("Cannot have negative lines")
            
        self.product_lines[product] = current + qty

        # Return operation cost (positive for purchase, negative for sale/refund)
        return qty * self.config["base_line_cost"]