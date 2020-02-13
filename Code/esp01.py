from machine import Pin, PWM, ADC
import time

p2 = Pin(2, Pin.OUT)

while True:
    p2.off()
    time.sleep(5)
    p2.on()
    time.sleep(5)
