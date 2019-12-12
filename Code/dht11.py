from machine import Pin
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


d = dht.DHT11(Pin(mini.D4))


def readDHT():
    d.measure()  # 開始測量
    hum = d.humidity()  # 濕度
    temp = d.temperature()  # 溫度
    dew = get_dew_point_c(temp, hum)  # 露點溫度
    status = dew_point_comfort_status(dew)
    frost = get_frost_point_c(temp, dew)  # 霜凍點
    return (str(hum)+'%', str(temp)+'\u00b0C', str(frost)+'\u00b0C', str(dew)+'\u00b0C', status)


while True:
    (hum, temp, frost, dew, status) = readDHT()
    print('Humidity: ' + hum)
    print('Temperature: ' + temp)
    print('Dew Point: {}, {}'.format(dew, status))
    print('Frost Point: ' + frost)
    time.sleep(10)  # 10秒測量一次
