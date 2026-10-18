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
    bg_css = ".stApp { background: linear-gradient(rgba(0, 0, 0, 0.50), rgba(0, 0, 0, 0.50)), url('data:image/jpg;base64," + bin_str + "'); background-size: cover; background-position: center; background-attachment: fixed; }"
else:
    bg_css = ".stApp { background-color: #F9F6F0; color: #2C2C2C; }"

st.markdown("""
    <style>
    """ + bg_css + """
    [data-testid="stSidebar"] {
        display: none;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #2C2C2C !important;
    }
    .home-title {
        color: #FFFFFF !important;
        text-align: center;
        text-shadow: 1px 1px 4px rgba(0,0,0,0.8);
        font-size: 20px !important;
        margin-top: 5px !important;
        margin-bottom: 5px !important;
    }
    .logo-container {
        text-align: center;
        margin-top: 0px;
        margin-bottom: 5px;
    }
    .logo-img {
        max-width: 95px !important;
        height: auto;
        border-radius: 6px;
        box-shadow: 0px 2px 8px rgba(0, 0, 0, 0.3);
    }
    div.stButton > button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.94) !important;
        color: #1A1A1A !important;
        border: 2px solid #C5C0B7 !important;
        border-radius: 10px !important;
        height: 130px !important;
        width: 100% !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        white-space: pre-wrap !important;
        line-height: 1.3 !important;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.25) !important;
        transition: all 0.2s ease-in-out !important;
        padding: 10px !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFFFFF !important;
        border-color: #2C2C2C !important;
        transform: translateY(-2px) !important;
        box-shadow: 0px 6px 14px rgba(0, 0, 0, 0.35) !important;
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

if st.session_state.modulo_attivo == "HOME":
    col_l1, col_l2, col_l3 = st.columns([1, 1, 1])
    with col_l2:
        logo_file = None
        if os.path.exists("logo.jpg"):
            logo_file = "logo.jpg"
        elif os.path.exists("IMG_7106.jpg"):
            logo_file = "IMG_7106.jpg"

        if logo_file:
            logo_bin = get_base64_of_bin_file(logo_file)
            st.markdown('<div class="logo-container"><img src="data:image/jpg;base64,' + logo_bin + '" class="logo-img"></div>', unsafe_allow_html=True)
        else:
            st.markdown("<h2 class='home-title'>NICOLI RIZZI</h2>", unsafe_allow_html=True)

    st.markdown("<h2 class='home-title'>PANNELLO DI GESTIONE OPERATIVA</h2>", unsafe_allow_html=True)

    with st.container():
        c_u1, c_u2 = st.columns(2)
        with c_u1:
            st.session_state.utente_corrente = st.text_input("Operatore / Utente:", value=st.session_state.utente_corrente)
        with c_u2:
            st.session_state.ruolo = st.selectbox("Ruolo Operativo:", ["Operatore / Dipendente", "Socio / Amministratore"], index=0 if st.session_state.ruolo == "Operatore / Dipendente" else 1)

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)

    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        if st.button("RAPPORTINO GIORNALIERO\n\nInserimento attività e ore", key="btn_rap", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "RAPPORTINO"
            st.rerun()

    with r1_c2:
        if st.button("CALENDARIO E STORICO\n\nConsultazione e verifiche", key="btn_cal", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "CALENDARIO"
            st.rerun()

    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        if st.button("REGISTRO BILICI CIPPATO\n\nPartenze e consegne", key="btn_bil", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "BILICI"
            st.rerun()

    with r2_c2:
        if st.button("PARCO MACCHINE\n\nMezzi e manutenzioni", key="btn_flotta", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "FLOTTA"
            st.rerun()

    st.markdown("<p style='text-align: center; color: #FFFFFF; font-weight: 500; font-size: 12px; margin-top: 15px; text-shadow: 1px 1px 3px #000;'>Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali Conto Terzi</p>", unsafe_allow_html=True)

elif st.session_state.modulo_attivo == "RAPPORTINO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Rapportino Giornaliero Attività")
    st.caption("Utente collegato: **" + st.session_state.utente_corrente + "** (" + st.session_state.ruolo + ")")
    
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
            st.markdown("**Lavorazione #" + str(i+1) + "**")
            col_l1, col_l2, col_l3, col_l4 = st.columns([1.5, 1.5, 3, 3])
            
            with col_l1:
                ora_in = st.time_input("Ora Inizio #" + str(i+1), value=datetime.strptime("07:30", "%H:%M").time(), key="in_" + str(i))
            with col_l2:
                ora_fi = st.time_input("Ora Fine #" + str(i+1), value=datetime.strptime("12:00", "%H:%M").time(), key="fi_" + str(i))
            with col_l3:
                m_sel = st.selectbox("Mezzo / Attrezzatura #" + str(i+1), opzioni_mezzi, key="m_sel_" + str(i))
                if m_sel == "Altro / Inserimento Manuale":
                    m_final = st.text_input("Specifica mezzo a mano #" + str(i+1), placeholder="es. Motosega Stihl 661", key="m_man_" + str(i))
                else:
                    m_final = m_sel
            with col_l4:
                desc_lav = st.text_input("Descrizione Attività #" + str(i+1), placeholder="es. Cippatura ramaglie", key="desc_" + str(i))
                
            lavorazioni_data.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), m_final, desc_lav))
            st.markdown("")

        submitted = st.form_submit_button("Salva Rapportino Completo")
        
    col_add_btn, _ = st.columns([2, 5])
    with col_add_btn:
        if st.button("Aggiungi un'altra riga di lavoro", type="secondary"):
            st.session_state.num_righe_lavoro += 1
            st.rerun()

    if submitted:
        data_formatted = data_rep.strftime("%d/%m/%Y")
        sql_head = "INSERT INTO rapportini_v3 (data, utente, cliente, ore_totali, note) VALUES (?,?,?,?,?)"
        c.execute(sql_head, (data_formatted, st.session_state.utente_corrente, cliente, ore_totali, note_giornaliere))
        rap_id = c.lastrowid
        
        sql_detail = "INSERT INTO dettagli_lavorazioni_v3 (rapportino_id, ora_inizio, ora_fine, mezzo, descrizione) VALUES (?, ?, ?, ?, ?)"
        for ora_in, ora_fi, m_final, desc_lav in lavorazioni_data:
            c.execute(sql_detail, (rap_id, ora_in, ora_fi, m_final, desc_lav))
            
        conn.commit()
        st.session_state