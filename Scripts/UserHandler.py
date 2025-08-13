import tornado.web
import Controllers
import json
import asyncio

#### Сделать потом возможность разбора сообщений от контроллеров по типу устройства, чтобы не было как сейчас все в общей куче.

class HTTPHandlerClient(tornado.web.RequestHandler):
   async def post(self):
      try:
         JsonData = json.loads(self.request.body)
         ChipId = JsonData['ChipId']
         TypeMesseage = JsonData['TypeMesseage']

         TypeResponse = None
         Request      = None

         ### общие команды
         if (TypeMesseage == "GetState"): 
            TypeResponse = "State"
            Request = {"TypeMesseage": TypeMesseage}

         if (TypeMesseage == "Reboot"):
            Request = {"TypeMesseage": TypeMesseage}

         ### команды для телеметрии
         if (TypeMesseage == "UpdateZoneName"):
            TypeResponse = "UpdateZoneName"
            Request = {
               "TypeMesseage": TypeMesseage,
               "NumZone": JsonData['NumZone'],
               "OldName": JsonData['OldName'],
               "NewName": JsonData['NewName']
            }

         ### команды для контроллеров лент
         if (TypeMesseage == "GetSettingLed"):
            TypeResponse = "LedSetting"
            Request = {
               "TypeMesseage": TypeMesseage,
            }

         if (TypeMesseage == "UpdateSettingLed"):
            IsDetectedMove = JsonData.get('IsDetectedMove')
            if IsDetectedMove:
               Request = {
                  "TypeMesseage": TypeMesseage,
                  "LedCount": JsonData['LedCount'],
                  "IsDetectedMove": JsonData['IsDetectedMove']
               }
            else:
               Request = {
                  "TypeMesseage": TypeMesseage,
                  "LedCount": JsonData['LedCount']
               }    
            
         if (TypeMesseage == "SetStateToLed"):
            Request = {
               "TypeMesseage": "SetState",
               "Mode": JsonData['Mode'],
               "ColorR": JsonData['ColorR'],
               "ColorG": JsonData['ColorG'],
               "ColorB": JsonData['ColorB'] 
            }

         if (TypeMesseage == "SetSpeedToLed"):
            Request = {
               "TypeMesseage": "SetSpeed",
               "Speed": JsonData['Speed']
            }

         if (TypeMesseage == "SetBrightnessToLed"):
            Request = {
               "TypeMesseage": "SetBrightness",
               "Brightness": JsonData['Brightness']
            }

         # Находим нужное устройство
         Device = None
         for client in Controllers.WebSocketESP.DeviceList:
            if client['ChipId'] == ChipId:
               Device = client['ws']
               break
         
         if not Device: raise Exception("Устройство не найдено или не подключено")
                  
         # Отправляем запрос устройству
         await Device.write_message(json.dumps(Request))
         
         # Если ждать ответ не надо, то отдадим в web ответ сразу
         if not TypeResponse: 
            self.write({'status': 'success'})
            return    
         
         # Ждем ответ   
         Response = await Device.WaitResponse(ChipId, TypeResponse)
                
         self.write({'status': 'success', 'response': Response})  
           
      except asyncio.TimeoutError:
         self.set_status(408)
         self.write({'error': 'Timeout waiting for response'})
      except Exception as e:
         self.set_status(400)
         self.write({'error': str(e)})