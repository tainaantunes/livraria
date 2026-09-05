import sqlite3, re
from pathlib import Path
from datetime import datetime
P = Path(__file__).parent
DB = P / 'biblioteca.db'

def clean_title_raw(t):
    if not t:
        return t
    t = t.strip()
    t = t.lstrip('\ufeff')
    parts = [p.strip() for p in t.split(';') if p.strip() != '']
    if parts:
        while parts and re.fullmatch(r"[\d\-\s]*L?", parts[0]):
            parts.pop(0)
        while parts and re.fullmatch(r"^\d+$", parts[0]):
            parts.pop(0)
        while parts and re.fullmatch(r"^\d+$", parts[-1]):
            parts.pop(-1)
        if parts:
            return ' ; '.join(parts)
    t2 = re.sub(r'^\s*[0-9]{1,6}L\s*[:;\-]*\s*', '', t)
    t2 = re.sub(r'^\s*[0-9]{1,6}\s*[:;\-]*\s*', '', t2)
    return t2.strip()

if not DB.exists():
    print('Database not found:', DB)
    raise SystemExit(1)

conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute('SELECT id, titulo FROM livros')
rows = cur.fetchall()
updated = 0
for id, titulo in rows:
    cleaned = clean_title_raw(titulo)
    if cleaned and cleaned != titulo:
        try:
            cur.execute('UPDATE livros SET titulo=? WHERE id=?', (cleaned, id))
            updated += 1
        except Exception as e:
            print('Error updating', id, e)

conn.commit()
conn.close()
print('Titles cleaned:', updated)
