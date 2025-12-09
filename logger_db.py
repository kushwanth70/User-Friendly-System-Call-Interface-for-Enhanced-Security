import sqlite3, time, json

DB = "logs.sqlite"

def init_db():
    conn = sqlite3.connect(DB, check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS logs
                   (id INTEGER PRIMARY KEY, ts INTEGER, user TEXT, action TEXT, params TEXT, outcome TEXT)''')
    conn.commit()
    return conn

_conn = init_db()

def log(user, action, params, outcome):
    ts = int(time.time())
    cur = _conn.cursor()
    cur.execute('INSERT INTO logs (ts, user, action, params, outcome) VALUES (?, ?, ?, ?, ?)',
                (ts, user, action, json.dumps(params), outcome))
    _conn.commit()

def fetch_logs(limit=200):
    cur = _conn.cursor()
    cur.execute('SELECT id, ts, user, action, params, outcome FROM logs ORDER BY id DESC LIMIT ?', (limit,))
    return cur.fetchall()
