import tornado.websocket
import base64
import ParseIncomingMesseage


SECRET_KEY = "Mesn72154_"  
USERNAME = "Anjey"         

class WebSocketESP(tornado.websocket.WebSocketHandler):
   ping_interval = 30 
   ping_timeout  = 10

   DeviceList = []  # Список подключенных устройств
   def on_pong(self, data): 
      pass
      # Вызывается при получении Pong от клиента
      # print(f"Получен Pong от {self}: {data}")


   def open(self):
      auth_header = self.request.headers.get("Authorization")
      print("Authorization header:", auth_header)

      if auth_header:
         try:
            auth_decoded = base64.b64decode(auth_header).decode("utf-8")
            username, password = auth_decoded.split(':')
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

   def on_message(self, message):
      print("Принял сообщение: %s" % message)
      ParseIncomingMesseage.ParseMesseage(self, message)

   def on_close(self):
      print("Соединение закрыто")
      for client in list(self.DeviceList):
            if client['ws'] == self:
               ChipId = client["ChipId"]
               Message = f'Контроллер с UID {ChipId} отключился'
               print(Message)
               self.clients.remove(client)

   def check_origin(self, origin):
      return True  