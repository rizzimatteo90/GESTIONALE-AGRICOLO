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
    bg_css = ".stApp { background: linear-gradient(rgba(0, 0, 0, 0.60), rgba(0, 0, 0, 0.60)), url('data:image/jpeg;base64," + bin_str + "'); background-size: cover; background-position: center; background-attachment: fixed; }"
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
    header {
        visibility: hidden !important;
        height: 0px !important;
    }
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 0.8rem !important;
        padding-right: 0.8rem !important;
        max-width: 500px !important;
        margin: 0 auto !important;
    }
    h1, h2, h3, h4, h5, h6, span, p, [data-testid="stMarkdownContainer"] {
        color: """ + text_color + """ !important;
    }
    label {
        color: """ + text_color + """ !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        text-shadow: """ + label_shadow + """;
        margin-bottom: 2px !important;
    }
    .logo-container {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2px 0 6px 0;
        box-sizing: border-box;
        background: transparent !important;
    }
    .logo-img {
        display: block;
        max-width: 180px !important;
        height: auto !important;
        max-height: 65px !important;
        object-fit: contain;
        background: transparent !important;
        border-radius: 6px;
        mix-blend-mode: multiply;
    }
    .logo-fallback {
        color: #FFFFFF !important;
        font-size: 26px;
        line-height: 1.1;
        font-weight: 900;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.8);
    }
    div.stButton > button[kind="primary"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #1A1A1A !important;
        border: 1.5px solid #C5C0B7 !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 68px !important;
        min-height: 68px !important;
        max-height: 68px !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        white-space: normal !important;
        line-height: 1.15 !important;
        box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.3) !important;
        padding: 4px 6px !important;
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
        font-weight: 800 !important;
        font-size: 12px !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #FFFFFF !important;
        border-color: #2C2C2C !important;
    }
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #D0CBC3 !important;
        border-radius: 6px !important;
        font-weight: 500 !important;
    }
    .streamlit-expanderHeader {
        background-color: #F3EFE6;
        border-radius: 6px;
    }
    .stSelectbox {
        margin-bottom: 4px !important;
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
        st.markdown('<div class="logo-container"><img src="data:' + mime + ';base64,' + logo_bin + '" class="logo-img" alt="Logo"></div>', unsafe_allow_html=True)
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
                nuovo_nome = st.text_input("Nome e cognome dipendente")
                registra_nome = st.form_submit_button("Registra")
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
                        st.success("Operatore registrato!")
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
                    accesso_admin = st.form_submit_button("Accedi")
                if accesso_admin:
                    if password_inserita == pwd_configurata:
                        st.session_state.admin_autenticato = True
                        st.session_state.ruolo = "Amministratore"
                        st.success("Accesso autorizzato!")
                        st.rerun()
                    else:
                        st.error("Password non corretta.")
                        st.session_state.ruolo = "Operatore"
            else:
                st.session_state.ruolo = "Amministratore"
                if st.button("Esci da Amministratore", key="logout_admin", type="secondary"):
                    st.session_state.admin_autenticato = False
                    st.session_state.ruolo = "Operatore"
                    st.session_state.ruolo_scelto = "Operatore"
                    st.rerun()
        else:
            st.session_state.ruolo = "Operatore"
            st.session_state.admin_autenticato = False

    st.markdown('<div style="margin-top: 4px;"></div>', unsafe_allow_html=True)
    
    riga_1_c1, riga_1_c2 = st.columns(2, gap="small")
    with riga_1_c1:
        if st.button("RAPPORTINO GIORNALIERO", key="btn_rap", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "RAPPORTINO"
            st.rerun()
    with riga_1_c2:
        if st.button("CALENDARIO E STORICO", key="btn_cal", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "CALENDARIO"
            st.rerun()

    st.markdown('<div style="margin-top: 4px;"></div>', unsafe_allow_html=True)
    
    riga_2_c1, riga_2_c2 = st.columns(2, gap="small")
    with riga_2_c1:
        if st.button("REGISTRO BILICI CIPPATO", key="btn_bil", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "BILICI"
            st.rerun()
    with riga_2_c2:
        if st.button("PARCO MACCHINE", key="btn_flotta", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "FLOTTA"
            st.rerun()

    st.markdown('<p style="text-align: center; color: #FFFFFF; font-weight: 600; font-size: 10px; margin-top: 8px; text-shadow: 1px 1px 2px #000;">Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali</p>', unsafe_allow_html=True)

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
        if not st.session_state.utente_corrente:
            st.error("Seleziona o registra prima il tuo nome nella Home.")
            st.stop()
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

    if st.session_state.ruolo == "Operatore":
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
                        "end": (dt_obj + timedelta(days=1)).strftime("%Y-%m-%d"),
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

            if st.session_state.ruolo == "Operatore":
                c.execute(
                    "SELECT * FROM rapportini_v3 WHERE data = ? AND utente = ?",
                    (data_sel_str, st.session_state.utente_corrente),
                )
            else:
                c.execute("SELECT * FROM rapportini_v3 WHERE data = ?", (data_sel_str,))
            rapporti_giorno = c.fetchall()

            if rapporti_giorno:
                st.markdown("#### Rapportini del **" + data_sel_str + "**")
                for rap in rapporti_giorno:
                    rap_id, r_data, r_ut, r_cli, r_ore, r_note = rap
                    expander_label = "Cliente: " + r_cli + " | Operatore: " + r_ut + " | Ore: " + str(r_ore) + "h"
                    with st.expander(expander_label):
                        st.write("**Operatore:** " + r_ut)
                        st.write("**Cliente:** " + r_cli)
                        st.write("**Ore Lavorate:** " + str(r_ore) + " ore")
                        note_text = r_note if r_note else 'Nessuna nota inserita'
                        st.write("**Note:** " + note_text)
                        
                        df_det = pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v3 WHERE rapportino_id = ?", conn, params=(rap_id,))
                        if not df_det.empty:
                            st.dataframe(df_det, use_container_width=True)
            else:
                st.info("Nessun rapportino presente per la data " + data_sel_str + ".")
        else:
            st.warning("Nessun rapportino salvato nel sistema.")

    with tab_lista:
        if st.session_state.ruolo != "Amministratore":
            st.info("La modifica e l'eliminazione dei rapportini sono riservate all'amministratore e ai soci autorizzati.")
        elif not df_rap.empty:
            st.dataframe(df_rap, use_container_width=True)
            st.markdown("---")
            st.subheader("Gestione / Modifica / Eliminazione Rapportino")
            id_selezionato = st.selectbox("Seleziona ID Rapportino:", df_rap['id'].tolist())
            
            row_sel = df_rap[df_rap['id'] == id_selezionato].iloc[0]
            with st.expander("Modifica Scheda #" + str(id_selezionato)):
                with st.form("form_edit_rap_v3"):
                    n_cliente = st.text_input("Cliente", value=row_sel['cliente'] or '')
                    n_ore = st.number_input("Ore Totali", value=float(row_sel['ore_totali']))
                    n_note = st.text_area("Note", value=row_sel['note'] or '')
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        b_up = st.form_submit_button("Aggiorna Rapportino")
                    with c_btn2:
                        b_del = st.form_submit_button("Elimina Rapportino")
                        
                    if b_up:
                        c.execute("UPDATE rapportini_v3 SET cliente=?, ore_totali=?, note=? WHERE id=?", (n_cliente, n_ore, n_note, id_selezionato))
                        conn.commit()
                        st.success("Rapportino aggiornato!")
                        st.rerun()
                    elif b_del:
                        c.execute("DELETE FROM rapportini_v3 WHERE id=?", (id_selezionato,))
                        c.execute("DELETE FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?", (id_selezionato,))
                        conn.commit()
                        st.warning("Rapportino eliminato!")
                        st.rerun()

# ==============================================================================
# MODULO 3: REGISTRO BILICI CIPPATO
# ==============================================================================
elif st.session_state.modulo_attivo == "BILICI":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Registro Spedizioni Bilici Cippato")

    with st.expander("Registra Nuova Partenza Bilico", expanded=True):
        with st.form("form_bilico_v3", clear_on_submit=True):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                data_partenza = st.date_input("Data di Partenza (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            with col_b2:
                cliente_b = st.text_input("Cliente / Destinazione", placeholder="Inserisci il nome del cliente o dell'impianto")

            sub_b = st.form_submit_button("Registra Partenza Bilico")
            if sub_b:
                data_b_fmt = data_partenza.strftime("%d/%m/%Y")
                c.execute("INSERT INTO bilici_v3 (data_partenza, cliente) VALUES (?,?)", (data_b_fmt, cliente_b))
                conn.commit()
                st.success("Partenza bilico registrata per il cliente '" + cliente_b + "' in data " + data_b_fmt + ".")

    df_bilici = pd.read_sql_query("SELECT data_partenza AS 'Data Partenza', cliente AS 'Cliente' FROM bilici_v3 ORDER BY id DESC", conn)
    st.subheader("Storico Partenze Bilici")
    if not df_bilici.empty:
        st.dataframe(df_bilici, use_container_width=True)
    else:
        st.info("Nessuna partenza registrata nel sistema.")

# ==============================================================================
# MODULO 4: PARCO MACCHINE & MANUTENZIONI
# ==============================================================================
elif st.session_state.modulo_attivo == "FLOTTA":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Gestione Parco Macchine & Attrezzature")

    if st.session_state.ruolo != "Amministratore":
        st.warning("La gestione del parco macchine e del registro manutenzioni è riservata all'amministratore e ai soci autorizzati.")
    else:
        tab1, tab2 = st.tabs(["Schede Mezzi & Ore Inizio Anno", "Registro Manutenzioni"])

        with tab1:
            st.subheader("Aggiungi Mezzo o Attrezzatura alla Flotta")
            with st.form("form_attrezzatura_v3", clear_on_submit=True):
                col_a, col_b, col_c, col_d = st.columns(4)
                with col_a:
                    nome_m = st.text_input("Nome / Modello Mezzo", placeholder="es. Valtra S400")
                with col_b:
                    tipo_c = st.selectbox("Unità di Misura", ["Ore", "Chilometri"])
                with col_c:
                    anno_rif = st.number_input("Anno Registrazione", min_value=2020, max_value=2035, value=current_year, step=1)
                with col_d:
                    valore_init = st.number_input("Ore/Km a Inizio Anno (" + str(anno_rif) + ")", min_value=0.0, step=10.0)

                sub_m = st.form_submit_button("Salva Mezzo")
                if sub_m:
                    try:
                        c.execute("INSERT INTO attrezzature_v3 (nome, tipo_conteggio, anno_riferimento, valore_inizio_anno) VALUES (?,?,?,?)",
                                  (nome_m, tipo_c, anno_rif, valore_init))
                        conn.commit()
                        st.success("Mezzo registrato con successo!")
                    except Exception:
                        st.error("Errore: Mezzo già presente a sistema.")

            df_att = pd.read_sql_query("SELECT nome AS 'Mezzo', tipo_conteggio AS 'Unità di Misura', anno_riferimento AS 'Anno Riferimento', valore_inizio_anno AS 'Valore Inizio Anno' FROM attrezzature_v3", conn)
            st.subheader("Flotta Aziendale")
            st.dataframe(df_att, use_container_width=True)

        with tab2:
            st.subheader("Registra Manutenzione / Intervento")
            c.execute("SELECT id, nome FROM attrezzature_v3")
            att_list = c.fetchall()

            if att_list:
                dict_att = {row[1]: row[0] for row in att_list}
                mezzo_man = st.selectbox("Seleziona Mezzo", list(dict_att.keys()))

                with st.form("form_manutenzione_v3", clear_on_submit=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        data_man = st.date_input("Data Intervento (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
                        tipo_m = st.selectbox("Tipo Intervento", ["Tagliando / Ordinaria", "Riparazione Straordinaria", "Sostituzione Lame / Catene / Ingrassaggio"])
                        ore_momento = st.number_input("Ore/Km della Macchina al momento del lavoro", min_value=0.0, step=5.0)
                    with col2:
                        eseguito = st.text_input("Eseguito Da", placeholder="es. Meccanico Interno / Officina Autorizzata")
                        costo = st.number_input("Costo Sostenuto (€)", min_value=0.0, step=10.0)
                        desc_man = st.text_area("Dettaglio Lavori Svolti e Pezzi Sostituiti")

                    sub_man = st.form_submit_button("Salva Manutenzione")
                    if sub_man:
                        data_m_fmt = data_man.strftime("%d/%m/%Y")
                        c.execute("INSERT INTO manutenzioni_v3 (attrezzatura_id, data, tipo, ore_km_al_momento, eseguito_da, descrizione, costo) VALUES (?,?,?,?,?,?,?)",
                                  (dict_att[mezzo_man], data_m_fmt, tipo_m, ore_momento, eseguito, desc_man, costo))
                        conn.commit()
                        st.success("Manutenzione registrata con successo!")

                df_man = pd.read_sql_query("""
                    SELECT m.data AS 'Data', a.nome AS 'Mezzo', m.tipo AS 'Tipo Intervento', m.ore_km_al_momento AS 'Ore/Km', 
                           m.eseguito_da AS 'Eseguito Da', m.descrizione AS 'Descrizione', m.costo AS 'Costo (€)' 
                    FROM manutenzioni_v3 m 
                    JOIN attrezzature_v3 a ON m.attrezzatura_id = a.id 
                    ORDER BY m.id DESC""", conn)
                st.subheader("Storico Manutenzioni")
                st.dataframe(df_man, use_container_width=True)
            else:
                st.warning("Aggiungi prima un mezzo nella scheda 'Schede Mezzi & Ore Inizio Anno'.")