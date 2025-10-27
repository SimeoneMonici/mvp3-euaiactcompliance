import json
try:
    with open('questions.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
    questions = data["questions"]
    per_system_qs = data["per_system_qs"]
    extra_qs = data["extra_qs"]
    print(f"Caricato da questions.json: {len(questions)} generali, {len(per_system_qs)} per sistema, {sum(len(v) for v in extra_qs.values() if isinstance(v, list)) + sum(len(sub) for v in extra_qs.values() if isinstance(v, dict) for sub in v.values())} extra.")
except Exception as e:
    print(f"Errore: {e}. Configurazioni vuote.")
    questions = []
    per_system_qs = []
    extra_qs = {}

