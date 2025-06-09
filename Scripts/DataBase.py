import bcrypt
import sqlite3
import os
import random
import string
import aiosqlite
import asyncio

script_dir = os.path.dirname(os.path.abspath(__file__))
PATHDATABASE = os.path.join(script_dir, '../DataBase/IOT_Sysytem.db')

# Функция для добавления пользователя
async def AddUser(login, password):
   hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())   
   characters = string.ascii_letters + string.digits 
   token = ''.join(random.choices(characters, k=6))

   async with aiosqlite.connect(PATHDATABASE) as db:
      await db.execute('''
      INSERT INTO Users (Login, Password, Token) VALUES (?, ?, ?)
      ''', (login, hashed_password, token))
      await db.commit()

# Проверить пользователя по паролю
async def CheckUser(login, password):
   async with aiosqlite.connect(PATHDATABASE) as db:
      cursor = await db.execute('SELECT Password FROM Users WHERE Login = ?', (login,))
      result = await cursor.fetchone()

   if result and bcrypt.checkpw(password.encode('utf-8'), result[0]): 
      return True 
   return False

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