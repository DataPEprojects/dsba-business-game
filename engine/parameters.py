from engine.market_generator import MarketGenerator

class Parameters:
    """Manages game parameters and caches turn data."""
    def __init__(self, total_turns=20):
        self.total_turns = total_turns
        self.generator = MarketGenerator(total_turns=total_turns)
        self._cache = {}  # caches generated turns

    def get_turn(self, turn_number):
        """Returns turn parameters (generated or in cache)."""
        if turn_number not in self._cache:
            self._cache[turn_number] = self.generator.get_turn_data(turn_number)
        return self._cache[turn_number]