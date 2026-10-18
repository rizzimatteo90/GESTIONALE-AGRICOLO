import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date

# Configurazione della Pagina
st.set_page_config(
    page_title="Gestionale Cantiere, Cippato & Flotta",
    page_icon="🚜",
    layout="wide"
)

# Connessione / Inizializzazione Database SQLite
conn = sqlite3.connect('gestionale_cantiere.db', check_same_thread=False)
c = conn.cursor()

# Creazione Tabelle
c.execute('''CREATE TABLE IF NOT EXISTS rapportini (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,
    utente TEXT,
    cantiere TEXT,
    ora_inizio TEXT,
    ora_fine TEXT,
    mezzo TEXT,
    ore_totali REAL,
    note TEXT
)''')

c.execute('''CREATE TABLE IF NOT EXISTS bilici (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data_ora TEXT,
    cantiere_origine TEXT,
    destinazione TEXT,
    vettore TEXT,
    targa TEXT,
    materiale TEXT,
    quantita_ton REAL,
    ddt_note TEXT
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

# --- SIDEBAR & PROFILO ---
st.sidebar.image("https://img.icons8.com/color/96/tractor.png", width=70)
st.sidebar.title("Gestionale Cantiere")

ruolo = st.sidebar.radio("Seleziona Ruolo Accesso:", ["👷 Operatore / Dipendente", "👔 Socio / Amministratore"])
utente_corrente = st.sidebar.text_input("Nome / Email Utente:", value="Mario Rossi")

menu = st.sidebar.selectbox("Navigazione Moduli:", [
    "📝 Inserimento Rapportino",
    "📅 Calendario & Storico Rapportini",
    "🚛 Registro Bilici Cippato",
    "🛠️ Parco Macchine & Manutenzioni"
])

st.sidebar.markdown("---")
st.sidebar.caption("© Gestionale Agricolo & Forestale")

# --- MODULO 1: RAPPORTINO GIORNALIERO ---
if menu == "📝 Inserimento Rapportino":
    st.header("📝 Inserimento Rapportino Giornaliero")
    st.info(f"Utente collegato: **{utente_corrente}** ({ruolo})")

    with st.form("form_rapportino", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            data_rep = st.date_input("Data Lavoro", date.today())
            cantiere = st.text_input("Cantiere / Cliente / Lotto Boschivo", placeholder="es. Bosco Tenuta Verde - Lotto 2")
            ora_inizio = st.time_input("Ora Inizio Lavorazione")
        with col2:
            ora_fine = st.time_input("Ora Fine Lavorazione")
            ore_totali = st.number_input("Ore Totali Lavorate nella Giornata", min_value=0.0, step=0.5, value=8.0)

        # Selezione Mezzo o Inserimento Manuale
        c.execute("SELECT nome FROM attrezzature")
        attrezzature_db = [row[0] for row in c.fetchall()]
        opzioni_mezzi = attrezzature_db + ["Altro / Inserimento Manuale"]

        mezzo_sel = st.selectbox("Mezzo / Attrezzatura Utilizzata", opzioni_mezzi)
        if mezzo_sel == "Altro / Inserimento Manuale":
            mezzo_finale = st.text_input("Specifica a mano il mezzo o l'attrezzatura usata:", placeholder="es. Motosega Stihl 661 / Spaccalegna")
        else:
            mezzo_finale = mezzo_sel

        note = st.text_area("Note, Commenti e Lavorazioni Svolte", placeholder="Descrivi il lavoro svolto, consumo gasolio, anomalie sui mezzi...")

        submitted = st.form_submit_button("💾 Salva Rapportino")
        if submitted:
            c.execute("""INSERT INTO rapportini (data, utente, cantiere, ora_inizio, ora_fine, mezzo, ore_totali, note) 
                         VALUES (?,?,?,?,?,?,?,?)""",
                      (str(data_rep), utente_corrente, cantiere, str(ora_inizio), str(ora_fine), mezzo_finale, ore_totali, note))
            conn.commit()
            st.success("✅ Rapportino inserito con successo!")

# --- MODULO 2: CALENDARIO & STORICO ---
elif menu == "📅 Calendario & Storico Rapportini":
    st.header("📅 Calendario & Storico Rapportini")

    if ruolo == "👷 Operatore / Dipendente":
        st.info(f"Visualizzazione e modifica limitata ai soli rapportini di: **{utente_corrente}**")
        df = pd.read_sql_query("SELECT * FROM rapportini WHERE utente = ? ORDER BY data DESC", conn, params=(utente_corrente,))
    else:
        st.success("Vista Amministratore: Accesso completo a tutti i rapportini aziendali.")
        df = pd.read_sql_query("SELECT * FROM rapportini ORDER BY data DESC", conn)

    if not df.empty:
        st.dataframe(df, use_container_width=True)
        
        # Sezione di modifica/eliminazione per il dipendente/amministratore
        st.subheader("✏️ Modifica o Elimina un Rapportino")
        id_list = df['id'].tolist()
        id_selezionato = st.selectbox("Seleziona ID Rapportino da Gestire:", id_list)
        
        row_sel = df[df['id'] == id_selezionato].iloc[0]
        with st.expander(f"Modifica Rapportino #{id_selezionato}"):
            with st.form("form_edit_rapportino"):
                new_cantiere = st.text_input("Cantiere", value=row_sel['cantiere'])
                new_mezzo = st.text_input("Mezzo", value=row_sel['mezzo'])
                new_ore = st.number_input("Ore Totali", value=float(row_sel['ore_totali']))
                new_note = st.text_area("Note", value=row_sel['note'])
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    btn_update = st.form_submit_button("💾 Aggiorna Rapportino")
                with col_btn2:
                    btn_delete = st.form_submit_button("🗑️ Elimina Rapportino")
                
                if btn_update:
                    c.execute("UPDATE rapportini SET cantiere=?, mezzo=?, ore_totali=?, note=? WHERE id=?",
                              (new_cantiere, new_mezzo, new_ore, new_note, id_selezionato))
                    conn.commit()
                    st.success("Rapportino aggiornato!")
                    st.rerun()
                elif btn_delete:
                    c.execute("DELETE FROM rapportini WHERE id=?", (id_selezionato,))
                    conn.commit()
                    st.warning("Rapportino eliminato!")
                    st.rerun()
    else:
        st.warning("Nessun rapportino trovato nel sistema.")

# --- MODULO 3: REGISTRO BILICI CIPPATO ---
elif menu == "🚛 Registro Bilici Cippato":
    st.header("🚛 Registro Partenze Bilici Cippato")

    with st.expander("➕ Registra Nuova Partenza Bilico", expanded=True):
        with st.form("form_bilico", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                data_ora_b = st.date_input("Data Partenza", date.today())
                cantiere_orig = st.text_input("Cantiere / Lotto Origine", placeholder="es. Cantiere Val Parma")
                destinazione = st.text_input("Destinazione / Centrale Biomassa", placeholder="es. Centrale Enel / Impianto X")
                vettore = st.text_input("Trasportatore / Ditta Vettore", placeholder="es. Trasporti Rossi Srl")
            with col2:
                targa = st.text_input("Targa Bilico / Camion", placeholder="es. FX123YY")
                materiale = st.selectbox("Tipologia Materiale", ["Cippato Ramaglie", "Cippato Tronchi / A1", "Ciocco", "Verde / Rifiuto", "Altro"])
                quantita = st.number_input("Peso / Quantità (Tonnellate o Quintali)", min_value=0.0, step=0.1)
                ddt_note = st.text_input("N° Formulario / DDT / Note", placeholder="es. DDT n. 450 - Umidità 35%")

            sub_b = st.form_submit_button("🚚 Registra Partenza Bilico")
            if sub_b:
                c.execute("""INSERT INTO bilici (data_ora, cantiere_origine, destinazione, vettore, targa, materiale, quantita_ton, ddt_note) 
                             VALUES (?,?,?,?,?,?,?,?)""",
                          (str(data_ora_b), cantiere_orig, destinazione, vettore, targa, materiale, quantita, ddt_note))
                conn.commit()
                st.success("✅ Partenza bilico registrata correttamente!")

    df_bilici = pd.read_sql_query("SELECT * FROM bilici ORDER BY id DESC", conn)
    st.subheader("📋 Storico Spedizioni Cippato")
    if not df_bilici.empty:
        st.dataframe(df_bilici, use_container_width=True)
        st.metric(label="Totale Materiale Spedito (Tonnellate/Q.li)", value=f"{df_bilici['quantita_ton'].sum():.2f}")
    else:
        st.info("Nessuna spedizione registrata al momento.")

# --- MODULO 4: PARCO MACCHINE & MANUTENZIONI ---
elif menu == "🛠️ Parco Macchine & Manutenzioni":
    st.header("🛠️ Gestione Parco Macchine & Manutenzioni")

    tab1, tab2 = st.tabs(["🚜 Schede Mezzi & Ore Inizio Anno", "🔧 Registro Manutenzioni"])

    with tab1:
        st.subheader("Registra Nuovo Mezzo / Attrezzatura")
        with st.form("form_attrezzatura", clear_on_submit=True):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                nome_m = st.text_input("Nome / Modello Mezzo", placeholder="es. Valtra S400 / JENZ HEM 583")
            with col_b:
                tipo_c = st.selectbox("Unità di Misura Conteggio", ["Ore", "Chilometri"])
            with col_c:
                valore_init = st.number_input("Ore / Km a Inizio Anno (01/01)", min_value=0.0, step=10.0)

            sub_m = st.form_submit_button("💾 Salva Mezzo in Flotta")
            if sub_m:
                try:
                    c.execute("INSERT INTO attrezzature (nome, tipo_conteggio, valore_inizio_anno) VALUES (?,?,?)",
                              (nome_m, tipo_c, valore_init))
                    conn.commit()
                    st.success("✅ Mezzo aggiunto alla flotta!")
                except Exception as e:
                    st.error("Errore: Il mezzo potrebbe essere già stato registrato.")

        df_att = pd.read_sql_query("SELECT * FROM attrezzature", conn)
        st.subheader("📋 Parco Macchine Aziendale")
        st.dataframe(df_att, use_container_width=True)

    with tab2:
        st.subheader("Registra Intervento di Manutenzione / Tagliando")
        c.execute("SELECT id, nome FROM attrezzature")
        att_list = c.fetchall()

        if att_list:
            dict_att = {row[1]: row[0] for row in att_list}
            mezzo_man = st.selectbox("Seleziona Mezzo / Macchina", list(dict_att.keys()))

            with st.form("form_manutenzione", clear_on_submit=True):
                col1, col2 = st.columns(2)
                with col1:
                    data_man = st.date_input("Data Intervento", date.today())
                    tipo_m = st.selectbox("Tipologia Intervento", ["Tagliando / Ordinaria", "Riparazione Straordinaria", "Sostituzione Lame / Catene / Ingrassaggio"])
                    ore_momento = st.number_input("Ore/Km della Macchina al momento del lavoro", min_value=0.0, step=5.0)
                with col2:
                    eseguito = st.text_input("Eseguito Da", placeholder="es. Meccanico Interno / Officina Autorizzata")
                    costo = st.number_input("Costo Sostenuto (€)", min_value=0.0, step=10.0)
                    desc_man = st.text_area("Dettaglio Lavori, Pezzi Sostituiti, Olio, Filtri...")

                sub_man = st.form_submit_button("🔧 Salva Manutenzione")
                if sub_man:
                    c.execute("""INSERT INTO manutenzioni (attrezzatura_id, data, tipo, ore_km_al_momento, eseguito_da, descrizione, costo) 
                                 VALUES (?,?,?,?,?,?,?)""",
                              (dict_att[mezzo_man], str(data_man), tipo_m, ore_momento, eseguito, desc_man, costo))
                    conn.commit()
                    st.success("✅ Manutenzione registrata con successo!")

            df_man = pd.read_sql_query("""
                SELECT m.data, a.nome AS Mezzo, m.tipo, m.ore_km_al_momento AS Ore_Km, 
                       m.eseguito_da, m.descrizione, m.costo AS Costo_Euro 
                FROM manutenzioni m 
                JOIN attrezzature a ON m.attrezzatura_id = a.id 
                ORDER BY m.id DESC""", conn)
            st.subheader("📜 Storico Manutenzioni Svolte")
            st.dataframe(df_man, use_container_width=True)
        else:
            st.warning("Aggiungi prima un mezzo nella scheda 'Schede Mezzi & Ore Inizio Anno'.")
