import os, base64, secrets
from datetime import datetime, date, timedelta
import pandas as pd
import streamlit as st
import plotly.express as px
from database import init_db, get_connection, authenticate, register_user, create_remember_token, validate_remember_token, revoke_remember_token, list_users, set_user_role
from pdf_reports import genera_pdf_rapportino, genera_pdf_report_mensile
try:
    from streamlit_calendar import calendar
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False
try:
    import extra_streamlit_components as stx
    cookies = stx.CookieManager(key="nr_cookie_manager")
except Exception:
    cookies = None

st.set_page_config(page_title="Nicoli Rizzi | Gestione operativa", page_icon="🌿", layout="wide", initial_sidebar_state="collapsed")
init_db()
conn=get_connection(); c=conn.cursor()

def asset_b64(name):
    try:
        with open(os.path.join(os.path.dirname(__file__),name),'rb') as f: return base64.b64encode(f.read()).decode()
    except Exception: return ''
logo=asset_b64('logo_bianco.png')
bg_path=next((p for p in ['sfondo.jpg','IMG_8234.jpg','background.jpg'] if os.path.exists(p)),None)
bg=asset_b64(bg_path) if bg_path else ''
logged=bool(st.session_state.get('auth_user'))
home=(st.session_state.get('modulo_attivo','HOME')=='HOME')
css_bg=(f"linear-gradient(120deg,rgba(7,19,26,.78),rgba(7,19,26,.65)),url(data:image/jpeg;base64,{bg})" if bg and home else "linear-gradient(135deg,#17252b,#31434a)" if home else "#f4f6f5")
text_col='#fff' if home else '#1d292d'
st.markdown(f'''<style>
:root{{--nr-green:#2f6b4f;--nr-dark:#17252b;--nr-muted:#64716d;}}
[data-testid="stSidebar"]{{display:none}} header[data-testid="stHeader"]{{background:transparent}} .block-container{{max-width:1120px;padding:1.2rem clamp(.8rem,3vw,2rem) 3rem!important}}
.stApp{{background:{css_bg};background-size:cover;background-position:center;background-attachment:fixed;color:{text_col}}}
[data-testid="stMarkdownContainer"] p, h1,h2,h3,h4,label{{color:{text_col if home else '#1d292d'} }}
.brand{{display:flex;flex-direction:column;align-items:center;text-align:center;padding:.2rem 0 1.2rem}}
.brand img{{width:clamp(105px,20vw,155px);height:auto;object-fit:contain;filter:drop-shadow(0 3px 8px #0008)}}
.brand .subtitle{{font-size:.78rem;letter-spacing:.14em;font-weight:700;color:#f2f5f3;margin-top:.45rem;text-transform:uppercase}}
.user-strip{{display:flex;align-items:center;justify-content:space-between;gap:.6rem;padding:.75rem 1rem;border:1px solid #ffffff30;border-radius:14px;background:#ffffff14;margin:.25rem 0 1rem}}
.module-card{{border:1px solid #dbe2dd;border-radius:15px;padding:1rem;background:#fff;color:#1d292d;min-height:108px;box-shadow:0 4px 14px #10231b12}}
div.stButton>button{{border-radius:12px;min-height:46px;font-weight:650;white-space:normal}}
div.stButton>button[kind="primary"]{{background:#2f6b4f;border:1px solid #2f6b4f;color:white}}
div.stButton>button[kind="secondary"]{{background:#fff;color:#26352e;border:1px solid #d5ded7}}
[data-testid="stForm"]{{border:1px solid #e0e6e1;border-radius:14px;padding:1rem;background:#ffffff}}
[data-testid="stTextInput"] input,[data-testid="stNumberInput"] input,[data-testid="stDateInput"] input,[data-testid="stSelectbox"] div[data-baseweb="select"]{{border-radius:9px}}
[data-testid="stMetric"]{{background:#fff;border:1px solid #e0e6e1;border-radius:12px;padding:.8rem}}
footer{{visibility:hidden}} [data-testid="stToolbar"]{{visibility:hidden;height:0}}
@media(max-width:640px){{.block-container{{padding:.6rem .75rem 2rem!important}}.brand img{{width:112px}}.brand .subtitle{{font-size:.65rem;letter-spacing:.08em}} h1{{font-size:1.55rem!important}} [data-testid="stHorizontalBlock"]{{gap:.55rem}}}}
</style>''',unsafe_allow_html=True)

def go_home(): st.session_state.modulo_attivo='HOME'
def login_user(user, remember=True):
    st.session_state.auth_user=user['nome']; st.session_state.auth_role=user['ruolo']; st.session_state.modulo_attivo='HOME'
    if cookies and remember:
        token=secrets.token_urlsafe(32); create_remember_token(user['id'],token)
        try: cookies.set('nr_session',token,expires_at=datetime.now()+timedelta(days=30),same_site='strict',secure=True)
        except Exception: pass

def logout():
    try:
        token=cookies.get('nr_session') if cookies else None
        if token: revoke_remember_token(token)
        if cookies: cookies.delete('nr_session')
    except Exception: pass
    for k in ['auth_user','auth_role','modulo_attivo','utente_corrente']: st.session_state.pop(k,None)
    st.rerun()

if 'modulo_attivo' not in st.session_state: st.session_state.modulo_attivo='HOME'
if not st.session_state.get('auth_user') and cookies:
    try:
        tok=cookies.get('nr_session')
        u=validate_remember_token(tok) if tok else None
        if u: st.session_state.auth_user=u['nome']; st.session_state.auth_role=u['ruolo']
    except Exception: pass

# Accesso / registrazione
if not st.session_state.get('auth_user'):
    st.markdown(f'<div class="brand">{f"<img src=\'data:image/png;base64,{logo}\' alt=\'Logo Nicoli Rizzi\'>" if logo else "<h1>NICOLI RIZZI</h1>"}<div class="subtitle">Servizi agricoli e forestali · Contoterzi</div></div>',unsafe_allow_html=True)
    a,b=st.columns(2)
    with a:
        st.subheader('Accedi')
        with st.form('login_form'):
            username=st.text_input('Nome utente',placeholder='es. mario.rossi').strip().lower()
            password=st.text_input('Password',type='password')
            remember=st.checkbox('Ricordami su questo dispositivo',value=True)
            submit=st.form_submit_button('Accedi',type='primary',use_container_width=True)
        if submit:
            u=authenticate(username,password)
            if u:
                login_user(u, remember=remember); st.rerun()
            else: st.error('Credenziali non corrette.')
    with b:
        st.subheader('Prima registrazione')
        with st.form('register_form'):
            nome=st.text_input('Nome e cognome')
            new_username=st.text_input('Nome utente',placeholder='univoco, senza spazi').strip().lower()
            p1=st.text_input('Crea password',type='password')
            p2=st.text_input('Ripeti password',type='password')
            reg=st.form_submit_button('Crea account',use_container_width=True)
        if reg:
            if len(' '.join(nome.split()))<3 or len(new_username)<3 or not new_username.replace('.','').replace('_','').isalnum(): st.error('Inserisci nome completo e nome utente valido (almeno 3 caratteri).')
            elif len(p1)<10: st.error('La password deve contenere almeno 10 caratteri.')
            elif p1!=p2: st.error('Le password non coincidono.')
            else:
                try:
                    uid=register_user(' '.join(nome.split()),new_username,p1)
                    st.success('Account creato. Per motivi di sicurezza, l’amministratore deve abilitarlo e assegnare il ruolo.')
                except ValueError as e: st.error(str(e))
    st.info('Il primo account registrato va abilitato come amministratore tramite la procedura di inizializzazione documentata nel README. Non scegliere il ruolo da un menu pubblico.')
    st.stop()

user=st.session_state.auth_user; role=st.session_state.auth_role
st.markdown(f'<div class="user-strip"><div><strong>Accesso effettuato</strong><br>{user} · {role}</div><div>Sessione personale</div></div>',unsafe_allow_html=True)
with st.sidebar:
    st.write(f'**{user}** · {role}')
    if st.button('Esci',use_container_width=True): logout()

if st.session_state.modulo_attivo=='HOME':
    st.markdown(f'<div class="brand">{f"<img src=\'data:image/png;base64,{logo}\' alt=\'Logo aziendale\'>" if logo else "<h1>NICOLI RIZZI</h1>"}<div class="subtitle">Servizi agricoli e forestali · Contoterzi</div></div>',unsafe_allow_html=True)
    st.markdown('### Area operativa')
    st.caption('Scegli un modulo. I dati vengono salvati nel database aziendale.')
    modules=[('📝','Rapportino giornaliero','RAPPORTINO'),('🗓️','Calendario e storico','CALENDARIO'),('🚛','Registro bilici cippato','BILICI'),('🚜','Parco macchine e report','FLOTTA')]
    for i in range(0,4,2):
        cols=st.columns(2)
        for col,(ico,title,key) in zip(cols,modules[i:i+2]):
            with col:
                st.markdown(f'<div class="module-card"><div style="font-size:1.5rem">{ico}</div><strong>{title}</strong></div>',unsafe_allow_html=True)
                if st.button('Apri modulo →',key='open_'+key,use_container_width=True): st.session_state.modulo_attivo=key; st.rerun()
    st.caption('Nicoli Rizzi S.r.l. · Gestione operativa')

else:
    st.button('← Home',on_click=go_home)
    if st.session_state.modulo_attivo=='RAPPORTINO':
        st.title('Rapportino giornaliero')
        with st.form('form_rapportino',clear_on_submit=True):
            d1,d2=st.columns(2)
            with d1: data_rep=st.date_input('Data lavorazione',date.today(),format='DD/MM/YYYY'); cliente=st.text_input('Cliente / cantiere')
            with d2: ore_totali=st.number_input('Ore totali',min_value=0.0,max_value=24.0,step=.5,value=8.0); note=st.text_area('Note, gasolio, meteo')
            c.execute('SELECT nome FROM attrezzature_v3 ORDER BY nome'); mezzi=[r[0] for r in c.fetchall()]+['Altro / inserimento manuale']
            n=st.number_input('Numero lavorazioni',min_value=1,max_value=12,value=1,step=1)
            work=[]
            for i in range(int(n)):
                st.markdown(f'**Lavorazione {i+1}**'); x,y,z=st.columns([1,1,2])
                with x: start=st.time_input('Inizio',value=datetime.strptime('07:30','%H:%M').time(),key=f'start{i}')
                with y: end=st.time_input('Fine',value=datetime.strptime('12:00','%H:%M').time(),key=f'end{i}')
                with z: machine=st.selectbox('Mezzo',mezzi,key=f'machine{i}'); desc=st.text_input('Attività',key=f'desc{i}')
                if machine=='Altro / inserimento manuale': machine=st.text_input('Specifica mezzo',key=f'manual{i}')
                work.append((start.strftime('%H:%M'),end.strftime('%H:%M'),machine,desc))
            save=st.form_submit_button('Salva rapportino',type='primary',use_container_width=True)
        if save:
            if not cliente.strip(): st.error('Inserisci il cliente o il cantiere.')
            else:
                c.execute('INSERT INTO rapportini_v3 (data,utente,cliente,ore_totali,note) VALUES (?,?,?,?,?)',(data_rep.strftime('%d/%m/%Y'),user,cliente.strip(),ore_totali,note.strip())); rid=c.lastrowid
                c.executemany('INSERT INTO dettagli_lavorazioni_v3 (rapportino_id,ora_inizio,ora_fine,mezzo,descrizione) VALUES (?,?,?,?,?)',[(rid,*w) for w in work]); conn.commit(); st.success('Rapportino salvato.'); st.rerun()

    elif st.session_state.modulo_attivo=='CALENDARIO':
        st.title('Calendario e storico'); st.caption('Le giornate con rapportini sono evidenziate nel calendario.')
        if role=='Amministratore': df=pd.read_sql_query('SELECT * FROM rapportini_v3 ORDER BY id DESC',conn)
        else: df=pd.read_sql_query('SELECT * FROM rapportini_v3 WHERE utente=? ORDER BY id DESC',conn,params=(user,))
        df['data_dt']=pd.to_datetime(df['data'],format='%d/%m/%Y',errors='coerce') if not df.empty else pd.Series(dtype='datetime64[ns]')
        events=[]
        for _,r in df.iterrows():
            if pd.notna(r['data_dt']): events.append({'title':f"{r['utente']} · {r['cliente']} · {r['ore_totali']} h" if role=='Amministratore' else f"{r['cliente']} · {r['ore_totali']} h",'start':r['data_dt'].strftime('%Y-%m-%d'),'end':(r['data_dt']+pd.Timedelta(days=1)).strftime('%Y-%m-%d'),'allDay':True,'backgroundColor':'#2f6b4f','borderColor':'#2f6b4f'})
        if HAS_CALENDAR: calendar(events=events,options={'initialView':'dayGridMonth','height':650,'locale':'it','firstDay':1,'headerToolbar':{'left':'prev,next today','center':'title','right':'dayGridMonth,listMonth'}},key='main_calendar')
        else: st.warning('Per il calendario interattivo installa streamlit-calendar.')
        st.subheader('Rapportini registrati')
        if not df.empty:
            show=df.drop(columns=['data_dt'],errors='ignore').copy(); st.dataframe(show,use_container_width=True,hide_index=True)
            st.download_button('Esporta storico CSV',show.to_csv(index=False).encode('utf-8-sig'),'storico_rapportini.csv','text/csv')
        else: st.info('Nessun rapportino registrato. Il calendario resta visibile e si aggiornerà automaticamente quando verranno salvati i rapportini.')

    elif st.session_state.modulo_attivo=='BILICI':
        st.title('Registro bilici cippato')
        with st.form('form_bilici',clear_on_submit=True):
            d1,d2=st.columns(2)
            with d1: dp=st.date_input('Data partenza',date.today(),format='DD/MM/YYYY')
            with d2: dest=st.text_input('Cliente / destinazione')
            save=st.form_submit_button('Registra partenza',type='primary',use_container_width=True)
        if save:
            if not dest.strip(): st.error('Inserisci la destinazione.')
            else: c.execute('INSERT INTO bilici_v3 (data_partenza,cliente) VALUES (?,?)',(dp.strftime('%d/%m/%Y'),dest.strip())); conn.commit(); st.success('Partenza registrata.')
        df=pd.read_sql_query('SELECT id, data_partenza AS "Data partenza", cliente AS "Cliente / destinazione" FROM bilici_v3 ORDER BY id DESC',conn); st.dataframe(df,use_container_width=True,hide_index=True)

    elif st.session_state.modulo_attivo=='FLOTTA':
        st.title('Parco macchine e report')
        if role!='Amministratore': st.warning('Modulo riservato all’amministratore.')
        else:
            tabs=st.tabs(['Mezzi','Manutenzioni','Report PDF','Analisi'])
            with tabs[0]:
                with st.form('new_machine',clear_on_submit=True):
                    name=st.text_input('Nome / modello mezzo'); unit=st.selectbox('Unità di conteggio',['Ore','Chilometri']); initial=st.number_input('Valore inizio anno',min_value=0.0); add=st.form_submit_button('Salva mezzo',type='primary')
                if add:
                    try: c.execute('INSERT INTO attrezzature_v3 (nome,tipo_conteggio,anno_riferimento,valore_inizio_anno) VALUES (?,?,?,?)',(name.strip(),unit,datetime.now().year,initial)); conn.commit(); st.success('Mezzo salvato.')
                    except Exception: st.error('Nome mancante o mezzo già presente.')
                st.dataframe(pd.read_sql_query('SELECT nome AS Mezzo,tipo_conteggio AS Unità,valore_inizio_anno AS "Inizio anno" FROM attrezzature_v3 ORDER BY nome',conn),use_container_width=True,hide_index=True)
            with tabs[1]:
                st.dataframe(pd.read_sql_query("SELECT m.data AS Data,a.nome AS Mezzo,m.tipo AS Intervento,m.costo AS 'Costo (€)' FROM manutenzioni_v3 m JOIN attrezzature_v3 a ON m.attrezzatura_id=a.id ORDER BY m.id DESC",conn),use_container_width=True,hide_index=True)
            with tabs[2]:
                typ=st.selectbox('Tipo report',['Rapportino giornaliero','Report mensile dipendente','Report mensile aziendale'])
                if typ=='Rapportino giornaliero':
                    df0=pd.read_sql_query('SELECT id,data,utente,cliente,ore_totali,note FROM rapportini_v3 ORDER BY id DESC',conn)
                    if not df0.empty:
                        rid=st.selectbox('Rapportino',df0.id.tolist(),format_func=lambda v:f"#{v} · {df0.loc[df0.id==v,'data'].iloc[0]} · {df0.loc[df0.id==v,'utente'].iloc[0]}")
                        r=c.execute('SELECT * FROM rapportini_v3 WHERE id=?',(rid,)).fetchone(); details=pd.read_sql_query('SELECT ora_inizio AS "Ora inizio",ora_fine AS "Ora fine",mezzo AS Mezzo,descrizione AS Attività FROM dettagli_lavorazioni_v3 WHERE rapportino_id=?',conn,params=(rid,))
                        pdf=genera_pdf_rapportino(r[1],r[2],r[3],r[4],r[5],details); st.download_button('Scarica PDF',pdf,f'Rapportino_{rid}.pdf','application/pdf',type='primary')
                else:
                    month=st.text_input('Mese (MM/AAAA)',value=date.today().strftime('%m/%Y'))
                    try: datetime.strptime(month,'%m/%Y'); pattern='%/'+month if False else month[0:2]+'/'+month[3:]
                    except Exception: pattern=''
                    if pattern:
                        if typ=='Report mensile dipendente':
                            names=pd.read_sql_query('SELECT DISTINCT utente FROM rapportini_v3 ORDER BY utente',conn).utente.tolist()
                            if names:
                                nm=st.selectbox('Dipendente',names); data=pd.read_sql_query('SELECT data AS Data,cliente AS Cliente,ore_totali AS Ore,note AS Note FROM rapportini_v3 WHERE utente=? AND substr(data,4,7)=?',conn,params=(nm,pattern)); title=f'Report {nm} {month}'
                            else: data=pd.DataFrame(); title='Report mensile'
                        else: data=pd.read_sql_query('SELECT data AS Data,utente AS Operatore,cliente AS Cliente,ore_totali AS Ore FROM rapportini_v3 WHERE substr(data,4,7)=?',conn,params=(pattern,)); title=f'Report aziendale {month}'
                        if st.button('Prepara PDF'): st.session_state['pdf_month_data']=data; st.session_state['pdf_month_title']=title
                        if 'pdf_month_data' in st.session_state: st.download_button('Scarica report PDF',genera_pdf_report_mensile(st.session_state['pdf_month_title'],st.session_state['pdf_month_data']), 'Report_mensile.pdf','application/pdf')
            with tabs[3]:
                hours=pd.read_sql_query('SELECT cliente,SUM(ore_totali) ore FROM rapportini_v3 GROUP BY cliente',conn)
                if not hours.empty: st.plotly_chart(px.bar(hours,x='cliente',y='ore',title='Ore registrate per cliente'),use_container_width=True)
                costs=pd.read_sql_query('SELECT a.nome mezzo,SUM(m.costo) costo FROM manutenzioni_v3 m JOIN attrezzature_v3 a ON m.attrezzatura_id=a.id GROUP BY a.nome',conn)
                if not costs.empty: st.plotly_chart(px.pie(costs,names='mezzo',values='costo',title='Costi manutenzione per mezzo'),use_container_width=True)
                st.subheader('Gestione account')
                users=list_users()
                if users:
                    for u in users:
                        cols=st.columns([3,2,2])
                        cols[0].write(f"**{u['nome']}** · `{u['username']}`")
                        cols[1].write(u['ruolo']+' · '+('attivo' if u['attivo'] else 'in attesa'))
                        if u['id']!=1 and cols[2].button('Abilita operatore' if not u['attivo'] else 'Rendi admin' if u['ruolo']!='Amministratore' else 'Revoca admin',key=f"role_{u['id']}"):
                            set_user_role(u['id'],'Operatore' if u['attivo'] and u['ruolo']=='Amministratore' else 'Amministratore' if u['attivo'] else 'Operatore',active=True); st.rerun()
    conn.close()
