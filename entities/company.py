class Company:
    def __init__(self, name, is_player=False, ai_behavior=None):
        self.name = name
        self.is_player = is_player
        self.ai_behavior = ai_behavior
        self.cash = 100000
        self.profit = 0
        self.factories = {}   # { "USA": [Factories, ...], ... }
        self.stock = {}       # { "A": qty, ... }
        self.revenue = 0

        # Indicateurs financiers (reset chaque tour)
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}

        # Décisions de vente par produit : {"A": {"country": "", "price": 0}, ...}
        self.sales_decisions = {}

    def ensure_all_products(self, products):
        """Initialise les clés de stock pour les produits fournis."""
        for p in products:
            self.stock.setdefault(p, 0)

    def reset_all_past_inf(self):
        """Reset des indicateurs spécifiques à chaque tour."""
        self.revenue = 0
        self.costs = {"production": 0, "maintenance": 0, "marketing": 0, "transport": 0, "taxes": 0}

    # --- Décisions (compatibilité avec world.py) ---
    def set_decision(self, product, field, value):
        """Enregistre la décision (pays ou prix) pour un produit."""
        if product not in self.sales_decisions:
            self.sales_decisions[product] = {"country": "", "price": 0}
        self.sales_decisions[product][field] = value

    def get_decision(self, product):
        """Retourne la décision pour un produit (country, price)."""
        return self.sales_decisions.get(product, {"country": "", "price": 0})

    # --- Gestion des usines / lignes (compatible avec Factories.modify_lines) ---
    def set_production_lines(self, country, product, qty):
        """
        Ajuste le nombre total de lignes pour `product` dans `country` en répartissant
        l'ajustement sur les usines existantes. Les coûts/recettes sont appliqués à self.cash.
        Silencieux en cas d'erreur (world.py appelle sans crash).
        """
        if country not in self.factories or not self.factories[country]:
            return

        factories = self.factories[country]
        current_total = sum(f.product_lines.get(product, 0) for f in factories)
        diff = qty - current_total

        # Augmenter les lignes
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
                # Vérif argent
                if cost > 0 and self.cash < cost:
                    # rollback
                    try:
                        f.modify_lines(product, -can_add)
                    except Exception:
                        pass
                    break
                # appliquer coût
                self.cash -= cost
                remaining -= can_add

        # Réduire les lignes
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
                # cost sera négatif => subtracting it adds cash
                self.cash -= cost
                remaining_to_remove -= to_remove

    def buy_factory(self, country, cost=0, factory_obj=None):
        """
        Ajoute une usine au pays. Si `cost` fourni (>0), on débite self.cash.
        Si factory_obj fourni, on l'utilise ; sinon on crée une nouvelle Factories.
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