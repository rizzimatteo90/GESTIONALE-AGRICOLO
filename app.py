import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os
import base64

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

if bin_str and st.session_state.get('modulo_attivo', 'HOME') == 'HOME':
    bg_css = ".stApp { background: linear-gradient(rgba(0, 0, 0, 0.55), rgba(0, 0, 0, 0.55)), url('data:image/jpg;base64," + bin_str + "'); background-size: cover; background-position: center; background-attachment: fixed; }"
else:
    bg_css = ".stApp { background-color: #F9F6F0; color: #2C2C2C; }"

st.markdown("""
    <style>
    """ + bg_css + """
    [data-testid="stSidebar"] {
        display: none;
    }
    h1, h2, h3, h4, h5, h6, span {
        color: #FFFFFF !important;
    }
    label {
        color: #FFFFFF !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    }
    .home-title {
        color: #FFFFFF !important;
        text-align: center;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
        font-size: 20px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
        font-weight: 700;
    }
    .logo-container {
        text-align: center;
        margin-top: 0px;
        margin-bottom: 2px;
    }
    .logo-img {
        max-width: 85px !important;
        height: auto;
        border-radius: 8px;
        mix-blend-mode: multiply;
        background-color: transparent !important;
    }
    div.stButton > button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1A1A1A !important;
        border: 2px solid #C5C0B7 !important;
        border-radius: 12px !important;
        aspect-ratio: 1 / 1 !important;
        width: 100% !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        white-space: pre-wrap !important;
        line-height: 1.3 !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        padding: 10px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFFFFF !important;
        border-color: #2C2C2C !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 16px rgba(0, 0, 0, 0.4) !important;
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
conn.commit()

if 'modulo_attivo' not in st.session_state:
    st.session_state.modulo_attivo = "HOME"
if 'ruolo' not in st.session_state:
    st.session_state.ruolo = "Operatore / Dipendente"
if 'utente_corrente' not in st.session_state:
    st.session_state.utente_corrente = "Mario Rossi"

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# ==============================================================================
# HOME PAGE
# ==============================================================================
if st.session_state.modulo_attivo == "HOME":
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        logo_file = None
        if os.path.exists("logo.jpg"):
            logo_file = "logo.