import tornado.web
import Controllers
import json
import asyncio

class HTTPHandlerClient(tornado.web.RequestHandler):
   #async def get(self):
      #Messeage = json.dumps({"TypeMesseage": "StartOTA"}, ensure_ascii=False)
      #Controllers.WebSocketESP.DeviceList[0]['ws'].write_message(Messeage)

   async def post(self):
      try:
         JsonData = json.loads(self.request.body)
         ChipId = JsonData['ChipId']
         TypeMesseage = JsonData['TypeMesseage']

         TypeResponse = None
         Request      = None
         if (TypeMesseage == "GetState"): 
            TypeResponse = "State"
            Request = {"TypeMesseage": TypeMesseage}

         # Находим нужное устройство
         Device = None
         for client in Controllers.WebSocketESP.DeviceList:
            if client['ChipId'] == ChipId:
               Device = client['ws']
               break
         
         if not Device: raise Exception("Устройство не найдено или не подключено")
         
         # Отправляем запрос устройству
         await Device.write_message(json.dumps(Request))

         # Ждем ответ
         Response = await Device.WaitResponse(ChipId, TypeResponse)
                
         self.write({
               'status': 'success',
               'response': Response
         })    
      except asyncio.TimeoutError:
         self.set_status(408)
         self.write({'error': 'Timeout waiting for response'})
      except Exception as e:
         self.set_status(400)
         self.write({'error': str(e)})