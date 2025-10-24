import streamlit as st
import pandas as pd
import json
from questions_config import questions, per_system_qs, extra_qs
from utils import render_question
from gap_calculator import calculate_results, check_condition
from io import BytesIO
import csv

st.set_page_config(page_title="AI Compliance v15.8", layout="wide")
st.title("AI Compliance Analyzer - **v15.8**")

# --- INIZIALIZZAZIONE ---
if 'answers' not in st.session_state:
    st.session_state.answers = {q["id"]: "" for q in questions}
if 'system_answers' not in st.session_state:
    st.session_state.system_answers = [{} for _ in range(1)]
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'num_systems' not in st.session_state:
    st.session_state.num_systems = 1
if 'current_system' not in st.session_state:
    st.session_state.current_system = 0

# --- SIDEBAR ---
with st.sidebar:
    st.header("**Navigazione v15.8**")
    if st.button("Reinizializza"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    if st.session_state.step > 0 and st.button("Indietro"):
        st.session_state.step -= 1
        st.rerun()
    st.write(f"**Step:** {st.session_state.step}/3")

    # SCELTE CHIAVE
    sys = st.session_state.system_answers[st.session_state.current_system]
    st.subheader("**Scelte Chiave**")
    st.write(f"**Settore:** {st.session_state.answers.get('q1_1', '')}")
    st.write(f"**Ruolo:** {sys.get('q2_4', '')}")
    st.write(f"**Caso d'uso:** {sys.get('q2_5', '')}")
    st.write(f"**Rischio:** {sys.get('q2_8', '')}")

    # ELENCO SISTEMI
    st.subheader("**Sistemi IA**")
    for i, s in enumerate(st.session_state.system_answers):
        name = s.get("q2_1", s.get("q2_4", f"Sistema {i+1}"))
        st.write(f"**{name}**")

# --- CARICA RECOMMENDATIONS ---
def load_recommendations(role):
    role_map = {
        "Sviluppatore": "recommendations_sviluppatore.json",
        "Utilizzatore": "recommendations_user.json",
        "Importatore": "recommendations_importer.json",
        "Distributore": "recommendations_distributore.json"
    }
    path = role_map.get(role, "recommendations_general.json")
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {r["question_id"]: r for r in data["recommendations"]}
    except:
        return {}

# --- STEP 0: PROFILO AZIENDALE ---
if st.session_state.step == 0:
    st.header("**Step 0: Profilo Aziendale**")
    with st.expander("1. Governance Aziendale", expanded=True):
        for q in questions:
            st.session_state.answers[q["id"]] = render_question(q, q["id"], st.session_state.answers.get(q["id"], ""))
            if q.get("ref"):
                st.caption(f"**Riferimento:** {q['ref']}")
    if st.button("Step 1"):
        st.session_state.step = 1
        st.rerun()

# --- STEP 1: INVENTORY BASE ---
elif st.session_state.step == 1:
    st.header("**Step 1: Inventory Base**")
    num = st.number_input("Numero Sistemi IA:", min_value=1, max_value=10, value=st.session_state.num_systems)
    if num != st.session_state.num_systems:
        diff = num - len(st.session_state.system_answers)
        if diff > 0:
            st.session_state.system_answers.extend([{} for _ in range(diff)])
        else:
            st.session_state.system_answers = st.session_state.system_answers[:num]
        st.session_state.num_systems = num
        st.rerun()

    all_saved = True
    for i in range(num):
        with st.expander(f"Sistema {i+1}", expanded=i == st.session_state.current_system):
            sys = st.session_state.system_answers[i]
            with st.form(f"base_{i}"):
                for q in per_system_qs[:6]:
                    sys[q["id"]] = render_question(q, f"{q['id']}_{i}", sys.get(q["id"], ""))
                    if q.get("ref"):
                        st.caption(f"**Riferimento:** {q['ref']}")
                if st.form_submit_button("Salva Sistema"):
                    st.session_state.current_system = i
                    st.rerun()
            if not all(sys.get(q["id"]) for q in per_system_qs[:6]):
                all_saved = False
                st.warning(f"Sistema {i+1}: Compila tutte le domande base")
    if all_saved and st.button("Vai a Step 2"):
        st.session_state.step = 2
        st.rerun()

# --- STEP 2: DOMANDE DETTAGLIATE PER TUTTI I SISTEMI ---
elif st.session_state.step == 2:
    st.header("**Step 2: Domande Dettagliate**")
    all_saved = True
    for i in range(st.session_state.num_systems):
        with st.expander(f"Sistema {i+1} - {st.session_state.system_answers[i].get('q2_1', 'Senza nome')}", expanded=i == st.session_state.current_system):
            sys = st.session_state.system_answers[i]
            role = sys.get("q2_4", "")
            with st.form(f"detailed_{i}"):
                groups = {
                    "Sviluppatore": [], "Utilizzatore": [], "High-Risk": [],
                    "GPAI": [], "Generativa": [], "Generali": []
                }
                supply_chain_qs = []
                for q in per_system_qs[6:]:
                    cond = q.get("condition")
                    show = cond is None or all(
                        sys.get(k, "") == v if isinstance(v, str) else sys.get(k, "") in v
                        for k, v in cond.items()
                    )
                    if show:
                        if role in ["Importatore", "Distributore"]:
                            supply_chain_qs.append(q)
                        elif cond and "q2_4" in cond:
                            r = cond["q2_4"]
                            if isinstance(r, list): r = r[0]
                            if r == role:
                                groups[r].append(q)
                        elif cond and "q2_8" in cond and "Alto" in cond["q2_8"]:
                            groups["High-Risk"].append(q)
                        elif cond and "q2_14" in cond:
                            groups["GPAI"].append(q)
                        elif cond and "q2_37" in cond:
                            groups["Generativa"].append(q)
                        else:
                            groups["Generali"].append(q)

                if role in ["Importatore", "Distributore"] and supply_chain_qs:
                    with st.expander("**Obblighi Supply Chain**", expanded=True):
                        for q in supply_chain_qs:
                            sys[q["id"]] = render_question(q, f"{q['id']}_{i}", sys.get(q["id"], ""))
                            if q.get("ref"):
                                st.caption(f"**Riferimento:** {q['ref']}")
                for group_name, qs in groups.items():
                    if qs:
                        with st.expander(f"**{group_name}**", expanded=True):
                            for q in qs:
                                sys[q["id"]] = render_question(q, f"{q['id']}_{i}", sys.get(q["id"], ""))
                                if q.get("ref"):
                                    st.caption(f"**Riferimento:** {q['ref']}")
                for cat, sub_qs in extra_qs.items():
                    if isinstance(sub_qs, list):
                        cat_show = any(
                            q.get("condition") is None or all(
                                sys.get(k, "") == v if isinstance(v, str) else sys.get(k, "") in v
                                for k, v in q.get("condition", {}).items()
                            )
                            for q in sub_qs
                        )
                        if cat_show:
                            with st.expander(f"**Extra: {cat.upper()}**", expanded=True):
                                for q in sub_qs:
                                    cond = q.get("condition", {})
                                    q_show = cond is None or all(
                                        sys.get(k, "") == v if isinstance(v, str) else sys.get(k, "") in v
                                        for k, v in cond.items()
                                    )
                                    if q_show:
                                        sys[q["id"]] = render_question(q, f"{q['id']}_{i}", sys.get(q["id"], ""))
                                        if q.get("ref"):
                                            st.caption(f"**Riferimento:** {q['ref']}")
                if st.form_submit_button("Salva Sistema"):
                    st.session_state.current_system = i
                    st.rerun()
            if not all(sys.get(q["id"]) for q in per_system_qs[6:] if q.get("condition") is None or all(sys.get(k, "") == v if isinstance(v, str) else sys.get(k, "") in v for k, v in q.get("condition", {}).items())):
                all_saved = False
                st.warning(f"Sistema {i+1}: Compila tutte le domande dettagliate")
    if all_saved and st.button("Calcola Risultati"):
        general_score, gaps, system_scores, system_gaps_list = calculate_results(st.session_state)
        st.session_state.results = (general_score, gaps, system_scores, system_gaps_list)
        st.session_state.step = 3
        st.rerun()

# --- STEP 3: RISULTATI + ROADMAP PER SISTEMA ---
elif st.session_state.step == 3:
    st.header("**Step 3: Risultati v15.8**")
    general_score, gaps, system_scores, system_gaps_list = st.session_state.results
    st.metric("**Conformità Generale**", f"{general_score:.1f}%")
    for i, pct in enumerate(system_scores):
        name = st.session_state.system_answers[i].get("q2_1", f"Sistema {i+1}")
        st.metric(f"**{name}**", f"{pct:.1f}%")
    st.subheader("Gap Analysis")
    gap_list = []
    for gid, g in gaps.items():
        if gid.startswith('q1_'):
            gap_list.append({"Sistema": "Generale", "Gap": f"{gid}: {g['question']}", "Risposta": g["response"], "Risk": g["risk_flag"]})
    for sys_gaps in system_gaps_list:
        for gap in sys_gaps["Gaps"]:
            gap["Sistema"] = sys_gaps["system_name"]
            gap_list.append(gap)
    if gap_list:
        df = pd.DataFrame(gap_list)
        st.dataframe(df.style.set_properties(**{'text-align': 'left', 'font-size': '14px'}).set_table_styles([
            {'selector': 'th.col0', 'props': [('width', '400px'), ('font-size', '14px')]},
            {'selector': 'td.col0', 'props': [('font-size', '14px')]}
        ]), use_container_width=True)
    else:
        st.success("Nessun gap critico!")
    st.subheader("Roadmap")
    roadmap = []
    for gap in gap_list:
        if isinstance(gap, dict) and "Gap" in gap:
            q_id = gap["Gap"].split(":")[0].strip()
            role = next((s["q2_4"] for s in st.session_state.system_answers if s.get("q2_1", "").lower() in gap["Sistema"].lower()), "")
            recs = load_recommendations(role)
            r = recs.get(q_id)
            if r:
                cond = r.get("condition", "")
                if "risposta = 'No'" in cond and gap["Risposta"] == "No":
                    roadmap.append({
                        "Sistema": gap["Sistema"],
                        "Gap": gap["Gap"],
                        "Azione": r["recommendation"],
                        "Priorità": r["priority"],
                        "Tempistica": r["timeline"],
                        "Riferimento": r.get("reference", ""),
                        "Benefici": r.get("benefits", "")
                    })
                elif "risposta < 3" in cond and gap["Risposta"] < 3:
                    roadmap.append({
                        "Sistema": gap["Sistema"],
                        "Gap": gap["Gap"],
                        "Azione": r["recommendation"],
                        "Priorità": r["priority"],
                        "Tempistica": r["timeline"],
                        "Riferimento": r.get("reference", ""),
                        "Benefici": r.get("benefits", "")
                    })
    if roadmap:
        st.dataframe(roadmap)
    else:
        st.success("Nessuna azione richiesta!")
    # --- DOWNLOAD ---
    from results import generate_excel, generate_roadmap_csv
    excel = generate_excel()
    csv_data = generate_roadmap_csv()
    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Excel Completo", excel, "AI_Compliance_v15.8.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    with col2:
        st.download_button("Roadmap CSV", csv_data, "Roadmap_v15.8.csv", "text/csv")
    # --- DEBUG ---
    with st.expander("**DEBUG: Risposte Complete**", expanded=False):
        st.write("**Generali:**", st.session_state.answers)
        for i, sys in enumerate(st.session_state.system_answers):
            st.write(f"**Sistema {i+1}:**", sys)
    if st.button("Nuova Analisi"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()