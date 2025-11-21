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

   if DataJson['TypeMesseage'] == 'ToDataBase':     await DataBase.SetDataToDataBase(DataJson, ChipId)

   if DataJson['TypeMesseage'] == 'GetFirmware':        await SendFirmware(self)
   if DataJson['TypeMesseage'] == 'NextFirmwarePacket': await SendNextFirmwareChunk(self)
   if DataJson['TypeMesseage'] == 'OtaFinish':          await OtaFinishHandler(self, ChipId) 


progress_status = {}  # Словарь для хранения прогресса по ChipId
firmware_positions = {}  # Храним текущую позицию в файле для каждого устройства
def CheckPlatform(firmware_path, TypeDevice, ChipId):
   try:
      with open(firmware_path, 'rb') as f:

         f.seek(-39, 2)  # Перемещаемся к footer (39 байт с конца)
         footer = f.read(39)
         
         platform_from_file = footer[32:39].decode('utf-8').strip()
         
         print(f"Платформа из файла: '{platform_from_file}'")
         print(f"Тип устройства: '{TypeDevice}'")
         
         # Проверяем совместимость по TypeDevice
         if TypeDevice == "Telemetry" and platform_from_file != "ESP8266":
            print(f"Прошивка для {platform_from_file}, а устройство ESP8266 (Telemetry)")
            progress_status[ChipId] = {"progress": 100, "status": "error", "message": "Прошивка для esp32"}
            return False
               
         elif TypeDevice == "LedController" and platform_from_file != "ESP32":
            print(f"Прошивка для {platform_from_file}, а устройство ESP32 (LedController)")
            progress_status[ChipId] = {"progress": 100, "status": "error", "message": "Прошивка для esp8266"}
            return False

         else: return True

   except Exception as e:
      print(f"Ошибка при проверке платформы: {e}")
      progress_status[ChipId] = {"progress": 100, "status": "error", "message": "Ошибка при проверке платформы"}
      return False
   
async def SendFirmware(self):
   Device = Controllers.WebSocketESP.FindDeviceByWebSocket(self)
   
   if not Device:
      print("Не удалось найти устройство для отправки прошивки")
      return

   ChipId = Device['ChipId']
   TypeDevice = Device['TypeDevice']

   firmware_filename = f"firmware_{ChipId}.bin"
   firmware_path = os.path.join(firmware_filename)

   if CheckPlatform(firmware_path, TypeDevice, ChipId) == True:
      self.firmware_file = open(firmware_path, 'rb')
      self.file_size = os.path.getsize(firmware_path)
      self.sent_bytes = 0
      
      progress_status[ChipId] = {"progress": 0, "status": "in_progress"}
      
      # Отправляем первый чанк
      await SendNextFirmwareChunk(self)

async def SendNextFirmwareChunk(self):
   Device = Controllers.WebSocketESP.FindDeviceByWebSocket(self)
   
   if not Device:
      print("Не удалось найти устройство для отправки прошивки")
      return

   ChipId = Device['ChipId']
   
   if not hasattr(self, 'firmware_file') or self.firmware_file.closed:
      print(f"Файл прошивки не открыт для устройства {ChipId}")
      return

   try:
      chunk = self.firmware_file.read(2048)
      if not chunk:
         return
   
      await self.write_message(chunk, binary=True)
   
      self.sent_bytes += len(chunk)
   
      progress = round((self.sent_bytes / self.file_size) * 99)
      progress_status[ChipId] = {"progress": progress, "status": "in_progress"}
      print(f"\rПрогресс: {progress}% (отправлено {self.sent_bytes} из {self.file_size} байт)", end="", flush=True)
      
   except Exception as e:
      print(f"Ошибка отправки чанка: {e}")
      progress_status[ChipId] = {"progress": 0, "status": "error", "message": str(e)}
      if hasattr(self, 'firmware_file'):
         self.firmware_file.close()

async def OtaFinishHandler(self, ChipId):
   print(f"Устройство {ChipId} сообщило об успешном завершении OTA")
   
   if hasattr(self, 'firmware_file') and not self.firmware_file.closed:
      self.firmware_file.close()
      print(f"Файл прошивки для {ChipId} закрыт")
   
   progress_status[ChipId] = {"progress": 100, "status": "completed"}

async def LogHandler(self, Json, ChipId):
   Device = Controllers.WebSocketESP.FindDeviceByChipId(ChipId)
   if Device:
      Log = Json['Log']
      DeviceName = Device['DeviceName']  
      print(f"Получил лог от {ChipId}:{DeviceName} ---> {Log}")

async def Authentication(self, Json, ChipId):
   Token = Json['Token']
   DeviceType = Json['TypeDevice']
   Build = Json['Build']

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
   
   # Инициализируем структуру для нового токена, если его нет
   if Token not in Controllers.WebSocketESP.DeviceList:
      Controllers.WebSocketESP.DeviceList[Token] = []
   
   # Ищем устройство в списке для данного токена
   for client in Controllers.WebSocketESP.DeviceList[Token]:
      if client['ChipId'] == ChipId:
         # Обновляем существующее устройство
         client['ws'] = self
         client['Build'] = Build
         FoundDevice = True
         break

   if not FoundDevice:
      # Добавляем устройство как новое для данного токена
      Controllers.WebSocketESP.DeviceList[Token].append({
         'ChipId': ChipId, 
         'DeviceName': DeviceName, 
         'TypeDevice': DeviceType,
         'Build': Build,
         'ws': self
      })

   print(Controllers.WebSocketESP.DeviceList)