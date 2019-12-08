import time
import mini
from machine import Pin

led = Pin(mini.D4, Pin.OUT)
switch = Pin(mini.D7, Pin.IN, Pin.PULL_UP)  # 啟用上拉電阻

while True:
    if switch.value() == 0:  # 讀取開關值
        time.sleep_ms(20)
        if switch.value() == 0:
            led.value(not led.value())  # 設定燈光，反相
            while switch.value() == 0:
                pass                    #等待中，什麼都不做