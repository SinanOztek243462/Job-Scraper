import sqlite3

c = sqlite3.connect('jobs.db')
try:
    c.execute('ALTER TABLE loadouts ADD COLUMN title_must_include TEXT DEFAULT ""')
except sqlite3.OperationalError:
    pass

try:
    c.execute('ALTER TABLE loadouts ADD COLUMN title_must_exclude TEXT DEFAULT ""')
except sqlite3.OperationalError:
    pass

c.commit()
print("DB columns added.")
