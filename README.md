# AI Compliance Analyzer

App per analizzare il livello di compliance aziendale all'AI Act UE. Sviluppata come strumento per consulenti.

## Come Avviare
1. Installa dipendenze: `pip install -r requirements.txt`
2. Avvia l'app: `streamlit run app.py`
3. URL: http://localhost:8501

## Funzionalità
- Step 1: Profilo Aziendale (settore, dimensione, team).
- Step 2: Inventory Sistemi IA (ruolo, caso d'uso, rischio).
- Step 3: Domande Extra parametrizzate per settore/ruolo/rischio.
- Risultati: Punteggio conformità, gap, roadmap, Excel/CSV export.

## Progressi
- v6.54: Flusso completo, aggiunta sistemi, debug log.
- v6.70/6.71: Correzioni punteggi, eliminazione duplicati, aggiunta q2_38_sanita.

## To-Do
- Correggere etichetta 2.43 (Esclusioni).
- Test scenari aggiuntivi (Utilizzatore, Importatore).

Contatta per feedback!