COUNTRY_CONFIG = {
    "USA": {
        "base_line_cost": 130,
        "efficiency_multiplier": 1.5,
        "max_capacity": 20,
        "maintenance_cost":20,
    },
    "China": {
        "base_line_cost": 80,
        "efficiency_multiplier": 0.9,
        "max_capacity": 20,
        "maintenance_cost":20,
    },
    "France": {
        "base_line_cost": 100,
        "efficiency_multiplier": 1.2,
        "max_capacity": 20,
        "maintenance_cost":20,
    },
}


class Factories:
    def __init__(self,country,config):
        self.country = country
        self.config = config[country]
        self.capacity = self.config["max_capacity"]
        self.num_lines = 0
    
    def can_add_line(self, qty = 1):
        return self.num_lines + qty <= self.capacity
    
    def can_del_line(self, qty = 1):
        return self.num_lines - qty >= 0
    
    def add_line(self,qty=1):
        if not self.can_add_line(qty):
            raise  ValueError("Not enough capacity")
        total_cost = self.config["base_line_cost"] * qty
        self.num_lines += qty
        return total_cost #the idea is to substract this from the cash of the player; + the maintenance cost
    
    def del_line(self,qty=1):
        if not self.can_del_line:
            raise  ValueError("Not enough lines")
        self.num_lines
        self.num_lines -= qty
    
    def maintenance_cost(self):
        return self.num_lines * self.config["maintenance_cost"]

usines_test_00000001 = Factories('USA', COUNTRY_CONFIG)

usines_test_00000001.add_line(20)
usines_test_00000001
print(usines_test_00000001.maintenance_cost)