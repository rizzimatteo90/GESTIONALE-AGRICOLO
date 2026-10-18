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
    /* MODULI QUADRATI PERFETTI */
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
            st.session_state.utente_corrente = st.text_input("Utente:", value=st.session_state.utente_corrente)
        with c_u2:
            st.session_state.ruolo = st.selectbox("Ruolo Operativo:", ["Operatore / Dipendente", "Socio / Amministratore"], index=0 if st.session_state.ruolo == "Operatore / Dipendente" else 1)

    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)

    # GRIGLIA MODULI QUADRATI
    r1_c1, r1_c2 = st.columns(2)
    with r1_c1:
        if st.button("RAPPORTINO\nGIORNALIERO", key="btn_rap", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "RAPPORTINO"
            st.rerun()

    with r1_c2:
        if st.button("CALENDARIO\nE STORICO", key="btn_cal", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "CALENDARIO"
            st.rerun()

    st.markdown("<div style='margin-top: 5px;'></div>", unsafe_allow_html=True)
    r2_c1, r2_c2 = st.columns(2)

    with r2_c1:
        if st.button("REGISTRO\nBILICI CIPPATO", key="btn_bil", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "BILICI"
            st.rerun()

    with r2_c2:
        if st.button("PARCO\nMACCHINE", key="btn_flotta", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "FLOTTA"
            st.rerun()

    st.markdown("<p style='text-align: center; color: #FFFFFF; font-weight: 600; font-size: 11px; margin-top: 10px; text-shadow: 1px 1px 3px #000;'>Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali Conto Terzi</p>", unsafe_allow_html=True)

# ==============================================================================
# MODULO 1: RAPPORTINO GIORNALIERO
# ==============================================================================
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
        st.session_state.num_righe_lavoro = 1  
        st.success("Rapportino registrato con successo in data " + data_formatted + "!")

# ==============================================================================
# MODULO 2: CALENDARIO & STORICO
# ==============================================================================
elif st.session_state.modulo_attivo == "CALENDARIO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Calendario & Storico Rapportini")

    if st.session_state.ruolo == "Operatore / Dipendente":
        st.info("Visualizzazione rapportini inseriti da: **" + st.session_state.utente_corrente + "**")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v3 WHERE utente = ? ORDER BY id DESC", conn, params=(st.session_state.utente_corrente,))
    else:
        st.success("Vista Amministratore / Socio: Monitoraggio completo dell'attività aziendale.")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v3 ORDER BY id DESC", conn)

    tab_cal, tab_lista = st.tabs(["Vista Calendario Mensile", "Elenco Dettagliato & Modifica"])

    with tab_cal:
        st.subheader("Calendario delle Attività")
        
        if not df_rap.empty:
            events = []
            for _, r in df_rap.iterrows():
                try:
                    dt_obj = datetime.strptime(r['data'], "%d/%m/%Y")
                    date_iso = dt_obj.strftime("%Y-%m-%d")
                    events.append({
                        "title": r['utente'] + " - " + r['cliente'] + " (" + str(r['ore_totali']) + "h)",
                        "start": date_iso,
                        "end": date_iso,
                        "allDay": True
                    })
                except Exception:
                    pass

            calendar_options = {
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek"
                },
                "initialView": "dayGridMonth",
                "locale": "it"
            }

            if HAS_CALENDAR:
                calendar(events=events, options=calendar_options, key="cal_view")

            st.markdown("---")
            st.subheader("Consulta i Rapportini per Data Specifica")
            data_selezionata = st.date_input("Seleziona Giorno da Ispezionare", date.today(), format="DD/MM/YYYY")
            data_sel_str = data_selezionata.strftime("%d/%m/%Y")

            c.execute("SELECT * FROM rapportini_v3 WHERE data = ?", (data_sel_str,))
            rapporti_giorno = c.fetchall()

            if rapporti_giorno:
                st.markdown("#### Rapportini del **" + data_sel_str + "**")
                for rap in rapporti_giorno:
                    rap_id, r_data, r_ut, r_cli, r_ore, r_note = rap
                    with st.expander("Cliente: " + r_cli + " | Operatore: " + r_ut + " | Ore: