from engine.market_generator import MarketGenerator

class Parameters:
    def __init__(self, total_turns=20):
        self.total_turns = total_turns
        self.generator = MarketGenerator(total_turns=total_turns)
        self._cache = {}  # Cache les tours générés

    def get_turn(self, turn_number):
        """Retourne les paramètres du tour (généré ou en cache)."""
        if turn_number not in self._cache:
            self._cache[turn_number] = self.generator.get_turn_data(turn_number)
        return self._cache[turn_number]