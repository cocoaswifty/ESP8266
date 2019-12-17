# -*- coding: utf-8 -*-

import machine
import ubinascii
import time
import dht
from machine import Pin
from umqtt.simple import MQTTClient

config = {
    'broker': 'mqtt.thingspeak.com',
    'user': 'cubie',  # 使用者名稱
    'key': 'OOO',  # MQTT key
    # 用戶識別名稱，使用控制板實體位址
    'id': 'room/' + ubinascii.hexlify(machine.unique_id()).decode(),
    'topic': b'channels/938945/publish/XXX'  # Weite Key
}

client = MQTTClient(client_id=config['id'],
                    server=config['broker'],
                    user=config['user'],
                    password=config['key'])

d = dht.DHT11(Pin(2))
d.measure()

data = 'field1={}&field2={}'.format(
    d.temperature(),
    d.humidity())

client.connect()
client.publish(config['topic'], data.encode())  # 發布主題
time.sleep(2)
client.disconnect()
