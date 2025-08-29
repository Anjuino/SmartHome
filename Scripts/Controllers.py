import tornado.websocket
import base64
import ParseIncomingMesseage
import asyncio

SECRET_KEY = "Mesn72154_"  
USERNAME = "Anjey"         

class WebSocketESP(tornado.websocket.WebSocketHandler):

   ping_interval = 65 
   ping_timeout  = 60

   DeviceList = []         # Список подключенных устройств

   ResponseBuffer = {}  # Добавляем словарь для ожидающих ответов
    
   async def WaitResponse(self, chip_id, response_type, timeout=5):
      future = asyncio.Future()
      key = (chip_id, response_type)
      self.ResponseBuffer[key] = future
      
      try:     return await asyncio.wait_for(future, timeout)
      finally: self.ResponseBuffer.pop(key, None)

   def on_pong(self, data): 
      pass
      # Вызывается при получении Pong от клиента
      # print(f"Получен Pong от {self}: {data}")


   async def open(self):
      AuthHeader = self.request.headers.get("Authorization")
      print("Authorization header:", AuthHeader)

      if AuthHeader:
         try:
            AuthDecoded = base64.b64decode(AuthHeader.split()[1]).decode("utf-8")
            username, password = AuthDecoded.split(':')
            print("Контроллер:", username)
            print("Пароль:", password)

            if username == USERNAME and password == SECRET_KEY: print("Соединение открыто")
            else:
               print("Имя пользователя или пароль не совпали")
               self.close()
               return
            
         except Exception as e:
            print("Неверный формат заголовка:", e)
            self.close()
            return
      else:
         print("Нет заголовка авторизации")
         self.close()
         return

   async def on_message(self, message):
      #print("Принял сообщение: %s" % message)
      await ParseIncomingMesseage.ParseMesseage(self, message)

   def on_close(self):
      for client in list(self.DeviceList):
            if client['ws'] == self:
               ChipId = client["ChipId"]
               print(f'Контроллер с UID {ChipId} отключился')
               self.DeviceList.remove(client)
      #print(self.DeviceList)

   def check_origin(self, origin):
      return True  