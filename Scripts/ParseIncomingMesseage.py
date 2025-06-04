import json
import DataBase
import asyncio
import os

async def ParseMesseage(self, Messeage):
   DataJson = json.loads(Messeage)

   TypeMesseage = DataJson['TypeMesseage']
   ChipId = DataJson['ChipId']

   # Проверяем, есть ли ожидающий этот ответ запрос
   key = (ChipId, TypeMesseage)
   if key in self.ResponseBuffer and not self.ResponseBuffer[key].done(): 
      self.ResponseBuffer[key].set_result(DataJson)
   
   if DataJson['TypeMesseage'] == 'Authentication': await Authentication(self, DataJson, ChipId)      
   if DataJson['TypeMesseage'] == 'Log':            await LogHandler(self, DataJson, ChipId)
   if DataJson['TypeMesseage'] == 'GetFirmware':    await SendFirmware(self)


async def SendFirmware(self):
   chunk_size = 4096  # 4 КБ за раз
   totalReadSize = 0
   try:
      with open("firmware.bin", 'rb') as f:
         file_size = os.path.getsize("firmware.bin")
         while True:

            chunk = f.read(chunk_size)
            if not chunk:
               print("Отправил прошивку") 
               break  # Файл закончился
      
            # Проверяем, что соединение ещё открыто
            if self.ws_connection.is_closing():
               print("Клиент отключился, отмена отправки")
               return
            
            await self.write_message(chunk, binary=True)
            totalReadSize += chunk_size

            print(f"\rПрогресс: {round((totalReadSize / file_size) * 99)} %", end="", flush=True)
            await asyncio.sleep(0.3)
   except Exception as e:
      print(f"Ошибка: {e}")

async def LogHandler(self, Json, ChipId):
   for index, client in enumerate(self.DeviceList):
      if client['ChipId'] == ChipId:
         Log = Json['Log']
         DeviceName = client['DeviceName']  
         print(f"Получил лог от {ChipId}:{DeviceName} ---> {Log}")
         break

async def Authentication(self, Json, ChipId):
   Token = Json['Token']
   
   # Проверяем наличие контроллера в базе
   if await DataBase.CheckController(ChipId):
      pass  # Контроллер уже есть в базе
   else: 
      if await DataBase.SetController(ChipId, Token):
         pass  # Контроллер успешно добавлен
      else:
         print("Токен контроллера неверный")
         Messeage = json.dumps({"Command": "ResetToken"}, ensure_ascii=False)
         await self.write_message(Messeage)
         return

   DeviceName = await DataBase.GetControllerName(ChipId)
   FoundDevice = False
   
   # Ищем устройство в списке
   for index, client in enumerate(self.DeviceList):
      if client['ChipId'] == ChipId:
         #print("Обновляю устройство в списке") 
         # Обновляем существующее устройство
         self.DeviceList[index]['ws'] = self
         FoundDevice = True
         break

   if not FoundDevice:
      #print("Добавляю устройство как новое") 
      self.DeviceList.append({
         'ChipId': ChipId, 
         'DeviceName': DeviceName, 
         'ws': self
      })

   print(self.DeviceList)