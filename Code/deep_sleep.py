# -*- coding: utf-8 -*-

import machine
import time

rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)  # 觸發來源ALARM0, deep sleep模式
rtc.alarm(rtc.ALARM0, 10000)  # 鬧鈴 10秒後觸發

if machine.reset_cause() == machine.DEEPSLEEP_RESET:  # 導致重置因素
    print('woke from a deep sleep')
else:
    print('power on or hard reset')

for i in range(5):  # 倒數5秒
    print('Going sleep in {} sec.'.format(5-i))
    time.sleep(1)

machine.deepsleep()  # 進入 deep sleep模式
