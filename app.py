import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import base64
from datetime import timedelta

try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

st.set_page_config(
    page_title="Nicoli Rizzi - Servizi Agricoli e Forestali",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except Exception:
        return ""

bg_image_path = None
if os.path.exists("sfondo.jpg"):
    bg_image_path = "sfondo.jpg"
elif os.path.exists("IMG_8234.jpg"):
    bg_image_path = "IMG_8234.jpg"

bin_str = ""
if bg_image_path:
    bin_str = get_base64_of_bin_file(bg_image_path)

is_home = st.session_state.get('modulo_attivo', 'HOME') == 'HOME'
if bin_str and is_home:
    bg_css = ".stApp { background: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)), url('data:image/jpeg;base64," + bin_str + "'); background-size: cover; background-position: center; background-attachment: fixed; }"
else:
    bg_css = ".stApp { background-color: #F9F6F0; color: #2C2C2C; }"

text_color = "#FFFFFF" if is_home and bin_str else "#2C2C2C"
label_shadow = "1px 1px 2px rgba(0,0,0,0.8)" if is_home and bin_str else "none"

st.markdown("""
    <style>
    """ + bg_css + """
    [data-testid="stSidebar"] {
        display: none;
    }
    h1, h2, h3, h4, h5, h6, span, p, [data-testid="stMarkdownContainer"] {
        color: """ + text_color + """ !important;
    }
    label {
        color: """ + text_color + """ !important;
        font-weight: 600 !important;
        text-shadow: """ + label_shadow + """;
    }
    .logo-container {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 10px 0 20px 0;
        box-sizing: border-box;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    .logo-img {
        display: block;
        width: min( min(80vw, 420px), 100% ) !important;
        max-width: 420px !important;
        height: 120px !important;
        object-fit: contain;
        background: transparent !important;
        filter: grayscale(1) invert(1) contrast(1.15) brightness(1.15);
        mix-blend-mode: screen;
    }
    .logo-fallback {
        color: #FFFFFF !important;
        font-size: clamp(32px, 6vw, 64px);
        line-height: 1.05;
        font-weight: 900;
        text-align: center;
        text-shadow: 2px 2px 5px rgba(0,0,0,0.8);
    }
    .st-key-home_modules {
        max-width: 450px !important;
        margin-left: auto !important;
        margin-right: auto !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.97) !important;
        color: #1A1A1A !important;
        border: 2px solid #C5C0B7 !important;
        border-radius: 14px !important;
        aspect-ratio: 1 / 1 !important;
        width: 100% !important;
        min-height: 0 !important;
        height: 195px !important;
        max-height: 195px !important;
        font-size: clamp(16px, 1.4vw, 21px) !important;
        font-weight: 850 !important;
        white-space: normal !important;
        overflow-wrap: anywhere !important;
        line-height: 1.15 !important;
        box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.2s ease-in-out !important;
        padding: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {
        color: #1A1A1A !important;
        width: 100% !important;
        text-align: center !important;
        font-weight: 850 !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFFFFF !important;
        border-color: #2C2C2C !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.45) !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D0CBC3 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #F0EBE3 !important;
        color: #000000 !important;
    }
    .streamlit-expanderHeader {
        background-color: #F3EFE6;
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

conn = sqlite3.connect('gestionale_cantiere.db', check_same_thread=False)
conn.execute('PRAGMA foreign_keys = ON')
c = conn.cursor()

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
c.execute('''CREATE TABLE IF NOT EXISTS utenti_app (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL COLLATE NOCASE UNIQUE,
    creato_il TEXT DEFAULT CURRENT_TIMESTAMP
)''')
conn.commit()

def password_amministratore_configurata():
    return "Billabong4e48"

if 'modulo_attivo' not in st.session_state:
    st.session_state.modulo_attivo = "HOME"
if 'ruolo' not in st.session_state:
    st.session_state.ruolo = "Operatore"
if 'utente_corrente' not in st.session_state:
    st.session_state.utente_corrente = ""
if 'admin_autenticato' not in st.session_state:
    st.session_state.admin_autenticato = False
if 'ruolo_scelto' not in st.session_state:
    st.session_state.ruolo_scelto = "Operatore"

try:
    nome_url = str(st.query_params.get("utente", "")).strip()
except Exception:
    nome_url = ""
if nome_url and not st.session_state.utente_corrente:
    c.execute("SELECT nome FROM utenti_app WHERE nome = ? COLLATE NOCASE", (nome_url,))
    trovato = c.fetchone()
    if trovato:
        st.session_state.utente_corrente = trovato[0]

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# ==============================================================================
# HOME PAGE
# ==============================================================================
if st.session_state.modulo_attivo == "HOME":
    logo_file = None
    if os.path.exists("logo.png"):
        logo_file = "logo.png"
    elif os.path.exists("logo.jpg"):
        logo_file = "logo.jpg"
    elif os.path.exists("IMG_7106.jpg"):
        logo_file = "IMG_7106.jpg"

    if logo_file:
        logo_bin = get_base64_of_bin_file(logo_file)
        mime = "image/png" if logo_file.lower().endswith(".png") else "image/jpeg"
        st.markdown(
            '<div class="logo-container"><img src="data:' + mime + ';base64,' + logo_bin + '" class="logo-img" alt="Logo Nicoli Rizzi"></div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="logo-container"><div class="logo-fallback">NICOLI RIZZI</div></div>', unsafe_allow_html=True)

    with st.container():
        c.execute("SELECT nome FROM utenti_app ORDER BY nome COLLATE NOCASE")
        utenti_registrati = [r[0] for r in c.fetchall()]
        opzioni_utenti = ["-- Seleziona operatore --"] + utenti_registrati + ["+ Registra nuovo operatore"]
        default_utente = st.session_state.utente_corrente if st.session_state.utente_corrente in utenti_registrati else "-- Seleziona operatore --"
        
        try:
            idx_default = opzioni_utenti.index(default_utente)
        except ValueError:
            idx_default = 0

        selezione_utente = st.selectbox("Operatore:", opzioni_utenti, index=idx_default, key="selezione_utente_home")
        
        if selezione_utente == "+ Registra nuovo operatore":
            with st.form("registra_operatore_form"):
                nuovo_nome = st.text_input("Nome e cognome del dipendente")
                registra_nome = st.form_submit_button("Registra operatore")
            if registra_nome:
                nome_pulito = " ".join(nuovo_nome.split())
                if not nome_pulito:
                    st.error("Inserisci nome e cognome.")
                else:
                    try:
                        c.execute("INSERT INTO utenti_app (nome) VALUES (?)", (nome_pulito,))
                        conn.commit()
                        st.session_state.utente_corrente = nome_pulito
                        st.query_params["utente"] = nome_pulito
                        st.success("Operatore registrato. Dalle prossime volte potrà selezionare il proprio nome.")
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.session_state.utente_corrente = nome_pulito
                        st.query_params["utente"] = nome_pulito
                        st.rerun()
        elif selezione_utente != "-- Seleziona operatore --":
            st.session_state.utente_corrente = selezione_utente
            try:
                st.query_params["utente"] = selezione_utente
            except Exception:
                pass

        scelta_ruolo = st.selectbox("Ruolo:", ["Operatore", "Amministratore"], key="ruolo_scelto")
        if scelta_ruolo == "Amministratore":
            pwd_configurata = password_amministratore_configurata()
            if not st.session_state.admin_autenticato:
                with st.form("login_amministratore_form"):
                    password_inserita = st.text_input("Password amministratore", type="password")
                    accesso_admin = st.form_submit_button("Accedi come amministratore")
                if accesso_admin:
                    if password_inserita == pwd_configurata:
                        st.session_state.admin_autenticato = True
                        st.session_state.ruolo = "Amministratore"
                        st.success("Accesso amministratore autorizzato.")
                        st.rerun()
                    else:
                        st.error("Password non corretta.")
                        st.session_state.ruolo = "Operatore"
            else:
                st.session_state.ruolo = "Amministratore"
                if st.button("Esci dall'account amministratore", key="logout_admin", type="secondary"):
                    st.session_state.admin_autenticato = False
                    st.session_state.ruolo = "Operatore"
                    st.session_state.ruolo_scelto = "Operatore"
                    st.rerun()
        else:
            st.session_state.ruolo = "Operatore"
            st.session_state.admin_autenticato = False

    st.markdown("<div style='