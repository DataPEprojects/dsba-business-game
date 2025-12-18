import json
import os

class Parameters:
    """Charge les paramètres du monde à partir des fichiers JSON de /data/parameters."""
    def __init__(self, folder_path="data/parameters"):
        self.turns = {}
        "prends chaque fichiers nommé JSON dans le folder"
        for file in sorted(os.listdir(folder_path)):
            if file.endswith(".json"):
                turn_number = int(file.split("_")[1].split(".")[0])
                with open(os.path.join(folder_path, file), "r", encoding="utf-8") as f:
                    self.turns[turn_number] = json.load(f)

    def get_turn(self, turn_number: int) -> dict:
        """Renvoie le dictionnaire de paramètres pour le tour demandé."""
        return self.turns.get(turn_number, self.turns[max(self.turns.keys())])
