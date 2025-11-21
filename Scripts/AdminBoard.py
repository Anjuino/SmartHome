import tornado.web
import json
import ParseIncomingMesseage
import Controllers
import DataBase
import hashlib
import time

admin_sessions = {} # Хранилище сессий админов

class AdminHandler(tornado.web.RequestHandler):
    async def get(self):
        session_id = self.get_cookie("admin_session")
        if not await self.check_admin_session(session_id):
            self.render("../static/html/AdminLogin.html")  # Показываем страницу логина
            return
        
        self.render("../static/html/AdminPanel.html")

    async def post(self):
        # Если это запрос на авторизацию
        if self.get_argument('action', default=None) == 'login':
            await self.handle_login()
            return
        
        # Для API запросов проверяем либо сессию админа, либо токен пользователя
        if not await self.check_access():
            self.set_status(401)
            self.write({"error": "Требуется авторизация"})
            return
        
        await self.handle_admin_post()          # Обрабатываем запрос
    
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
            if user_token and await DataBase.CheckToken(user_token):
                return True
        except:
            pass
        
        return False
    
    async def check_admin_session(self, session_id):
        if not session_id or session_id not in admin_sessions:
            return False
        
        session = admin_sessions.get(session_id)
        if session and time.time() < session['expires']:
            return True
        else:
            # Удаляем просроченную сессию
            if session_id in admin_sessions:
                del admin_sessions[session_id]
            return False
    
    async def handle_login(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        
        if await self.verify_admin_credentials(username, password):
            # Создаем сессию
            session_id = hashlib.sha256(f"{username}{time.time()}".encode()).hexdigest()
            admin_sessions[session_id] = {
                'username': username,
                'created': time.time(),
                'expires': time.time() + 3600  # 1 час
            }
            
            self.set_cookie("admin_session", session_id, expires=time.time() + 3600)
            self.write({"status": "success", "redirect": "/Admin"})
        else:
            self.set_status(401)
            self.write({"error": "Неверные учетные данные"})
    
    async def verify_admin_credentials(self, username, password):
        # Простая проверка (можно добавить проверку из базы)
        if username == "admin" and password == "admin":
            return True
        return False
    
    async def handle_admin_post(self):
        JsonData = json.loads(self.request.body)
        TypeMesseage = JsonData['TypeMesseage']

        if (TypeMesseage == "GetListDevice"): 
            Token = JsonData.get('Token')
            
            # Если токен пустой или None - отдаем весь список всех устройств (только для админов)
            if not Token:
                # Проверяем что это админ (по сессии)
                session_id = self.get_cookie("admin_session")
                if await self.check_admin_session(session_id):
                    ListDevice = []
                    for token_clients in Controllers.WebSocketESP.DeviceList.values():
                        for client in token_clients:
                            ListDevice.append({
                                "ChipId": client["ChipId"], 
                                "TypeDevice": client["TypeDevice"], 
                                "DeviceName": client["DeviceName"]
                            })
                else:
                    self.set_status(403)
                    self.write({"error": "Доступ запрещен"})
                    return
            # Иначе ищем устройства по конкретному токену (для пользователей)
            elif Token in Controllers.WebSocketESP.DeviceList:
                ListDevice = [
                    {
                        "ChipId": client["ChipId"], 
                        "TypeDevice": client["TypeDevice"], 
                        "DeviceName": client["DeviceName"]
                    } for client in Controllers.WebSocketESP.DeviceList[Token]
                ]
            else: 
                ListDevice = []  # Если нет устройств для этого токена
                
            self.write(json.dumps(ListDevice))

        if (TypeMesseage == "GetIpDevice"):
            ChipId = JsonData.get('ChipId')
            
            Device = Controllers.WebSocketESP.FindDeviceByChipId(ChipId)
            
            if Device:
                ws_object = Device['ws']
                ip_address = ws_object.request.remote_ip
                response = { 'IP': ip_address}
            else: 
                response = { 'IP': None, 'status': 'device_not_found' }
            
            self.write(json.dumps(response))

        if (TypeMesseage == "GetProgress"):
            ChipId = JsonData.get('ChipId') 
            status = ParseIncomingMesseage.progress_status.get(int(ChipId), {"progress": 0, "status": "not_started"})
            self.write(status)

        if (TypeMesseage == "UpdateNameController"):
            ChipId = JsonData.get('ChipId')
            DeviceName = JsonData.get('NewName')
            await DataBase.UpdateControllerName(ChipId, DeviceName)

            Device = Controllers.WebSocketESP.FindDeviceByChipId(ChipId)
            if Device:
                Device['DeviceName'] = DeviceName

            self.write({"status": "success"})

        if (TypeMesseage == "UpdateToken"):
            pass