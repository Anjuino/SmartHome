import tornado.web
import os

FIRMWARE_PATH = "firmware.bin"

class OTAHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("../static/html/OTA.html")

    async def post(self):
        if 'firmware' not in self.request.files:
            self.write("Нет файла")
            return
        
        file_info = self.request.files['firmware'][0]
        filename = file_info['filename']
        if not filename.endswith('.bin'):
            self.write("Формат файла должен быть bin")
            return

        firmware_path = os.path.join("firmware.bin")
        with open(firmware_path, 'wb') as f:
            f.write(file_info['body'])

        self.write("Файл загружен")

class FirmwareHandler(tornado.web.RequestHandler):
    async def get(self):
        if not os.path.exists(FIRMWARE_PATH):
            self.set_status(404)
            self.write("Прошивка не найдена")
            return
        
        self.set_header('Content-Type', 'application/octet-stream')
        with open(FIRMWARE_PATH, 'rb') as f:
            self.write(f.read())
