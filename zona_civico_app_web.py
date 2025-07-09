
import streamlit as st
import pandas as pd
import re

# Configura pagina
st.set_page_config(page_title="Zona Civico Bologna", page_icon="📍", layout="centered")

# Carica il file Excel
@st.cache_data
def carica_dati():
    df = pd.read_excel("CARTELLONI_BOLOGNA.xlsx", sheet_name="Foglio1", skiprows=3)
    return df

# Estrae la parte numerica dal civico barrato
def normalizza_civico(civico_str):
    numero = re.match(r"(\d+)", civico_str)
    return int(numero.group(1)) if numero else None

# Controlla se il civico è nell'intervallo giusto con la stessa parità
def trova_zona_per_civico(df, via, civico_input):
    via = via.strip().upper()
    civico = normalizza_civico(civico_input)
    risultati = []

    for _, row in df.iterrows():
        denominazione = str(row['Denominazione']).strip().upper()
        toponimo = str(row['Topomimo']).strip().upper()
        dal_al = str(row.get('DAL AL', '')).strip()

        if via in denominazione or via in toponimo:
            intervalli = re.findall(r'dal\s+(\d+)\s+al\s+(\d+)', dal_al, flags=re.IGNORECASE)
            for inizio, fine in intervalli:
                inizio = int(inizio)
                fine = int(fine)
                if (inizio % 2 == civico % 2) and (inizio <= civico <= fine):
                    risultati.append({
                        'Via': denominazione.title(),
                        'Civico': civico_input,
                        'Zona': row['Zona'],
                        'CAP': row['CAP'],
                        'Intervallo coperto': f'dal {inizio} al {fine}'
                    })
    return pd.DataFrame(risultati)

# ---- INTERFACCIA ----

st.markdown(
    "<h1 style='color:#005BAC;text-align:center;'>📍 Zona Civico Bologna</h1>", unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center;color:#F6BE00;font-size:18px;'>Scopri a quale zona e CAP appartiene un civico</p>",
    unsafe_allow_html=True
)

df = carica_dati()

via_input = st.text_input("🔎 Inserisci la via:", placeholder="Es. Via Massarenti")
civico_input = st.text_input("🏠 Inserisci il numero civico:", placeholder="Es. 137/2")

if st.button("Cerca Zona"):
    if not via_input or not civico_input:
        st.error("⚠️ Inserisci sia la via che il civico.")
    else:
        risultati = trova_zona_per_civico(df, via_input, civico_input)
        if not risultati.empty:
            st.success("✅ Zona trovata!")
            st.dataframe(risultati, use_container_width=True)
        else:
            st.warning("❌ Nessuna zona trovata per il civico indicato.")

# Footer responsive
st.markdown("---")
st.markdown(
    "<div style='text-align:center;font-size:13px;color:gray;'>Ottimizzato per smartphone e desktop - © 2025</div>",
    unsafe_allow_html=True
)
