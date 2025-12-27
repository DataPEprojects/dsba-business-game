class Company:
    """Represents a company (player or AI) with factories, inventory, and financial data."""
    def __init__(self, name, is_player=False, ai_behavior=None):
        self.name = name
        self.is_player = is_player
        self.ai_behavior = ai_behavior
        self.cash = 10000000
        self.profit = 0
        self.factories = {}   # { "USA": [Factories, ...], ... }
        self.stock = {}       # { "A": qty, ... }
        self.revenue = 0

        # Financial indicators (reset each turn)
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}

        # Sales decisions per product
        self.sales_decisions = {}

    def ensure_all_products(self, products):
        """Initializes stock entries for provided products."""
        for p in products:
            self.stock.setdefault(p, 0)

    def reset_all_past_inf(self):
        """Resets turn-specific indicators."""
        self.revenue = 0
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}

    # Decision management (compatibility with world.py)
    def set_decision(self, product, field, value):
        """Records decision (country or price) for a product."""
        if product not in self.sales_decisions:
            self.sales_decisions[product] = {"country": "", "price": 0}
        self.sales_decisions[product][field] = value

    def get_decision(self, product):
        """Returns the decision for a product (country, price)."""
        return self.sales_decisions.get(product, {"country": "", "price": 0})

    # Factory and production line management
    def set_production_lines(self, country, product, qty):
        """Adjusts total lines for product in country across factories.
        Applies costs/revenues to self.cash. Silent on errors (for world.py).
        """
        if country not in self.factories or not self.factories[country]:
            return

        factories = self.factories[country]
        current_total = sum(f.product_lines.get(product, 0) for f in factories)
        diff = qty - current_total

        # Increase lines
        if diff > 0:
            remaining = diff
            for f in factories:
                if remaining <= 0:
                    break
                can_add = min(f.free_space, remaining)
                if can_add <= 0:
                    continue
                try:
                    cost = f.modify_lines(product, can_add)
                except Exception:
                    continue
                # Verify sufficient cash
                if cost > 0 and self.cash < cost:
                    # rollback
                    try:
                        f.modify_lines(product, -can_add)
                    except Exception:
                        pass
                    break
                # Apply cost
                self.cash -= cost
                remaining -= can_add

        # Decrease lines
        elif diff < 0:
            remaining_to_remove = -diff
            for f in factories:
                if remaining_to_remove <= 0:
                    break
                current_in_f = f.product_lines.get(product, 0)
                if current_in_f <= 0:
                    continue
                to_remove = min(current_in_f, remaining_to_remove)
                try:
                    cost = f.modify_lines(product, -to_remove)
                except Exception:
                    continue
                # Cost is negative => subtracting adds cash
                self.cash -= cost
                remaining_to_remove -= to_remove

    def buy_factory(self, country, cost=0, factory_obj=None):
        """Adds a factory to the country. Deducts cost if provided.
        Creates new Factories object if factory_obj not provided.
        """
        from entities.factory import Factories, COUNTRY_CONFIG

        if cost and self.cash < cost:
            raise ValueError("Not enough cash to buy factory")

        if factory_obj is None:
            new_factory = Factories(country, COUNTRY_CONFIG)
        else:
            new_factory = factory_obj

        if country not in self.factories:
            self.factories[country] = []
        self.factories[country].append(new_factory)

        if cost:
            self.cash -= cost