import streamlit as st

def render_question(q, q_id, current_answer):
    tooltip = q.get("notes", "Riferimento normativo non specificato")  # Ripristino: usa notes per tooltip (es. refs da AI Act PDF)
    if q["type"] == "Scala 1-5":
        tooltip = "1 = Nessun impatto, 5 = Impatto significativo"  # Ripristino: override per scala
    if q["type"] == "Sì/No":
        options = ["Sì", "No"]
        index = options.index(current_answer) if current_answer in options else 0
        return st.radio(q["question"], options, index=index, key=q_id, help=tooltip)  # Ripristino: help
    elif q["type"] in ["Multipla", "Drop down"]:  # Ripristino: alias Multipla per drop-down singola
        options = q.get("options", [])
        index = options.index(current_answer) if current_answer in options else 0
        return st.selectbox(q["question"], options, index=index, key=q_id, help=tooltip)
    elif q["type"] == "Scala 1-5":
        val = current_answer if current_answer else 3
        slider_val = st.slider(q["question"], min_value=1, max_value=5, value=val, key=q_id, help=tooltip)
        return min(5, max(1, int(slider_val)))  # Ripristino: clamp per robustezza
    elif q["type"] == "Testo libero" or q["type"] == "Aperta":  # Supporta vecchio "Aperta"
        return st.text_input(q["question"], value=current_answer, key=q_id, help=tooltip)
    elif q["type"] == "Selezione multipla":
        return st.multiselect(q["question"], q["options"], default=current_answer if isinstance(current_answer, list) else [], key=q_id, help=tooltip)
    else:
        return st.text_input(q["question"], value=current_answer, key=q_id, help=tooltip)  # Default con tooltip