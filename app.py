import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import os

# Per integrare il componente grafico calendario stile Google Calendar
try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

# Configurazione della Pagina
st.set_page_config(
    page_title="Nicoli Rizzi - Gestione Conto Terzi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Connessione / Inizializzazione Database SQLite
conn = sqlite3.connect('gestionale_cantiere.db', check_same_thread=False)
c = conn.cursor()

# Creazione Tabelle
c.execute('''CREATE TABLE IF NOT EXISTS rapportini_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    utente TEXT,
    cliente TEXT,
    ore_totali REAL,
    note TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS dettagli_lavorazioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rapportino_id INTEGER,
    ora_inizio TEXT,
    ora_fine TEXT,
    mezzo TEXT,
    descrizione TEXT,
    FOREIGN KEY(rapportino_id) REFERENCES rapportini_v2(id) ON DELETE CASCADE
)''')

c.execute('''CREATE TABLE IF NOT EXISTS bilici_v2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_partenza TEXT,
    cliente TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS attrezzature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    tipo_conteggio TEXT,
    valore_inizio_anno REAL
)''')

c.execute('''CREATE TABLE IF NOT EXISTS manutenzioni (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attrezzatura_id INTEGER,
    data TEXT,
    tipo TEXT,
    ore_km_al_momento REAL,
    eseguito_da TEXT,
    descrizione TEXT,
    costo REAL,
    FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature(id)
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
    
    with st.form("form_rapportino_v2"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_rep = st.date_input("Data Lavorazione (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            cliente = st.text_input("Cliente", placeholder="Inserisci il nome del cliente")
        with col_d2:
            ore_totali = st.number_input("Ore Totali Lavorate nella Giornata", min_value=0.0, step=0.5, value=8.0)
            note_giornaliere = st.text_area("Note / Osservazioni Generali", placeholder="Note complessive della giornata, consumo gasolio, condizioni meteo/terreno...")

        st.markdown("---")
        st.subheader("Dettaglio Lavorazioni della Giornata")
        st.caption("Puoi inserire più attività svolte nella stessa giornata specificando gli orari e i mezzi usati.")
        
        # Recupero mezzi salvati a database
        c.execute("SELECT nome FROM attrezzature")
        attrezzature_db = [row[0] for row in c.fetchall()]
        opzioni_mezzi = attrezzature_db + ["Altro / Inserimento Manuale"]

        # Inserimento dinamico di fino a 5 lavorazioni per foglio
        num_lavorazioni = st.number_input("Numero di lavorazioni svolte oggi:", min_value=1, max_value=8, value=1, step=1)
        
        lavorazioni_data = []
        for i in range(int(num_lavorazioni)):
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
                desc_lav = st.text_input(f"Descrizione Attività #{i+1}", placeholder="es. Cippatura ramaglie / Abbattimento", key=f"desc_{i}")
                
            lavorazioni_data.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), m_final, desc_lav))

        submitted = st.form_submit_button("Salva Rapportino Completo")
        if submitted:
            data_formatted = data_rep.strftime("%d/%m/%Y")
            
            # Inserisci la testata del rapportino
            c.execute("INSERT INTO rapportini_v2 (data, utente, cliente, ore_totali, note) VALUES (?,?,?,?,?)",
                      (data_formatted, utente_corrente, cliente, ore_totali, note_giornaliere))
            rap_id = c.lastrowid
            
            # Inserisci i dettagli delle singole lavorazioni
            for ora_in, ora_fi, m_final, desc_lav in lavorazioni_data:
                c.execute("INSERT INTO dettagli_lavorazioni (rapportino_id, ora_inizio, ora_fine, mezzo, descrizione) VALUES (?,?,?,?,?)",
                          (rap_id, ora_in, ora_fi, m_final, desc_lav))
                
            conn.commit()
            st.success(f"Rapportino per il cliente '{cliente}' registrato con successo in data {data_formatted}!")

# --- MODULO 2: CALENDARIO & STORICO ---
elif menu == "Calendario & Storico Rapportini":
    st.title("Calendario & Storico Rapportini")

    if ruolo == "Operatore / Dipendente":
        st.info(f"Visualizzazione riservata ai soli rapportini inseriti da: **{utente_corrente}**")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v2 WHERE utente = ? ORDER BY id DESC", conn, params=(utente_corrente,))
    else:
        st.success("Vista Amministratore / Socio: Monitoraggio completo dell'attività aziendale.")
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v2 ORDER BY id DESC", conn)

    tab_cal, tab_lista = st.tabs(["Vista Calendario Mensile", "Elenco Dettagliato & Modifica"])

    with tab_cal:
        st.subheader("Calendario delle Attività")
        
        if not df_rap.empty:
            # Creazione eventi per il grafico calendario
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
            else:
                st.caption("Modulo visuale esteso in fase di caricamento. Utilizzare il selettore data sottostante:")

            st.markdown("---")
            st.subheader("Consulta i Rapportini per Data Specifica")
            data_selezionata = st.date_input("Seleziona Giorno da Ispezionare", date.today(), format="DD/MM/YYYY")
            data_sel_str = data_selezionata.strftime("%d/%m/%Y")

            c.execute("SELECT * FROM rapportini_v2 WHERE data = ?", (data_sel_str,))
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
                        
                        # Recupero dettagli lavorazioni
                        df_det = pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni WHERE rapportino_id = ?", conn, params=(rap_id,))
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
                with st.form("form_edit_rap"):
                    n_cliente = st.text_input("Cliente", value=row_sel['cliente'])
                    n_ore = st.number_input("Ore Totali", value=float(row_sel['ore_totali']))
                    n_note = st.text_area("Note", value=row_sel['note'])
                    
                    c_btn1, c_btn2 = st.columns(2)
                    with c_btn1:
                        b_up = st.form_submit_button("Aggiorna Rapportino")
                    with c_btn2:
                        b_del = st.form_submit_button("Elimina Rapportino")
                        
                    if b_up:
                        c.execute("UPDATE rapportini_v2 SET cliente=?, ore_totali=?, note=? WHERE id=?", (n_cliente, n_ore, n_note, id_selezionato))
                        conn.commit()
                        st.success("Rapportino aggiornato!")
                        st.rerun()
                    elif b_del:
                        c.execute("DELETE FROM rapportini_v2 WHERE id=?", (id_selezionato,))
                        c.execute("DELETE FROM dettagli_lavorazioni WHERE rapportino_id=?", (id_selezionato,))
                        conn.commit()
                        st.warning("Rapportino eliminato!")
                        st.rerun()

# --- MODULO 3: REGISTRO BILICI CIPPATO ---
elif menu == "Registro Bilici Cippato":
    st.title("Registro Spedizioni Bilici Cippato")

    with st.expander("Registra Nuova Partenza Bilico", expanded=True):
        with st.form("form_bilico_v2", clear_on_submit=True):
            col_b1, col_b2 = st.columns(2)
            with col_b1:
                data_partenza = st.date_input("Data di Partenza (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            with col_b2:
                cliente_b = st.text_input("Cliente / Destinazione", placeholder="Inserisci il nome del cliente o dell'impianto")

            sub_b = st.form_submit_button("Registra Partenza Bilico")
            if sub_b:
                data_b_fmt = data_partenza.strftime("%d/%m/%Y")
                c.execute("INSERT INTO bilici_v2 (data_partenza, cliente) VALUES (?,?)", (data_b_fmt, cliente_b))
                conn.commit()
                st.success(f"Partenza bilico registrata per il cliente '{cliente_b}' in data {data_b_fmt}.")

    df_bilici = pd.read_sql_query("SELECT id AS 'ID', data_partenza AS 'Data Partenza', cliente AS 'Cliente' FROM bilici_v2 ORDER BY id DESC", conn)
    st.subheader("Storico Partenze Bilici")
    if not df_bilici.empty:
        st.dataframe(df_bilici, use_container_width=True)
    else:
        st.info("Nessuna partenza registrata nel sistema.")

# --- MODULO 4: PARCO MACCHINE & MANUTENZIONI ---
elif menu == "Parco Macchine & Manutenzioni":
    st.title("Gestione Parco Macchine & Attrezzature")

    tab1, tab2 = st.tabs(["Schede Mezzi & Ore Inizio Anno", "Registro Manutenzioni"])

    with tab1:
        st.subheader("Aggiungi Mezzo o Attrezzatura alla Flotta")
        with st.form("form_attrezzatura_v2", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                nome_m = st.text_input("Nome / Modello Mezzo", placeholder="es. Valtra S400 / Cippatrice JENZ")
            with col_b:
                tipo_c = st.selectbox("Unità di Misura Conteggio", ["Ore", "Chilometri"])
            with col_c:
                valore_init = st.number_input("Ore / Km a Inizio Anno (01/01)", min_value=0.0, step=10.0)

            sub_m = st.form_submit_button("Salva Mezzo")
            if sub_m:
                try:
                    c.execute("INSERT INTO attrezzature (nome, tipo_conteggio, valore_inizio_anno) VALUES (?,?,?)",
                              (nome_m, tipo_c, valore_init))
                    conn.commit()
                    st.success("Mezzo registrato con successo!")
                except Exception:
                    st.error("Errore: Mezzo già presente a sistema.")

        df_att = pd.read_sql_query("SELECT id AS 'ID', nome AS 'Mezzo', tipo_conteggio AS 'Unità', valore_inizio_anno AS 'Valore Inizio Anno' FROM attrezzature", conn)
        st.subheader("Flotta Aziendale")
        st.dataframe(df_att, use_container_width=True)

    with tab2:
        st.subheader("Registra Manutenzione / Intervento")
        c.execute("SELECT id, nome FROM attrezzature")
        att_list = c.fetchall()

        if att_list:
            dict_att = {row[1]: row[0] for row in att_list}
            mezzo_man = st.selectbox("Seleziona Mezzo", list(dict_att.keys()))

            with st.form("form_manutenzione_v2", clear_on_submit=True):
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
                    c.execute("""INSERT INTO manutenzioni (attrezzatura_id, data, tipo, ore_km_al_momento, eseguito_da, descrizione, costo) 
                                 VALUES (?,?,?,?,?,?,?)""",
                              (dict_att[mezzo_man], data_m_fmt, tipo_m, ore_momento, eseguito, desc_man, costo))
                    conn.commit()
                    st.success("Manutenzione registrata con successo!")

            df_man = pd.read_sql_query("""
                SELECT m.data AS 'Data', a.nome AS 'Mezzo', m.tipo AS 'Tipo Intervento', m.ore_km_al_momento AS 'Ore/Km', 
                       m.eseguito_da AS 'Eseguito Da', m.descrizione AS 'Descrizione', m.costo AS 'Costo (€)' 
                FROM manutenzioni m 
                JOIN attrezzature a ON m.attrezzatura_id = a.id 
                ORDER BY m.id DESC""", conn)
            st.subheader("Storico Manutenzioni")
            st.dataframe(df_man, use_container_width=True)
        else:
            st.warning("Aggiungi prima un mezzo nella scheda 'Schede Mezzi & Ore Inizio Anno'.")