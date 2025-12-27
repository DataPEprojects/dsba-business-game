import uuid

# Configuration for each country: costs, efficiency, capacity, and maintenance
COUNTRY_CONFIG = {
    "USA": {
        "base_line_cost": 130,
        "efficiency_multiplier": 1.5,
        "max_capacity": 20,
        "maintenance_cost": 400,
    },
    "China": {
        "base_line_cost": 80,
        "efficiency_multiplier": 0.9,
        "max_capacity": 20,
        "maintenance_cost": 100,
    },
    "France": {
        "base_line_cost": 100,
        "efficiency_multiplier": 1.2,
        "max_capacity": 20,
        "maintenance_cost": 300,
    },
}


class Factories:
    def __init__(self, country, config):
        self.id = str(uuid.uuid4())[:8]
        self.country = country
        self.config = config[country]
        self.capacity = self.config["max_capacity"]
        # Track number of production lines per product
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

        # Return operation cost (positive for purchase, negative for refund)
        return qty * self.config["base_line_cost"]