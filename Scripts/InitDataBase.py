import sqlite3
import os

def create_database():
    PATHDATABASE = '/root/Flash/IOT_System.db'
        
    try:
        # Подключаемся к базе данных (создается автоматически, если не существует)
        conn = sqlite3.connect(PATHDATABASE)
        cursor = conn.cursor()
        
        # Создаем таблицу Temperature
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Temperature (
            ChipId           INTEGER,
            Temperature      REAL,
            Time             TEXT
        )  
        ''')
        
        # Создаем таблицу Humidity
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Humidity (
            ChipId           INTEGER,
            Humidity         REAL,
            Time             TEXT
        )  
        ''')
        
        # Создаем таблицу CO2ppm
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CO2ppm (
            ChipId           INTEGER,
            CO2ppm           REAL,
            Time             TEXT
        )  
        ''')
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

        # Сохраняем изменения
        conn.commit()
        print("База данных успешно создана!")
        print(f"Путь: {PATHDATABASE}")
        print("Созданные таблицы: Temperature, Humidity, CO2ppm")
        
    except sqlite3.Error as e:
        print(f"Ошибка при создании базы данных: {e}")
        
    finally:
        # Закрываем соединение
        if conn:
            conn.close()

create_database()            