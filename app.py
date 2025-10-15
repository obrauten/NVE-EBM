import subprocess
import sys
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="EBM – Energibruksmodell (NVE)", layout="wide")

INPUT_DIR = Path("input")
OUTPUT_DIR = Path("output")

st.title("EBM – Energibruksmodell (NVE)")
st.caption("Denne appen kjører NVEs EBM under panseret og viser nøkkeltabeller fra resultatfilene.")

# --- Hjelpefunksjoner ---
def run_cmd(args):
    """Kjør et CLI-kall og returner (ok,bool), stdout/stderr som tekst."""
    try:
        res = subprocess.run(args, capture_output=True, text=True, check=False)
        out = (res.stdout or "") + ("\n" + res.stderr if res.stderr else "")
        ok = (res.returncode == 0)
        return ok, out.strip()
    except Exception as e:
        return False, f"Feil ved kjøring: {e}"

def read_xlsx(name):
    fp = OUTPUT_DIR / name
    if fp.exists():
        try:
            return pd.read_excel(fp)
        except Exception as e:
            st.warning(f"Kunne ikke lese {name}: {e}")
    return None

# --- Sidepanel ---
st.sidebar.header("Kjøring")
with st.sidebar:
    st.write("1) Opprett input-mappe (første gang) → 2) Kjør EBM → 3) Se resultater")
    open_results = st.checkbox("Åpne Excel lokalt etter kjøring (`--open`)", value=False,
                               help="Virker kun lokalt (ikke i Streamlit Cloud).")
    colA, colB = st.columns(2)
    with colA:
        if st.button("1) Opprett/oppdater input"):
            ok, out = run_cmd(["ebm", "--create-input"])
            st.code(out or "(ingen output)")
            if ok:
                st.success("Input-mappe opprettet/oppdatert.")
            else:
                st.error("Klarte ikke å opprette input. Se logg over.")
    with colB:
        if st.button("2) Kjør EBM"):
            args = ["ebm"]
            if open_results:
                args.append("--open")
            ok, out = run_cmd(args)
            st.code(out or "(ingen output)")
            if ok and OUTPUT_DIR.exists():
                st.success("Kjøring ferdig. Bla i fanene under.")
            else:
                st.error("Kjøringen feilet eller fant ikke /output. Se logg over.")

st.divider()

# --- Resultatfaner ---
tabs = st.tabs([
    "Areal (area.xlsx)",
    "Energi – sum (energy_use.xlsx)",
    "Formål (energy_purpose.xlsx)",
    "Oppvarmingssystemer (heating_system_share.xlsx)",
    "Rå filer i /output"
])

with tabs[0]:
    df = read_xlsx("area.xlsx")
    st.write("**area.xlsx** – arealfordeling (BRA) over tid, kategorier/TEK.")
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Kjør EBM først, eller verifiser at /output/area.xlsx finnes.")

with tabs[1]:
    df = read_xlsx("energy_use.xlsx")
    st.write("**energy_use.xlsx** – levert energi fordelt på energiprodukt (el, fjernvarme, bio …).")
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Kjør EBM først, eller verifiser at /output/energy_use.xlsx finnes.")

with tabs[2]:
    df = read_xlsx("energy_purpose.xlsx")
    st.write("**energy_purpose.xlsx** – sluttbruk per formål (romoppv., VV, lys, utstyr …).")
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Kjør EBM først, eller verifiser at /output/energy_purpose.xlsx finnes.")

with tabs[3]:
    df = read_xlsx("heating_system_share.xlsx")
    st.write("**heating_system_share.xlsx** – lastdekning og miks av varmesystemer over tid.")
    if df is not None:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Kjør EBM først, eller verifiser at /output/heating_system_share.xlsx finnes.")

with tabs[4]:
    if OUTPUT_DIR.exists():
        files = sorted([p.name for p in OUTPUT_DIR.glob("*.xlsx")])
        if files:
            st.write("Filer i `/output`:")
            for fn in files:
                st.write(f"- `{fn}`")
        else:
            st.info("Ingen Excel-filer funnet i /output ennå.")
    else:
        st.info("Mappen /output finnes ikke. Kjør EBM først.")
