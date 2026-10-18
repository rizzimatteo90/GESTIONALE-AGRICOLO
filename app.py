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
    initial_sidebar_state="collapsed"
)

# --- STILE GRAFICO PERSONALIZZATO ---
st.markdown("""
    <style>
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

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# ==============================================================================
# SCHERMATA HOME PAGE
# ==============================================================================
if st.session_state.modulo_attivo == "HOME":
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

    c_u1, c_u2 = st.columns(2)
    with c_u1:
        st.session_state.utente_corrente = st.text_input("Operatore / Utente:", value=st.session_state.utente_corrente)
    with c_u2:
        st.session_state.ruolo = st.selectbox("Ruolo Operativo:", ["Operatore / Dipendente", "Socio / Amministratore"], index=0 if st.session_state.ruolo == "Operatore / Dipendente" else 1)

    st.markdown("<br>", unsafe_allow_html=True)

    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("""<div class="home-card"><h3>📋 RAPPORTINO GIORNALIERO</h3><p>Inserisci le attività svolte, gli orari, i mezzi usati e le ore totali.</p></div>""", unsafe_allow_html=True)
        if st.button("Apri Rapportino Giornaliero", use_container_width=True):
            st.session_state.modulo_attivo = "RAPPORTINO"
            st.rerun()

    with row1_col2:
        st.markdown("""<div class="home-card"><h3>📅 CALENDARIO & STORICO</h3><p>Consulta il calendario mensile delle attività e lo storico dei rapportini.</p></div>""", unsafe_allow_html=True)
        if st.button("Apri Calendario & Storico", use_container_width=True):
            st.session_state.modulo_attivo = "CALENDARIO"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("""<div class="home-card"><h3>🚛 REGISTRO BILICI CIPPATO</h3><p>Registra le uscite e le partenze dei bilici di cippato per i clienti.</p></div>""", unsafe_allow_html=True)
        if st.button("Apri Registro Bilici Cippato", use_container_width=True):
            st.session_state.modulo_attivo = "BILICI"
            st.rerun()

    with row2_col2:
        st.markdown("""<div class="home-card"><h3>🛠️ PARCO MACCHINE & MANUTENZIONI</h3><p>Gestisci i mezzi aziendali, le ore/km di inizio anno e il registro tagliandi.</p></div>""", unsafe_allow_html=True)
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
        if st.button("➕ Aggiungi un'altra riga di lavoro", type="secondary"):
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
        st.success(f"Rapportino per il cliente '{cliente}' registrato con successo in data {data_formatted}!")

# ==============================================================================
# MODULO 2: CALENDARIO & STORICO
# ==============================================================================
elif st.session_state.modulo_attivo == "CALENDARIO":
    st.button("⬅️ Torna alla Home", on_click=torna_home)
    st.title("Calendario & Storico Rapportini")

    if st.session_state.ruolo == "Operatore / Dipendente":
        st.info(f"Visualizzazione riservata ai soli rapportini inseriti da: **{st.session_state.utente_corrente}**")
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
                        "title": f"{r['utente']} - {r['cliente']} ({r['ore_totali']}h)",
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
                st.markdown(f"#### Rapportini del **{data_sel_str}**")
                for rap in rapporti_giorno:
                    rap_id, r_data, r_ut, r_cli, r_ore, r_note = rap
                    with st.expander(f"Cliente: {r_cli} | Operatore: {r_ut} | Ore Totali: {r_ore}h"):
                        st.write(f"**Operatore:** {r_ut}")
                        st.write(f"**Cliente:** {r_cli}")
                        st.write(f"**Ore Lavorate:** {r_ore} ore")
                        st.write(f"**Note:** {r_note if r_note else 'Nessuna nota inserita'}")
                        
                        df_det = pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v3 WHERE rapportino_id = ?", conn, params=(rap_id,))
                        if not df_det.empty:
                            st.dataframe(df_det, use_container_width=True)
            else:
                st.info(f"Nessun rapportino presente per la data {data_sel_str}.")
        else:
            st.warning("Nessun rapportino salvato nel sistema.")

    with tab_lista:
        if not df_rap.empty:
            st.dataframe(df_rap, use_container_width=True)
            st.markdown("---")
            st.subheader("Gestione / Modifica / Eliminazione Rapportino")
            id_selezionato = st.selectbox("Seleziona ID Rapportino:", df_rap['id'].tolist())
            
            row_sel = df_rap[df_rap['id'] == id_selezionato].iloc[0]
            with st.expander(f"Modifica Scheda #{id_selezionato}"):
                with st.form("form_edit_rap_v3"):
                    n_cliente = st.text_input("Cliente", value=row_sel['cliente'])
                    n_ore = st.number_input("Ore Totali", value=float(row_sel['ore_totali']))
                    n_note = st.text_area("Note", value=row_sel['note'])
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        b_up = st.form_submit_button("Aggiorna Rapportino")
                    with c_btn2:
                        b_del = st.form_submit_button("Elimina Rapportino")
                        
                    if b_up:
                        c.execute("UPDATE rapportini_v3 SET cliente=?, ore_totali=?, note=? WHERE id=?", (n_cliente, n_ore, n_note, id_selezionato))
                        conn.commit()