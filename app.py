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

# --- STILE GRAFICO PERSONALIZZATO ---
st.markdown("""
    <style>
    .stApp {
        background-color: #F9F6F0;
        color: #2C2C2C;
    }
    [data-testid="stSidebar"] {
        background-color: #F3EFE6;
        border-right: 1px solid #E5E0D8;
    }
    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #2C2C2C !important;
    }
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
    div.stButton > button[kind="secondary"] {
        background-color: #FFFFFF !important;
        color: #2C2C2C !important;
        border: 1px solid #CCCCCC !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background-color: #EFEFEF !important;
        color: #000000 !important;
    }
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
c.execute('''CREATE TABLE IF NOT EXISTS dipendenti (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    ruolo_default TEXT
)''')

c.execute("SELECT COUNT(*) FROM dipendenti")
if c.fetchone()[0] == 0:
    c.execute("INSERT INTO dipendenti (nome, ruolo_default) VALUES (?, ?)", ("Mario Rossi", "Operatore / Dipendente"))
    conn.commit()

c.execute('''CREATE TABLE IF NOT EXISTS rapportini_v4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    utente TEXT,
    cliente TEXT,
    ore_totali REAL,
    note TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS dettagli_lavorazioni_v4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rapportino_id INTEGER,
    ora_inizio TEXT,
    ora_fine TEXT,
    mezzo TEXT,
    descrizione TEXT,
    FOREIGN KEY(rapportino_id) REFERENCES rapportini_v4(id) ON DELETE CASCADE
)''')

c.execute('''CREATE TABLE IF NOT EXISTS bilici_v4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_partenza TEXT,
    cliente TEXT
)''')

current_year = datetime.now().year
c.execute('''CREATE TABLE IF NOT EXISTS attrezzature_v4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    tipo_conteggio TEXT,
    anno_riferimento INTEGER,
    valore_inizio_anno REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS manutenzioni_v4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attrezzatura_id INTEGER,
    data TEXT,
    tipo TEXT,
    ore_km_al_momento REAL,
    eseguito_da TEXT,
    descrizione TEXT,
    costo REAL,
    FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature_v4(id)
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

if 'ruolo_sel' not in st.session_state:
    st.session_state.ruolo_sel = "Operatore / Dipendente"
if 'utente_sel' not in st.session_state:
    st.session_state.utente_sel = "Mario Rossi"

ruolo = st.sidebar.radio(
    "Ruolo Operativo:",
    ["Operatore / Dipendente", "Socio / Amministratore"],
    index=0 if st.session_state.ruolo_sel == "Operatore / Dipendente" else 1
)
st.session_state.ruolo_sel = ruolo

c.execute("SELECT nome FROM dipendenti ORDER BY nome ASC")
lista_dipendenti = [row[0] for row in c.fetchall()]
if not lista_dipendenti:
    lista_dipendenti = ["Mario Rossi"]

idx_ut = lista_dipendenti.index(st.session_state.utente_sel) if st.session_state.utente_sel in lista_dipendenti else 0

if ruolo == "Socio / Amministratore":
    utente_corrente = st.sidebar.selectbox("Seleziona Utente Amministratore / Socio:", lista_dipendenti, index=idx_ut)
else:
    utente_corrente = st.sidebar.selectbox("Il tuo Nome (Operatore):", lista_dipendenti, index=idx_ut)

st.session_state.utente_sel = utente_corrente

menu_opzioni = [
    "Rapportino Giornaliero",
    "Calendario & Storico Rapportini",
    "Registro Bilici Cippato",
    "Parco Macchine & Manutenzioni"
]

if ruolo == "Socio / Amministratore":
    menu_opzioni.append("⚙️ Gestione Dipendenti & Personale")

menu = st.sidebar.selectbox("Modulo di Lavoro:", menu_opzioni)

st.sidebar.markdown("---")
st.sidebar.caption("Nicoli Rizzi S.r.l. - Gestione Operativa")

# --- MODULO 1: RAPPORTINO GIORNALIERO ---
if menu == "Rapportino Giornaliero":
    st.title("Rapportino Giornaliero Attività")
    st.caption(f"Utente collegato: **{utente_corrente}** ({ruolo})")

    with st.form("form_rapportino_v4"):
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

        c.execute("SELECT nome FROM attrezzature_v4")
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
        c.execute("INSERT INTO rapportini_v4 (data, utente, cliente, ore_totali, note) VALUES (?,?,?,?,?)",
                  (data_formatted, utente_corrente, cliente, ore_totali, note_giornaliere))
        rap_id = c.lastrowid

        for ora_in, ora_fi, m_final, desc_lav in lavorazioni_data:
            c.execute("INSERT INTO dettagli_lavorazioni_v4 (rapportino_id, ora_inizio, ora_fine, mezzo, descrizione) VALUES (?,?,?,?,?)",
                      (rap_id, ora_in, ora_fi, m_final, desc_lav))

        conn.commit()
        st.session_state.num_righe_lavoro = 1
        st.success(f"Rapportino per il cliente '{cliente}' registrato con successo in data {data_formatted}!")

# --- MODULO 2: CALENDARIO & STORICO ---
elif menu == "Calendario & Storico Rapportini":
    st.title("Calendario & Storico Rapportini")

    if ruolo == "Operatore / Dipendente":
        st.info(f"Visualizzazione riservata ai soli rapportini inseriti da: **{utente_corrente}**")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v4 WHERE utente = ? ORDER BY id DESC", conn, params=(utente_corrente,))
    else:
        st.success("Vista Amministratore / Socio: Monitoraggio completo dell'attività aziendale.")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v4 ORDER BY id DESC", conn)

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

            if ruolo == "Operatore / Dipendente":
                c.execute("SELECT * FROM rapportini_v4 WHERE data = ? AND utente = ?", (data_sel_str, utente_corrente))
            else:
                c.execute("SELECT * FROM rapportini_v4 WHERE data = ?", (data_sel_str,))
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

                        df_det = pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v4 WHERE rapportino_id = ?", conn, params=(rap_id,))
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
                with st.form("form_edit_rap_v4"):
                    n_cliente = st.text_input("Cliente", value=row_sel['cliente'])
                    n_ore = st.number_input("Ore Totali", value=float(row_sel['ore_totali']))
                    n_note = st.text_area("Note", value=row_sel['note'])

                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        b_up = st.form_submit_button("Aggiorna Rapportino")
                    with c_btn2:
                        b_del = st.form_submit_button("Elimina Rapportino")

                    if b_up:
                        c.execute("UPDATE rapportini_v4 SET cliente=?, ore_totali=?, note=? WHERE id=?", (n_cliente, n_ore, n_note, id_selezionato))
                        conn.commit()
                        st.success("Rapportino aggiornato!")
                        st.rerun()
                    elif b_del:
                        c.execute("DELETE FROM rapportini_v4 WHERE id=?", (id_selezionato,))
                        c.execute("DELETE FROM dettagli_lavorazioni_v4 WHERE rapportino_id=?", (id_selezionato,))
                        conn.commit()
                        st.warning("Rapportino eliminato!")
                        st.rerun()

# --- MODULO 3: REGISTRO BILICI CIPPATO ---
elif menu == "Registro Bilici Cippato":
    st.title("Registro