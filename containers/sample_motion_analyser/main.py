#!/usr/bin/env python3

"""A MQTT to InfluxDB Bridge

This script receives MQTT data and saves those to InfluxDB.

"""

import re
from typing import NamedTuple

import paho.mqtt.client as mqtt
from influxdb import InfluxDBClient
import statistics
from json import dumps

INFLUXDB_ADDRESS = 'influxdb'
INFLUXDB_USER = 'root'
INFLUXDB_PASSWORD = 'root'
INFLUXDB_DATABASE = 'ambient'

MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
# e.g. (un)cached/device_type/device_id
MOTION_SENSOR_TYPE = 'motion'
MQTT_TOPIC = '+/{}/+'.format(MOTION_SENSOR_TYPE)
MQTT_CLIENT_ID = 'motion_sensor_summariser'

influxdb_client = InfluxDBClient(INFLUXDB_ADDRESS, 8086, INFLUXDB_USER, INFLUXDB_PASSWORD, database=INFLUXDB_DATABASE)


def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    """The callback for when a PUBLISH message is received from the server."""
    topic = msg.topic

    # Because of the subscription definition, this topic will have to have 3 parts:
    cached, device_type, device_id = topic.split('/')
    print(cached, device_type, device_id)

    get_and_send_stats_for_ms(device_type=device_type, device_id=device_id, client=client)


def get_and_send_stats_for_ms(device_type, device_id, client=None):
    # Calculate and emit the activity level (proportion of period active) for various activity window lengths for this
    # motion sensor
    print("get_and_send_stats_for_ms", device_id, device_type)

    for period in ['15m', '30m', '1h']:
        # fill(previous) to make the data step-change data, because the sensor only
        # sends whent there is a change in state
        query = "SELECT max(value)  FROM {} WHERE time >= now() - {} and device_name='{}' group by " \
                "time(30s) fill(previous);".format(device_type, period, device_id)
        resp = influxdb_client.query(query)

        # keep only values which are not None:
        data_list = [val['max'] for val in resp.get_points(measurement=MOTION_SENSOR_TYPE) if val['max'] is not None]

        proportion_active = statistics.mean(data_list)

        if client is not None:
            topic = "cached/motion_sensor_summary_{}_activity/{}".format(period, device_id)
            payload = \
                "motion_sensor_summary_{}_activity,type=motion_sensor_summary_{}_activity,device_name={} " \
                "value={}".format(period, period,
                                  device_id, proportion_active)
            print("SENDING", topic, payload)
            client.publish(topic, payload)


    ### And report the number of firings per hour over the last n hours:
    query = "SELECT count(value) FROM {} WHERE time >= now() -24h and device_name='{}' GROUP BY time(1h)".\
        format(device_type, device_id)
    resp = influxdb_client.query(query)
    data_list = [val['count'] for val in resp.get_points(measurement=MOTION_SENSOR_TYPE) if val['count'] is not None]
    topic = "uncached/motion_sensor_summary_profile/{}".format(device_id)
    payload = \
        "motion_sensor_summary_profile,type=motion_sensor_summary_profile,device_name={} " \
        "value={}".format(device_id, dumps(data_list))
    print("SENDING", topic, payload)
    client.publish(topic, payload)

def main():

    # dev and debugging:
    # get_and_send_stats_for_ms(device_type='dummy_motion_sensor', device_id='ms1')

    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message

    mqtt_client.connect(MQTT_ADDRESS, 1883, keepalive=60)
    mqtt_client.loop_forever()


if __name__ == '__main__':
    print('Started: Example Motion Sensor Analyser')
    main()
