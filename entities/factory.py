import uuid # Generate unique IDs

# Configuration for each country: costs, efficiency, capacity, and maintenance
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
    """Represents a production facility with capacity, efficiency, and maintenance costs."""
    def __init__(self, country, config):
        self.id = str(uuid.uuid4())[:8] # e.g., "a1b2c3d4"
        self.country = country
        self.config = config[country]
        self.capacity = self.config["max_capacity"]
        # Track lines per product: {'A': 5, 'B': 0}
        self.product_lines = {} 
    
    @property
    def total_lines_used(self):
        """Total number of production lines currently in use."""
        return sum(self.product_lines.values())

    @property
    def free_space(self):
        """Available capacity for new production lines."""
        return self.capacity - self.total_lines_used

    # Property to calculate maintenance dynamically
    @property
    def maintenance_cost(self):
        return self.total_lines_used * self.config["maintenance_cost"]

    def modify_lines(self, product, qty):
        """Adds or removes production lines for a product. Returns cost (positive=purchase, negative=refund)."""
        current = self.product_lines.get(product, 0)
        
        # Check constraints
        if qty > 0 and self.free_space < qty:
            raise ValueError("Not enough capacity")
        if qty < 0 and current + qty < 0:
            raise ValueError("Cannot have negative lines")
            
        self.product_lines[product] = current + qty

        # Return operation cost (positive if buying, negative if selling/refunding)
        return qty * self.config["base_line_cost"]