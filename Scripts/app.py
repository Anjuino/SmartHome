import asyncio  
import tornado.web
import Controllers
import UserHandler
import AdminBoard
import OTA

def make_app():
   return tornado.web.Application([
      (r"/ws",                      Controllers.WebSocketESP),        # Открытие соединения для контроллеров
      (r"/Admin",                   AdminBoard.AdminHandler),         # Страница с админкой для конкретного пользователя. Из полезного пока только прошивка контроллера и получение состояния (в идеале это пространство для тестирования запросов)
      (r"/Device/SendMesseage",     UserHandler.HTTPHandlerClient),   # Эндпоинт по которому можно отправлять сообщения в контроллер
      (r"/Device/OTA",              OTA.OTAHandler),                  # Эндпоинт по которому можно загрузить прошивку на сервер
   ])

async def main():
   app = make_app()
   app.listen(7777)
   print("Запустил сервер")
   await asyncio.Event().wait()

if __name__ == "__main__":
   #DataBase.add_user("Uniport", "l9k0167kcb")
   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())
   loop.close()