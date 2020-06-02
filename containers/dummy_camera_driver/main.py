#!/usr/bin/env python3

"""
A simulation of a motion sensor driver to produce virtual motion sensor data.
"""

import paho.mqtt.client as mqtt
from time import sleep
import base64
import glob
import random

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
# e.g. (un)cached/device_type/device_id
#MQTT_TOPIC = '+/+/+'
#MQTT_REGEX = '([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'dummy_camera_driver'
SENSOR_NAME = 'dummy_camera_1'
IMAGE_DIR = "images/"

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

    images = glob.glob(IMAGE_DIR + "*.jpg")
    print(images)
    motion_detected_last_time = True
    motion_detected_now = True
    while True:
        sleep(5)

        # send a random image (TODO: do in sequence later):
        encoded_image = convertImageToBase64(random.choice(images))
        mqtt_client.publish("uncached/camera_image/{}".format(SENSOR_NAME),
                                "images,type=image,device_name={} value={}".format(SENSOR_NAME,
                                                                                    str(encoded_image)))

def convertImageToBase64(path):
    with open(path, "rb") as image_file:
        encoded = base64.b64encode(image_file.read())
        return encoded


if __name__ == '__main__':
    print('Started: Virtual Camera Driver')
    main()
