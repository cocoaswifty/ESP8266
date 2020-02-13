"""
### 材料：
- ESP8266
- 土壤濕度檢測

### 需求：
- [ ] 如果土壤濕度低於ＸＸ 開
- [ ] 如果土壤濕度高於ＸＸ或超過 5 分鐘 關
- [ ] 資料透過 MQTT 上傳至 Thingspeak

### 腳位：
D0, RST 接一個2kΩ 電阻，deep sleep 喚醒時 D0 會輸出訊號到 RST
A0 類比訊號腳位，土壤濕度檢測
D6 = const(12)  土壤濕度檢測
D7 = const(13)  霧化器
"""
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import urequests as req
import ubinascii
import machine
import network
import ntptime
import time


def init():
    rtc = machine.RTC()  # GPIO16(D0),輸出低電位訊號，接一個1KΩ到RST腳位
    # 觸發來源ALARM0, deep sleep模式
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    if rtc.memory() == b'':
        setUTC8Time()  # 校正時間
        rtc.memory(b'0')  # 存入0來代表已校正時間

    tm_min = time.localtime()[4]
    tm_sec = time.localtime()[5]
    # print('time.localtime():', time.localtime())

    rtc.alarm(rtc.ALARM0, ((60-tm_min)*60-tm_sec)*1000)    # 等待X秒到整點喚醒
    # rtc.alarm(rtc.ALARM0, (10*60*1000))    # 等待X秒到整點喚醒


def connectAP():
    wlan = network.WLAN(network.STA_IF)  # 設定成STA模式
    if not wlan.isconnected():
        wlan.active(True)  # 啟用無線網路
        wlan.connect('XXX', 'XXX')

    timeout = time.time() + 10   # 連線超過 10 秒 跳出
    while not wlan.isconnected():  # 等待，直到連線成功
        if time.time() > timeout:
            break
        pass

    # print('network config:', wlan.ifconfig())
    return wlan


def setUTC8Time():  # 校正時間
    time.sleep(2)
    wlan = connectAP()  # 連網
    try:
        t = ntptime.time() + 28800  # 加8小時
        tm = time.localtime(t)
        machine.RTC().datetime(
            tm[0:3] + (0, ) + tm[3:6] + (0, ))  # 轉成RTC格式

        # print('now:', time.localtime())
    except Exception as e:
        print('Error!', e)

    wlan.disconnect  # 斷網


def publishMqtt(data):
    config = {
        'broker': 'mqtt.thingspeak.com',
        'user': 'user',  # 使用者名稱
        'key': 'XXX',  # MQTT key
        # 用戶識別名稱，使用控制板實體位址
        'id': 'room/' + ubinascii.hexlify(machine.unique_id()).decode(),
        'topic': b'channels/941717/publish/XXX'  # Write API Key
    }

    client = MQTTClient(client_id=config['id'],
                        server=config['broker'],
                        user=config['user'],
                        password=config['key'])

    wlan = connectAP()

    try:
        client.connect()
        client.publish(config['topic'], data.encode())
        time.sleep(2)
        client.disconnect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        client.disconnect()

    wlan.disconnect


def publishIFTTT(watering_time):
    wlan = connectAP()
    apiURL = ('https://maker.ifttt.com/trigger/watering/with/key/XXX?value1={}').format(
        watering_time
    )
    try:
        req.get(apiURL)
    except Exception as e:
        print('Error!', e)

    wlan.disconnect


def spray():
    sprayer = Pin(13, Pin.OUT)  # D7 伺服馬達
    sprayer.on()    # 開水
    time.sleep(60)  # 澆水1分鐘
    sprayer.off()      # 關水


def getSoil():
    adc = ADC(0)  # 類比輸入0腳位
    soil = 1024 - adc.read()  # 讀取 土壤濕度類比值 1024=乾旱, 越小越濕
    # yl69 = Pin(12, Pin.IN)  # D6 土壤濕度感測器
    # dry = yl69.value()    # 土壤乾旱 0=潮濕 1=乾旱

    # print('土壤濕度類比值：', str(soil))
    # print('土壤乾旱 0=潮濕 1=乾旱：', str(dry))

    return soil


init()
if machine.reset_cause() == machine.DEEPSLEEP_RESET:    # 導致重置因素
    soil = getSoil()
    watering_time = 0   # 持續澆水時間

    while getSoil() <= 300:   # 水分低於 300
        spray()
        watering_time += 1

    if watering_time != 0:
        publishIFTTT(watering_time)

    data = 'field1={}&field2={}'.format(soil, watering_time)
    publishMqtt(data)

# print('Going to sleep...')
machine.deepsleep()
