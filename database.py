import sqlite3

def get_connection():
    conn = sqlite3.connect('gestionale_cantiere.db', check_same_thread=False)
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    conn = get_connection()
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
    conn.close()