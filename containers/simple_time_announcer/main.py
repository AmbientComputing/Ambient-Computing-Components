#!/usr/bin/env python3

"""
A simple logic component to periodically emit the current time
"""

import paho.mqtt.client as mqtt
from time import sleep
import os
import datetime

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_CLIENT_ID = 'simple_time_announcer'
NOTIFICATION_INTERVAL_SECONDS = int(os.environ['NOTIFICATION_INTERVAL_SECONDS'])

def main():
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_start()

    # Time example emits the message on a fixed timer, a better version would 
    # use a scheduler, such as APScheduler to decide when to trigger the notification
    sleep(10)
    while True:

        t = datetime.datetime.now()
        hour = t.hour
        min = t.minute
        msg = "The time is now {} {} {}".format(hour, 'owe' if min<10 else '', min)
        print(msg)
        mqtt_client.publish("uncached/google_home_broadcast/blank", 
                            msg)

        sleep(NOTIFICATION_INTERVAL_SECONDS)


if __name__ == '__main__':
    print('Started: Simple Time Announcer')
    main()
