import streamlit as st
import pandas as pd  # Importazione di pandas
from questions_config import questions, per_system_qs, extra_qs  # Rimossa multi_options
from utils import render_question, update_state
from gap_calculator import calculate_results  # Importa la funzione

st.title("AI Compliance Analyzer - Web App")

# Inizializzazione stato
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'system_answers' not in st.session_state:
    st.session_state.system_answers = []
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'num_systems' not in st.session_state:
    st.session_state.num_systems = 1
if 'current_system' not in st.session_state:
    st.session_state.current_system = 0

# Sidebar
with st.sidebar:
    st.header("Navigazione")
    if st.button("Reinizializza"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    if st.session_state.get('step', 0) > 0:
        if st.button("Indietro"):
            st.session_state.step -= 1
            if st.session_state.step == 1 and st.session_state.current_system > 0:
                st.session_state.current_system -= 1
            st.rerun()
    st.write(f"Step: {st.session_state.get('step', 0)} / 3")
    st.subheader("Risposte Chiave")
    if 'answers' in st.session_state:
        st.write(f"Settore: {st.session_state.answers.get('1.1 Qual è il settore principale dell\'azienda?', 'Non specificato')}")
        st.write(f"Dimensione: {st.session_state.answers.get('1.2 Qual è la dimensione dell\'azienda?', 'Non specificato')}")
    if 'system_answers' in st.session_state:
        for i, sys in enumerate(st.session_state.system_answers):
            ruolo = sys.get('Quali ruoli ricopre l’organizzazione rispetto al sistema IA?', 'Non specificato')
            st.write(f"Sistema {i+1}: {sys.get('Nome', 'Non specificato')} (Ruolo: {ruolo}, Caso: {sys.get('Caso d\'uso specifico del sistema?', 'Non specificato')}, Rischio: {sys.get('Qual è il livello di rischio?', 'Non specificato')})")

# Step 0: Profilo Aziendale
if st.session_state.step == 0:
    st.header("Profilo Aziendale")
    for q in questions:  # Include tutte le domande
        current_answer = render_question(q, q["question"], st.session_state.answers.get(q["question"]))
        if q["question"] == "1.1 Qual è il settore principale dell'azienda?" and current_answer:
            st.session_state.answers[q["question"]] = current_answer
        st.session_state.answers[q["question"]] = current_answer
    with st.sidebar:
        st.number_input("Numero sistemi IA", min_value=1, value=st.session_state.num_systems, key="num_systems_input", on_change=lambda: st.session_state.update({'num_systems': st.session_state.num_systems_input}) or st.rerun())
        st.session_state.num_systems = st.session_state.num_systems_input
        if st.button("Avanti a Inventory Sistemi"):
            st.session_state.system_answers = [{} for _ in range(st.session_state.num_systems)]
            st.session_state.step = 1
            st.rerun()

# Step 1: Inventory Sistemi
elif st.session_state.step == 1:
    st.header(f"Inventory Sistemi IA ({st.session_state.current_system + 1}/{st.session_state.num_systems})")
    sys_ans = st.session_state.system_answers[st.session_state.current_system]
    sys_ans["Nome"] = st.text_input("Nome Sistema", value=sys_ans.get("Nome", ""), key=f"sys_name_{st.session_state.current_system}")
    sys_ans["Descrizione"] = st.text_area("Descrizione", value=sys_ans.get("Descrizione", ""), key=f"sys_desc_{st.session_state.current_system}")
    sys_ans["Funzione"] = st.text_input("Funzione", value=sys_ans.get("Funzione", ""), key=f"sys_func_{st.session_state.current_system}")
    for q in per_system_qs:
        sys_ans[q["question"]] = render_question(q, f'sys_{st.session_state.current_system}_{q["question"]}', sys_ans.get(q["question"]))
    # Condizionale caso d’uso
    caso_uso = sys_ans.get("Caso d’uso specifico del sistema?")
    settore = st.session_state.answers.get("1.1 Qual è il settore principale dell'azienda?")
    if caso_uso in extra_qs["caso_uso"] and caso_uso != settore:
        st.subheader(f"Domande Extra per Caso d’uso: {caso_uso}")
        for eq in extra_qs["caso_uso"][caso_uso]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_caso_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    # Condizionale ruolo
    ruolo_sistema = sys_ans.get("Quali ruoli ricopre l’organizzazione rispetto al sistema IA?")
    rischio = sys_ans.get("Qual è il livello di rischio?")
    if ruolo_sistema:
        st.subheader(f"Domande Extra per Ruolo: {ruolo_sistema}")
        role_questions = []
        if ruolo_sistema == "Utilizzatore" and rischio == "Alto rischio":
            role_questions.extend([
                {"question": "Hai condotto una FRIA?", "type": "Sì/No", "ref": "AI Act Art. 29a", "notes": "Scoring: Critico se no. Penalità: -30%. Roadmap: Implementa entro ago 2026; Esempio: Audit diritti entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
            ])
        elif ruolo_sistema == "Sviluppatore" and rischio == "Alto rischio":
            role_questions.extend([
                {"question": "Hai condotto assessment rischio (Art. 9)?", "type": "Sì/No", "ref": "AI Act Art. 9", "notes": "Scoring: Critico se no. Penalità: -25%. Roadmap: Esegui entro ago 2026; Esempio: Valutazione rischio entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
            ])
        elif ruolo_sistema == "Importatore":
            role_questions.extend([
                {"question": "Verificato conformity da provider?", "type": "Sì/No", "ref": "AI Act Art. 23", "notes": "Scoring: Alto gap se no. Penalità: -20%. Roadmap: Verifica entro 3 mesi; Esempio: Controlla certificati entro Q1 2025.", "score_weight": 2, "risk_flag": "Medium"},
                {"question": "Hai segnalato non-conformità a autorità?", "type": "Sì/No", "ref": "AI Act Art. 23", "notes": "Scoring: Medio se no. Penalità: -10%. Roadmap: Segnala entro 6 mesi; Esempio: Notifica entro Q3 2025.", "score_weight": 1, "risk_flag": "Low"}
            ])
        elif ruolo_sistema == "Distributore":
            role_questions.extend([
                {"question": "Mantenuti records per traceability?", "type": "Sì/No", "ref": "AI Act Art. 24", "notes": "Scoring: Medio. Penalità: -15%. Roadmap: Archivia entro Q1 2026; Esempio: Crea archivio entro Q4 2025.", "score_weight": 1, "risk_flag": "Low"},
                {"question": "Hai informato su non-conformità?", "type": "Sì/No", "ref": "AI Act Art. 24", "notes": "Scoring: Medio se no. Penalità: -10%. Roadmap: Notifica entro 6 mesi; Esempio: Avvisa entro Q3 2025.", "score_weight": 1, "risk_flag": "Low"}
            ])
        elif ruolo_sistema == "Rappresentante":
            role_questions.extend([
                {"question": "Conservi documentazione per 10 anni?", "type": "Sì/No", "ref": "AI Act Art. 25", "notes": "Scoring: Medio se no. Penalità: -15%. Roadmap: Archivia entro Q1 2026; Esempio: Archivia entro Q4 2025.", "score_weight": 1, "risk_flag": "Low"},
                {"question": "Hai designato un referente UE?", "type": "Sì/No", "ref": "AI Act Art. 25", "notes": "Scoring: Medio se no. Penalità: -10%. Roadmap: Nomina entro 6 mesi; Esempio: Designa entro Q3 2025.", "score_weight": 1, "risk_flag": "Low"}
            ])
        elif ruolo_sistema == "Sviluppatore":
            role_questions.extend([
                {"question": "Hai un sistema di gestione della qualità?", "type": "Sì/No", "ref": "AI Act Art. 17", "notes": "Scoring: Basso se no. Penalità: -10%. Roadmap: Adotta entro Q4 2025; Esempio: Implementa QMS entro Q3 2025.", "score_weight": 1, "risk_flag": "Low"},
                {"question": "Documentazione tecnica completa?", "type": "Sì/No", "ref": "AI Act Art. 11", "notes": "Scoring: Medio. Penalità: -15%. Roadmap: Completa entro Q1 2026; Esempio: Redigi manuale entro Q4 2025.", "score_weight": 1, "risk_flag": "Low"},
                {"question": "Hai condotto assessment rischio (Art. 9)?", "type": "Sì/No", "ref": "AI Act Art. 9", "notes": "Scoring: Critico se no. Penalità: -25%. Roadmap: Esegui entro ago 2026; Esempio: Valutazione rischio entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
            ])
        elif ruolo_sistema == "Utilizzatore":
            role_questions.extend([
                {"question": "Hai policy per monitoraggio post-market?", "type": "Sì/No", "ref": "AI Act Art. 29", "notes": "Scoring: Critico se no. Penalità: -25%. Roadmap: Implementa entro Q4 2025; Esempio: Crea policy entro Q3 2025.", "score_weight": 2, "risk_flag": "Medium"},
                {"question": "Informati lavoratori su uso IA?", "type": "Sì/No", "ref": "AI Act Art. 26; Legge 132/2025", "notes": "Scoring: Alto gap se no. Penalità: -20%. Roadmap: Informativa entro 6 mesi (Obbligo Legge 132/2025); Esempio: Workshop entro Q2 2025.", "score_weight": 2, "risk_flag": "Medium"}
            ])
        elif ruolo_sistema == "Altro":
            role_questions.extend([
                {"question": "Specifica il ruolo aggiuntivo", "type": "Aperta", "ref": "AI Act Art. 3", "notes": "Scoring: Specifica per conformità. Roadmap: Definisci entro 3 mesi; Esempio: Descrivi ruolo entro Q1 2025.", "score_weight": 1, "risk_flag": "N/A"}
            ])
        for eq in role_questions:
            sys_ans[eq["question"]] = render_question(eq, f'sys_ruolo_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    # Condizionale livello di rischio
    rischio = sys_ans.get("Qual è il livello di rischio?")
    if rischio == "Proibito":
        st.subheader("Domande Extra per Rischio Proibito")
        for eq in [{"question": "Hai ottenuto autorizzazione specifica?", "type": "Sì/No", "ref": "AI Act Art. 5", "notes": "Scoring: Critico se no. Penalità: -40%. Roadmap: Ottieni entro feb 2025; Esempio: Richiedi deroghe entro Q4 2024.", "score_weight": 3, "risk_flag": "High"}]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_proibito_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    elif rischio == "Alto rischio" and ruolo_sistema == "Utilizzatore":
        st.subheader("Domande Extra per Alto Rischio (Utilizzatore)")
        for eq in [
            {"question": "Hai condotto una FRIA?", "type": "Sì/No", "ref": "AI Act Art. 29a", "notes": "Scoring: Critico se no. Penalità: -30%. Roadmap: Implementa entro ago 2026; Esempio: Audit diritti entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
        ]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_alto_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    elif rischio == "Alto rischio" and ruolo_sistema == "Sviluppatore":
        st.subheader("Domande Extra per Alto Rischio (Sviluppatore)")
        for eq in [
            {"question": "Hai condotto assessment rischio (Art. 9)?", "type": "Sì/No", "ref": "AI Act Art. 9", "notes": "Scoring: Critico se no. Penalità: -25%. Roadmap: Esegui entro ago 2026; Esempio: Valutazione rischio entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
        ]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_alto_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    elif rischio in ["Rischio limitato", "Minimo"]:
        st.subheader("Domande Extra per Rischio Limitato/Minimo")
        for eq in [
            {"question": "Usa deepfake o emotion recognition?", "type": "Sì/No", "ref": "AI Act Art. 52", "notes": "Scoring: Medio se sì. Penalità: -10%. Roadmap: Implementa disclosure entro feb 2025; Esempio: Aggiungi etichetta entro Q1 2025.", "score_weight": 1, "risk_flag": "Low"},
            {"question": "Hai implementato disclosure su IA generativa?", "type": "Sì/No", "ref": "AI Act Art. 52", "notes": "Scoring: Medio se no. Penalità: -10%. Roadmap: Aggiungi entro 3 mesi; Esempio: Notifica utenti entro Q1 2025.", "score_weight": 1, "risk_flag": "Low"}
        ]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_minlim_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    # Condizionale settoriale critico
    settore = st.session_state.answers.get("1.1 Qual è il settore principale dell'azienda?")
    if settore in ["Sanità", "Forze dell'ordine", "Immigrazione", "Infrastrutture critiche", "Componenti di sicurezza", "Giustizia"]:
        st.subheader("Domande Extra per Settore Critico")
        for eq in [
            {"question": "Hai autorizzazioni per sistemi critici?", "type": "Sì/No", "ref": "AI Act Art. 6", "notes": "Scoring: Alto gap se no. Penalità: -20%. Roadmap: Richiedi entro 3 mesi; Esempio: Contatta autorità entro Q1 2025.", "score_weight": 2, "risk_flag": "Medium"},
            {"question": "Rischi sanzioni (fino 4% fatturato)?", "type": "Sì/No", "ref": "AI Act Art. 71", "notes": "Scoring: Critico se sì. Penalità: -30%. Roadmap: Mitiga entro 6 mesi; Esempio: Audit legale entro Q2 2025.", "score_weight": 3, "risk_flag": "High"}
        ]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_critico_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    # Snellimento per PMI
    dimensione = st.session_state.answers.get("1.2 Qual è la dimensione dell'azienda?")
    if dimensione in ["Micro (<10 dipendenti)", "Piccola (10-50)", "Media (50-250)"]:
        st.subheader("Domande Extra per PMI")
        for eq in [
            {"question": "Hai accesso a sandbox UE?", "type": "Sì/No", "ref": "AI Act Art. 69", "notes": "Scoring: Basso se no. Penalità: -5%. Roadmap: Richiedi entro Q1 2026; Esempio: Iscriviti entro Q4 2025.", "score_weight": 1, "risk_flag": "Low"},
            {"question": "Riduci sanzioni (2% fatturato) applicata?", "type": "Sì/No", "ref": "AI Act Art. 69", "notes": "Scoring: Medio se no. Penalità: -10%. Roadmap: Verifica entro 6 mesi; Esempio: Richiedi esenzione entro Q2 2025.", "score_weight": 1, "risk_flag": "Low"}
        ]:
            sys_ans[eq["question"]] = render_question(eq, f'sys_pmi_{st.session_state.current_system}_{eq["question"]}', sys_ans.get(eq["question"]))
    with st.sidebar:
        if st.button("Avanti Sistema"):
            st.session_state.current_system += 1
            if st.session_state.current_system >= st.session_state.num_systems:
                st.session_state.step = 2
            st.rerun()
        if st.button("Aggiungi Sistema"):
            st.session_state.num_systems += 1
            st.session_state.system_answers.append({})
            st.rerun()

# Step 2: Extra basati su settore
elif st.session_state.step == 2:
    st.header("Domande Extra Condizionali")
    settore = st.session_state.answers.get("1.1 Qual è il settore principale dell'azienda?")
    if settore and settore in extra_qs["settore"]:
        st.subheader(f"Extra per Settore: {settore}")
        for eq in extra_qs["settore"][settore]:
            st.session_state.answers[eq["question"]] = render_question(eq, f'extra_sett_{eq["question"]}', st.session_state.answers.get(eq["question"]))
    else:
        st.subheader("Extra per Settore Non Specificato")
        for eq in extra_qs["settore"]["Altro"]:
            st.session_state.answers[eq["question"]] = render_question(eq, f'extra_sett_{eq["question"]}', st.session_state.answers.get(eq["question"]))
    with st.sidebar:
        if st.button("Calcola Risultati"):
            st.session_state.step = 3
            st.write("Debug: Passaggio a Step 3 avviato")  # Debug per verificare il clic
            st.rerun()

# Step 3: Risultati
elif st.session_state.step == 3:
    general_pct, general_gaps, system_scores, system_gaps = calculate_results(st.session_state)  # Passa st.session_state
    st.write(f"Debug: General Gaps: {len(general_gaps)}, System Gaps: {len(system_gaps)}")  # Debug sui gap
    st.write(f"Totale Conformità Generale: {general_pct:.2f}% (Rischio: {max(g['Risk'] for g in general_gaps) if general_gaps else 'Basso'})")
    for i, sys_pct in enumerate(system_scores):
        st.write(f"Sistema {i+1}: {sys_pct:.2f}% (Rischio: {max(g['Risk'] for g in system_gaps[i]['Gaps']) if system_gaps and system_gaps[i]['Gaps'] else 'Basso'})")
    avg_sys = sum(system_scores) / len(system_scores) if system_scores else 0
    st.write(f"Media Sistemi: {avg_sys:.2f}%")
    st.header("Roadmap di Adeguamento")
    all_gaps = general_gaps + [gap for sys in system_gaps for gap in sys["Gaps"]]
    st.write(f"Debug: Numero totale di gap: {len(all_gaps)}")  # Debug per verificare i gap
    if all_gaps:
        df = pd.DataFrame(all_gaps)
        st.write("Debug: Tabella dei gap pronta")  # Debug per la tabella
        st.table(df[["Gap", "Risposta", "Azione", "Priorità", "Tempistica", "Risk"]])
    else:
        st.warning("Nessun gap rilevato. Prova a rispondere 'No' a domande con 'Alto gap' o scale < 3.")
    # Debug con riepilogo di tutte le domande e risposte
    st.write("### Riepilogo Domande e Risposte")
    for q in questions:  # Include tutte le domande di Step 0
        ans = st.session_state.answers.get(q["question"], "Non risposto")
        st.write(f"Domanda: {q['question']} - Risposta: {ans}")
    for i, sys_ans in enumerate(st.session_state.system_answers):
        st.write(f"### Sistema {i+1} - Risposte")
        # Include tutte le domande definite in per_system_qs
        for q in per_system_qs:
            ans = sys_ans.get(q["question"], "Non risposto")
            # Determina il tipo in base al contenuto
            q_type = q.get("type", "Sì/No" if isinstance(ans, str) and ans in ["Sì", "No"] else "Scala 1-5" if isinstance(ans, (int, float)) else "Aperta")
            st.write(f"Domanda: {q['question']} - Risposta: {ans} (Tipo: {q_type})")
        # Include domande extra (es. Nome, Descrizione, Funzione)
        for k, v in sys_ans.items():
            if k not in [q["question"] for q in per_system_qs]:
                q_type = "Aperta" if not v or (isinstance(v, str) and not v.strip()) else "Testo"
                st.write(f"Domanda: {k} - Risposta: {v} (Tipo: {q_type})")