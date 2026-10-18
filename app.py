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

# Configurazione della Pagina (Senza sidebar iniziale)
st.set_page_config(
    page_title="Nicoli Rizzi - Servizi Agricoli e Forestali",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STILE GRAFICO PERSONALIZZATO ---
st.markdown("""
    <style>
    /* Nasconde la sidebar di default */
    [data-testid="stSidebar"] {
        display: none;
    }
    .stApp {
        background-color: #F9F6F0;
        color: #2C2C2C;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #2C2C2C !important;
    }
    /* Pulsanti Generici */
    .stButton>button {
        background-color: #2C2C2C;
        color: #F9F6F0;
        border-radius: 6px;
        border: none;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #4A4A4A;
        color: #FFFFFF;
    }
    /* Stile specifico per il pulsante Aggiungi Riga */
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D0CBC3 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #F0EBE3 !important;
        color: #000000 !important;
    }
    .streamlit-expanderHeader {
        background-color: #F3EFE6;
        border-radius: 6px;
    }
    /* Carte Home Page */
    .home-card {
        background-color: #FFFFFF;
        border: 1px solid #E0DCD3;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.03);
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

# Session state per la navigazione interna
if 'modulo_attivo' not in st.session_state:
    st.session_state.modulo_attivo = "HOME"
if 'ruolo' not in st.session_state:
    st.session_state.ruolo = "Operatore / Dipendente"
if 'utente_corrente' not in st.session_state:
    st.session_state.utente_corrente = "Mario Rossi"

# Funzione per tornare alla home
def torna_home():
    st.session_state.modulo_attivo = "HOME"

# ==============================================================================
# SCHERMATA HOME PAGE
# ==============================================================================
if st.session_state.modulo_attivo == "HOME":
    
    # Logo e Intestazione Centrata
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if os.path.exists("logo.jpg"):
            st.image("logo.jpg", use_container_width=True)
        elif os.path.exists("IMG_7106.jpg"):
            st.image("IMG_7106.jpg", use_container_width=True)
        else:
            st.markdown("<h2 style='text-align: center;'>NICOLI RIZZI</h2><p style='text-align: center;'>Servizi Agricoli e Forestali Conto Terzi</p>", unsafe_allow_html=True)
            
    st.markdown("<h3 style='text-align: center; margin-top: 10px;'>Pannello di Gestione Operativa</h3>", unsafe_allow_html=True)
    st.markdown("---")

    # Selezione Utente & Ruolo in alto nella Home
    c_u1, c_u2 = st.columns(2)
    with c_u1:
        st.session_state.utente_corrente = st.text_input("Operatore / Utente:", value=st.session_state.utente_corrente)
    with c_u2:
        st.session_state.ruolo = st.selectbox("Ruolo Operativo:", ["Operatore / Dipendente", "Socio / Amministratore"], index=0 if st.session_state.ruolo == "Operatore / Dipendente" else 1)

    st.markdown("<br>", unsafe_allow_html=True)

    # Griglia 2x2 dei Moduli di Lavoro (Quadrate)
    row1_col1, row1_col2 = st.columns(2)
    
    with row1_col1:
        st.markdown("""
            <div class="home-card">
                <h3>📋 RAPPORTINO GIORNALIERO</h3>
                <p>Inserisci le attività svolte, gli orari, i mezzi usati e le ore totali.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Apri Rapportino Giornaliero", use_container_width=True):
            st.session_state.modulo_attivo = "RAPPORTINO"
            st.rerun()

    with row1_col2:
        st.markdown("""
            <div class="home-card">
                <h3>📅 CALENDARIO & STORICO</h3>
                <p>Consulta il calendario mensile delle attività e lo storico dei rapportini.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Apri Calendario & Storico", use_container_width=True):
            st.session_state.modulo_attivo = "CALENDARIO"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("""
            <div class="home-card">
                <h3>🚛 REGISTRO BILICI CIPPATO</h3>
                <p>Registra le uscite e le partenze dei bilici di cippato per i clienti.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Apri Registro Bilici Cippato", use_container_width=True):
            st.session_state.modulo_attivo = "BILICI"
            st.rerun()

    with row2_col2:
        st.markdown("""
            <div class="home-card">
                <h3>🛠️ PARCO MACCHINE & MANUTENZIONI</h3>
                <p>Gestisci i mezzi aziendali, le ore/km di inizio anno e il registro tagliandi.</p>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Apri Parco Macchine", use_container_width=True):
            st.session_state.modulo_attivo = "FLOTTA"
            st.rerun()

    st.markdown("---")
    st.caption("<p style='text-align: center;'>Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali</p>", unsafe_allow_html=True)

# ==============================================================================
# MODULO 1: RAPPORTINO GIORNALIERO
# ==============================================================================
elif st.session_state.modulo_attivo == "RAPPORTINO":
    st.button("⬅️ Torna alla Home", on_click=torna_home)
    st.title("Rapportino Giornaliero Attività")
    st.caption(f"Utente collegato: **{st.session_state.utente_corrente}** ({st.session_state.ruolo})")
    
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