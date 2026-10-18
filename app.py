import os
import base64
import sqlite3
from datetime import datetime, date, timedelta
import pandas as pd
import streamlit as st

try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

st.set_page_config(page_title="Nicoli Rizzi - Servizi Agricoli e Forestali", layout="wide", initial_sidebar_state="collapsed")
DB_PATH = "gestionale_cantiere.db"
ADMIN_PASSWORD = "Billabong4e48"
CURRENT_YEAR = datetime.now().year


def img64(path):
    try:
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    except OSError:
        return ""

bg_path = next((p for p in ("sfondo.jpg", "IMG_8234.jpg") if os.path.exists(p)), None)
bg64 = img64(bg_path) if bg_path else ""
is_home = st.session_state.get("modulo_attivo", "HOME") == "HOME"
if bg64 and is_home:
    bg_css = f".stApp {{ background: linear-gradient(rgba(0,0,0,.55),rgba(0,0,0,.55)), url('data:image/jpeg;base64,{bg64}'); background-size:cover; background-position:center; background-attachment:fixed; }}"
else:
    bg_css = ".stApp { background-color:#F9F6F0; color:#2C2C2C; }"
text_color = "#FFFFFF" if is_home and bg64 else "#2C2C2C"
shadow = "1px 1px 2px rgba(0,0,0,.8)" if is_home and bg64 else "none"
st.markdown(f"""
<style>
{bg_css}
[data-testid="stSidebar"] {{display:none;}}
h1,h2,h3,h4,h5,h6,p,[data-testid="stMarkdownContainer"] {{color:{text_color};}}
label {{color:{text_color}!important;font-weight:600!important;text-shadow:{shadow};}}
.logo-container {{width:100%;display:flex;align-items:center;justify-content:center;text-align:center;padding:8px 0 22px;box-sizing:border-box;background:transparent!important;}}
.logo-img {{display:block;width:min(92vw,650px)!important;max-width:650px!important;height:190px!important;object-fit:contain;background:transparent!important;filter:grayscale(1) invert(1) contrast(1.15) brightness(1.15);mix-blend-mode:screen;}}
.logo-fallback {{color:#fff!important;font-size:clamp(42px,7vw,78px);line-height:1.05;font-weight:900;text-align:center;text-shadow:2px 2px 5px rgba(0,0,0,.8);}}
.st-key-home_modules {{max-width:760px!important;margin-left:auto!important;margin-right:auto!important;}}
div.stButton>button[kind="primary"] {{background:rgba(255,255,255,.97)!important;color:#1A1A1A!important;border:2px solid #C5C0B7!important;border-radius:16px!important;width:100%!important;min-height:0!important;height:270px!important;max-height:270px!important;aspect-ratio:1/1!important;font-size:clamp(17px,1.7vw,23px)!important;font-weight:850!important;white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.15!important;box-shadow:0 6px 16px rgba(0,0,0,.35)!important;transition:all .2s ease-in-out!important;padding:14px!important;display:flex!important;align-items:center!important;justify-content:center!important;text-align:center!important;}}
div.stButton>button[kind="primary"] p,div.stButton>button[kind="primary"] span {{color:#1A1A1A!important;width:100%!important;text-align:center!important;font-weight:850!important;}}
div.stButton>button[kind="primary"]:hover {{background:#fff!important;border-color:#2C2C2C!important;transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(0,0,0,.45)!important;}}
div.stButton>button[kind="secondary"] {{background:#fff!important;color:#2C2C2C!important;border:1px solid #D0CBC3!important;border-radius:6px!important;font-weight:500!important;}}
div.stButton>button[kind="secondary"]:hover {{background:#F0EBE3!important;color:#000!important;}}
.streamlit-expanderHeader {{background:#F3EFE6;border-radius:6px;}}
@media(max-width:700px) {{.logo-img {{width:94vw!important;height:145px!important;}} div.stButton>button[kind="primary"] {{height:190px!important;max-height:190px!important;font-size:16px!important;padding:8px!important;}}}}
</style>
""", unsafe_allow_html=True)

# Database
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
conn.execute("PRAGMA foreign_keys = ON")
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS rapportini_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,data TEXT,utente TEXT,cliente TEXT,ore_totali REAL,note TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS dettagli_lavorazioni_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,rapportino_id INTEGER,ora_inizio TEXT,ora_fine TEXT,mezzo TEXT,descrizione TEXT,FOREIGN KEY(rapportino_id) REFERENCES rapportini_v3(id) ON DELETE CASCADE)""")
c.execute("""CREATE TABLE IF NOT EXISTS bilici_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,data_partenza TEXT,cliente TEXT)""")
c.execute("""CREATE TABLE IF NOT EXISTS attrezzature_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT UNIQUE,tipo_conteggio TEXT,anno_riferimento INTEGER,valore_inizio_anno REAL)""")
c.execute("""CREATE TABLE IF NOT EXISTS manutenzioni_v3 (id INTEGER PRIMARY KEY AUTOINCREMENT,attrezzatura_id INTEGER,data TEXT,tipo TEXT,ore_km_al_momento REAL,eseguito_da TEXT,descrizione TEXT,costo REAL,FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature_v3(id))""")
c.execute("""CREATE TABLE IF NOT EXISTS utenti_app (id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL COLLATE NOCASE UNIQUE,creato_il TEXT DEFAULT CURRENT_TIMESTAMP)""")
conn.commit()

# Session state
for key, value in {"modulo_attivo":"HOME", "utente_corrente":"", "ruolo":"Operatore", "admin_autenticato":False, "num_righe_lavoro":1}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# L'URL può preselezionare un operatore già registrato, ma non concede privilegi.
try:
    nome_url = str(st.query_params.get("utente", "")).strip()
except Exception:
    nome_url = ""
if nome_url and not st.session_state.utente_corrente:
    c.execute("SELECT nome FROM utenti_app WHERE nome=? COLLATE NOCASE", (nome_url,))
    trovato = c.fetchone()
    if trovato:
        st.session_state.utente_corrente = trovato[0]

def torna_home():
    st.session_state.modulo_attivo = "HOME"

# HOME
if st.session_state.modulo_attivo == "HOME":
    logo_file = next((p for p in ("logo.png", "logo.jpg", "IMG_7106.jpg") if os.path.exists(p)), None)
    if logo_file:
        logo_data = img64(logo_file)
        mime = "image/png" if logo_file.lower().endswith(".png") else "image/jpeg"
        st.markdown(f'<div class="logo-container"><img src="data:{mime};base64,{logo_data}" class="logo-img" alt="Logo Nicoli Rizzi"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="logo-container"><div class="logo-fallback">NICOLI RIZZI</div></div>', unsafe_allow_html=True)

    c.execute("SELECT nome FROM utenti_app ORDER BY nome COLLATE NOCASE")
    utenti = [r[0] for r in c.fetchall()]
    opzioni = ["-- Seleziona operatore --"] + utenti + ["+ Registra nuovo operatore"]
    default = st.session_state.utente_corrente if st.session_state.utente_corrente in utenti else "-- Seleziona operatore --"
    selezione = st.selectbox("Operatore:", opzioni, index=opzioni.index(default), key="selezione_utente_home")
    if selezione == "+ Registra nuovo operatore":
        with st.form("registra_operatore_form"):
            nuovo_nome = st.text_input("Nome e cognome del dipendente")
            registra = st.form_submit_button("Registra operatore")
        if registra:
            nome = " ".join(nuovo_nome.split())
            if not nome:
                st.error("Inserisci nome e cognome.")
            else:
                try:
                    c.execute("INSERT INTO utenti_app(nome) VALUES(?)", (nome,))
                    conn.commit()
                    st.session_state.utente_corrente = nome
                    st.query_params["utente"] = nome
                    st.rerun()
                except sqlite3.IntegrityError:
                    c.execute("SELECT nome FROM utenti_app WHERE nome=? COLLATE NOCASE", (nome,))
                    existing = c.fetchone()
                    st.session_state.utente_corrente = existing[0] if existing else nome
                    st.query_params["utente"] = st.session_state.utente_corrente
                    st.rerun()
    elif selezione == "-- Seleziona operatore --":
        st.session_state.utente_corrente = ""
    else:
        st.session_state.utente_corrente = selezione
        st.query_params["utente"] = selezione

    scelta_ruolo = st.selectbox("Ruolo:", ["Operatore", "Amministratore"], key="ruolo_scelto")
    if scelta_ruolo == "Amministratore":
        # La richiesta password compare SOLO dopo aver scelto Amministratore.
        if not st.session_state.admin_autenticato:
            with st.form("login_amministratore_form"):
                password = st.text_input("Password amministratore", type="password")
                login = st.form_submit_button("Accedi come amministratore")
            if login:
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_autenticato = True
                    st.session_state.ruolo = "Amministratore"
                    st.success("Accesso amministratore autorizzato.")
                    st.rerun()
                else:
                    st.session_state.admin_autenticato = False
                    st.session_state.ruolo = "Operatore"
                    st.error("Password non corretta. Accesso come operatore.")
        else:
            st.session_state.ruolo = "Amministratore"
            if st.button("Esci dall'account amministratore", key="logout_admin", type="secondary"):
                st.session_state.admin_autenticato = False
                st.session_state.ruolo = "Operatore"
                st.session_state.ruolo_scelto = "Operatore"
                st.rerun()
    else:
        # Selezionando Operatore non viene chiesta alcuna password.
        st.session_state.ruolo = "Operatore"
        st.session_state.admin_autenticato = False

    st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
    with st.container(key="home_modules"):
        col1, col2 = st.columns(2, gap="medium")
        with col1:
            if st.button("RAPPORTINO GIORNALIERO ATTIVITÀ", key="btn_rap", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "RAPPORTINO"; st.rerun()
        with col2:
            if st.button("CALENDARIO E STORICO RAPPORTINI", key="btn_cal", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "CALENDARIO"; st.rerun()
        st.markdown('<div style="margin-top:12px"></div>', unsafe_allow_html=True)
        col3, col4 = st.columns(2, gap="medium")
        with col3:
            if st.button("REGISTRO SPEDIZIONI BILICI CIPPATO", key="btn_bil", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "BILICI"; st.rerun()
        with col4:
            if st.button("GESTIONE PARCO MACCHINE E ATTREZZATURE", key="btn_flotta", type="primary", use_container_width=True):
                st.session_state.modulo_attivo = "FLOTTA"; st.rerun()
    st.markdown('<p style="text-align:center;font-weight:600;font-size:11px;margin-top:15px;text-shadow:1px 1px 3px #000">Nicoli Rizzi S.r.l. - Servizi Agricoli e Forestali Conto Terzi</p>', unsafe_allow_html=True)

# RAPPORTINO
elif st.session_state.modulo_attivo == "RAPPORTINO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Rapportino Giornaliero Attività")
    st.caption(f"Utente collegato: {st.session_state.utente_corrente or 'Nessun operatore selezionato'} ({st.session_state.ruolo})")
    with st.form("form_rapportino_v3"):
        d1, d2 = st.columns(2)
        with d1:
            data_rep = st.date_input("Data Lavorazione (GG/MM/AAAA)", date.today(), format="DD/MM/YYYY")
            cliente = st.text_input("Cliente", placeholder="Inserisci il nome del cliente")
        with d2:
            ore = st.number_input("Ore Totali Lavorate nella Giornata", min_value=0.0, step=0.5, value=8.0)
            note = st.text_area("Note / Osservazioni Generali", placeholder="Note complessive, consumo gasolio, condizioni meteo...")
        st.markdown("---"); st.subheader("Dettaglio Lavorazioni della Giornata")
        c.execute("SELECT nome FROM attrezzature_v3 ORDER BY nome")
        mezzi = [r[0] for r in c.fetchall()] + ["Altro / Inserimento Manuale"]
        lavori = []
        for i in range(st.session_state.num_righe_lavoro):
            st.markdown(f"**Lavorazione #{i+1}**")
            a,b,d,e = st.columns([1.3,1.3,3,3])
            with a: ora_in = st.time_input(f"Ora Inizio #{i+1}", value=datetime.strptime("07:30","%H:%M").time(), key=f"in_{i}")
            with b: ora_fi = st.time_input(f"Ora Fine #{i+1}", value=datetime.strptime("12:00","%H:%M").time(), key=f"fi_{i}")
            with d:
                m = st.selectbox(f"Mezzo / Attrezzatura #{i+1}", mezzi, key=f"m_{i}")
                mezzo = st.text_input(f"Specifica mezzo #{i+1}", key=f"mm_{i}", placeholder="es. Motosega Stihl 661") if m == "Altro / Inserimento Manuale" else m
            with e: descr = st.text_input(f"Descrizione Attività #{i+1}", key=f"desc_{i}", placeholder="es. Cippatura ramaglie")
            lavori.append((ora_in.strftime("%H:%M"), ora_fi.strftime("%H:%M"), mezzo, descr))
        salva = st.form_submit_button("Salva Rapportino Completo")
    if st.button("Aggiungi un'altra riga di lavoro", type="secondary"):
        st.session_state.num_righe_lavoro += 1; st.rerun()
    if salva:
        if not st.session_state.utente_corrente:
            st.error("Seleziona o registra prima il tuo nome nella Home."); st.stop()
        data_fmt = data_rep.strftime("%d/%m/%Y")
        c.execute("INSERT INTO rapportini_v3(data,utente,cliente,ore_totali,note) VALUES(?,?,?,?,?)", (data_fmt,st.session_state.utente_corrente,cliente,ore,note))
        rap_id = c.lastrowid
        c.executemany("INSERT INTO dettagli_lavorazioni_v3(rapportino_id,ora_inizio,ora_fine,mezzo,descrizione) VALUES(?,?,?,?,?)", [(rap_id,*x) for x in lavori])
        conn.commit(); st.session_state.num_righe_lavoro = 1; st.success(f"Rapportino registrato con successo in data {data_fmt}!")

# CALENDARIO / STORICO
elif st.session_state.modulo_attivo == "CALENDARIO":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Calendario & Storico Rapportini")
    admin = st.session_state.ruolo == "Amministratore" and st.session_state.admin_autenticato
    if not admin:
        st.info(f"Visualizzazione rapportini inseriti da: **{st.session_state.utente_corrente}**")
        df = pd.read_sql_query("SELECT * FROM rapportini_v3 WHERE utente=? ORDER BY id DESC", conn, params=(st.session_state.utente_corrente,))
    else:
        st.success("Vista Amministratore: monitoraggio completo dell'attività aziendale.")
        df = pd.read_sql_query("SELECT * FROM rapportini_v3 ORDER BY id DESC", conn)
    tab_cal, tab_lista = st.tabs(["Vista Calendario Mensile", "Elenco Dettagliato & Modifica"])
    with tab_cal:
        st.subheader("Calendario delle Attività")
        if not df.empty:
            events=[]
            for _,r in df.iterrows():
                try:
                    dt=datetime.strptime(r["data"],"%d/%m/%Y")
                    events.append({"title":f"{r['utente']} - {r['cliente'] or ''} ({r['ore_totali']}h)","start":dt.strftime("%Y-%m-%d"),"end":(dt+timedelta(days=1)).strftime("%Y-%m-%d"),"allDay":True})
                except (ValueError,TypeError): pass
            if HAS_CALENDAR:
                calendar(events=events, options={"headerToolbar":{"left":"prev,next today","center":"title","right":"dayGridMonth,timeGridWeek"},"initialView":"dayGridMonth","locale":"it"}, key="cal_view")
            else: st.info("Per visualizzare il calendario installa streamlit-calendar: pip install streamlit-calendar")
            st.markdown("---"); st.subheader("Consulta i Rapportini per Data Specifica")
            giorno=st.date_input("Seleziona Giorno da Ispezionare",date.today(),format="DD/MM/YYYY").strftime("%d/%m/%Y")
            if admin: c.execute("SELECT * FROM rapportini_v3 WHERE data=? ORDER BY id DESC",(giorno,))
            else: c.execute("SELECT * FROM rapportini_v3 WHERE data=? AND utente=? ORDER BY id DESC",(giorno,st.session_state.utente_corrente))
            rapporti=c.fetchall()
            if rapporti:
                st.markdown(f"#### Rapportini del **{giorno}**")
                for rap in rapporti:
                    rid,rd,ru,rc,ro,rn=rap
                    with st.expander(f"Cliente: {rc or ''} | Operatore: {ru} | Ore: {ro}h"):
                        st.write(f"**Operatore:** {ru}"); st.write(f"**Cliente:** {rc or ''}"); st.write(f"**Ore lavorate:** {ro} ore"); st.write(f"**Note:** {rn or 'Nessuna nota inserita'}")
                        det=pd.read_sql_query("SELECT ora_inizio AS 'Ora Inizio', ora_fine AS 'Ora Fine', mezzo AS 'Mezzo / Attrezzatura', descrizione AS 'Descrizione Lavoro' FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?",conn,params=(rid,))
                        if not det.empty: st.dataframe(det,use_container_width=True)
            else: st.info(f"Nessun rapportino presente per la data {giorno}.")
        else: st.warning("Nessun rapportino salvato nel sistema.")
    with tab_lista:
        if not admin:
            st.info("La modifica e l'eliminazione dei rapportini sono riservate all'amministratore autorizzato.")
        elif not df.empty:
            st.dataframe(df,use_container_width=True); st.markdown("---"); st.subheader("Gestione / Modifica / Eliminazione Rapportino")
            rid=st.selectbox("Seleziona ID Rapportino:",df["id"].tolist()); row=df[df["id"]==rid].iloc[0]
            with st.expander(f"Modifica Scheda #{rid}"):
                with st.form("form_edit_rap_v3"):
                    nc=st.text_input("Cliente",value=row["cliente"] or ""); no=st.number_input("Ore Totali",min_value=0.0,value=float(row["ore_totali"] or 0)); nn=st.text_area("Note",value=row["note"] or "")
                    x,y=st.columns(2)
                    with x: aggiorna=st.form_submit_button("Aggiorna Rapportino")
                    with y: elimina=st.form_submit_button("Elimina Rapportino")
                    if aggiorna:
                        c.execute("UPDATE rapportini_v3 SET cliente=?,ore_totali=?,note=? WHERE id=?",(nc,no,nn,rid)); conn.commit(); st.success("Rapportino aggiornato."); st.rerun()
                    if elimina:
                        c.execute("DELETE FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?",(rid,)); c.execute("DELETE FROM rapportini_v3 WHERE id=?",(rid,)); conn.commit(); st.warning("Rapportino eliminato."); st.rerun()
        else: st.info("Non ci sono rapportini da visualizzare.")

# BILICI
elif st.session_state.modulo_attivo == "BILICI":
    st.button("Torna alla Home", on_click=torna_home, type="secondary")
    st.title("Registro Spedizioni Bilici Cippato")
    with st.expander("Registra Nuova Partenza Bilico",expanded=True):
        with st.form("form_bilico_v3",clear_on_submit=True):
            a,b=st.columns(2)
            with a: data_p=date.today(); data_p=st.date_input("Data di Partenza (GG/MM/AAAA)",data_p,format="DD/MM/YYYY")
            with b: cliente_b=st.text_input("Cliente / Destinazione",placeholder="Nome cliente o impianto")
            invia=st.form_submit_button("Registra Partenza Bilico")
            if invia:
                if not cliente_b.strip(): st.error("Inserisci il cliente o la destinazione.")
                else:
                    fmt=data_p.strftime("%d/%m/%Y"); c.execute("INSERT INTO bilici_v3(data_partenza,cliente) VALUES(?,?)",(fmt,cliente_b.strip())); conn.commit(); st.success(f"Partenza bilico registrata per '{cliente_b.strip()}' in data {fmt}.")
    dfb=pd.read_sql_query("SELECT data_partenza AS 'Data Partenza',cliente AS 'Cliente' FROM bilici_v3 ORDER BY id DESC",conn)
    st.subheader("Storico Partenze Bilici")
    if not dfb.empty: st.dataframe(dfb,use_container_width=True)
    else: st.info("Nessuna partenza registrata nel sistema.")

# FLOTTA
elif st.session_state.modulo_attivo == "FLOTTA":
    st.button("Torna alla Home",on_click=torna_home,type="secondary")
    st.title("Gestione Parco Macchine & Attrezzature")
    if st.session_state.ruolo != "Amministratore" or not st.session_state.admin_autenticato:
        st.warning("La gestione del parco macchine e del registro manutenzioni è riservata all'amministratore autorizzato.")
    else:
        t1,t2=st.tabs(["Schede Mezzi & Ore Inizio Anno","Registro Manutenzioni"])
        with t1:
            st.subheader("Aggiungi Mezzo o Attrezzatura alla Flotta")
            with st.form("form_attrezzatura_v3",clear_on_submit=True):
                a,b,d,e=st.columns(4)
                with a: nome_m=st.text_input("Nome / Modello Mezzo",placeholder="es. Valtra S400")
                with b: tipo=st.selectbox("Unità di Misura",["Ore","Chilometri"])
                with d: anno=st.number_input("Anno Registrazione",min_value=2000,max_value=2100,value=CURRENT_YEAR,step=1)
                with e: valore=st.number_input(f"Ore/Km a Inizio Anno ({int(anno)})",min_value=0.0,step=10.0)
                salva_m=st.form_submit_button("Salva Mezzo")
                if salva_m:
                    if not nome_m.strip(): st.error("Inserisci il nome del mezzo.")
                    else:
                        try:
                            c.execute("INSERT INTO attrezzature_v3(nome,tipo_conteggio,anno_riferimento,valore_inizio_anno) VALUES(?,?,?,?)",(nome_m.strip(),tipo,int(anno),valore)); conn.commit(); st.success("Mezzo registrato."); st.rerun()
                        except sqlite3.IntegrityError: st.error("Esiste già un mezzo con questo nome.")
            dfa=pd.read_sql_query("SELECT nome AS 'Mezzo',tipo_conteggio AS 'Unità di Misura',anno_riferimento AS 'Anno Riferimento',valore_inizio_anno AS 'Valore Inizio Anno' FROM attrezzature_v3 ORDER BY nome",conn)
            st.subheader("Flotta Aziendale"); st.dataframe(dfa,use_container_width=True)
        with t2:
            st.subheader("Registra Manutenzione / Intervento")
            c.execute("SELECT id,nome FROM attrezzature_v3 ORDER BY nome"); att=c.fetchall()
            if att:
                mappa={r[1]:r[0] for r in att}; mezzo_man=st.selectbox("Seleziona Mezzo",list(mappa.keys()))
                with st.form("form_manutenzione_v3",clear_on_submit=True):
                    a,b=st.columns(2)
                    with a:
                        data_man=st.date_input("Data Intervento (GG/MM/AAAA)",date.today(),format="DD/MM/YYYY")
                        tipo_man=st.selectbox("Tipo Intervento",["Tagliando / Ordinaria","Riparazione Straordinaria","Sostituzione Lame / Catene / Ingrassaggio"])
                        ore_man=st.number_input("Ore/Km della Macchina al momento del lavoro",min_value=0.0,step=5.0)
                    with b:
                        eseguito=st.text_input("Eseguito Da",placeholder="Meccanico interno / officina")
                        costo=st.number_input("Costo Sostenuto (€)",min_value=0.0,step=10.0)
                        descr=st.text_area("Dettaglio Lavori Svolti e Pezzi Sostituiti")
                    salva_man=st.form_submit_button("Salva Manutenzione")
                    if salva_man:
                        fmt=data_man.strftime("%d/%m/%Y")
                        c.execute("INSERT INTO manutenzioni_v3(attrezzatura_id,data,tipo,ore_km_al_momento,eseguito_da,descrizione,costo) VALUES(?,?,?,?,?,?,?)",(mappa[mezzo_man],fmt,tipo_man,ore_man,eseguito.strip(),descr.strip(),costo)); conn.commit(); st.success("Manutenzione registrata."); st.rerun()
                dfm=pd.read_sql_query("SELECT m.data AS 'Data',a.nome AS 'Mezzo',m.tipo AS 'Tipo Intervento',m.ore_km_al_momento AS 'Ore/Km',m.eseguito_da AS 'Eseguito Da',m.descrizione AS 'Descrizione',m.costo AS 'Costo (€)' FROM manutenzioni_v3 m JOIN attrezzature_v3 a ON m.attrezzatura_id=a.id ORDER BY m.id DESC",conn)
                st.subheader("Storico Manutenzioni"); st.dataframe(dfm,use_container_width=True)
            else: st.warning("Aggiungi prima un mezzo nella scheda 'Schede Mezzi & Ore Inizio Anno'.")

conn.close()
