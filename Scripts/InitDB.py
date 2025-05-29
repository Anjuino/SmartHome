import sqlite3
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
PATHDATABASE = os.path.join(script_dir, '../DataBase/IOT_Sysytem.db')

conn = sqlite3.connect(PATHDATABASE)
cursor = conn.cursor()

# Создаем таблицу пользователей
cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
   Id       INTEGER PRIMARY KEY AUTOINCREMENT,
   Login    TEXT UNIQUE NOT NULL,
   Password TEXT NOT NULL,
   Token    TEXT UNIQUE NOT NULL
)
''')

# Создаем таблицу контроллеров
cursor.execute('''
CREATE TABLE IF NOT EXISTS Controllers (
   Id          INTEGER PRIMARY KEY AUTOINCREMENT,
   ChipId      TEXT NOT NULL,
   DeviceName  TEXT,
   UserId      INTEGER NOT NULL,
   FOREIGN KEY (UserId) REFERENCES Users (Id),
   UNIQUE(ChipId)
)
''')

conn.commit()