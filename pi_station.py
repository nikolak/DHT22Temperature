#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import time
import traceback
from datetime import datetime as dt
from math import sqrt

import Adafruit_DHT
import requests

SENSOR = Adafruit_DHT.DHT22
PIN = 4
WEB_API = os.environ.get('PI_STATION_API', "http://example.com/api/v1/update/")
SECRET_AUTH_KEY = os.environ.get('PI_STATION_SECRET_AUTH_KEY', 'your_secret_key_here_or_in_env')


def _convert_c_to_f(c):
    return c * 1.8 + 32


def _convert_f_to_c(f):
    return (f - 32) * 0.55555


def _compute_heat_index(temperature, percent_humidity, is_fahrenheit):
    # Converted from https://github.com/adafruit/DHT-sensor-library/blob/master/DHT.cpp

    if not is_fahrenheit:
        temperature = _convert_c_to_f(temperature)

    hi = 0.5 * (temperature + 61.0 + ((temperature - 68.0) * 1.2) + (percent_humidity * 0.094));

    if hi > 79:
        hi = -42.379 + \
             2.04901523 * temperature + \
             10.14333127 * percent_humidity + \
             -0.22475541 * temperature * percent_humidity + \
             -0.00683783 * pow(temperature, 2) + \
             -0.05481717 * pow(percent_humidity, 2) + \
             0.00122874 * pow(temperature, 2) * percent_humidity + \
             0.00085282 * temperature * pow(percent_humidity, 2) + \
             -0.00000199 * pow(temperature, 2) * pow(percent_humidity, 2)

    if (percent_humidity < 13) and (temperature >= 80.0) and (temperature <= 112.0):
        hi -= ((13.0 - percent_humidity) * 0.25) * sqrt((17.0 - abs(temperature - 95.0)) * 0.05882)

    else:
        if (percent_humidity > 85.0) and (temperature >= 80.0) and (temperature <= 87.0):
            hi += ((percent_humidity - 85.0) * 0.1) * ((87.0 - temperature) * 0.2)

    return hi if is_fahrenheit else _convert_f_to_c(hi)


def get_sensor_data():
    temperature_c, temperature_f, humidity, hic, hif = None, None, None, None, None
    try:
        humidity, temperature_c = Adafruit_DHT.read_retry(SENSOR, PIN)
    except:
        print 'Reading data failed...'

    if humidity is not None and temperature_c is not None:
        temperature_f = _convert_c_to_f(temperature_c)
        hic = _compute_heat_index(temperature_c, humidity, is_fahrenheit=False)  # heat index celsius
        hif = _compute_heat_index(temperature_f, humidity, is_fahrenheit=True)

    return temperature_c, temperature_f, humidity, hic, hif


def post_data(temp_c, temp_f, humidity, hic, hif):
    payload = {
        'celsius': temp_c,
        'fahrenheit': temp_f,
        'humidity': humidity,
        'hic': hic,
        'hif': hif,
        'key': SECRET_AUTH_KEY
    }
    try:
        r = requests.post(WEB_API, data=payload)
        if r.status_code == 400:
            print 'Wrong request. Invalid secret key?'
        if r.status_code == 200:
            if r.json().get('store') == 'OK':
                print 'Data posted to the API'
        else:
            print 'API post error. HTTP Code: {}, response: {}'.format(r.status_code,
                                                                       r.text)
    except:
        print 'Something went wrong while posting the data...'


if __name__ == '__main__':
    while True:
        try:
            time.sleep(10)
            temp_c, temp_f, humidity, hic, hif = get_sensor_data()
            if any([i is None for i in [temp_c, temp_f, humidity, hic, hif]]):
                print 'Some of the values are invalid... skipping'
                continue

            print '-' * 50
            print "UTC {}".format(dt.utcnow())
            print 'Humidity: {}%\tTemperature:{}°C\t{}°F\tHeat Index:{}°C\t{}°F'.format(temp_c,
                                                                                        temp_f,
                                                                                        humidity,
                                                                                        hic,
                                                                                        hif)
            post_data(temp_c, temp_f, humidity, hic, hif)
        except KeyboardInterrupt:
            print "Exiting..."
            exit(0)
        except Exception:
            traceback.print_exc(file=sys.stdout)
