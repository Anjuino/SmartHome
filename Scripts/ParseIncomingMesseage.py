import json
import DataBase


def ParseMesseage(self, Messeage):

   DataJson = json.loads(Messeage)

   if (DataJson['TypeMesseage'] == 'Authentication'): Authentication(self, DataJson)

            

def Authentication(self, Json):

   ChipId     = Json['ChipId']
   Token      = Json['Token']
   
   print(ChipId)
   print(Token)
   """if (DataBase.CheckController(ChipId)): pass        # Смотрю наличие контроллера в базе, если есть, то иду дальше, если нет, то записываю
   else: 
      if (DataBase.SetController(ChipId, Token)): pass
      else:
         print("Токен контроллера неверный")
         Messeage = json.dumps({"Command": "ResetToken"}, ensure_ascii=False)
         self.write_message(Messeage)
         return
         # Вот тут отправить в контроллер событие что токен который он передал не найден и нужно сбросить текущий токен и перезагрузиться


   DeviceName = DataBase.GetControllerName(ChipId)   
   FoundDevice = False
   for client in list(self.DeviceList):
      if client['ChipId'] == ChipId: 
         self.clients['ws'] = self
         FoundDevice = True
         break

   if not FoundDevice:
      self.clients.append({'ChipId' : ChipId, 
                           'DeviceName': DeviceName, 
                           'ws': self,
                           'Sensors': []}) # добавляем новый
                """