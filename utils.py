import streamlit as st  # Importazione di streamlit
from questions_config import questions, per_system_qs, extra_qs

def render_question(question_data, key, default_value=None):
    """
    Renderizza un input Streamlit in base al tipo di domanda.
    """
    question = question_data["question"]
    q_type = question_data.get("type", "Aperta")
    value = default_value if default_value is not None else ""

    if q_type == "Sì/No":
        return st.radio(question, ["Sì", "No"], key=key, index=0 if value == "Sì" else 1 if value == "No" else 0)
    elif q_type == "Multipla":
        options = question_data.get("options", [])  # Ottiene le opzioni dalla domanda
        return st.selectbox(question, options, key=key, index=options.index(value) if value in options else 0)  # Selezione singola
    elif q_type == "Scala 1-5":
        return st.slider(question, 1, 5, value if isinstance(value, (int, float)) else 3, key=key)
    elif q_type == "Aperta":
        return st.text_input(question, value, key=key)
    return value

def update_state():
    """
    Funzione placeholder per aggiornare lo stato (se necessario).
    """
    pass