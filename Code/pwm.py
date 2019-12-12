from machine import Pin, PWM, Timer
import mini


led = Pin(mini.D4, Pin.OUT)
pwm = PWM(led, 1000)  # 指定頻率為1000
# pwm.freq(10)  # 調低工作頻率(1~1000)，越低LED越閃爍
# pwm.duty(900)  # 提高工作週期佔比(0~1023)，越低LED越亮
# pwm

step = 32  # 亮度階段值
_duty = 0  # pwm工作週期值
ms = round(1500 / step)  # 1.5秒內的定時觸發尖閣時間，四捨五入


def breath(t):  # 呼吸燈
    global _duty, step
    _duty += step  # 改變工作週期

    if _duty > 1000:
        _duty = 1000
        step *= -1  # 反轉亮度

    if _duty < 0:
        _duty = 0
        step *= -1  # 反轉亮度

    pwm.duty(_duty)  # 調整工作週期佔比(0~1023)，越低LED越亮


tim = Timer(-1)  # ESP8266 計時器編號為-1
tim.init(period=ms, mode=Timer.PERIODIC, callback=breath)

try:
    while True:
        pass
except:
    tim.deinit()
    pwm.deinit()    # 關閉PWM功能
    led.value(0)
    print('stopped!')
