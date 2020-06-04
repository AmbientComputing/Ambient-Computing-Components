#!/usr/bin/env python3

"""
A simulation of a motion sensor driver to produce virtual motion sensor data.
"""

import paho.mqtt.client as mqtt
from time import sleep
import random

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
# e.g. (un)cached/device_type/device_id
MQTT_TOPIC = '+/+/+'
MQTT_REGEX = '([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'dummy_motion_sensor'
SENSOR_NAME = 'dummy_ms_1'

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def main():
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_start()

    motion_detected_last_time = True
    motion_detected_now = True
    while True:
        sleep(2)

        # motion state changes at random with an average inversion frequency of 0.1:
        if random.random() > 0.9:
            motion_detected_now = not motion_detected_last_time

        # emit current motion state ONLY if it has changed since last time:
        if motion_detected_now != motion_detected_last_time:
            print('simulated motion state has changed to: ', motion_detected_now)

            mqtt_client.publish("cached/motion/{}".format(SENSOR_NAME),
                                "motion,type=motion,device_name={} value={}".format(SENSOR_NAME,
                                                                                    int(motion_detected_now)))

        motion_detected_last_time = motion_detected_now






if __name__ == '__main__':
    print('Started: Virtual Motion Sensor Driver')
    main()
