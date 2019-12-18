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

from machine import Pin, PWM, ADC
import time
import mini
from umqtt.simple import MQTTClient
import dht
import machine
import network
import ubinascii
from servo import Servo


class Target(Servo):
    def rand(self):
        r = random.randint(0, 180)  # 0~180的隨機數
        print('Turn to ' + str(r))
        self.rotate(r)


def get_dew_point_c(t_air_c, rel_humidity):
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return round((B * alpha) / (A - alpha), 1)


dht11 = Pin(mini.D5, Pin.IN)  # 溫濕度傳感器
sg90 = Target(mini.D6)  # 伺服馬達
yl69 = Pin(mini.D7, Pin.IN)  # 土壤濕度感測器
adc = ADC(0)  # 類比輸入0腳位
# led = Pin(mini.D4, Pin.OUT)  # LED 腳位

# LED = PWM(led, 1000)  # 指定 PWM 頻率


rtc = machine.RTC()  # GPIO16(D0),輸出低電位訊號，接一個1KΩ到RST腳位
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  # 觸發來源ALARM0, deep sleep模式
rtc.alarm(rtc.ALARM0, 20000)  # 20秒喚醒一次

sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

if sta_if.isconnected():  # 確認網路是否連線
    print('WiFi connected!')
else:
    sta_if.connect('WiFi網路ID', 'WiFi密碼')
    print(sta_if.ifconfig())

config = {
    'broker': 'mqtt.thingspeak.com',
    'user': 'cubie',
    'key': 'ＯＯＯ',
    'id': 'room/' + ubinascii.hexlify(machine.unique_id()).decode(),
    'topic': b'channels/352801/publish/ＸＸＸ'
}

client = MQTTClient(client_id=config['id'],
                    server=config['broker'],
                    user=config['user'],
                    password=config['key'])


if machine.reset_cause() == machine.DEEPSLEEP_RESET:    # 導致重置因素
    d = dht.DHT11(dht11)
    d.measure()  # 開始測量
    val = adc.read()  # 讀取

    print('溫度：', str(d.temperature()))
    print('濕度：', str(d.humidity()))
    print('露點溫度：', str(get_dew_point_c(d.temperature(), d.humidity())))
    print('土壤濕度類比：', str(val))
    print('土壤濕度 0=潮濕 1=乾旱：', str(yl69.value()))

    data = 'field1={}&field2={}&field3={}&field4={}&field5={}'.format(
        d.temperature(),    # 溫度
        d.humidity(),   # 濕度
        get_dew_point_c(temp, hum),  # 露點溫度
        val,    # 土壤濕度類比
        yl69.value()    # 土壤濕度 0=潮濕 1=乾旱
    )

    client.connect()
    client.publish(config['topic'], data.encode())
    time.sleep(2)
    client.disconnect()

    if yl69.value() == 1:
        sg90.rotate(180)
        time.sleep(5)
        sg90.rotate(0)

print('Going to sleep...')
machine.deepsleep()
