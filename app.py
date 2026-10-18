import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import os
import base64
import plotly.express as px

from database import init_db, get_connection
from pdf_reports import genera_pdf_rapportino, genera_pdf_report_mensile

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

init_db()
conn = get_connection()
c = conn.cursor()

def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    except Exception:
        return ""

bg_image_path = "sfondo.jpg" if os.path.exists("sfondo.jpg") else ("IMG_8234.jpg" if os.path.exists("IMG_8234.jpg") else None)
bin_str = get_base64_of_bin_file(bg_image_path) if bg_image_path else ""

is_home = st.session_state.get('modulo_attivo', 'HOME') == 'HOME'
bg_css = f".stApp {{ background: linear-gradient(rgba(0,0,0,0.60), rgba(0,0,0,0.60)), url('data:image/jpeg;base64,{bin_str}'); background-size: cover; background-position: center; background-attachment: fixed; }}" if (bin_str and is_home) else ".stApp { background-color: #F9F6F0; color: #2C2C2C; }"

text_color = "#FFFFFF" if is_home and bin_str else "#2C2C2C"
label_shadow = "1px 1px 2px rgba(0,0,0,0.8)" if is_home and bin_str else "none"

st.markdown(f"""
    <style>
    {bg_css}
    [data-testid="stSidebar"] {{ display: none; }}
    header {{ visibility: hidden !important; height: 0px !important; }}
    .block-container {{ padding: 0.4rem 0.8rem 2.5rem 0.8rem !important; max-width: 520px !important; margin: 0 auto !important; }}
    h1, h2, h3, h4, h5, h6, span, p, [data-testid="stMarkdownContainer"] {{ color: {text_color} !important; }}
    label {{ color: {text_color} !important; font-weight: 600 !important; font-size: 13px !important; text-shadow: {label_shadow}; margin-bottom: 2px !important; }}
    
    .logo-container {{ width: 100%; display: flex; align-items: center; justify-content: center; padding: 6px 0 10px 0; background: transparent !important; }}
    .logo-img {{ 
        display: block; 
        max-width: 210px !important; 
        max-height: 140px !important; 
        object-fit: contain; 
        background: transparent !important;
        mix-blend-mode: screen;
        filter: invert(1) grayscale(1) brightness(2.2);
    }}
    .logo-fallback {{ color: #FFFFFF !important; font-size: 26px; font-weight: 900; text-align: center; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }}
    
    .footer-azienda {{
        width: 100%;
        background-color: rgba(0, 0, 0, 0.75);
        color: #FFFFFF !important;
        text-align: center;
        padding: 10px 8px;
        margin-top: 25px;
        margin-bottom: 20px;
        border-radius: 8px;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.5);
    }}

    div.stButton > button[kind="primary"] {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        color: #000000 !important;
        border: 1.5px solid #C5C0B7 !important;
        border-radius: 10px !important;
        width: 100% !important;
        height: 62px !important;
        font-size: 12px !important;
        font-weight: 900 !important;
        line-height: 1.15 !important;
        box-shadow: 0px 3px 8px rgba(0, 0, 0, 0.3) !important;
        padding: 4px 6px !important;
    }}
    div.stButton > button[kind="primary"] p,
    div.stButton > button[kind="primary"] span {{
        color: #000000 !important;
        font-weight: 900 !important;
    }}
    div.stButton > button[kind="secondary"] {{ background-color: #FFFFFF !important; color: #2C2C2C !important; border: 1px solid #D0CBC3 !important; border-radius: 6px !important; }}
    </style>
""", unsafe_allow_html=True)

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

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# ==============================================================================
# HOME PAGE
# ==============================================================================
if st.session_state.modulo_attivo == "HOME":
    logo_file = None
    for filename in ["IMG_7106.jpg", "logo.png", "logo.jpg", "LOGO.png", "LOGO.jpg", "logo.jpeg"]:
        if os.path.exists(filename):
            logo_file = filename
            break

    if logo_file:
        logo_bin = get_base64_of_bin_file(logo_file)
        mime = "image/png" if logo_file.lower().endswith(".png") else "image/jpeg"
        st.markdown(f'''
            <div class="logo-container">
                <img src="data:{mime};base64,{logo_bin}" class="logo-img" alt="Logo">
            </div>
        ''', unsafe_allow_html=True)
    else:
        st.markdown('''
            <div class="logo-container">
                <div class="logo-fallback">NICOLI RIZZI</div>
            </div>
        ''', unsafe_allow_html=True)

    c.execute("SELECT nome FROM utenti_app ORDER BY nome COLLATE NOCASE")
    utenti_registrati = [r[0] for r in c.fetchall()]
    opzioni_utenti = ["-- Seleziona operatore --"] + utenti_registrati + ["+ Registra nuovo operatore"]
    
    idx_default = opzioni_utenti.index(st.session_state.utente_corrente) if st.session_state.utente_corrente in utenti_registrati else 0
    selezione_utente = st.selectbox("Operatore:", opzioni_utenti, index=idx_default, key="selezione_utente_home")

    if selezione_utente == "+ Registra nuovo operatore":
        with st.form("registra_operatore_form"):
            nuovo_nome = st.text_input("Nome e cognome dipendente")
            if st.form_submit_button("Registra"):
                nome_pulito = " ".join(nuovo_nome.split())
                if nome_pulito:
                    try:
                        c.execute("INSERT INTO utenti_app (nome) VALUES (?)", (nome_pulito,))
                        conn.commit()
                        st.session_state.utente_corrente = nome_pulito
                        st.rerun()
                    except Exception:
                        pass
    elif selezione_utente != "-- Seleziona operatore --":
        st.session_state.utente_corrente = selezione_utente

    scelta_ruolo = st.selectbox("Ruolo:", ["Operatore", "Amministratore"], key="ruolo_scelto")
    if scelta_ruolo == "Amministratore":
        if not st.session_state.admin_autenticato:
            with st.form("login_amministratore_form"):
                password_inserita = st.text_input("Password amministratore", type="password")
                if st.form_submit_button("Accedi"):
                    if password_inserita == password_amministratore_configurata():
                        st.session_state.admin_autenticato = True
                        st.session_state.ruolo = "Amministratore"
                        st.rerun()
                    else:
                        st.error("Password non corretta.")
        else:
            st.session_state.ruolo = "Amministratore"
            if st.button("Esci da Amministratore", key="logout_admin", type="secondary"):
                st.session_state.admin_autenticato = False
                st.session_state.ruolo = "Operatore"
                st.rerun()
    else:
        st.session_state.ruolo = "Operatore"

    st.markdown('<div style="margin-top: 6px;"></div>', unsafe_allow_html=True)
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
        if st.button("PARCO MACCHINE & REPORT", key="btn_flotta", type="primary", use_container_width=True):
            st.session_state.modulo_attivo = "FLOTTA"
            st.rerun()

    # Scritta aziendale staccata in basso
    st.markdown('''
        <div class="footer-azienda">
            Nicoli Rizzi S.R.L. - Lavorazioni Agro Forestali in Contoterzi
        </div>
    ''', unsafe_allow_html=True)

# ==============================================================================
# MODULO 1: RAPPORTINO GIORNALIERO
# ==============================================================================
elif st.session_state.modulo_attivo == "RAPPORTINO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Rapportino Giornaliero")
    
    with st.form("form_rapportino_v3"):
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            data_rep = st.date_input("Data Lavorazione", date.today(), format="DD/MM/YYYY")
            cliente = st.text_input("Cliente", placeholder="Nome cliente")
        with col_d2:
            ore_totali = st.number_input("Ore Totali Lavorate", min_value=0.0, step=0.5, value=8.0)
            note_giornaliere = st.text_area("Note / Gasolio / Meteo", placeholder="Note generali...")

        c.execute("SELECT nome FROM attrezzature_v3")
        opzioni_mezzi = [row[0] for row in c.fetchall()] + ["Altro / Inserimento Manuale"]

        if 'num_righe_lavoro' not in st.session_state:
            st.session_state.num_righe_lavoro = 1

        lavorazioni_data = []
        for i in range(st.session_state.num_righe_lavoro):
            st.markdown(f"**Lavorazione #{i+1}**")
            col_l1, col_l2, col_l3 = st.columns([1, 2, 2])
            with col_l1:
                ora_in = st.time_input(f"Inizio #{i+1}", value=datetime.strptime("07:30", "%H:%M").time(), key=f"in_{i}")
                ora_fi = st.time_input(f"Fine #{i+1}", value=datetime.strptime("12:00", "%H:%M").time(), key=f"fi_{i}")
            with col_l2:
                m_sel = st.selectbox(f"Mezzo #{i+1}", opzioni_mezzi, key=f"m_sel_{i}")
                m_final = st.text_input(f"Specifica mezzo #{i+1}", key=f"m_man_{i}") if m_sel == "Altro / Inserimento Manuale" else m_sel
            with col_l3:
                desc_lav = st.text_input(f"Attività #{i+1}", placeholder="es. Cippatura", key=f"desc_{i}")
                
            lavorazioni_data.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), m_final, desc_lav))

        submitted = st.form_submit_button("Salva Rapportino")

    if st.button("Aggiungi riga di lavoro", type="secondary"):
        st.session_state.num_righe_lavoro += 1
        st.rerun()

    if submitted:
        if not st.session_state.utente_corrente:
            st.error("Seleziona prima il tuo nome nella Home.")
        else:
            data_formatted = data_rep.strftime("%d/%m/%Y")
            c.execute("INSERT INTO rapportini_v3 (data, utente, cliente, ore_totali, note) VALUES (?,?,?,?,?)",
                      (data_formatted, st.session_state.utente_corrente, cliente, ore_totali, note_giornaliere))
            rap_id = c.lastrowid
            
            for ora_in, ora_fi, m_final, desc_lav in lavorazioni_data:
                c.execute("INSERT INTO dettagli_lavorazioni_v3 (rapportino_id, ora_inizio, ora_fine, mezzo, descrizione) VALUES (?,?,?,?,?)",
                          (rap_id, ora_in, ora_fi, m_final, desc_lav))
                
            conn.commit()
            st.session_state.num_righe_lavoro = 1
            st.success(f"Rapportino salvato con successo per il {data_formatted}!")

# ==============================================================================
# MODULO 2: CALENDARIO & STORICO
# ==============================================================================
elif st.session_state.modulo_attivo == "CALENDARIO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Calendario & Storico")

    if st.session_state.ruolo == "Operatore":
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v3 WHERE utente = ? ORDER BY id DESC", conn, params=(st.session_state.utente_corrente,))
    else:
        df_rap = pd.read_sql_query("SELECT * FROM rapportini_v3 ORDER BY id DESC", conn)

    tab_cal, tab_lista = st.tabs(["Calendario", "Elenco & Gestione"])

    with tab_cal:
        if not df_rap.empty and HAS_CALENDAR:
            events = []
            for _, r in df_rap.iterrows():
                try:
                    dt_obj = datetime.strptime(r['data'], "%d/%m/%Y")
                    events.append({
                        "title": f"{r['utente']} - {r['cliente']} ({r['ore_totali']}h)",
                        "start": dt_obj.strftime("%Y-%m-%d"),
                        "end": (dt_obj + timedelta(days=1)).strftime("%Y-%m-%d"),
                        "allDay": True
                    })
                except Exception:
                    pass
            calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}, "locale": "it"}, key="cal_view")

    with tab_lista:
        if not df_rap.empty:
            st.dataframe(df_rap, use_container_width=True)

# ==============================================================================
# MODULO 3: REGISTRO BILICI
# ==============================================================================
elif st.session_state.modulo_attivo == "BILICI":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Registro Bilici Cippato")

    with st.form("form_bilico_v3", clear_on_submit=True):
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            data_partenza = st.date_input("Data Partenza", date.today(), format="DD/MM/YYYY")
        with col_b2:
            cliente_b = st.text_input("Cliente / Destinazione")
        if st.form_submit_button("Registra Partenza"):
            c.execute("INSERT INTO bilici_v3 (data_partenza, cliente) VALUES (?,?)", (data_partenza.strftime("%d/%m/%Y"), cliente_b))
            conn.commit()
            st.success("Bilico registrato!")

    df_bilici = pd.read_sql_query("SELECT data_partenza AS 'Data Partenza', cliente AS 'Cliente' FROM bilici_v3 ORDER BY id DESC", conn)
    st.dataframe(df_bilici, use_container_width=True)

# ==============================================================================
# MODULO 4: FLOTTA, MANUTENZIONI & REPORT PDF AMMINISTRATORE
# ==============================================================================
elif st.session_state.modulo_attivo == "FLOTTA":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Parco Macchine & Report Amministratore")

    if st.session_state.ruolo != "Amministratore":
        st.warning("Area riservata esclusivamente all'amministratore.")
    else:
        tab1, tab2, tab_pdf, tab_grafici = st.tabs(["Mezzi", "Manutenzioni", "📄 Report PDF", "📊 Grafici"])

        with tab1:
            with st.form("form_attrezzatura_v3", clear_on_submit=True):
                nome_m = st.text_input("Nome / Modello Mezzo")
                tipo_c = st.selectbox("Unità", ["Ore", "Chilometri"])
                valore_init = st.number_input("Valore Inizio Anno", min_value=0.0)
                if st.form_submit_button("Salva Mezzo"):
                    try:
                        c.execute("INSERT INTO attrezzature_v3 (nome, tipo_conteggio, anno_riferimento, valore_inizio_anno) VALUES (?,?,?,?)",
                                  (nome_m, tipo_c, datetime.now().year, valore_init))
                        conn.commit()
                        st.success("Mezzo salvato!")
                    except Exception:
                        st.error("Mezzo già esistente.")

            df_att = pd.read_sql_query("SELECT nome AS 'Mezzo', tipo_conteggio AS 'Unità', valore_inizio_anno AS 'Inizio Anno' FROM attrezzature_v3", conn)
            st.dataframe(df_att, use_container_width=True)

        with tab2:
            df_man = pd.read_sql_query("""
                SELECT m.data AS 'Data', a.nome AS 'Mezzo', m.tipo AS 'Tipo Intervento', m.costo AS 'Costo (€)' 
                FROM manutenzioni_v3 m JOIN attrezzature_v3 a ON m.attrezzatura_id = a.id ORDER BY m.id DESC""", conn)
            st.dataframe(df_man, use_container_width=True)

        with tab_pdf:
            st.subheader("Generazione Report PDF (Riservato Admin)")
            
            scelta_pdf = st.selectbox("Seleziona Tipo di Report", ["Rapportino Giornaliero", "Report Mensile Dipendente", "Report Mensile Aziendale"])
            
            if scelta_pdf == "Rapportino Giornaliero":
                df_tutti = pd.read_sql_query("SELECT id, data, utente, cliente, ore_totali FROM rapportini_v3 ORDER BY id DESC", conn)
                if not df_tutti.empty:
                    id_rap = st.selectbox("Seleziona Rapportino", df_tutti['id'].tolist(), format_func=lambda x: f"ID {x} - {df_tutti[df_tutti['id']==x]['data'].values[0]} ({df_tutti[df_tutti['id']==x]['cliente'].values[0]})")
                    
                    c.execute("SELECT * FROM rapportini_v3 WHERE id=?", (id_rap,))
                    r_dati = c.fetchone()
                    df_det = pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v3 WHERE rapportino_id = ?", conn, params=(id_rap,))
                    
                    pdf_b = genera_pdf_rapportino(r_dati[1], r_dati[2], r_dati[3], r_dati[4], r_dati[5], df_det)
                    st.download_button("📄 Scarica PDF Rapportino", data=pdf_b, file_name=f"Rapportino_{r_dati[3]}_{r_dati[1].replace('/','-')}.pdf", mime="application/pdf", type="primary")

            elif scelta_pdf == "Report Mensile Dipendente":
                c.execute("SELECT DISTINCT utente FROM rapportini_v3")
                utenti_db = [r[0] for r in c.fetchall()]
                if utenti_db:
                    u_sel = st.selectbox("Seleziona Dipendente", utenti_db)
                    m_sel = st.selectbox("Mese (MM/AAAA)", ["10/2026", "09/2026", "11/2026", "12/2026", "01/2027", "02/2027", "03/2027", "04/2027", "05/2027", "06/2027", "07/2027", "08/2027", "09/2027"])
                    
                    df_dip = pd.read_sql_query("SELECT data AS 'Data', cliente AS 'Cliente', ore_totali AS 'Ore', note AS 'Note' FROM rapportini_v3 WHERE utente = ? AND data LIKE ?", conn, params=(u_sel, f"%{m_sel}"))
                    pdf_b = genera_pdf_report_mensile(f"Report Mensile Dipendente: {u