
import streamlit as st
import pandas as pd
import re
import unidecode

# Configura pagina
st.set_page_config(page_title="Zona Civico Bologna", page_icon="📍", layout="centered")

# Carica il file Excel
@st.cache_data
def carica_dati():
    df = pd.read_excel("CARTELLONI_BOLOGNA.xlsx", sheet_name=0, skiprows=3)
    return df

# Funzioni di normalizzazione
def normalizza_nome(nome):
    nome = str(nome).lower()
    nome = unidecode.unidecode(nome)
    nome = ' '.join(nome.split())
    return nome

def nomi_simili(nome1, nome2):
    set1 = set(normalizza_nome(nome1).split())
    set2 = set(normalizza_nome(nome2).split())
    return set1 == set2 or set1.issubset(set2) or set2.issubset(set1)

def estrai_numero_civico(civico_str):
    match = re.match(r"(\d+)", str(civico_str))
    return int(match.group(1)) if match else None

# Funzione principale: ricerca civico
def trova_zona_per_civico(df, via, civico_input):
    civico = estrai_numero_civico(civico_input)
    via_norm = normalizza_nome(via)
    risultati = []

    for _, row in df.iterrows():
        denominazione = str(row['Denominazione'])
        toponimo = str(row['Topomimo'])
        dal_al = str(row.get('DAL AL', '')).strip()

        if nomi_simili(via, denominazione) or nomi_simili(via, toponimo):
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
                        'Intervallo coperto': f'dal {inizio} al {fine}',
                        'Comune': row['Comune']
                    })
    return pd.DataFrame(risultati)

# Funzione: ricerca solo per via
def trova_zone_per_via(df, via):
    via_norm = normalizza_nome(via)
    risultati = []

    for _, row in df.iterrows():
        denominazione = str(row['Denominazione'])
        toponimo = str(row['Topomimo'])
        if nomi_simili(via, denominazione) or nomi_simili(via, toponimo):
            risultati.append({
                'Via': denominazione.title(),
                'Zona': row['Zona'],
                'CAP': row['CAP'],
                'Comune': row['Comune'],
                'Intervalli': row.get('DAL AL', '')
            })
    return pd.DataFrame(risultati).drop_duplicates()

# ---- INTERFACCIA ----
st.markdown("<h1 style='color:#005BAC;text-align:center;'>📍 Zona Civico Bologna</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:#F6BE00;font-size:18px;'>Ricerca zona da indirizzo con supporto intelligente</p>", unsafe_allow_html=True)

df = carica_dati()

tab1, tab2 = st.tabs(["🔎 Ricerca via + civico", "📄 Solo via (senza civico)"])

# Ricerca via + civico
with tab1:
    via_input = st.text_input("📍 Inserisci la via:", placeholder="Es. via scusa valle")
    civico_input = st.text_input("🏠 Inserisci il numero civico:", placeholder="Es. 137/2")

    if st.button("🔍 Cerca Zona"):
        if not via_input or not civico_input:
            st.error("Inserisci sia la via che il civico.")
        else:
            risultati = trova_zona_per_civico(df, via_input, civico_input)
            if not risultati.empty:
                st.success("✅ Trovata corrispondenza!")
                st.dataframe(risultati, use_container_width=True)
            else:
                st.warning("❌ Nessuna zona trovata per il civico indicato.")

# Ricerca solo via
with tab2:
    via_only = st.text_input("📍 Inserisci solo il nome della via:", placeholder="Es. via scusa valle")

    if st.button("📄 Mostra zone per via"):
        if not via_only:
            st.error("Inserisci il nome della via.")
        else:
            risultati_via = trova_zone_per_via(df, via_only)
            if not risultati_via.empty:
                st.success(f"✅ Trovate {len(risultati_via)} zone associate a questa via.")
                st.dataframe(risultati_via, use_container_width=True)
            else:
                st.warning("❌ Nessuna zona trovata per questa via.")

st.markdown("---")
st.markdown("<div style='text-align:center;font-size:13px;color:gray;'>Ottimizzato per errori comuni e vie invertite – Funziona anche su smartphone</div>", unsafe_allow_html=True)
