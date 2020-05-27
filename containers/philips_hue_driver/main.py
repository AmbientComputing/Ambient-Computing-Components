
import os
from phue import Bridge, PhueRegistrationException
from time import sleep
import paho.mqtt.client as mqtt
from json.decoder import JSONDecodeError


if 'HUE_IP' in os.environ:
    HUE_IP = os.environ['HUE_IP']
else:
    HUE_IP = '192.168.1.101'
POLL_INTERVAL = 3  # seconds

MQTT_ADDRESS = 'mosquitto'

MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_CLIENT_ID = 'philips_hue_driver'

print("Connecting to Philips Hue Hub, IP: {}".format(HUE_IP))

retry = True
while retry:
    try:
        b = Bridge(HUE_IP, config_file_path='/data/config_file.config')
        retry = False

    except PhueRegistrationException as e:
        print("The link button has not been pressed (on hub IP:{}) in the last "
              "30 seconds, please press and pairing will begin".format(HUE_IP))
        sleep(3)
    except JSONDecodeError as e:
        print("Error decoding HUE Hub response, is the hub IP ({}) correct?".format(HUE_IP))

# If the app is not registered and the button is not pressed, press the button and call connect() (this only needs to be run a single time)
b.connect()

# Get the bridge state (This returns the full dictionary that you can explore)
# print(b.get_api())


class ChangeTracker:
    def __init__(self):
        self.state_dict = {}

    def change_to_transmit(self, new_key, new_val):
        if new_key not in self.state_dict:
            self.state_dict[new_key] = new_val
            return new_val
        else:
            if self.state_dict[new_key] != new_val:
                self.state_dict[new_key] = new_val
                return new_val

        return None

def on_connect(client, userdata, flags, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('MQTT Connected with result code ' + str(rc))
    # client.subscribe(MQTT_TOPIC)

mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
mqtt_client.on_connect = on_connect
mqtt_client.connect(MQTT_ADDRESS, 1883, keepalive=60)
mqtt_client.loop_start()

print('Sensor types: ', set([val.type for val in b.sensors]))
# Sensor types:  {'CLIPGenericFlag', 'ZLLPresence', 'Daylight', 'ZLLTemperature', 'CLIPGenericStatus', 'ZLLLightLevel'}
# Need to log: ZLLTemperature, ZLLPresence, ZLLLightLevel, Daylight
# [print(val.name, val.type, val._get('state')) for val in b.sensors if val.type=='ZLLTemperature']
# [print(val.name, val.type, val._get('state')) for val in b.sensors if val.type=='ZLLPresence']
# [print(val.name, val.type, val._get('state')) for val in b.sensors if val.type=='ZLLLightLevel']
# [print(val.name, val.type, val._get('state')) for val in b.sensors if val.type=='Daylight']


light_change_tracker = ChangeTracker()
sensor_change_tracker = ChangeTracker()
while True:

    for light in b.lights:
        # TODO: "ConnectionResetError: [Errno 54] Connection reset by peer" occurs here:
        try:
            light_name, light_state = light.name, light._get('on')
        except ConnectionResetError as e:
            print('ERROR: ', e, ' try again')
            light_name, light_state = light.name, light._get('on')

        change = light_change_tracker.change_to_transmit(light_name, light_state)
        if change is not None:
            print("light changed: ", light_name, change, light_state)
            # TODO: send the name and change value
            # mqtt_client.publish("cached/light_state_change/{}".format(light_name.replace(' ', '_')), int(bool(change)))
            type = "light_state_change"
            mqtt_client.publish("cached/{}/{}".format(type, light_name.replace(' ', '_')),
                                "{},type={},device_name={} value={}".format(type,
                                                                            type,
                                                                            light_name.replace(' ', '_'),
                                                                            int(bool(change))))

    for sensor in b.sensors:
        try:
            sen_name, raw_sen_val, sen_type = sensor.name, sensor._get('state'), sensor.type
        except ConnectionResetError as e:
            print('ERROR: ', e, ' try again')
            sen_name, raw_sen_val, sen_type = sensor.name, sensor._get('state'), sensor.type

        if sen_type =='ZLLTemperature':
            sen_val = raw_sen_val['temperature']/100
            type = 'temperature'
        elif sen_type == 'ZLLPresence':
            sen_val = int(bool(raw_sen_val['presence']))
            type = 'motion'
        elif sen_type == 'ZLLLightLevel':
            sen_val = raw_sen_val['lightlevel']
            type = 'light_sensor'
        else:
            # if it is not one of the sensors of interest, go to next loop iteration
            continue

        # print(sen_name, sen_val, sen_type)
        change = sensor_change_tracker.change_to_transmit(sen_name, sen_val)
        if change is not None:
            print("sensor changed: ", sen_name, change, sen_val)
            mqtt_client.publish("cached/{}/{}".format(type, sen_name.replace(' ', '_')),
                                "{},type={},device_name={} value={}".format(type,
                                                                            type,
                                                                            sen_name.replace(' ', '_'),
                                                                            change)
                                )

    sleep(POLL_INTERVAL)


# TODO:
# - wrap code in docker container with external persistence of bridge settings
# + send out change messages for lights
# + figure out how to get motion sensor states
# + figure out how to get temperature states

