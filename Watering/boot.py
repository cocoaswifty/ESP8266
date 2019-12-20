import gc
import esp
import network
import ntptime
import machine
import time


def connectAP(ssid, pwd):
    wlan = network.WLAN(network.STA_IF)  # 設定成STA模式
    if not wlan.isconnected():
        wlan.active(True)  # 啟用無線網路
        wlan.connect(ssid, pwd)

    while not wlan.isconnected():  # 等待，直到連線成功
        pass

    print('network config:', wlan.ifconfig())


def setUTC8Time():
    t = ntptime.time() + 28800  # 加8小時
    tm = time.localtime(t)
    machine.RTC().datetime(tm[0:3] + (0, ) + tm[3:6] + (0, ))  # 轉成RTC格式
    print('now:', time.localtime())


esp.osdebug(None)  # 開啟除錯功能
connectAP('City free wifi', 'QQQ')
setUTC8Time()
gc.collect()
