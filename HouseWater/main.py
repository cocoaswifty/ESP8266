"""
### 材料：
- ESP8266
- 12V 電源
- 繼電器

### 需求：
- [ ] 定時開關
- [ ] 可網路控制開關時間
- [ ] 資料透過 MQTT 上傳至 Thingspeak

### 腳位：
D7 = const(13)  繼電器開關

10分鐘跑一次
設定ＯＯＯ = Write Key
https://api.thingspeak.com/update?api_key=ＯＯＯ&field1=3&field2=[3,6,9]&field3=180

field1:  手動開關
1 開水
0 關水
3 一般關閉狀態

field2:  幾點澆水
[3,6,9]

field3:  持續時間(秒)
180
"""

from umqtt.simple import MQTTClient
from machine import Pin, ADC
import urequests as req
import ubinascii
import machine
import network
import ntptime
import ujson
import time
import dht


def connectAP():
    wlan = network.WLAN(network.STA_IF)  # 設定成STA模式
    if not wlan.isconnected():
        wlan.active(True)  # 啟用無線網路
        wlan.connect('ＯＯＯ', 'ＯＯＯ')

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

    except Exception as e:
        print('Error!', e)

    time.sleep(2)
    wlan.disconnect  # 斷網


def publishMqtt(data):
    config = {
        'broker': 'mqtt.thingspeak.com',
        'user': 'user',  # 使用者名稱
        'key': 'ＯＯＯ',  # MQTT key
        # 用戶識別名稱，使用控制板實體位址
        'id': 'room/' + ubinascii.hexlify(machine.unique_id()).decode(),
        'topic': b'channels/938945/publish/ＯＯＯ'  # Write API Key
    }

    client = MQTTClient(client_id=config['id'],
                        server=config['broker'],
                        user=config['user'],
                        password=config['key'])

    wlan = connectAP()  # 連網

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


def watering(timer, duration):
    sprayer = Pin(13, Pin.OUT)  # D7 繼電器開關
    sprayer.on()    # 開水
    time.sleep(int(duration))  # 澆水1分鐘
    sprayer.off()      # 關水
    tm_hour = time.localtime()[3]
    data = 'field1={}&field2={}&field3={}&field4={}'.format(
        3, timer, duration, tm_hour)
    publishMqtt(data)


def setingCallback(topic, msg):
    obj = ujson.loads(msg)  # json轉dic
    # print(topic, msg)
    # print('----------------------')
    # print('switch:',  obj['field1'])
    # print('timer:', obj['field2'])
    # print('duration:', obj['field3'])
    if obj['field1'] == '1':    # open
        watering(obj['field2'], obj['field3'])
    if obj['field1'] == '0':    # close
        sprayer = Pin(13, Pin.OUT)  # D7 繼電器開關
        sprayer.off()      # 關水

    timer = ujson.loads(obj['field2'])

    tm_hour = time.localtime()[3]   # 時
    tm_min = time.localtime()[4]    # 分
    if tm_min <= 10:
        if tm_hour in timer:
            watering(obj['field2'], obj['field3'])


def subscribeMQTT():
    config = {
        'broker': 'mqtt.thingspeak.com',
        'user': 'cubie',    # 使用者名稱
        'key': 'ＯＯＯ',  # MQTT key
        # 用戶識別名稱，使用控制板實體位址
        'id': 'iot/'+ubinascii.hexlify(machine.unique_id()).decode(),
        'topic': b'channels/938945/subscribe/json/ＯＯＯ'  # Read API Key
    }

    client = MQTTClient(client_id=config['id'],
                        server=config['broker'],
                        user=config['user'],
                        password=config['key'])
    client.set_callback(setingCallback)

    wlan = connectAP()  # 連網
    try:
        client.connect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        client.disconnect()
    client.subscribe(config['topic'])  # 訂閱主題

    try:
        client.wait_msg()   # 查看訊息
    except:
        client.disconnect()
    wlan.disconnect


setUTC8Time()  # 校正時間
while True:
    subscribeMQTT()
    time.sleep(10*60)
