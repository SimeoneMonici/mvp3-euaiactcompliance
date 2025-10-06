from questions_config import questions, per_system_qs, extra_qs

def calculate_results(session_state):
    # Calcolo scoring generale
    general_score = 100  # Base 100%
    count = 0
    general_gaps = []
    for q in questions:
        ans = None
        if q["question"] in session_state.answers:
            ans = session_state.answers.get(q["question"])
        if ans is not None:
            weight = q.get("score_weight", 1)
            count += weight
            if q["type"] == "Sì/No":
                if ans == "No" and ("Critico" in q["notes"] or "Alto gap" in q["notes"]):
                    try:
                        penalita = float(q["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in q["notes"] else 10
                        general_score -= penalita
                        azione = q["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in q["notes"] else "Azione non definita"
                    except IndexError:
                        penalita = 10
                        azione = "Azione default"
                    prio = "Alta" if "Critico" in q["notes"] else "Media"
                    tempistica = "Immediata (Legge 132/2025)" if "Legge 132/2025" in q["ref"] else "Entro 3 mesi"
                    general_gaps.append({"Gap": q["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": q["risk_flag"]})
            elif q["type"] == "Scala 1-5":
                if int(ans) < 3 and ("Alto gap" in q["notes"] or "Critico" in q["notes"]):
                    try:
                        penalita = float(q["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in q["notes"] else 10
                        general_score -= penalita
                        azione = q["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in q["notes"] else "Azione non definita"
                    except IndexError:
                        penalita = 10
                        azione = "Azione default"
                    prio = "Alta"
                    tempistica = "Entro 6 mesi"
                    general_gaps.append({"Gap": q["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": q["risk_flag"]})
            elif q["type"] == "Multipla":
                if ans and "Altro" in ans:
                    general_score -= 10  # Penalità generica
            elif q["type"] == "Aperta":
                if not ans.strip():
                    general_score -= 5  # Penalità minima
    general_pct = max(0, min(100, general_score)) if count else 0

    # Scoring per sistemi
    system_scores = []
    system_gaps = []
    for i, sys_ans in enumerate(session_state.system_answers):
        sys_score = 100  # Base 100%
        sys_count = 0
        sys_gaps_local = []
        rischio = sys_ans.get("Qual è il livello di rischio?")
        ruolo_sistema = sys_ans.get("Quali ruoli ricopre l’organizzazione rispetto al sistema IA?")
        dimensione = None
        if "1.2 Qual è la dimensione dell'azienda?" in session_state.answers:
            dimensione = session_state.answers.get("1.2 Qual è la dimensione dell'azienda?")
        risk_multiplier = 4 if rischio == "Proibito" else 2 if rischio == "Alto rischio" else 1
        for q in per_system_qs:
            ans = sys_ans.get(q["question"])
            if ans:
                weight = q.get("score_weight", 1)
                sys_count += weight
                if q["type"] == "Sì/No":
                    if ans == "No" and ("Critico" in q.get("notes", "") or "Alto gap" in q.get("notes", "")):
                        try:
                            penalita = float(q.get("notes", "").split("Penalità: -")[1].split("%")[0]) if "Penalità:" in q.get("notes", "") else 10
                            azione = q.get("notes", "").split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in q.get("notes", "") else "Azione non definita"
                        except IndexError:
                            penalita = 10
                            azione = "Azione default"
                        penalita_adjusted = penalita * risk_multiplier * (1.5 if ruolo_sistema == "Utilizzatore" and rischio == "Alto rischio" else 1)
                        if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                            penalita_adjusted /= 2
                        sys_score -= min(penalita_adjusted, sys_score)
                        prio = "Alta"
                        tempistica = "Entro 3 mesi"
                        sys_gaps_local.append({"Gap": q["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": q.get("risk_flag", "Low")})
                elif q["type"] == "Scala 1-5":
                    if int(ans) < 3 and ("Alto gap" in q.get("notes", "") or "Critico" in q.get("notes", "")):
                        try:
                            penalita = float(q.get("notes", "").split("Penalità: -")[1].split("%")[0]) if "Penalità:" in q.get("notes", "") else 10
                            azione = q.get("notes", "").split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in q.get("notes", "") else "Azione non definita"
                        except IndexError:
                            penalita = 10
                            azione = "Azione default"
                        penalita_adjusted = penalita * risk_multiplier
                        if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                            penalita_adjusted /= 2
                        sys_score -= min(penalita_adjusted, sys_score)
                        prio = "Alta"
                        tempistica = "Entro 6 mesi"
                        sys_gaps_local.append({"Gap": q["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": q.get("risk_flag", "Low")})
                elif q["type"] == "Multipla":
                    if q["question"] == "Qual è il livello di rischio?":
                        score = weight * 5 if ans == "Minimo" else weight * 3 if ans == "Rischio limitato" else weight * 1
                        sys_score += score
                elif q["type"] == "Aperta":
                    if not ans.strip():
                        sys_score -= 5
        # Extra caso d’uso
        caso_uso = sys_ans.get("Caso d’uso specifico del sistema?")
        if caso_uso in extra_qs["caso_uso"]:
            for eq in extra_qs["caso_uso"][caso_uso]:
                ans = sys_ans.get(eq["question"])
                if ans is not None:
                    weight = eq.get("score_weight", 1)
                    sys_count += weight
                    if eq["type"] == "Sì/No":
                        score = weight * 10 if ans == "Sì" else 0
                        if ans == "No":
                            try:
                                penalita = float(eq["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in eq["notes"] else 10
                                azione = eq["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in eq["notes"] else "Azione non definita"
                            except IndexError:
                                penalita = 10
                                azione = "Azione default"
                            penalita_adjusted = penalita * risk_multiplier * (1.5 if ruolo_sistema == "Utilizzatore" and rischio == "Alto rischio" else 1)
                            if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                                penalita_adjusted /= 2
                            sys_score -= min(penalita_adjusted, sys_score)
                            prio = "Alta"
                            tempistica = "Immediata (Legge 132/2025)" if "Legge 132/2025" in eq["ref"] else "Entro 3 mesi"
                            sys_gaps_local.append({"Gap": eq["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": eq["risk_flag"]})
                    elif eq["type"] == "Scala 1-5":
                        score = weight * int(ans) * 2
                        if int(ans) < 3 or (int(ans) > 2 and "Critico" in eq["notes"]):
                            try:
                                penalita = float(eq["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in eq["notes"] else 10
                                azione = eq["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in eq["notes"] else "Azione non definita"
                            except IndexError:
                                penalita = 10
                                azione = "Azione default"
                            penalita_adjusted = penalita * risk_multiplier
                            if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                                penalita_adjusted /= 2
                            sys_score -= min(penalita_adjusted, sys_score)
                            prio = "Alta"
                            tempistica = "Entro 6 mesi"
                            sys_gaps_local.append({"Gap": eq["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": eq["risk_flag"]})
                        sys_score += score
        # Extra ruolo
        if ruolo_sistema in extra_qs["ruolo"]:
            for eq in extra_qs["ruolo"][ruolo_sistema]:
                ans = sys_ans.get(eq["question"])
                if ans is not None:
                    weight = eq.get("score_weight", 1)
                    sys_count += weight
                    if eq["type"] == "Sì/No":
                        score = weight * 10 if ans == "Sì" else 0
                        if ans == "No":
                            try:
                                penalita = float(eq["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in eq["notes"] else 10
                                azione = eq["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in eq["notes"] else "Azione non definita"
                            except IndexError:
                                penalita = 10
                                azione = "Azione default"
                            penalita_adjusted = penalita * risk_multiplier
                            if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                                penalita_adjusted /= 2
                            sys_score -= min(penalita_adjusted, sys_score)
                            prio = "Alta"
                            tempistica = "Entro 3 mesi"
                            sys_gaps_local.append({"Gap": eq["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": eq["risk_flag"]})
                    elif eq["type"] == "Scala 1-5":
                        score = weight * int(ans) * 2
                        if int(ans) < 3:
                            try:
                                penalita = float(eq["notes"].split("Penalità: -")[1].split("%")[0]) if "Penalità:" in eq["notes"] else 10
                                azione = eq["notes"].split("Roadmap: ")[1].split(";")[0] if "Roadmap:" in eq["notes"] else "Azione non definita"
                            except IndexError:
                                penalita = 10
                                azione = "Azione default"
                            penalita_adjusted = penalita * risk_multiplier
                            if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
                                penalita_adjusted /= 2
                            sys_score -= min(penalita_adjusted, sys_score)
                            prio = "Alta"
                            tempistica = "Entro 6 mesi"
                            sys_gaps_local.append({"Gap": eq["question"], "Risposta": ans, "Azione": azione, "Priorità": prio, "Tempistica": tempistica, "Risk": eq["risk_flag"]})
                        sys_score += score
        sys_pct = max(0, min(100, sys_score)) if sys_count else 0
        system_scores.append(sys_pct)
        if sys_gaps_local:
            system_gaps.append({"Sistema": i+1, "Gaps": sys_gaps_local})
    return general_pct, general_gaps, system_scores, system_gaps