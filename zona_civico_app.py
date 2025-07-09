import streamlit as st
import pandas as pd
import re
from unidecode import unidecode

@st.cache_data
def carica_dati():
    df = pd.read_excel("CARTELLONI_BOLOGNA.xlsx")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    df['via'] = df['via'].astype(str)
    df['zona'] = df['zona'].astype(str)
    return df

def normalizza_testo(testo):
    testo = testo.lower()
    testo = unidecode(testo)
    testo = re.sub(r"[^a-z0-9 ]", "", testo)
    parole = testo.split()
    return " ".join(sorted(parole))

def estrai_civico(testo):
    match = re.search(r"(\d+[a-zA-Z]?)(/\d+)?", testo)
    return match.group(0) if match else None

def filtra_per_via(df, via_input):
    via_norm = normalizza_testo(via_input)
    df['via_norm'] = df['via'].apply(normalizza_testo)
    risultati = df[df['via_norm'].str.contains(via_norm)]
    return risultati.drop(columns=["via_norm"])

def cerca_civico(df_via, civico_input):
    if not civico_input:
        return df_via
    civico = civico_input.split('/')[0]
    try:
        civico = int(re.sub(r"[^0-9]", "", civico))
    except:
        return pd.DataFrame()
    pari = (civico % 2 == 0)
    for _, riga in df_via.iterrows():
        da = riga['dal']
        a = riga['al']
        solo_pari = str(riga['solo_pari']).strip().lower() == 'si'
        solo_dispari = str(riga['solo_dispari']).strip().lower() == 'si'
        if da <= civico <= a:
            if (solo_pari and pari) or (solo_dispari and not pari) or (not solo_pari and not solo_dispari):
                return pd.DataFrame([riga])
    return pd.DataFrame()

def main():
    st.markdown("# 📍 Zona Civico Bologna")
    st.markdown("**Scopri a quale zona e CAP appartiene un civico o una via a Bologna**")

    df = carica_dati()
    query = st.text_input("Inserisci via e civico (es. 'Via Mazzini 147/A') oppure solo la via")

    if query:
        civico = estrai_civico(query)
        via = query.replace(civico, "") if civico else query
        risultati = filtra_per_via(df, via)
        if risultati.empty:
            st.warning("⚠️ Nessuna via trovata.")
        else:
            finali = cerca_civico(risultati, civico)
            if not finali.empty:
                st.success("✅ Trovata corrispondenza:")
                st.dataframe(finali)
            else:
                st.info("ℹ️ Ecco tutte le zone trovate per questa via:")
                st.dataframe(risultati)

if __name__ == "__main__":
    main()
