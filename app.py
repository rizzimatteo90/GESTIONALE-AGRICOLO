import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os

try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

# Configurazione della Pagina
st.set_page_config(
    page_title="Nicoli Rizzi - Servizi Agricoli e Forestali",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- STILE GRAFICO PERSONALIZZATO (Tono sfondo logo Nicoli Rizzi + Stile Pulsanti) ---
st.markdown("""
    <style>
    /* Colore di sfondo generale dell'app in tinta con lo sfondo del logo */
    .stApp {
        background-color: #F9F6F0;
        color: #2C2C2C;
    }
    /* Personalizzazione Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F3EFE6;
        border-right: 1px solid #E5E0D8;
    }
    /* Intestazioni e Testi */
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #2C2C2C !important;
    }
    /* Pulsanti principali (Salva / Azioni principali) */
    .stButton>button {
        background-color: #2C2C2C;
        color: #F9F6F0;
        border-radius: 4px;
        border: none;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #4A4A4A;
        color: #FFFFFF;
    }
    /* Stile specifico per il pulsante Aggiungi Riga (Sfondo bianco, scritta nera) */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D0CBC3 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #F0EBE3 !important;
        color: #000000 !important;
    }
    /* Schede ed Expander */
    .streamlit-expanderHeader {
        background-color: #F3EFE6;
        border-radius: 4px;
    }
    </style>
""", unsafe_allow_html=True)

# Connessione / Inizializzazione Database SQLite
conn = sqlite3.connect('gestionale_cantiere.db', check_same_thread=False)
c = conn.cursor()

# Creazione Tabelle
c.execute('''CREATE TABLE IF NOT EXISTS rapportini_v3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    utente TEXT,
    cliente TEXT,
    ore_totali REAL,
    note TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS dettagli_lavorazioni_v3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rapportino_id INTEGER,
    ora_inizio TEXT,
    ora_fine TEXT,
    mezzo TEXT,
    descrizione TEXT,
    FOREIGN KEY(rapportino_id) REFERENCES rapportini_v3(id) ON DELETE CASCADE
)''')

c.execute('''CREATE TABLE IF NOT EXISTS bilici_v3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_partenza TEXT,
    cliente TEXT
)''')

current_year = datetime.now().year
c.execute('''CREATE TABLE IF NOT EXISTS attrezzature_v3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    tipo_conteggio TEXT,
    anno_riferimento INTEGER,
    valore_inizio_anno REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS manutenzioni_v3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attrezzatura_id INTEGER,
    data TEXT,
    tipo TEXT,
    ore_km_al_momento REAL,
    eseguito_da TEXT,
    descrizione TEXT,
    costo REAL,
    FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature_v3(id)
)''')
conn.commit()

# --- SIDEBAR & HEADER CON LOGO ---
if os.path.exists("logo.jpg"):
    st.sidebar.image("logo.jpg", use_container_width=True)
elif os.path.exists("IMG_7106.jpg"):
    st.sidebar.image("IMG_7106.jpg", use_container_width=True)
else:
    st.sidebar.markdown("### **NICOLI RIZZI**\n*Servizi Agricoli e Forestali Conto Terzi*")

st.sidebar.markdown("---")
ruolo = st.sidebar.radio("Ruolo Operativo:", ["Operatore / Dipendente", "Socio / Amministratore"])
utente_corrente = st.sidebar.text_input("Operatore / Utente:", value="Mario Rossi")

menu = st.sidebar.selectbox("Modulo di Lavoro:", [
    "Rapportino Giornaliero",
    "Calendario & Storico Rapportini",
    "Registro Bilici Cippato",
    "Parco Macchine & Manutenzioni"
])

st.sidebar.markdown("---")
st.sidebar.caption("Nicoli Rizzi S.r.l. - Gestione Operativa")

# --- MODULO 1: RAPPORTINO GIORNALIERO ---
if menu == "Rapportino Giornaliero":
    st.title("Rapportino Giornaliero Attività")
    st.caption(f"Utente collegato: **{utente_corrente}** ({ruolo})")
    
    with st.form("form_rapportino_v3"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_rep = st.date_input("Data Lavorazione (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            cliente = st.text_input("Cliente", placeholder="Inserisci il nome del cliente")
        with col_d2:
            ore_totali = st.number_input("Ore Totali Lavorate nella Giornata", min_value=0.0, step=0.5, value=8.0)
            note_giornaliere = st.text_area("Note / Osservazioni Generali", placeholder="Note complessive, consumo gasolio, condizioni meteo...")

        st.markdown("---")
        st.subheader("Dettaglio Lavorazioni della Giornata")
        st.caption("Aggiungi le attività svolte durante la giornata.")
        
        c.execute("SELECT nome FROM attrezzature_v3")
        attrezzature_db = [row[0] for row in c.fetchall()]
        opzioni_mezzi = attrezzature_db + ["Altro / Inserimento Manuale"]

        if 'num_righe_lavoro' not in st.session_state:
            st.session_state.num_righe_lavoro = 1

        lavorazioni_data = []
        for i in range(st.session_state.num_righe_lavoro):
            st.markdown(f"**Lavorazione #{i+1}**")
            col_l1, col_l2, col_l3, col_l4 = st.columns([1.5, 1.5, 3, 3])
            
            with col_l1:
                ora_in = st.time_input(f"Ora Inizio #{i+1}", value=datetime.strptime("07:30", "%H:%M").time(), key=f"in_{i}")
            with col_l2:
                ora_fi = st.time_input(f"Ora Fine #{i+1}", value=datetime.strptime("12:00", "%H:%M").time(), key=f"fi_{i}")
            with col_l3:
                m_sel = st.selectbox(f"Mezzo / Attrezzatura #{i+1}", opzioni_mezzi, key=f"m_sel_{i}")
                if m_sel == "Altro / Inserimento Manuale":
                    m_final = st.text_input(f"Specifica mezzo a mano #{i+1}", placeholder="es. Motosega Stihl 661", key=f"m_man_{i}")
                else:
                    m_final = m_sel
            with col_l4:
                desc_lav = st.text_input(f"Descrizione Attività #{i+1}", placeholder="es. Cippatura ramaglie", key=f"desc_{i}")
                
            lavorazioni_data.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), m_final, desc_lav))
            st.markdown("")

        submitted = st.form_submit_button("Salva Rapportino Completo")
        
    col_add_btn, _ = st.columns([2, 5])
    with col_add_btn:
        if st.button("➕ Aggiungi un'altra riga di lavoro"):
            st.session_state.num_righe_lavoro += 1
            st.rerun()

    if submitted:
        data_formatted = data_rep.strftime("%d/%m/%Y")
        c.execute("INSERT INTO rapportini_v3 (data, utente, cliente, ore_totali, note) VALUES (?,?,?,?,?)",
                  (data_formatted, utente_corrente, cliente, ore_totali, note_giornaliere))
        rap_id = c.lastrowid
        
        for ora_in, ora_fi, m_final, desc_lav in lavorazioni_data:
            c.execute("INSERT INTO dettagli_lavor