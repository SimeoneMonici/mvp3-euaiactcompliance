# AI Compliance Analyzer v19.18
**Analisi conformità AI Act (EU) 2024/1689**
Strumento per PMI e sviluppatori – **Code of Practice GPAI 2025**.

---
## Obiettivo
Valutare il **livello di compliance** aziendale all’**AI Act** attraverso:
- Profilo aziendale
- Inventory sistemi IA (multi-sistema)
- Domande generali + per-sistema + extra condizionali (incl. GPAI/Generativa con Code of Practice)
- Calcolo automatico di **gap** e **score di conformità**
- **Roadmap di adeguamento** con priorità, tempistiche, riferimenti normativi (es. Art. 52, Code of Practice Transparency/Safety)

---
## Funzionalità
- 3 Step: Profilo → Inventory → GPAI/Generativa/PMI
- Tooltip con esempi + riferimenti UE (AI Act, Guidelines C(2025)5045/5052/924)
- Debug strutturato per step
- Download Excel + Roadmap CSV
- Allineato a Code of Practice (Copyright, Transparency, Safety/Security Chapters)

---
## Installazione
```bash
git clone https://github.com/SimeoneMonici/mvp3-euaiactcompliance.git
cd mvp3-euaiactcompliance
pip install -r requirements.txt
streamlit run app.py  # Avvia localmente