// Заглушки для функций настроек (ты их потом реализуешь)
function loadDeviceSettings() {
    console.log('Загрузка настроек для устройства:', selectedDevice);
}

function saveDeviceSettings() {
    console.log('Сохранение настроек для устройства:', selectedDevice);
}

// Отсортировать устройства по типу
function groupDevicesByType() {
    deviceTypes = {};
    allDevices.forEach(device => {
        const type = device.TypeDevice || 'Other';
        if (!deviceTypes[type]) deviceTypes[type] = [];
        deviceTypes[type].push(device);
    });
}

// Вывести виды устройств
function displayDeviceTypes() {
    const typesGrid = document.getElementById('deviceTypesGrid');
    if (Object.keys(deviceTypes).length === 0) {
        typesGrid.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">Устройства не найдены</div>';
        return;
    }

    let html = '';
    for (const [type, devices] of Object.entries(deviceTypes)) {
        const typeName = getTypeDisplayName(type);
        html += `<div class="device-card device-type" onclick="showDeviceList('${type}')">
                    <div class="device-name">${typeName}</div>
                    </div>`;
    }
    typesGrid.innerHTML = html;
}

// Загрузить список устройств 
function showDeviceList(type) {
    currentDeviceType = type;
    localStorage.setItem('currentDeviceType', type);
    router.navigate('deviceList');
}

// Получить устройства по опреденному типу
function loadDevicesByType(type) {
    const devicesList = document.getElementById('devicesList');
    const loadingDiv = document.getElementById('devicesLoading');
    
    devicesList.innerHTML = '';
    loadingDiv.classList.remove('hidden');

    const devices = deviceTypes[type] || [];
    if (devices.length === 0) {
        devicesList.innerHTML = '<div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #666;">Устройства не найдены</div>';
        loadingDiv.classList.add('hidden');
        return;
    }

    devicesList.innerHTML = devices.map(device => `
        <div class="device-card device-type-${type.toLowerCase()}" 
            onclick="selectDevice(${device.ChipId}, '${device.DeviceName}', '${device.TypeDevice}')">
            <div class="device-name">${device.DeviceName || 'Без имени'}</div>
        </div>
    `).join('');
    loadingDiv.classList.add('hidden');
}

// Получить тип устройства
function getTypeDisplayName(type) {
    const typeNames = {
        'Telemetry': 'Датчики',
        'LedController': 'Освещение',
        'Other': 'Другие устройства'
    };
    return typeNames[type] || type;
}

// Отрисовать интерфейс для определнного типа устройств
function prepareDeviceControlUI(deviceType) {
    const controlPanel = document.querySelector('.control-panel');
    let skeletonHTML = '';
    
    switch(deviceType) {
        case 'Telemetry':
            skeletonHTML = `
                <div class="telemetry-cards">
                    <div class="data-card temperature">
                        <h3>🌡️ Температура</h3>
                        <div class="data-value">--.-- °C</div>
                    </div>
                    <div class="data-card humidity">
                        <h3>💧 Влажность</h3>
                        <div class="data-value">--.-- %</div>
                    </div>
                    <div class="data-card co2">
                        <h3>CO2</h3>
                        <div class="data-value">--- ppm</div>
                    </div>
                </div>
            `;
            break;

        case 'LedController':
            skeletonHTML = `
                <div class="control-group">
                    <div class="control-row">
                        <div class="control-item">
                            <label for="brightness-control" class="control-label"> <span class="icon">💡</span> Яркость </label>
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <input type="range" id="brightness-control" class="control-slider" min="0" max="100" value="50" onchange="sendLedCommand('SetBrightnessToLed')">
                            </div>
                        </div>
                        
                        <div class="control-item">
                            <label for="speed-control" class="control-label"> <span class="icon">⚡</span> Скорость </label>
                            <div style="display: flex; align-items: center; gap: 15px;">
                                <input type="range" id="speed-control" class="control-slider" min="1" max="20" step="1" value="10" onchange="sendLedCommand('SetSpeedToLed')">
                            </div>
                        </div>
                    </div>
                    
                    <div class="control-row">
                        <div class="control-item">
                            <label class="control-label"> <span class="icon">🎨</span> Цвет </label>
                            <div class="color-picker-container">
                                <input type="color" id="color-control" class="control-color" value="#ffffff" onchange="sendLedCommand('SetStateToLed')">
                            </div>
                        </div>
                        
                        <div class="control-item">
                            <label for="mode-control" class="control-label"> <span class="icon">✨</span> Режим </label>
                            <select id="mode-control" class="control-select" onchange="sendLedCommand('SetStateToLed')">
                                <option value="1">Радуга</option>
                                <option value="2">Бегущий огонь</option>
                                <option value="3">Бегущие огни</option>
                                <option value="4">Одиночные огни (случайные)</option>
                                <option value="5">Вспышки</option>
                                <option value="6">Смена цветов</option>
                                <option value="7">Бегущий огонь 2</option>
                                <option value="8">Хаос</option>
                                <option value="9">2 бегущих огня</option>
                                <option value="249">Статичный цвет</option>
                                <option value="250">Выключить</option>
                            </select>
                        </div>
                    </div>
                </div>
            `;
            break;

        default:
            skeletonHTML = '<div>Загрузка управления...</div>';
    }
    controlPanel.innerHTML = skeletonHTML;
}

// Обработчик для нажатия на выбранное устройство
// Функция подготовит интерфейс и сделает первый запрос на получение состояния
function selectDevice(chipId, deviceName, deviceType) {
    selectedDevice = chipId;
    currentDeviceType = deviceType;
    localStorage.setItem('currentDeviceType', deviceType);
    prepareDeviceControlUI(deviceType);
    router.navigate('deviceControl');
}

// Запросы на контроллер освещения
async function sendLedCommand(TypeCommand) {
    if (!selectedDevice) return;
    
    const currentToken = localStorage.getItem('userToken');
    if (!currentToken) {
        router.navigate('login');
        return;
    }

    try {
        let requestData = {
            ChipId: selectedDevice,
            Token: currentToken,
            TypeMesseage: TypeCommand
        };

        // Добавляем параметры в зависимости от типа команды
        if (TypeCommand === "SetStateToLed") {
            const mode = document.getElementById('mode-control').value;
            const colorHex = document.getElementById('color-control').value;
            
            // Конвертируем hex в RGB
            const hexToRgb = (hex) => {
                const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                return result ? {
                    r: parseInt(result[1], 16),
                    g: parseInt(result[2], 16),
                    b: parseInt(result[3], 16)
                } : null;
            };
            
            const rgb = hexToRgb(colorHex);
            
            requestData.Mode = parseInt(mode);
            requestData.ColorR = rgb.r;
            requestData.ColorG = rgb.g;
            requestData.ColorB = rgb.b;
            
        } else if (TypeCommand === "SetBrightnessToLed") {
            const brightness = document.getElementById('brightness-control').value;
            requestData.Brightness = parseInt(brightness);
            
        } else if (TypeCommand === "SetSpeedToLed") {
            const speed = document.getElementById('speed-control').value;
            requestData.Speed = parseInt(speed);
        }

        const response = await fetch('./Device/SendMesseage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });

        const data = await response.json();
        if (response.ok) {
            console.log('Команда отправлена успешно:', TypeCommand);
        } else {
            console.error('Ошибка отправки команды:', data);
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
    }
}

// Функция запроса к беку на получение состояния устройства
async function GetState(TypeDevice) {
    if (!selectedDevice) return;
    const currentToken = localStorage.getItem('userToken');
    if (!currentToken) {
        router.navigate('login');
        return;
    }

    try {
        const response = await fetch('./Device/SendMesseage', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                ChipId:       selectedDevice,
                TypeMesseage: "GetState",
                Token:        currentToken
            })
        });

        const data = await response.json();
        if (response.ok && data.response) {
            ShowStateData(TypeDevice, data.response);
        }
    } catch (error) {
        console.error('Ошибка сети:', error);
    }
}

// Вывести данные по типу устройства
function ShowStateData(TypeDevice, Data) {
    const controlPanel = document.querySelector('.control-panel');
    const data = Data.Data && Data.Data[0] ? Data.Data[0] : Data;

    let HTML = '';
    if (TypeDevice === 'Telemetry') {

        if (data.Temperature !== undefined) HTML += `<div class="data-card temperature"><h3>🌡️ Температура</h3><div class="data-value">${data.Temperature.toFixed(2)} °C</div></div>`;
        if (data.Humidity !== undefined)    HTML += `<div class="data-card humidity"><h3>💧 Влажность</h3><div class="data-value">${data.Humidity.toFixed(2)} %</div></div>`;
        if (data.CO2ppm !== undefined)      HTML += `<div class="data-card co2"><h3>CO2</h3><div class="data-value">${data.CO2ppm} ppm</div></div>`;
        else                                HTML += `<div class="data-card co2"><h3>CO2</h3><div class="data-value">Нет датчика</div></div>`;

        if (!HTML) telemetryHTML = '<div class="no-data">Нет данных для отображения</div>';
        
        controlPanel.innerHTML = `<div class="telemetry-cards">${HTML}</div>`;
    }

    if (TypeDevice === 'LedController') {
        if (data.Brightness !== undefined) {
            document.getElementById('brightness-control').value = data.Brightness;
        }
        
        if (data.Speed !== undefined) {
            document.getElementById('speed-control').value = data.Speed;
        }
        
        if (data.ColorR !== undefined && data.ColorG !== undefined && data.ColorB !== undefined) {
            const rgbToHex = (r, g, b) => '#' + [r, g, b].map(x => {
                const hex = x.toString(16);
                return hex.length === 1 ? '0' + hex : hex;
            }).join('');
            
            const hexColor = rgbToHex(data.ColorR, data.ColorG, data.ColorB);
            document.getElementById('color-control').value = hexColor;
        }
        
        if (data.Mode !== undefined) {
            const modeSelect = document.getElementById('mode-control');
            
            if (data.Mode === 0) {
                const offOption = modeSelect.querySelector('option[value="250"]');
                if (offOption) {
                    offOption.textContent = 'Выключено';
                }
            } 
            // Если любой другой режим - меняем обратно на "Выключить"
            else {
                const offOption = modeSelect.querySelector('option[value="250"]');
                if (offOption) {
                    offOption.textContent = 'Выключить';
                }
            }
            
            // Устанавливаем значение в селекте
            modeSelect.value = data.Mode === 0 ? 250 : data.Mode;
            
            // Обновляем статус
            const modeNames = {
                0: 'Выключено',
                1: 'Радуга',
                2: 'Бегущий огонь', 
                3: 'Бегущие огни',
                4: 'Одиночные огни (случайные)',
                5: 'Вспышки',
                6: 'Смена цветов',
                7: 'Бегущий огонь 2',
                8: 'Хаос',
                9: '2 бегущих огня',
                249: 'Статичный цвет',
                250: data.Mode === 0 ? 'Выключено' : 'Выключить'
            };
            
        }
    }
}