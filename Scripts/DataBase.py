import bcrypt
import sqlite3
import os
import random
import string

script_dir = os.path.dirname(os.path.abspath(__file__))
PATHDATABASE = os.path.join(script_dir, '../DataBase/IOT_Sysytem.db')

# Функция для добавления пользователя
def AddUser(login, password):
   connection = sqlite3.connect(PATHDATABASE)
   cursor = connection.cursor()

   hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())   # Хеширование пароля

   characters = string.ascii_letters + string.digits 
   token = ''.join(random.choices(characters, k=6))

   cursor.execute('''
   INSERT INTO Users (Login, Password, Token) VALUES (?, ?, ?)
   ''', (login, hashed_password, token))

   connection.commit()
   connection.close()

# Проверить пользователя по паролю
def CheckUser(login, password):
   connection = sqlite3.connect(PATHDATABASE)
   cursor = connection.cursor()
   cursor.execute('SELECT Password FROM Users WHERE Login = ?', (login,))
   result = cursor.fetchone()
   connection.close()

   if result and bcrypt.checkpw(password.encode('utf-8'), result[0]): return True 

   return False  # Пароль неверный

# Найти контроллер по ChipId
def CheckController(ChipId):
   connection = sqlite3.connect(PATHDATABASE)
   cursor = connection.cursor()
   cursor.execute('SELECT ChipId FROM Controllers WHERE ChipId = ?', (ChipId,))
   result = cursor.fetchone()
   connection.close()

   if result is not None: return True   # ChipId найден
   else:                  return False  # ChipId не найден

# Найти имя контроллера по ChipId
def GetControllerName(ChipId):
   connection = sqlite3.connect(PATHDATABASE)
   cursor = connection.cursor()
   cursor.execute('SELECT DeviceName FROM Controllers WHERE ChipId = ?', (ChipId,))
   result = cursor.fetchone()
   connection.close()
   return result

# Записать контроллер в базу
def SetController(ChipId, Token):
   connection = sqlite3.connect(PATHDATABASE)
   cursor = connection.cursor()

   cursor.execute('SELECT Id FROM Users WHERE Token = ?', (Token,))
   User = cursor.fetchone()

   TokenIs = False

   if User:
      try:
         cursor.execute('INSERT INTO Comtrollers (ChipId, DeviceName, UserId) VALUES (?, ?, ?)', (ChipId, "NONE", User[0]))
         connection.commit()
         print(f'Контроллер с ChipId {ChipId} успешно добавлен для пользователя с Id {User[0]}.')
         TokenIs = True
      except sqlite3.IntegrityError:
         print(f'Контроллер с ChipId {ChipId} уже существует.')
         TokenIs = True
   else:
      print("Пользователь с таким токеном не найден.")

   
   connection.close()
   return TokenIs