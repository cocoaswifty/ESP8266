from machine import Pin
import time
p2 = Pin(2, Pin.OUT)

for i in range(3):
    p2.off()
    time.sleep(0.5)
    p2.on()
    time.sleep(0.5)
