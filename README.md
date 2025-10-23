# AI Compliance Analyzer  
**v15.4 – EU AI Act Readiness Tool**  
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)  
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32.0-red)](https://streamlit.io)  
[![AI Act](https://img.shields.io/badge/EU_AI_Act-2024%2F1689-green)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)

> **Strumento interattivo per valutare la conformità organizzativa all’EU AI Act (Reg. UE 2024/1689)**  
> Sviluppato per consulenti, DPO, compliance officer e team IA.

---

## Obiettivo
Valutare il **livello di compliance** aziendale all’**AI Act** attraverso:
- Profilo aziendale
- Inventory sistemi IA (multi-sistema)
- Domande generali + per-sistema + extra condizionali
- Calcolo automatico di **gap** e **score di conformità**
- **Roadmap di adeguamento** con priorità, tempistiche, riferimenti normativi

---

## Funzionalità (v15.4)

| Feature | Stato |
|-------|-------|
| Step 0: Profilo Aziendale | Done |
| Step 1: Inventory Sistemi IA | Done (1 sistema) |
| Step 2: Domande Extra (branching) | Done |
| Step 3: Risultati + Roadmap | Done |
| Download Excel completo | Done |
| Recommendations per ruolo (Sviluppatore, Utilizzatore, etc.) | Done |
| Branching condizionale (`condition` in `questions.json`) | Done |
| Gestione multi-sistema (prossimo: v15.5) | In progress |

---

## Installazione

```bash
git clone https://github.com/TUOUSUARIO/ai-compliance-analyzer.git
cd ai-compliance-analyzer
pip install -r requirements.txt