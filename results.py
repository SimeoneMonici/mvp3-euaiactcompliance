import streamlit as st
import pandas as pd
import openpyxl
from openpyxl.styles import Font
from io import BytesIO
from questions_config import questions, per_system_qs, extra_qs
from gap_calculator import calculate_results  # Importa la funzione dal nuovo modulo

def generate_excel(general_gaps, system_scores, system_gaps):
    wb = openpyxl.Workbook()
    ws_dom = wb.active
    ws_dom.title = "Domande"
    headers = ["Sezione", "Domanda", "Tipo", "Riferimento Normativo", "Note", "Score Weight", "Risk Flag"]
    for col, header in enumerate(headers, 1):
        ws_dom.cell(1, col, header).font = Font(bold=True)
    row = 2
    for q in questions:
        ws_dom.cell(row, 1, q["section"])
        ws_dom.cell(row, 2, q["question"])
        ws_dom.cell(row, 3, q.get("type"))
        ws_dom.cell(row, 4, q["ref"])
        ws_dom.cell(row, 5, q["notes"])
        ws_dom.cell(row, 6, q.get("score_weight", 1))
        ws_dom.cell(row, 7, q.get("risk_flag", "N/A"))
        row += 1
    for cat, sub_qs in extra_qs.items():
        if isinstance(sub_qs, dict):
            for subcat, qs in sub_qs.items():
                ws_dom.cell(row, 1, f"Extra {cat} - {subcat}")
                row += 1
                for q in qs:
                    ws_dom.cell(row, 2, q["question"])
                    ws_dom.cell(row, 3, q.get("type"))
                    ws_dom.cell(row, 4, q.get("ref", ""))
                    ws_dom.cell(row, 5, q.get("notes", ""))
                    ws_dom.cell(row, 6, q.get("score_weight", 1))
                    ws_dom.cell(row, 7, q.get("risk_flag", "N/A"))
                    row += 1
    ws_resp = wb.create_sheet("Risposte")
    ws_resp.cell(1, 1, "Domanda")
    ws_resp.cell(1, 2, "Risposta")
    for i, q in enumerate(questions, 2):
        ws_resp.cell(i, 1, q["question"])
        ws_resp.cell(i, 2, str(st.session_state.answers.get(q["question"], "")))
    ws_inv = wb.create_sheet("Inventory_Sistemi_IA")
    inv_headers = ["ID Sistema", "Nome", "Descrizione", "Funzione"] + [q["question"] for q in per_system_qs] + ["Punteggio (%)"]
    for col, header in enumerate(inv_headers, 1):
        ws_inv.cell(1, col, header)
    for row, sys_ans in enumerate(st.session_state.system_answers, 2):
        ws_inv.cell(row, 1, row - 1)
        ws_inv.cell(row, 2, sys_ans.get("Nome", ""))
        ws_inv.cell(row, 3, sys_ans.get("Descrizione", ""))
        ws_inv.cell(row, 4, sys_ans.get("Funzione", ""))
        col_idx = 5
        for q in per_system_qs:
            ws_inv.cell(row, col_idx, str(sys_ans.get(q["question"], "")))
            col_idx += 1
        ws_inv.cell(row, col_idx, system_scores[row-2] if row-2 < len(system_scores) else 0)
    ws_road = wb.create_sheet("Roadmap")
    road_headers = ["Gap", "Risposta", "Azione", "Priorità", "Tempistica", "Risk"]
    for col, header in enumerate(road_headers, 1):
        ws_road.cell(1, col, header)
    row = 2
    for gap in general_gaps + [gap for sys in system_gaps for gap in sys["Gaps"]]:
        ws_road.cell(row, 1, gap["Gap"])
        ws_road.cell(row, 2, gap["Risposta"])
        ws_road.cell(row, 3, gap["Azione"])
        ws_road.cell(row, 4, gap["Priorità"])
        ws_road.cell(row, 5, gap["Tempistica"])
        ws_road.cell(row, 6, gap["Risk"])
        row += 1
    output = BytesIO()
    wb.save(output)
    return output.getvalue()

def display_results():
    st.write("Debug: Entrato in Step 3")  # Debug iniziale Step 3
    try:
        general_pct, general_gaps, system_scores, system_gaps = calculate_results()
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
    except Exception as e:
        st.error(f"Errore durante il calcolo: {str(e)}")  # Cattura eventuali errori

if __name__ == "__main__":
    if st.session_state.get("step") == 3:
        display_results()