import json
import DataBase


def ParseMesseage(self, Messeage):

   DataJson = json.loads(Messeage)

   msg_type = DataJson.get('TypeMesseage')
   chip_id = None
   
   # Находим chip_id для этого соединения
   for client in self.DeviceList:
      if client['ws'] == self:
            chip_id = client["ChipId"]
            break
   
   if not chip_id:
      return
      
   # Проверяем, есть ли ожидающий этот ответ запрос
   key = (chip_id, msg_type)
   if key in self.pending_responses and not self.pending_responses[key].done():
      self.pending_responses[key].set_result(DataJson)

   if (DataJson['TypeMesseage'] == 'Authentication'): Authentication(self, DataJson)
   if (DataJson['TypeMesseage'] == 'State'):          
      print(DataJson)
      
   if (DataJson['TypeMesseage'] == 'Log'):            LogHandler(self, DataJson)

            
def LogHandler(self, Json):
   for index, client in enumerate(self.DeviceList):
      if client['ChipId'] == Json['ChipId']:

         ChipId = Json['ChipId']
         Log    = Json['Log']
         DeviceName = client['DeviceName']  
         print(f"Получил лог от {ChipId}:{DeviceName} ---> {Log}")
         break

def Authentication(self, Json):

   ChipId     = Json['ChipId']
   Token      = Json['Token']
   
   #print(ChipId)
   #print(Token)
   if (DataBase.CheckController(ChipId)): pass        # Смотрю наличие контроллера в базе, если есть, то иду дальше, если нет, то записываю
   else: 
      if (DataBase.SetController(ChipId, Token)): pass
      else:
         print("Токен контроллера неверный")
         Messeage = json.dumps({"Command": "ResetToken"}, ensure_ascii=False)
         self.write_message(Messeage)
         return
         # Вот тут отправить в контроллер событие что токен который он передал не найден и нужно сбросить текущий токен и перезагрузиться


   DeviceName = DataBase.GetControllerName(ChipId)
   #print(DeviceName)   
   FoundDevice = False
   # Ищем устройство в списке
   for index, client in enumerate(self.DeviceList):
      if client['ChipId'] == ChipId: 
         # Обновляем существующее устройство
         self.DeviceList[index]['ws'] = self
         FoundDevice = True
         break

   if not FoundDevice:
      self.DeviceList.append({'ChipId' : ChipId, 
                           'DeviceName': DeviceName, 
                           'ws': self}) # добавляем новый

   print(self.DeviceList)       