# AI Compliance Analyzer
App per analizzare il livello di compliance aziendale all'AI Act UE. Sviluppata come strumento per consulenti.

## Come Avviare
1. Installa dipendenze: `pip install -r requirements.txt`
2. Avvia l'app: `streamlit run app.py`
3. URL locale: http://localhost:8501
4. Deploy: https://mvp3-euaiactcompliance-w6qvrxoaryzmnmp6u3bfxp.streamlit.app/

## Funzionalità
- Step 1: Profilo Aziendale (settore, dimensione, team).
- Step 2: Inventory Sistemi IA (ruolo, caso d'uso, rischio).
- Step 3: Domande Extra parametrizzate per settore/ruolo/rischio.
- Risultati: Punteggio conformità (es. 0.00% Generale, 28.57% Sistema 1), gap, roadmap, export Excel/CSV.
- Supporto per settori critici (es. Difesa/Militare) con esclusioni AI Act (Art. 2).
- Interfaccia con disclaimer contestuali in Step 3.

## Progressi
- v6.54: Flusso completo, aggiunta sistemi, debug log.
- v6.70/6.71: Correzioni punteggi, eliminazione duplicati, aggiunta q2_38_sanita.
- v6.84: Risolti problemi di nesting con subheader, aggiunti disclaimer in Step 3, deploy stabile su Streamlit Cloud.

## To-Do
- Correggere etichetta 2.43 (Esclusioni).
- Test scenari aggiuntivi (Utilizzatore, Importatore).
- Fix Conformità Generale (attualmente 0.00% con risposte "Sì").
- Ripristinare expander per UI migliorata (in sviluppo).

## Contatti
Contatta per feedback o collaborazioni!