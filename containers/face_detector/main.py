#!/usr/bin/env python3

"""
Code to detect faces in images
"""

import paho.mqtt.client as mqtt
import numpy as np
import cv2
import base64
import os

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_TOPIC = '+/camera_image/+'
MQTT_OUTPUT_TOPIC = 'uncached/face_detect_image/{}'
MQTT_CLIENT_ID = 'face_detector'

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    print("New message on topic:", MQTT_TOPIC)
    payload = msg.payload.decode().split(" value=b'")[-1].rstrip("'")

    print(payload[0:50], payload[-50:])
    jpg_original = base64.b64decode(payload)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    im = cv2.imdecode(jpg_as_np, flags=1)
    print(im.shape)

    # Based on: https://towardsdatascience.com/face-detection-in-2-minutes-using-opencv-python-90f89d7c0f81
    face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    print(faces)
    for (x, y, w, h) in faces:
       im =  cv2.rectangle(im, (x, y), (x+w, y+h), ( 0, 255, 0), 4)

    device_name = msg.topic.split('/')[2]
    print(device_name)

    retval, buffer = cv2.imencode('.jpg', im)
    enc_im = base64.b64encode(buffer)

    client.publish(MQTT_OUTPUT_TOPIC.format(device_name), enc_im)

#    client.publish('uncached/google_home_broadcast/blank', message)


def main():
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883, keepalive=60)
    mqtt_client.loop_forever()

if __name__ == '__main__':
    print('Started: Example Face Detector')
    main()
