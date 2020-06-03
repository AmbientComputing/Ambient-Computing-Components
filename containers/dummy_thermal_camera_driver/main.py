import os
import time
import base64
import json
import paho.mqtt.client as mqtt


# MQTT_ADDRESS = 'test.mosquitto.org'
# MQTT_ADDRESS = '127.0.0.1'
MQTT_ADDRESS = 'mosquitto'
MQTT_USER = 'mqttuser'
MQTT_PASSWORD = 'mqttpassword'
MQTT_TOPIC = "uncached/thermal_camera_image/therm_cam_1"
MQTT_REGEX = '([^/]+)/([^/]+)/([^/]+)'
MQTT_CLIENT_ID = 'thermal_sensor_simulation'

dir_input = 'images/'
input_images = os.listdir(dir_input)

def on_connect(client, rc):
    """ The callback for when the client receives a CONNACK response from the server."""
    print('Connected with result code ' + str(rc))
    client.subscribe(MQTT_TOPIC)


def main():
    """ loop through images in a directory and send out at the framerate of the thermal camera"""
    mqtt_client = mqtt.Client(MQTT_CLIENT_ID)
    mqtt_client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.connect(MQTT_ADDRESS, 1883)
    mqtt_client.loop_start()

    for i in range(len(input_images)):
        with open(dir_input + input_images[i], "rb") as image_file:
            pic = input_images[i]
            encoded = base64.b64encode(image_file.read())
            encoded_image = str(encoded)
            # data = {'image': encoded, 'name': pic}
            # data = json.dumps(data)
        time.sleep(1)  # currently sending 1 image per second
        print('image_sent')
        mqtt_client.publish(MQTT_TOPIC,
                            "thermal_images,type=thermal_image,device_name=therm_cam_1 value={}".format(
                                                                               str(encoded_image)))

if __name__ == '__main__':
    print('Started: Thermal Sensor Simulation')
    main()
