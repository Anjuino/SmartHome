import json
import DataBase
import asyncio
import os
import Controllers

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


progress_status = {}  # Словарь для хранения прогресса по ChipId
async def SendFirmware(self):
   ChipId = None
   for client in self.DeviceList:
      if client['ws'] == self:
         ChipId = client['ChipId']
         break

   # Сохраняем оригинальные значения
   CurrentPingInterval = self.ping_interval
   CurrentPingTimeout  = self.ping_timeout
   
   # Временно отключаем пинги
   self.ping_interval = None
   self.ping_timeout = None
   
   try:
      firmware_filename = f"firmware_{ChipId}.bin"
      firmware_path = os.path.join(firmware_filename)

      chunk_size = 4096
      totalReadSize = 0
      with open(firmware_path, 'rb') as f:
         file_size = os.path.getsize(firmware_path)
         while True:
               chunk = f.read(chunk_size)
               if not chunk:
                  print("Отправил прошивку")
                  progress_status[ChipId] = {"progress": 100, "status": "completed"}
                  break
               
               if self.ws_connection.is_closing():
                  print("Клиент отключился, отмена отправки")
                  progress_status[ChipId] = {"progress": 0, "status": "failed"}
                  return
               
               await self.write_message(chunk, binary=True)
               totalReadSize += len(chunk)
               
               progress = round((totalReadSize / file_size) * 99)
               progress_status[ChipId] = {"progress": progress, "status": "in_progress"}
               print(f"\rПрогресс: {progress} %", end="", flush=True)
               await asyncio.sleep(0.3)
   except Exception as e:
      print(f"Ошибка: {e}")
      progress_status[ChipId] = {"progress": 0, "status": "error", "message": str(e)}
   finally:
      # Восстанавливаем оригинальные значения
      self.ping_interval = CurrentPingInterval
      self.ping_timeout = CurrentPingTimeout

async def Authentication(self, Json, ChipId):
   Token = Json['Token']
   DeviceType = Json['TypeDevice']

   # Проверяем наличие контроллера в базе
   if await DataBase.CheckController(ChipId): pass  # Контроллер уже есть в базе
   else: 
      if await DataBase.SetController(ChipId, Token): pass  # Контроллер успешно добавлен
      else:
         print("Токен контроллера неверный")
         Messeage = json.dumps({"Command": "ResetToken"}, ensure_ascii=False)
         await self.write_message(Messeage)
         return

   DeviceName = await DataBase.GetControllerName(ChipId)
   FoundDevice = False
   
   # Ищем устройство в списке
   for client in Controllers.WebSocketESP.DeviceList:
      if client['ChipId'] == ChipId:
         #print("Обновляю устройство в списке") 
         # Обновляем существующее устройство
         client['ws'] = self
         FoundDevice = True
         break

   if not FoundDevice:
      #print("Добавляю устройство как новое") 
      Controllers.WebSocketESP.DeviceList.append({
         'ChipId': ChipId, 
         'DeviceName': DeviceName, 
         'TypeDevice': DeviceType,
         'ws': self
      })

   print(Controllers.WebSocketESP.DeviceList)