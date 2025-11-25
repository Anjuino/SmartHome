import tornado.web
import Controllers
import json
import asyncio
import DataBase
import hashlib
import time
import ParseIncomingMesseage

# Хранилище сессий (можно вынести в общий модуль если нужно)
user_sessions = {}

class HTTPHandlerClient(tornado.web.RequestHandler):
    async def post(self):
        # Проверяем доступ: либо сессия админа, либо валидный токен пользователя
        if not await self.check_access():
            self.set_status(401)
            self.write({"error": "Требуется авторизация"})
            return
        
        # Обрабатываем команду
        await self.handle_command()
    
    async def check_access(self):
        """Проверяет доступ: либо сессия админа, либо валидный токен пользователя"""
        # Проверяем сессию админа
        session_id = self.get_cookie("admin_session")
        if await self.check_admin_session(session_id):
            return True
        
        # Проверяем токен пользователя из JSON тела
        try:
            JsonData = json.loads(self.request.body)
            user_token = JsonData.get('Token')
            chip_id = JsonData.get('ChipId')
            
            # Если есть токен - проверяем его валидность
            if user_token and await DataBase.CheckToken(user_token):
                # Дополнительно проверяем, что устройство принадлежит этому токену
                if chip_id and await self.check_device_ownership(user_token, chip_id):
                    return True
        except:
            pass
        
        return False
    
    async def check_admin_session(self, session_id):
        """Проверяет сессию админа (такая же логика как в AdminBoard)"""
        if not session_id:
            return False
        
        # Импортируем admin_sessions из AdminBoard или делаем общее хранилище
        try:
            from AdminBoard import admin_sessions
            session = admin_sessions.get(session_id)
            if session and time.time() < session['expires']:
                return True
        except:
            pass
        
        return False
    
    async def check_device_ownership(self, user_token, chip_id):
        """Проверяет, что устройство принадлежит пользователю с данным токеном"""
        # Проверяем в списке подключенных устройств
        if user_token in Controllers.WebSocketESP.DeviceList:
            for device in Controllers.WebSocketESP.DeviceList[user_token]:
                if device['ChipId'] == chip_id:
                    return True
        
        # Если устройство не в онлайн списке, проверяем в базе данных
        return await DataBase.CheckDeviceOwnership(user_token, chip_id)
    
    async def handle_command(self):
        try:
            JsonData = json.loads(self.request.body)
            ChipId = JsonData['ChipId']
            TypeMesseage = JsonData['TypeMesseage']

            TypeResponse = None
            Request      = None

            ### общие команды
            if (TypeMesseage == "GetState"): 
                TypeResponse = "State"
                Request = {"TypeMesseage": TypeMesseage}

            if (TypeMesseage == "Reboot"):
                Request = {"TypeMesseage": TypeMesseage}

            ### команды для телеметрии
            '''if (TypeMesseage == "UpdateZoneName"):
                TypeResponse = "UpdateZoneName"
                Request = {
                    "TypeMesseage": TypeMesseage,
                    "NumZone": JsonData['NumZone'],
                    "OldName": JsonData['OldName'],
                    "NewName": JsonData['NewName']
                }'''

            ### команды для контроллеров лент
            if (TypeMesseage == "GetSettingLed"):
                TypeResponse = "LedSetting"
                Request = {
                    "TypeMesseage": TypeMesseage,
                }

            if (TypeMesseage == "UpdateSettingLed"):
                IsDetectedMove = JsonData.get('IsDetectedMove')
                if IsDetectedMove:
                    Request = {
                        "TypeMesseage": TypeMesseage,
                        "LedCount": JsonData['LedCount'],
                        "IsDetectedMove": JsonData['IsDetectedMove']
                    }
                else:
                    Request = {
                        "TypeMesseage": TypeMesseage,
                        "LedCount": JsonData['LedCount']
                    }    
                
            if (TypeMesseage == "SetStateToLed"):
                Request = {
                    "TypeMesseage": "SetState",
                    "Mode": JsonData['Mode'],
                    "ColorR": JsonData['ColorR'],
                    "ColorG": JsonData['ColorG'],
                    "ColorB": JsonData['ColorB'] 
                }

            if (TypeMesseage == "SetSpeedToLed"):
                Request = {
                    "TypeMesseage": "SetSpeed",
                    "Speed": JsonData['Speed']
                }

            if (TypeMesseage == "SetBrightnessToLed"):
                Request = {
                    "TypeMesseage": "SetBrightness",
                    "Brightness": JsonData['Brightness']
                }

            if (TypeMesseage == "GetDataFromDB"):
                sensor_type = JsonData['SensorType']
                hours_back = JsonData.get('HoursBack', 12)
                
                # Получаем данные из БД
                sensor_data = await DataBase.get_sensor_data_from_db(ChipId, sensor_type, hours_back)
                
                self.write({'status': 'success', 'response': sensor_data})
                return  

            # Находим нужное устройство с помощью общей функции
            Device = Controllers.WebSocketESP.FindDeviceByChipId(ChipId)
            
            if not Device: 
                raise Exception("Устройство не найдено или не подключено")
                    
            # Отправляем запрос устройству
            await Device['ws'].write_message(json.dumps(Request))
            
            # Если ждать ответ не надо, то отдадим в web ответ сразу
            if not TypeResponse: 
                self.write({'status': 'success'})
                return    
            
            # Ждем ответ   
            Response = await Device['ws'].WaitResponse(ChipId, TypeResponse)
                    
            self.write({'status': 'success', 'response': Response})  
            
        except asyncio.TimeoutError:
            self.set_status(408)
            self.write({'error': 'Timeout waiting for response'})
        except Exception as e:
            self.set_status(400)
            self.write({'error': str(e)})

class AuthHandler(tornado.web.RequestHandler):
    async def get(self):
        self.render("../static/html/app.html")
        
    async def post(self):
        try:
            data = json.loads(self.request.body)
            login = data.get('login')
            password = data.get('password')
            
            if not login or not password:
                self.set_status(400)
                self.write({"error": "Логин и пароль обязательны"})
                return
            
            # Проверяем пользователя и получаем токен
            token = await DataBase.CheckUser(login, password)
            if token:
                self.write({
                    "token": token, 
                    "status": "success",
                    "message": "Авторизация успешна"
                })
            else:
                self.set_status(401)
                self.write({"error": "Неверный логин или пароль"})
                
        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"error": "Неверный формат JSON"})
        except Exception as e:
            self.set_status(500)
            self.write({"error": f"Ошибка сервера: {str(e)}"})