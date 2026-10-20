import os, sqlite3, hashlib, secrets
from datetime import datetime, timedelta
DB_PATH=os.environ.get('NR_DATABASE_PATH',os.path.join(os.path.dirname(__file__),'nicoli_rizzi.db'))
def get_connection():
    con=sqlite3.connect(DB_PATH,check_same_thread=False); con.row_factory=sqlite3.Row; return con
def _hash(password,salt=None):
    salt=salt or secrets.token_hex(16); value=hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),310000).hex(); return salt+'$'+value
def _verify(password,stored):
    try:
        salt,digest=stored.split('$',1); return secrets.compare_digest(_hash(password,salt).split('$',1)[1],digest)
    except Exception: return False
def init_db():
    con=get_connection(); c=con.cursor()
    c.executescript('''CREATE TABLE IF NOT EXISTS utenti_app(id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL,username TEXT UNIQUE,password_hash TEXT,ruolo TEXT NOT NULL DEFAULT 'Operatore',attivo INTEGER NOT NULL DEFAULT 0,creato_il TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS remember_tokens(token_hash TEXT PRIMARY KEY,user_id INTEGER NOT NULL,expires_at TEXT NOT NULL,FOREIGN KEY(user_id) REFERENCES utenti_app(id));
    CREATE TABLE IF NOT EXISTS rapportini_v3(id INTEGER PRIMARY KEY AUTOINCREMENT,data TEXT NOT NULL,utente TEXT NOT NULL,cliente TEXT,ore_totali REAL,note TEXT);
    CREATE TABLE IF NOT EXISTS dettagli_lavorazioni_v3(id INTEGER PRIMARY KEY AUTOINCREMENT,rapportino_id INTEGER NOT NULL,ora_inizio TEXT,ora_fine TEXT,mezzo TEXT,descrizione TEXT,FOREIGN KEY(rapportino_id) REFERENCES rapportini_v3(id));
    CREATE TABLE IF NOT EXISTS bilici_v3(id INTEGER PRIMARY KEY AUTOINCREMENT,data_partenza TEXT,cliente TEXT);
    CREATE TABLE IF NOT EXISTS attrezzature_v3(id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT UNIQUE,tipo_conteggio TEXT,anno_riferimento INTEGER,valore_inizio_anno REAL DEFAULT 0);
    CREATE TABLE IF NOT EXISTS manutenzioni_v3(id INTEGER PRIMARY KEY AUTOINCREMENT,attrezzatura_id INTEGER,data TEXT,tipo TEXT,costo REAL DEFAULT 0,FOREIGN KEY(attrezzatura_id) REFERENCES attrezzature_v3(id));''')
    # migrate legacy table with only name column
    cols=[r['name'] for r in c.execute('PRAGMA table_info(utenti_app)').fetchall()]
    for name,decl in [('username','TEXT'),('password_hash','TEXT'),('ruolo',"TEXT NOT NULL DEFAULT 'Operatore'"),('attivo','INTEGER NOT NULL DEFAULT 0'),('creato_il','TEXT')]:
        if name not in cols: c.execute(f'ALTER TABLE utenti_app ADD COLUMN {name} {decl}')
    # legacy users are not assigned credentials; keep them inactive until reset/registration
    c.execute('CREATE UNIQUE INDEX IF NOT EXISTS idx_users_username ON utenti_app(username) WHERE username IS NOT NULL')
    con.commit(); con.close()
def register_user(nome,username,password):
    con=get_connection(); c=con.cursor()
    if c.execute('SELECT 1 FROM utenti_app WHERE lower(username)=lower(?)',(username,)).fetchone(): con.close(); raise ValueError('Nome utente già utilizzato.')
    c.execute('INSERT INTO utenti_app(nome,username,password_hash,ruolo,attivo) VALUES(?,?,?,\'Operatore\',0)',(nome,username,_hash(password))); uid=c.lastrowid; con.commit(); con.close(); return uid
def authenticate(username,password):
    con=get_connection(); r=con.execute('SELECT * FROM utenti_app WHERE lower(username)=lower(?) AND attivo=1',(username,)).fetchone(); con.close()
    if r and r['password_hash'] and _verify(password,r['password_hash']): return {'id':r['id'],'nome':r['nome'],'ruolo':r['ruolo']}
    return None
def create_remember_token(uid,token):
    con=get_connection(); con.execute('INSERT INTO remember_tokens(token_hash,user_id,expires_at) VALUES(?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),uid,(datetime.utcnow()+timedelta(days=30)).isoformat())); con.commit(); con.close()
def validate_remember_token(token):
    if not token:return None
    con=get_connection(); r=con.execute('SELECT u.id,u.nome,u.ruolo,t.expires_at FROM remember_tokens t JOIN utenti_app u ON u.id=t.user_id WHERE t.token_hash=? AND u.attivo=1',(hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if not r or r['expires_at']<datetime.utcnow().isoformat():
        con.execute('DELETE FROM remember_tokens WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),)); con.commit(); con.close(); return None
    con.close(); return {'id':r['id'],'nome':r['nome'],'ruolo':r['ruolo']}
def revoke_remember_token(token):
    con=get_connection(); con.execute('DELETE FROM remember_tokens WHERE token_hash=?',(hashlib.sha256(token.encode()).hexdigest(),)); con.commit(); con.close()
def list_users():
    con=get_connection(); rows=con.execute('SELECT id,nome,username,ruolo,attivo FROM utenti_app ORDER BY nome COLLATE NOCASE').fetchall(); con.close(); return [dict(r) for r in rows]
def set_user_role(uid,role,active=True):
    con=get_connection(); con.execute('UPDATE utenti_app SET ruolo=?,attivo=? WHERE id=?',(role,int(active),uid)); con.commit(); con.close()
