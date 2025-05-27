import sqlite3

conn = sqlite3.connect('IOT_System.db')
cursor = conn.cursor()


cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   login TEXT UNIQUE NOT NULL,
   password TEXT NOT NULL,
   token TEXT UNIQUE NOT NULL
)
''')

# Создаем таблицу контроллеров
cursor.execute('''
CREATE TABLE IF NOT EXISTS controllers (
   id INTEGER PRIMARY KEY AUTOINCREMENT,
   chipid TEXT NOT NULL,
   token TEXT NOT NULL,
   user_id INTEGER NOT NULL,
   FOREIGN KEY (user_id) REFERENCES users (id),
   UNIQUE(chipid, token)
)
''')

conn.commit()