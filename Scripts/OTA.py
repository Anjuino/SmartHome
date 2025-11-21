import tornado.web
import os
import Controllers
import json

FIRMWARE_PATH = "firmware.bin"

class OTAHandler(tornado.web.RequestHandler):
    async def get(self):
        if not os.path.exists(FIRMWARE_PATH):
            self.set_status(404)
            self.write("Прошивка не найдена")
            return
        
        self.set_header('Content-Type', 'application/octet-stream')
        with open(FIRMWARE_PATH, 'rb') as f:
            self.write(f.read())

    async def post(self):
        # Проверяем наличие файла и chipid
        if 'firmware' not in self.request.files:
            self.write("Нет файла прошивки")
            return
            
        if 'ChipId' not in self.request.arguments:
            self.write("Не указан ChipId устройства")
            return

        # Получаем данные из запроса
        file_info = self.request.files['firmware'][0]
        chip_id = self.get_argument('ChipId')
        
        # Проверяем расширение файла
        filename = file_info['filename']
        if not filename.endswith('.bin'):
            self.write("Формат файла должен быть .bin")
            return

        try:
            # Создаем имя файла с chipid
            firmware_filename = f"firmware_{chip_id}.bin"
            firmware_path = os.path.join(firmware_filename)
            
            # Сохраняем файл
            with open(firmware_path, 'wb') as f:
                f.write(file_info['body'])
                
            self.write({
                'status': 'success',
                'message': 'Файл прошивки успешно загружен',
                'filename': firmware_filename,
                'chip_id': chip_id
            })

            chip_id = int(chip_id)
            Device = Controllers.WebSocketESP.FindDeviceByChipId(chip_id)

            if not Device: 
                print("Не нашел устройство")
                raise Exception("Устройство не найдено или не подключено")
            
            Request = {"TypeMesseage": "StartOTA"}
            # Отправляем запрос устройству
            Device['ws'].write_message(json.dumps(Request))
            
        except Exception as e:
            self.set_status(500)
            self.write({
                'status': 'error',
                'message': f'Ошибка при сохранении файла: {str(e)}'
            })

class FirmwareHandler(tornado.web.RequestHandler):
    async def get(self):
        if not os.path.exists(FIRMWARE_PATH):
            self.set_status(404)
            self.write("Прошивка не найдена")
            return
        
        self.set_header('Content-Type', 'application/octet-stream')
        with open(FIRMWARE_PATH, 'rb') as f:
            self.write(f.read())
