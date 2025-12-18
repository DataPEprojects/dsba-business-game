import json

with open(r"data\parameters\turn_1.json") as f:
    turn_config = json.load(f)

print(turn_config)