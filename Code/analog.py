from machine import Pin, PWM, ADC
import time

adc = ADC(0)  # 類比輸入0腳位
ledPin = Pin(2, Pin.OUT)  # LED 腳位
LED = PWM(ledPin, 1000)  # 指定 PWM 頻率

while True:
    val = adc.read()  # 讀取
    LED.duty(val)  # 改變亮度，工作週期占比
    print('POT:', str(val))
    time.sleep(0.5)
