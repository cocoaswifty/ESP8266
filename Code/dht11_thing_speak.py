# -*- coding: utf-8 -*-
import urequests as req
from machine import Pin, Timer
import dht
import time
import mini
import math


def get_frost_point_c(t_air_c, dew_point_c):
    """Compute the frost point in degrees Celsius
    :param t_air_c: current ambient temperature in degrees Celsius
    :type t_air_c: float
    :param dew_point_c: current dew point in degrees Celsius
    :type dew_point_c: float
    :return: the frost point in degrees Celsius
    :rtype: float
    """
    dew_point_k = 273.15 + dew_point_c
    t_air_k = 273.15 + t_air_c
    frost_point_k = dew_point_k - t_air_k + 2671.02 / \
        ((2954.61 / t_air_k) + 2.193665 * math.log(t_air_k) - 13.3448)
    return round(frost_point_k - 273.15, 1)


def get_dew_point_c(t_air_c, rel_humidity):
    """Compute the dew point in degrees Celsius
    :param t_air_c: current ambient temperature in degrees Celsius
    :type t_air_c: float
    :param rel_humidity: relative humidity in %
    :type rel_humidity: float
    :return: the dew point in degrees Celsius
    :rtype: float
    """
    A = 17.27
    B = 237.7
    alpha = ((A * t_air_c) / (B + t_air_c)) + math.log(rel_humidity/100.0)
    return round((B * alpha) / (A - alpha), 1)


def dew_point_comfort_status(dew):
    status = ''
    if dew <= 10:
        status = '太乾燥'
    elif dew >= 26:
        status = '小心中暑'
    elif dew >= 21:
        status = '悶熱'
    elif dew >= 18:
        status = '不舒服'
    else:
        status = '舒適'
    return status


def readDHT():
    try:
        d.measure()  # 開始測量
    except OSError as e:
        print(e)
        return

    hum = d.humidity()  # 濕度
    temp = d.temperature()  # 溫度
    dew = get_dew_point_c(temp, hum)  # 露點溫度
    status = dew_point_comfort_status(dew)
    frost = get_frost_point_c(temp, dew)  # 霜凍點
    return (str(hum), str(temp), str(frost), str(dew), status)


def sendDHT11(t):
    global apiURL, running

    (humid, temp, frost, dew, _) = readDHT()
    apiURL = '{url}?api_key={key}&field1={temp}&field2={humid}&field3={dew}&field4={frost}'.format(
        url='https://api.thingspeak.com/update',
        key='OOO',
        temp=temp,
        humid=humid,
        frost=frost,
        dew=dew
    )

    r = req.get(apiURL)

    if r.status_code != 200:
        t.deinit()
        print('Bad request error.')
        running = False
    else:
        print('Data saved, id:', r.text)


d = dht.DHT11(Pin(mini.D4))
running = True  # 預設不斷執行

tim = Timer(-1)  # 設置計時器20秒觸發一次
tim.init(period=20000, mode=Timer.PERIODIC, callback=sendDHT11)

try:
    while running:
        pass
except:
    tim.deinit()
    print('stopped')
