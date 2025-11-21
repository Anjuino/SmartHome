import bcrypt
import sqlite3
import os
import random
import string
import aiosqlite
import asyncio

#script_dir = os.path.dirname(os.path.abspath(__file__))
#PATHDATABASE = os.path.join(script_dir, '../DataBase/IOT_System.db') 
PATHDATABASE = '/root/Flash/IOT_System.db'


# Функция для добавления пользователя
async def AddUser(login, password):
   hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())   
   characters = string.ascii_letters + string.digits 
   #token = ''.join(random.choices(characters, k=6))
   token = '777507'

   async with aiosqlite.connect(PATHDATABASE) as db:
      await db.execute('''
      INSERT INTO Users (Login, Password, Token) VALUES (?, ?, ?)
      ''', (login, hashed_password, token))
      await db.commit()

# Проверить пользователя по паролю
async def CheckUser(login, password):
    async with aiosqlite.connect(PATHDATABASE) as db:
        cursor = await db.execute('SELECT Password, Token FROM Users WHERE Login = ?', (login,))
        result = await cursor.fetchone()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[0]):
        return result[1]  # Возвращаем токен пользователя
    return None  # Если авторизация не удалась

# Проверяет, что устройство принадлежит пользователю с данным токеном
async def CheckDeviceOwnership(token, chip_id):
   async with aiosqlite.connect(PATHDATABASE) as db:
      cursor = await db.execute(
         'SELECT 1 FROM Controllers WHERE ChipId = ? AND Token = ?', 
         (chip_id, token)
      )
      result = await cursor.fetchone()
      return result is not None

# Проверяет существует ли токен в базе 
async def CheckToken(token):
    async with aiosqlite.connect(PATHDATABASE) as db:
        cursor = await db.execute('SELECT 1 FROM Users WHERE Token = ?', (token,))
        result = await cursor.fetchone()
        return result is not None

# Найти контроллер по ChipId
async def CheckController(ChipId):
   async with aiosqlite.connect(PATHDATABASE) as db:
      cursor = await db.execute('SELECT ChipId FROM Controllers WHERE ChipId = ?', (ChipId,))
      result = await cursor.fetchone()
   return result is not None


# Найти имя контроллера по ChipId
async def GetControllerName(ChipId):
   async with aiosqlite.connect(PATHDATABASE) as db:
      cursor = await db.execute('SELECT DeviceName FROM Controllers WHERE ChipId = ?', (ChipId,))
      result = await cursor.fetchone()
   return result[0]

# Обновить имя контроллера по ChipId
async def UpdateControllerName(ChipId, new_name):
   async with aiosqlite.connect(PATHDATABASE) as db:
      await db.execute('UPDATE Controllers SET DeviceName = ? WHERE ChipId = ?', (new_name, ChipId))
      await db.commit()


# Записать контроллер в базу
async def SetController(ChipId, Token):
   TokenIs = False
   async with aiosqlite.connect(PATHDATABASE) as db:
      cursor = await db.execute('SELECT Id FROM Users WHERE Token = ?', (Token,))
      User = await cursor.fetchone()

      if User:
         try:
            await db.execute('''
            INSERT INTO Controllers (ChipId, DeviceName, UserId) 
            VALUES (?, ?, ?)
            ''', (ChipId, "NONE", User[0]))
            await db.commit()
            print(f'Контроллер с ChipId {ChipId} успешно добавлен для пользователя с Id {User[0]}.')
            TokenIs = True
         except aiosqlite.IntegrityError:
            print(f'Контроллер с ChipId {ChipId} уже существует.')
            TokenIs = True
      else:
         print("Пользователь с таким токеном не найден.")
   
   return TokenIs

async def SetDataToDataBase(DataJson, ChipId):
   try:
      async with aiosqlite.connect(PATHDATABASE) as db:
         if DataJson.get('Temperature') is not None: await _insert_sensor_data(db, ChipId, 'Temperature', DataJson['Temperature'])
         
         if DataJson.get('Humidity') is not None: await _insert_sensor_data(db, ChipId, 'Humidity', DataJson['Humidity'])
         
         if DataJson.get('CO2ppm') is not None: await _insert_sensor_data(db, ChipId, 'CO2ppm', DataJson['CO2ppm'])
               
   except Exception as e:
      print(f"Ошибка при работе с БД: {e}")

async def _insert_sensor_data(db, chip_id, sensor_type, value):
    try:
        async with db.cursor() as cursor:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
            
            query = f'INSERT INTO {sensor_type} (ChipId, {sensor_type}, Time) VALUES (?, ?, ?)'
            await cursor.execute(query, (chip_id, value, now))
            
    except sqlite3.IntegrityError as e:
        print(f"Ошибка целостности данных для {sensor_type}: {e}")
    except Exception as e:
        print(f"Ошибка при записи {sensor_type}: {e}")
