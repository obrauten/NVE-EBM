# EBM – Energibruksmodell (NVE) · Streamlit-wrapper

Denne appen pakker inn NVEs **EBM** som et enkelt webgrensesnitt: den genererer standard input,
kjører modellen og viser nøkkeltabeller fra `/output` (Excel).

## Kom i gang

```bash
python -m venv .venv
. .venv/bin/activate  # (Windows: .venv\Scripts\activate)
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
