"""
### 材料：
- ESP8266
- 溫濕度計 DHT11
- 霧化器

### 需求：
- [ ] 30分鐘澆水一次
- [ ] 如果濕度低於ＸＸ 開
- [ ] 如果濕度高於ＸＸ或超過 5 分鐘 關
- [ ] 資料透過 MQTT 上傳至 Thingspeak

### 腳位：
D0, RST 接一個2kΩ 電阻，deep sleep 喚醒時 D0 會輸出訊號到 RST
D5 = const(14)  溫濕度
D6 = const(12)  霧化器
"""
from umqtt.simple import MQTTClient
from machine import Pin, ADC
import urequests as req
import ubinascii
import machine
import network
import ntptime
import time
import dht


def init():
    rtc = machine.RTC()
    if rtc.memory() == b'':
        setUTC8Time()  # 校正時間
        rtc.memory(b'0')  # 存入0來代表已校正時間


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
    wlan = connectAP()  # 連網
    try:
        t = ntptime.time() + 28800  # 加8小時
        tm = time.localtime(t)
        machine.RTC().datetime(
            tm[0:3] + (0, ) + tm[3:6] + (0, ))  # 轉成RTC格式

    except Exception as e:
        print('Error!', e)

    time.sleep(2)
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

    time.sleep(2)
    wlan.disconnect


def spray():
    sprayer = Pin(12, Pin.OUT)  # D7 霧化器
    sprayer.on()    # 開水
    time.sleep(60)  # 澆水1分鐘
    sprayer.off()      # 關水


def readDHT():
    d = dht.DHT11(Pin(14))  # D5 溫濕度傳感器
    d.measure()  # 開始測量
    humi = d.humidity()   # 濕度
    temp = d.temperature()  # 溫度
    time.sleep(1)   # 避免連續讀取
    return (humi, temp)


while True:
    init()
    tm_min = time.localtime()[4]
    if tm_min in [00, 10, 20, 30, 40, 50]:
        watering_time = 0   # 持續澆水時間
        (start_humi, start_temp) = readDHT()
        (end_humi, end_temp) = (start_humi, start_temp)
        while readDHT()[0] <= 94:   # 濕度低於 94
            spray()
            (end_humi, end_temp) = readDHT()
            watering_time += 1
            if watering_time > 5:   # 超過5分鐘，終止澆水
                break

        data = 'field1={}&field2={}&field3={}&field4={}&field5={}'.format(
            start_humi, end_humi, start_temp, end_temp, watering_time)
        publishMqtt(data)
    time.sleep(60)
