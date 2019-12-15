from machine import Pin

led = Pin(2, Pin.OUT, value=1)  # 預設輸出高電位
sw = Pin(0, Pin.IN, Pin.PULL_UP)  # 開關接腳，啟用上拉電阻


def callback(p):
    global led
    led.value(not led.value())  # 切換led狀態


sw.irq(trigger=Pin.IRQ_RISING, handler=callback)  # IRQ中斷模式，低點位到高電位時觸發
# sw.irq(trigger=Pin.IRQ_FALLING, handler=callback)  # IRQ中斷模式，高點位到低電位時觸發
# sw.irq(trigger=Pin.IRQ_LOW_LEVEL, handler=callback)  # IRQ中斷模式，在低電位時持續觸發
# sw.irq(trigger=Pin.IRQ_HIGH_LEVEL, handler=callback)  # IRQ中斷模式，在高電位時持續觸發
