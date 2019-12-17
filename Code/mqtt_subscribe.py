# -*- coding: utf-8 -*-

import machine
import ubinascii
import ujson
from umqtt.simple import MQTTClient

config = {
    'broker': 'mqtt.thingspeak.com',
    'user': 'cubie',    # 使用者名稱
    'key': 'OOO',  # MQTT key
    # 用戶識別名稱，使用控制板實體位址
    'id': 'iot/'+ubinascii.hexlify(machine.unique_id()).decode(),
    'topic': b'channels/938945/subscribe/json/XXX'  # Read API Key
}


def subCallback(topic, msg):
    obj = ujson.loads(msg)  # json轉dic
    print(topic, msg)
    print('----------------------')
    print('temp:',  obj['field1'])
    print('humid:', obj['field2'])
    print('')


def main():
    client = MQTTClient(client_id=config['id'],
                        server=config['broker'],
                        user=config['user'],
                        password=config['key'])
    client.set_callback(subCallback)
    try:
        client.connect()
    except Exception as e:
        print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
        client.disconnect()
    client.subscribe(config['topic'])  # 訂閱主題

    try:
        while True:
            client.wait_msg()  # 10秒檢查一次
            time.sleep(10)
    except:
        client.disconnect()
        print('bye!')


main()
