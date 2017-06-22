import sqlite3
conn = sqlite3.connect('factbook.db')

c = conn.cursor()
c.execute('SELECT * FROM facts order by population desc limit 10;')

print(c.fetchall())
