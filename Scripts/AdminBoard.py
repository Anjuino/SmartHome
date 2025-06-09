import tornado.web
import json
import ParseIncomingMesseage
import Controllers
import DataBase

class AdminHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("../static/html/AdminPanel.html")

    async def post(self):
        JsonData = json.loads(self.request.body)
        TypeMesseage = JsonData['TypeMesseage']

        if (TypeMesseage == "GetListDevice"): 
            ListDevice = [{"ChipId": client["ChipId"], "TypeDevice": client["TypeDevice"], "DeviceName": client["DeviceName"]} for client in Controllers.WebSocketESP.DeviceList]  
            self.write(json.dumps(ListDevice)) # отправляем клиенту

        if (TypeMesseage == "GetProgress"):
            ChipId = JsonData.get('ChipId') 
            status = ParseIncomingMesseage.progress_status.get(int(ChipId), {"progress": 0, "status": "not_started"})
            self.write(status)

        if (TypeMesseage == "UpdateNameController"):
            ChipId = JsonData.get('ChipId')
            DeviceName =  JsonData.get('NewName')
            await DataBase.UpdateControllerName(ChipId, DeviceName)

            for client in Controllers.WebSocketESP.DeviceList:
                if client['ChipId'] == ChipId:
                    client['DeviceName'] = DeviceName
                    break

            self.write({"status": "success"})

