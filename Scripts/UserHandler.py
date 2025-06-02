import tornado.web
import Controllers
import json

class HTTPHandlerClient(tornado.web.RequestHandler):
   def get(self):
      Messeage = json.dumps({"TypeMesseage": "GetState"}, ensure_ascii=False)
      #Messeage = json.dumps({"TypeMesseage": "StartOTA"}, ensure_ascii=False)
      Controllers.WebSocketESP.DeviceList[0]['ws'].write_message(Messeage)