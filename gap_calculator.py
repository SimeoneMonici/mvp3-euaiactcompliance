import json
from utils import load_questions

def calculate_results(session_state):
    print("Caricamento questions_data...")
    questions_data = load_questions()
    print(f"questions_data: {questions_data.keys() if questions_data else 'None'}")
    general_questions = questions_data.get('questions', [])
    per_system_qs = questions_data.get('per_system_qs', [])
    extra_qs = questions_data.get('extra_qs', {})

    print(f"General questions: {len(general_questions)}, Per system: {len(per_system_qs)}, Extra: {len(extra_qs) if isinstance(extra_qs, dict) else 'N/A'}")

    # Estrai risposte
    general_responses = {q['id']: session_state.get(q['id'], '') for q in general_questions}
    system_answers = session_state.get('system_answers', [{}])

    print(f"General responses: {general_responses}")
    print(f"System answers: {system_answers}")

    # Check early per Difesa/Sicurezza Nazionale
    if general_responses.get('q1_1') in ["Difesa/Militare", "Sicurezza Nazionale"] and all(sys.get('q2_43', '') != 'Sì' for sys in system_answers):
        print("Esclusione per Difesa/Sicurezza Nazionale applicata.")
        return "L'AI Act non si applica a questo settore per scopi militari o di sicurezza nazionale (Art. 2) a meno che non sia escluso esplicitamente (q2_43). Analisi terminata.", [], [], []

    # Calcolo gap generali
    general_gaps = []
    for q in general_questions:
        ans = str(general_responses.get(q['id'], ''))
        if not ans and 'Alto gap' in q.get('notes', ''):  # Solo vuoti con Alto gap generano gap
            ans = 'No' if q.get('type', 'Sì/No') == 'Sì/No' else '0'
        elif not ans:  # Vuoti senza Alto gap non penalizzano
            continue
        if (q.get('type', 'Sì/No') == 'Sì/No' and ans == 'No' and 'Alto gap' in q.get('notes', '')) or \
           (q.get('type', 'Scala 1-5') == 'Scala 1-5' and ans.isdigit() and int(ans) < 3):
            gap_info = {
                "Gap": q['question'],
                "Risposta": ans,
                "Azione": extract_action(q.get('notes', '')),
                "Priorità": "Alta" if 'Alto gap' in q.get('notes', '') else "Media",
                "Tempistica": extract_tempistica(q.get('notes', '')),
                "Risk": q.get('risk_flag', 'Low')
            }
            general_gaps.append(gap_info)

    # Calcolo gap per ogni sistema
    system_gaps_list = []
    for sys_idx, sys_res in enumerate(system_answers):
        sys_gaps = []
        all_qs = per_system_qs.copy()
        for cat, sub_qs in extra_qs.items():
            if isinstance(sub_qs, dict):
                if cat == 'settore' and general_responses.get('q1_1') in sub_qs:
                    all_qs.extend(sub_qs[general_responses['q1_1']])
                elif cat == 'ruolo' and sys_res.get('q2_4') in sub_qs:
                    all_qs.extend(sub_qs[sys_res['q2_4']])
                elif cat == 'rischio' and sys_res.get('q2_8') in sub_qs:
                    all_qs.extend(sub_qs[sys_res['q2_8']])  # Aggiunge domande per Proibito
                elif cat == 'caso_uso' and sys_res.get('q2_5') in sub_qs:
                    all_qs.extend(sub_qs[sys_res['q2_5']])
                elif cat == 'esclusioni':
                    all_qs.extend(sub_qs)

        relevant_qs = [q for q in all_qs if 'condition' in q and check_condition(q['condition'], {**general_responses, **sys_res})]
        total_qs = len(per_system_qs) + len(set(q['id'] for q in relevant_qs))
        print(f"Total qs for system {sys_idx}: {total_qs}")

        for q in all_qs:
            if 'condition' in q and not check_condition(q['condition'], {**general_responses, **sys_res}):
                continue
            ans = str(sys_res.get(q['id'], ''))
            if not ans and 'Alto gap' in q.get('notes', ''):  # Solo vuoti critici generano gap
                ans = 'No' if q.get('type', 'Sì/No') == 'Sì/No' else '0'
            elif not ans:
                continue
            if (q.get('type', 'Sì/No') == 'Sì/No' and ans == 'No' and 'Alto gap' in q.get('notes', '')) or \
               (q.get('type', 'Scala 1-5') == 'Scala 1-5' and ans.isdigit() and int(ans) < 3) or \
               (q.get('id') in ['q2_16', 'q2_34'] and sys_res.get('q2_8') == 'Proibito' and ans != 'Sì'):
                gap_info = {
                    "Gap": q['question'],
                    "Risposta": ans,
                    "Azione": extract_action(q.get('notes', '')),
                    "Priorità": "Alta" if 'Alto gap' in q.get('notes', '') or q.get('id') in ['q2_16', 'q2_34'] else "Media",
                    "Tempistica": extract_tempistica(q.get('notes', '')),
                    "Risk": q.get('risk_flag', 'High' if q.get('id') in ['q2_16', 'q2_34'] else 'Low')
                }
                sys_gaps.append(gap_info)
        system_gaps_list.append(sys_gaps)

    general_pct = max(0, 100 - (len(general_gaps) * 10 / len(general_questions) * 100)) if len(general_questions) > 0 else 100
    system_scores = [max(0, 100 - (len(gaps) * 10 / total_qs * 100)) for gaps in system_gaps_list] if total_qs > 0 else [100]

    print(f"General pct: {general_pct}, System scores: {system_scores}")
    return general_pct, general_gaps, system_scores, system_gaps_list

def extract_action(notes):
    if "Azione" in notes:
        return notes.split("Azione")[1].split(".")[0].strip()
    return "Azione non specificata"

def extract_tempistica(notes):
    if "entro" in notes:
        return notes.split("entro")[1].split(".")[0].strip()
    return "Non specificata"

def check_condition(condition, responses):
    """Gestisce condizioni come dizionari, liste annidate e valori booleani."""
    print(f"DEBUG check_condition: condition={condition}, type={type(condition)}")
    if condition is None or condition is True:
        return True
    elif condition is False:
        return False
    elif isinstance(condition, dict):
        result = all(responses.get(k, "") == v for k, v in condition.items() if k in responses)
        print(f"DEBUG dict condition {condition} -> {result}")
        return result
    elif isinstance(condition, list):
        return any(check_condition(c, responses) for c in condition if isinstance(c, (dict, list)))
    else:
        print(f"DEBUG unknown condition type: {type(condition)}")
        return False
