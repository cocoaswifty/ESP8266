"""
### 材料：
- ESP8266
- 溫濕度計
- 土壤濕度檢測
- 伺服馬達 sg90

### 需求：
- [ ] 如果土壤濕度低於ＸＸ且露點溫度低於ＸＸ 開
- [ ] 早上時間 4,5,6, 8,9,10, 12,13,14 偵測一次
- [ ] 如果土壤濕度高於ＸＸ或超過 5 分鐘 關
- [ ] 資料透過 MQTT 上傳至 Thingspeak

### 腳位：
D0, RST 接一個2kΩ 電阻，deep sleep 喚醒時 D0 會輸出訊號到 RST
A0 類比訊號腳位，土壤濕度檢測
D5 = const(14)  溫濕度
D6 = const(12)  土壤濕度檢測
D7 = const(13)  伺服馬達
"""
from umqtt.simple import MQTTClient
from machine import Pin, ADC
from servo import Servo
import urequests as req
import ubinascii
import machine
import math
import time
import dht
import network
import ntptime


def connectAP():
    wlan = network.WLAN(network.STA_IF)  # 設定成STA模式
    if not wlan.isconnected():
        wlan.active(True)  # 啟用無線網路
        wlan.connect('City free wifi', 'XXX')

    timeout = time.time() + 10   # 連線超過 10 秒 跳出
    while not wlan.isconnected():  # 等待，直到連線成功
        if time.time() > timeout:
            break
        pass

    # print('network config:', wlan.ifconfig())
    return wlan


def setUTC8Time(rtc):  # 校正時間
    if rtc.memory() == b'':
        wlan = connectAP()  # 連網
        try:
            t = ntptime.time() + 28800  # 加8小時
            tm = time.localtime(t)
            machine.RTC().datetime(
                tm[0:3] + (0, ) + tm[3:6] + (0, ))  # 轉成RTC格式
            rtc.memory(b'0')  # 存入0來代表已校正時間
        except Exception as e:
            print('Error!', e)

        wlan.disconnect  # 斷網
    # print('now:', time.localtime())


def get_dew_point_c(t_air_c, rel_humidity):  # 計算露點溫度
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return round((B * alpha) / (A - alpha), 1)


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
        # print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
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


def watering(soil, dew):
    if soil >= 700 and dew <= 22:   # 水分高於 700, 露點溫度小於22
        conds = [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]  # 白天才澆水
        tm_hour = time.localtime()[3]  # 時
        if tm_hour in conds:
            watering_time = 0   # 持續澆水時間
            publishIFTTT(watering_time)

            # print('土壤乾旱，啟動澆水...')
            sg90 = Servo(13)  # D7 伺服馬達
            sg90.rotate(180)    # 開水

            while watering_time <= 5*60:    # 如果澆水超過5分鐘
                time.sleep(10)
                watering_time += 10
                if soil >= 900:
                    sg90.rotate(0)      # 關水
                    break
            sg90.rotate(0)      # 關水

            time.sleep(5)
            data = 'field6={}'.format(watering_time)
            publishMqtt(data)
            publishIFTTT(watering_time)


if __name__ == '__main__':
    rtc = machine.RTC()  # GPIO16(D0),輸出低電位訊號，接一個1KΩ到RST腳位
    setUTC8Time(rtc)  # 校正時間
    # 觸發來源ALARM0, deep sleep模式
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

    tm_min = time.localtime()[4]
    if tm_min != 0:
        rtc.alarm(rtc.ALARM0, (60 - tm_min)*60*1000)    # 等待X秒到整點喚醒
    elif tm_min == 0:
        rtc.alarm(rtc.ALARM0, 60*60*1000)  # 1小時喚醒一次

    if machine.reset_cause() == machine.DEEPSLEEP_RESET and tm_min == 0:    # 導致重置因素
        dht11 = Pin(14, Pin.IN)  # D5 溫濕度傳感器
        d = dht.DHT11(dht11)
        d.measure()  # 開始測量

        temp = d.temperature()  # 溫度
        humi = d.humidity()   # 濕度
        dew = get_dew_point_c(temp, humi)  # 露點溫度
        adc = ADC(0)  # 類比輸入0腳位
        soil = 1024 - adc.read()  # 讀取 土壤濕度類比值 1024=乾旱, 越小越濕
        yl69 = Pin(12, Pin.IN)  # D6 土壤濕度感測器
        dry = yl69.value()    # 土壤乾旱 0=潮濕 1=乾旱

        # print('溫度：', str(temp))
        # print('濕度：', str(humi))
        # print('露點溫度：', str(dew))
        # print('土壤濕度類比值：', str(soil))
        # print('土壤乾旱 0=潮濕 1=乾旱：', str(dry))
        # print('現在時間：', time.localtime())
        # print('時：', time.localtime()[3])
        # print('分：', time.localtime()[4])

        data = 'field1={}&field2={}&field3={}&field4={}&field5={}'.format(
            temp, humi, dew, soil, dry)
        publishMqtt(data)
        watering(soil, dew)

    # print('Going to sleep...')
    machine.deepsleep()
