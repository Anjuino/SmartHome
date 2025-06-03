import asyncio  
import tornado.web
import OTA
import Controllers
import UserHandler


def make_app():
   return tornado.web.Application([
      (r"/ws",                             Controllers.WebSocketESP),
      (r"/DeviceSetting/OTA",              OTA.OTAHandler),
      (r"/DeviceSetting/GetFirmware",      OTA.FirmwareHandler),
      (r"/DeviceSetting/SendMesseage",     UserHandler.HTTPHandlerClient), 
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