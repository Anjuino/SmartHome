import tornado.web
import Controllers
import json

class HTTPHandlerClient(tornado.web.RequestHandler):
   #async def get(self):
      #Messeage = json.dumps({"TypeMesseage": "StartOTA"}, ensure_ascii=False)
      #Controllers.WebSocketESP.DeviceList[0]['ws'].write_message(Messeage)

   async def post(self):
      try:
         data = json.loads(self.request.body)
         chip_id = data['chip_id']
         TypeMesseage = data['TypeMesseage']

         response_type = 'None'
         request_msg   = 'None' 

         if (TypeMesseage == "GetState"):
            response_type = "State"
            request_msg = {"TypeMesseage": TypeMesseage}
         
         # Находим нужное устройство
         device_ws = None
         for client in Controllers.WebSocketESP.DeviceList:
            if client['ChipId'] == chip_id:
               device_ws = client['ws']
               break
         
         if not device_ws:
            raise Exception("Устройство не найдено или не подключено")
         
         # Отправляем запрос и ждем ответ
         response = await device_ws.wait_for_response(
            chip_id=chip_id,
            response_type=response_type
         )
         
         # Отправляем запрос устройству
         await device_ws.write_message(json.dumps(request_msg))
         
         self.write({
               'status': 'success',
               'response': response
         })
         
      except asyncio.TimeoutError:
         self.set_status(408)
         self.write({'error': 'Timeout waiting for response'})
      except Exception as e:
         self.set_status(400)
         self.write({'error': str(e)})