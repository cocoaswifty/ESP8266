
def setUTC8Time():
    import time
    import ntptime
    import machine

    t = ntptime.time() + 28800  # 加8小時
    tm = time.localtime(t)
    machine.RTC().datetime(tm[0:3] + (0, ) + tm[3:6] + (0, ))  # 轉成RTC格式
    print(time.localtime())


setUTC8Time()
