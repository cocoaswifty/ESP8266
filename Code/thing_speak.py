# -*- coding: utf-8 -*-
import urequests as req

apiURL = '{url}?api_key={key}&field1={temp}&field2={humid}'.format(
    url='https://api.thingspeak.com/update',
    key='XXX',
    temp=21,
    humid=47
)

r = req.get(apiURL)

if r.status_code != 200:
    print('Bad request')
else:
    print('Data saved, id:', r.text)
