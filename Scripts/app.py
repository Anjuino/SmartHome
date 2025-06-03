import asyncio  
import tornado.web
import OTA
import Controllers
import UserHandler
import AdminBoard


def make_app():
   return tornado.web.Application([
      (r"/ws",                             Controllers.WebSocketESP), # Открытие соединения для контроллеров

      (r"/AdminBoard",                     AdminBoard.AdminHandler),  # Страница с админкой для конкретного пользователя. Из полезного пока только прошивка контроллера и получение состояния (в идеале это пространство для тестирования запросов)

      (r"/DeviceSetting/GetFirmware",      OTA.FirmwareHandler),      # Эндпоинт по которому сервер выдает прошивку по запросу от контроллера. Подумать как можно логику работы переместить в socket

      (r"/Device/SendMesseage",     UserHandler.HTTPHandlerClient),   # Эндпоинт по которому можно отправлять сообщения в контроллер
   ])

async def main():
   app = make_app()
   app.listen(7777)
   print("Запустил сервер")
   await asyncio.Event().wait()

if __name__ == "__main__":
   #DataBase.add_user("Uniport", "l9k0167kcb")
   #asyncio.run(main()) 
   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())
   loop.close()