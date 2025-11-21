import tornado.websocket
import base64
import ParseIncomingMesseage
import asyncio

SECRET_KEY = "Mesn72154_"  
USERNAME = "Anjey"         

class WebSocketESP(tornado.websocket.WebSocketHandler):

   ping_interval = 30  # 30 секунд  
   ping_timeout = 25   # 25 секунд

   DeviceList = {}  # {token: [devices]} # Список подключенных устройств
   ResponseBuffer = {}  # Добавляем словарь для ожидающих ответов

   @classmethod
   def FindDeviceByChipId(cls, chip_id):
      for clients in cls.DeviceList.values():
         for client in clients:
               if client.get('ChipId') == chip_id:
                  return client
      return None
   
   @classmethod
   def FindDeviceByWebSocket(cls, ws):
      for clients in cls.DeviceList.values():
         for client in clients:
               if client.get('ws') == ws:
                  return client
      return None


   def __init__(self, *args, **kwargs):
      super().__init__(*args, **kwargs)
      self.connect_time = asyncio.get_event_loop().time()
      #self.ping_count = 0

   async def WaitResponse(self, chip_id, response_type, timeout=5):
      future = asyncio.Future()
      key = (chip_id, response_type)
      self.ResponseBuffer[key] = future
      
      try:     return await asyncio.wait_for(future, timeout)
      finally: self.ResponseBuffer.pop(key, None)

   def on_ping(self, data):
      """Вызывается когда отправляем ping клиенту"""
      current_time = asyncio.get_event_loop().time()
      duration = current_time - self.connect_time
      #self.ping_count += 1
      #print(f"📤 Отправлен Ping #{self.ping_count} к {id(self)} - время соединения: {duration:.1f} сек")

   def on_pong(self, data):
      current_time = asyncio.get_event_loop().time()
      duration = current_time - self.connect_time
      #print(f"Pong от {id(self)} - соединение живо: {duration:.1f} сек")


   async def open(self):

      self.firmware_file = None
      self.file_size = 0
      self.sent_bytes = 0

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
      await ParseIncomingMesseage.ParseMesseage(self, message)

   def on_close(self):
      if self.firmware_file and not self.firmware_file.closed:
         self.firmware_file.close()
         print("Закрыт файл прошивки при разрыве соединения")

      #Device = WebSocketESP.FindDeviceByWebSocket(self)

      duration = asyncio.get_event_loop().time() - self.connect_time
      #print(f"Контроллер {Device['DeviceName']} отключился")
      print(f"Разрыв через {duration:.1f} секунд")
      #print(f"Причина: code={self.close_code}, reason={self.close_reason}")

      token_to_remove = None
      # Ищем устройство и запоминаем его токен
      for token, clients in WebSocketESP.DeviceList.items():  # Убрал Controllers.
         for i, client in enumerate(clients):
               if client['ws'] == self:
                  # Удаляем устройство из списка
                  del clients[i]
                  
                  # Если список клиентов для этого токена пуст, запоминаем токен для удаления
                  if not clients:
                     token_to_remove = token
                  break
         if token_to_remove:
               break
      
      # Удаляем токен если нужно
      if token_to_remove and token_to_remove in WebSocketESP.DeviceList:  # Убрал Controllers.
         del WebSocketESP.DeviceList[token_to_remove]

      #print(WebSocketESP.DeviceList)   

   def check_origin(self, origin):
      return True  