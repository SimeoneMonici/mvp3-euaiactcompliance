import json
from typing import Dict, List

def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def check_condition(condition: Dict, responses: Dict) -> bool:
    if not condition:
        return True
    return all(responses.get(k) == v for k, v in condition.items())

def flatten_extra_qs(extra_qs: Dict, responses: Dict) -> List[Dict]:
    flat = []
    for cat in extra_qs.values():
        if isinstance(cat, list):
            for q in cat:
                if isinstance(q, dict) and check_condition(q.get("condition", {}), responses):
                    flat.append(q)
    return flat

def calculate_gaps(questions_data: Dict, responses: Dict) -> Dict:
    gaps = {}
    all_qs = (
        questions_data["questions"] +
        questions_data["per_system_qs"] +
        flatten_extra_qs(questions_data["extra_qs"], responses)
    )
    for q in all_qs:
        q_id = q["id"]
        if q_id in responses:
            resp = responses[q_id]
            risk = q.get("risk_flag", "N/A")
            if risk in ["Medium", "High", "Critical"]:
                if q["type"] == "Sì/No" and resp == "No":
                    gaps[q_id] = {"question": q["question"], "response": resp, "risk_flag": risk}
                elif q["type"] == "Scala 1-5" and isinstance(resp, (int, float)) and resp < 3:
                    gaps[q_id] = {"question": q["question"], "response": resp, "risk_flag": risk}
    return gaps


def calculate_conformity_score(questions_data: Dict, responses: Dict, gaps: Dict) -> float:
    total = 0
    compliant = 0
    all_qs = (
        questions_data["questions"] +
        questions_data["per_system_qs"] +
        flatten_extra_qs(questions_data["extra_qs"], responses)
    )
    for q in all_qs:
        q_id = q["id"]
        if q_id in responses:
            weight = q.get("score_weight", 1)
            total += weight
            if q_id not in gaps:
                compliant += weight
    return (compliant / total * 100) if total > 0 else 100.0

def calculate_results(session_state: Dict) -> tuple:
    data = load_questions()
    answers = session_state.get('answers', {})
    system_answers = session_state.get('system_answers', [{}])
    all_resp = {**answers, **{k: v for d in system_answers for k, v in d.items()}}
    gaps = calculate_gaps(data, all_resp)
    general_score = calculate_conformity_score(data, answers, {k: v for k, v in gaps.items() if k.startswith('q1_')})
    system_scores = []
    system_gaps_list = []
    for sys in system_answers:
        sys_resp = {**answers, **sys}
        sys_gaps = calculate_gaps(data, sys_resp)
        score = calculate_conformity_score(data, sys_resp, sys_gaps)
        system_scores.append(score)
        system_gaps_list.append([{
            "Gap": f"{gid}: {g['question']}",
            "Risposta": g["response"],
            "Risk": g["risk_flag"]
        } for gid, g in sys_gaps.items() if not gid.startswith('q1_')])
    return general_score, gaps, system_scores, system_gaps_list