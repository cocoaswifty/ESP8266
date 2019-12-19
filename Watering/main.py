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
import ubinascii
import machine
import math
import time
import dht


def get_dew_point_c(t_air_c, rel_humidity): # 計算露點溫度
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return round((B * alpha) / (A - alpha), 1)


def publishMqtt(data):
    config = {
        'broker': 'mqtt.thingspeak.com',
        'user': 'user',  # 使用者名稱
        'key': 'XX',  # MQTT key
        # 用戶識別名稱，使用控制板實體位址
        'id': 'room/' + ubinascii.hexlify(machine.unique_id()).decode(),
        'topic': b'channels/941717/publish/XX'  # Write API Key
    }

    client = MQTTClient(client_id=config['id'],
                        server=config['broker'],
                        user=config['user'],
                        password=config['key'])

    try:
        client.connect()
        client.publish(config['topic'], data.encode())
        time.sleep(2)
        client.disconnect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        client.disconnect()


dht11 = Pin(14, Pin.IN)  # D5 溫濕度傳感器
sg90 = Servo(13)  # D7 伺服馬達
yl69 = Pin(12, Pin.IN)  # D6 土壤濕度感測器
adc = ADC(0)  # 類比輸入0腳位
tm_hour = time.localtime()[3]
tm_min = time.localtime()[4]

rtc = machine.RTC()  # GPIO16(D0),輸出低電位訊號，接一個1KΩ到RST腳位
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  # 觸發來源ALARM0, deep sleep模式

if tm_min != 00:
    rtc.alarm(rtc.ALARM0, (60 - tm_min)*60*1000)    # 等待X秒到整點喚醒
else:
    rtc.alarm(rtc.ALARM0, 60*60*1000)  # 1小時喚醒一次


if machine.reset_cause() == machine.DEEPSLEEP_RESET:    # 導致重置因素
    d = dht.DHT11(dht11)
    d.measure()  # 開始測量

    temp = d.temperature()  # 溫度
    humi = d.humidity()   # 濕度
    dew = get_dew_point_c(temp, humi)  # 露點溫度
    soil = adc.read()  # 讀取 土壤濕度類比值 1024=乾旱, 越小越濕
    dry = yl69.value()    # 土壤乾旱 0=潮濕 1=乾旱

    print('溫度：', str(temp))
    print('濕度：', str(humi))
    print('露點溫度：', str(dew))
    print('土壤濕度類比值：', str(soil))
    print('土壤乾旱 0=潮濕 1=乾旱：', str(dry))
    print('現在時間：', time.localtime())
    print('時：', time.localtime()[3])
    print('分：', time.localtime()[4])

    data = 'field1={}&field2={}&field3={}&field4={}&field5={}'.format(
        temp, humi, dew, soil, dry)
    publishMqtt(data)

    if soil <= 700 and dew <= 22:
        conds = [4,5,6,7,8,9,10,11,12,13,14,15] # 白天才澆水
        if tm_hour in conds:
            print('土壤乾旱，啟動澆水...')
            sg90.rotate(180)
            time.sleep(5)
            sg90.rotate(0)

print('Going to sleep...')
machine.deepsleep()
