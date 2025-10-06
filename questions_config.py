import json

# Carica il file JSON
with open('questions.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Estrai le configurazioni
questions = data["questions"]
per_system_qs = data["per_system_qs"]
extra_qs = data["extra_qs"]