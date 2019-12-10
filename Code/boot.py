import machine
import uos
import webrepl
import gc
import esp
esp.osdebug(None)  # 開啟除錯功能
# uos.dupterm(None, 1) # disable REPL on UART(0)


def connectAP(ssid, pwd):
    import network
    wlan = network.WLAN(network.STA_IF)  # 設定成STA模式
    if not wlan.isconnected():
        wlan.active(True)  # 啟用無線網路
        wlan.connect(ssid, pwd)

    while not wlan.isconnected():  # 等待，直到連線成功
        pass

    print('network config:', wlan.ifconfig())


connectAP('City free wifi', 'pwssword')
webrepl.start()
gc.collect()
