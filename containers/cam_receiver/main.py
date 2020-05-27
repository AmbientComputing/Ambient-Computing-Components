
import os
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer
from pyftpdlib.authorizers import DummyAuthorizer
import base64
import paho.mqtt.publish as publish

# import logging
# logging.basicConfig(level=logging.DEBUG)

#TODO: Make dynamic
mqtt_host = os.environ['MQTT_HOST'] if 'MQTT_HOST' in os.environ else '192.168.1.55'
mqtt_port = os.environ['MQTT_PORT'] if 'MQTT_PORT' in os.environ else 1883
passive_port_range_str = os.environ['PASSIVE_PORT_RANGE'] if 'PASSIVE_PORT_RANGE' in os.environ else '21001-21010'

class MyHandler(FTPHandler):

    def on_connect(self):
        print("%s:%s connected" % (self.remote_ip, self.remote_port))

    def on_disconnect(self):
        # do something when client disconnects
        pass

    def on_login(self, username):
        # do something when user login
        pass

    def on_logout(self, username):
        # do something when user logs out
        pass

    def on_file_sent(self, file):
        # do something when a file has been sent
        pass

    def on_file_received(self, file):
        # do something when a file has been received
        print('on_file_received', file)
        split_fpath = file.split('/')
        cam_name = split_fpath[-4]
        # TODO: fix image to be a format that Telegraf will recognise:
        encoded_image = self.convertImageToBase64(file)
        # self.convertImageToBase64(file).decode('ascii')
        print('encoded image ends with:',encoded_image[-10:-1])

        # Payload is using InfluxDB Line protocol format:
        # motion,sensor_type=camera,device_name=<> value=-60
        # = measurement,tag=tag1 measurement_name=vale <optional_timestamp>
        # publish a message for the image and for the indicator of motion:
        publish.multiple(
            [{
                "topic":"cached_file/camera_image/{}".format(cam_name),
                "payload":"images,type=image,device_name={} value={}".format(cam_name, str(encoded_image))
            },
            {
                "topic": "cached/camera_motion/{}".format(cam_name),
                "payload": "motion,type=motion,device_name={} value={}".format(cam_name, int(1))
            }],
            hostname=mqtt_host,
            port=mqtt_port
        )

    def on_incomplete_file_sent(self, file):
        # do something when a file is partially sent
        pass

    def on_incomplete_file_received(self, file):
        # remove partially uploaded files
        import os
        os.remove(file)

    def convertImageToBase64(self, path):
        with open(path, "rb") as image_file:
            encoded = base64.b64encode(image_file.read())
            return encoded


def main():
    print('Using MQTT Broker: {}:{}'.format(mqtt_host, mqtt_port))
    print('Passive Port Range:{}'.format(passive_port_range_str))
    authorizer = DummyAuthorizer()
    authorizer.add_user('user', '12345', homedir='.', perm='elradfmwMT')
    authorizer.add_anonymous(homedir='.', perm='elradfmwMT')

    handler = MyHandler
    handler.authorizer = authorizer
    # Needed to allow external docker ports to be accepted here:
    handler.permit_foreign_addresses = True

    # Passive ports needed or on_file_received never fires:
    passive_ports_tuple = passive_port_range_str.split('-')
    handler.passive_ports = range(int(passive_ports_tuple[0]), int(passive_ports_tuple[1]))

    server = FTPServer(('', 21000), handler)
    server.serve_forever()

if __name__ == "__main__":
    main()
