import asyncio  
import tornado.web
import OTA
import Controllers



def make_app():
   return tornado.web.Application([
      (r"/ws",           Controllers.WebSocketESP),
      (r"/ota",          OTA.OTAHandler),
      (r"/GetFirmware",  OTA.FirmwareHandler), 
   ])

async def main():
   app = make_app()
   app.listen(7777)
   print("запустил сервер")
   await asyncio.Event().wait()

if __name__ == "__main__":
   asyncio.run(main()) 