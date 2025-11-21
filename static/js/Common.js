function goBackToMain() { router.navigate('devices'); }
function goBackToList() { router.navigate('deviceList'); }
function showDeviceSettings() { router.navigate('deviceSettings'); }
function goBackToControl() { router.navigate('deviceControl'); }

async function loadDeviceTypes() {
    if (isLoadingDevices) return allDevices;

    const currentToken = localStorage.getItem('userToken');
    if (!currentToken) {
        router.navigate('login');
        return;
    }

    isLoadingDevices = true;
    
    try {
        const response = await fetch('./Admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                TypeMesseage: "GetListDevice",
                Token: currentToken
            })
        });

        allDevices = await response.json();
        groupDevicesByType();
        
        lastDevicesLoadTime = Date.now();
        localStorage.setItem('allDevices', JSON.stringify(allDevices));
        localStorage.setItem('deviceTypes', JSON.stringify(deviceTypes));
        localStorage.setItem('lastDevicesLoadTime', lastDevicesLoadTime.toString());
        
        displayDeviceTypes();
        return allDevices;
    } catch (error) {
        console.error('Ошибка загрузки устройств:', error);
        restoreFromLocalStorage();
        return null;
    } finally {
        isLoadingDevices = false;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    restoreFromLocalStorage();
    
    window.addEventListener('hashchange', () => {
        router.route();
    });

    router.route();
});

function logout() {
    localStorage.removeItem('userToken');
    localStorage.removeItem('allDevices');
    localStorage.removeItem('deviceTypes');
    localStorage.removeItem('currentDeviceType');
    localStorage.removeItem('lastDevicesLoadTime');
    userToken = null;
    allDevices = [];
    deviceTypes = {};
    lastDevicesLoadTime = 0;
    window.location.href = window.location.pathname;
}

function restoreFromLocalStorage() {
    try {
        const savedAllDevices = localStorage.getItem('allDevices');
        const savedDeviceTypes = localStorage.getItem('deviceTypes');
        const savedLoadTime = localStorage.getItem('lastDevicesLoadTime');
        
        if (savedAllDevices) allDevices = JSON.parse(savedAllDevices);
        if (savedDeviceTypes) deviceTypes = JSON.parse(savedDeviceTypes);
        if (savedLoadTime) lastDevicesLoadTime = parseInt(savedLoadTime);
        
        if (allDevices.length > 0) displayDeviceTypes();
    } catch (error) {
        console.error('Ошибка восстановления из localStorage:', error);
    }
}

window.addEventListener('storage', function(e) {
    if (e.key === 'userToken') {
        userToken = e.newValue;
        if (userToken) {
            window.location.reload();
        }
    }
});

document.getElementById('authForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const login = document.getElementById('login').value;
    const password = document.getElementById('password').value;

    try {
        const response = await fetch('./Auth', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ login, password })
        });

        const data = await response.json();

        if (response.ok) {
            userToken = data.token;
            localStorage.setItem('userToken', userToken);
            
            allDevices = [];
            deviceTypes = {};
            lastDevicesLoadTime = 0;
            
            router.navigate('devices');
        }
    } catch (error) {
        console.error('Ошибка авторизации:', error);
    }
});

function initializeApp() {
    userToken = localStorage.getItem('userToken');
    currentDeviceType = localStorage.getItem('currentDeviceType') || '';
    
    if (userToken) {
        document.getElementById('devicesSection').style.display = 'block';
        document.getElementById('appNav').style.display = 'block';
        if (window.location.hash === '' || window.location.hash === '#login') {
            window.location.hash = 'devices';
        }
    } 
    else document.getElementById('authSection').style.display = 'block';

}

if (typeof chrome !== 'undefined' && chrome.runtime) {
    const originalSendMessage = chrome.runtime.sendMessage;
    chrome.runtime.sendMessage = function(message, callback) {
        if (callback) {
            try {
                return originalSendMessage(message, callback);
            } catch (e) {
                if (!e.message.includes('port closed')) {
                    throw e;
                }
            }
        }
        return originalSendMessage(message);
    };
}

