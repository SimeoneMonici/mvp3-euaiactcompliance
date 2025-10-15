import streamlit as st

def render_question(question_data, key, default_value=None):
    question = question_data["question"]
    q_type = question_data.get("type", "Aperta")
    value = default_value if default_value is not None else ""
    tooltip = question_data.get("notes", "Riferimento normativo non specificato")
    if q_type == "Sì/No":
        return st.radio(question, ["Sì", "No"], key=key, index=0 if value == "Sì" else 1 if value == "No" else 0, help=tooltip)
    elif q_type == "Multipla":
        options = question_data.get("options", [])
        return st.selectbox(question, options, key=key, index=options.index(value) if value in options else 0, help=tooltip)
    elif q_type == "Scala 1-5":
        return min(5, max(1, int(st.slider(question, key=key, min_value=1, max_value=5, value=value if isinstance(value, (int, float)) and 1 <= value <= 5 else 3, help=tooltip))))
    elif q_type == "Aperta":
        return st.text_input(question, value, key=key, help=tooltip)
    return value

import json
def load_questions():
    with open('questions.json', 'r', encoding='utf-8') as f:
        return json.load(f)