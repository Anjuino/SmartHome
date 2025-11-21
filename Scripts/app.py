#555707 Тестовый токен MyHome l9k0167kcb
#777507 Родители Лены Home1 acea1459

import asyncio  
import tornado.web
import Controllers
import UserHandler
import AdminBoard
import DataBase
import os
import OTA
import json
current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def make_app():
   return tornado.web.Application([
      (r"/ws",                      Controllers.WebSocketESP),        # Открытие соединения для контроллеров
      (r"/Admin",                   AdminBoard.AdminHandler),         # Страница с админкой. Можно тестировать разные запросы на устройства.
      (r"/Device/SendMesseage",     UserHandler.HTTPHandlerClient),   # Эндпоинт по которому можно отправлять сообщения в контроллер
      (r"/Device/OTA",              OTA.OTAHandler),                  # Эндпоинт по которому можно загрузить прошивку на сервер с отправкой в выбранный контроллер
      (r"/Auth",                    UserHandler.AuthHandler),         # Авторизация для пользователей
      (r"/App",                     UserHandler.AuthHandler),         # Основное приложение

      (r"/(.*)", tornado.web.StaticFileHandler, {"path": current_dir})
   ])

async def main():
   app = make_app()
   app.listen(7777, '0.0.0.0')
   print("Запустил сервер")
   #await DataBase.AddUser("Home1", "acea1459")
   await asyncio.Event().wait()

if __name__ == "__main__":
   loop = asyncio.get_event_loop()
   loop.run_until_complete(main())
   loop.close()