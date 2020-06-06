#!/usr/bin/env python3

"""
Code to apply logic to analysed motion sensor data to decide what to say to the user to motivate healthy behaviour
"""

import paho.mqtt.client as mqtt
from time import sleep, time
import os

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_TOPIC = '+/motion_sensor_summary_15m_activity/+'
MQTT_OUTPUT_TOPIC = 'uncached/google_home_broadcast/blank'
MQTT_CLIENT_ID = 'activity_motivator'
MIN_SECS_BETWEEN_BROADCASTS = int(os.environ['MIN_SECS_BETWEEN_BROADCASTS'])
# Ensure we send a message at the start:
time_since_last = time() - MIN_SECS_BETWEEN_BROADCASTS
print(time_since_last, time())

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    global time_since_last
    payload = msg.payload
    analysis_val = float(payload.decode('utf-8').split('value=')[-1])
    print('Activity Level: {}'.format(analysis_val))

    if (time()-time_since_last)>MIN_SECS_BETWEEN_BROADCASTS:
        if analysis_val > 0.6:
            message = 'Well done for staying active, keep it up.'
        else:
            message = 'You have not been very active recently, keep active to stay healthy.'
        time_since_last = time()

    client.publish('uncached/google_home_broadcast/blank', message)


def main():
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    # when this component starts give some time for the Google Home component to discover
    # devices before we start listening for messages
    sleep(15)
    mqtt_client.connect(MQTT_ADDRESS, 1883, keepalive=60)
    mqtt_client.loop_forever()

if __name__ == '__main__':
    print('Started: Example Motion Sensor Analyser')
    main()
