from machine import Pin
import time
import mini
import dht

switch = Pin(mini.D4, Pin.IN)  # 接DO 開關信號輸出

while True:
    print('潮濕＝0 ' + str(switch.value()))  # 潮濕輸出0 乾燥輸出1
    time.sleep(3)
