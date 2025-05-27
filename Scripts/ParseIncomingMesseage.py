import json
import DataBase


def ParseMesseage(self, Messeage):

   DataJson = json.loads(Messeage)

   if (DataJson['TypeMesseage'] == 'Registration'): Registration(self, DataJson)

            

def Registration(self, Json):


# Найти в базе данных пользователя с указанным токеном и записать в таблицу контроллеров chipid token user и добавить в list

   FoundDevice = False
   for client in list(self.DeviceList):
      ChipId = 1
      if client['ChipId'] == ChipId: 
         self.clients['ws'] = self
         FoundDevice = True
         break

   if not FoundDevice:
      self.clients.append({'ChipId' : ChipId, 
                           'Type': DeviceType, 
                           'DeviceName': DeviceName, 
                           'ws': self,
                           'Sensors': []}) # добавляем новый
                