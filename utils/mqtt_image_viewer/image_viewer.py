import paho.mqtt.client as mqtt
import cv2
import numpy as np
import argparse
import base64


parser = argparse.ArgumentParser()
parser.add_argument('--host', default='127.0.0.1')
parser.add_argument('--topic', default='+/camera_image/+')

args = parser.parse_args()
print(args.host, args.topic)

window_name = args.topic

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(args.topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic)

    # split off the beginning telegraf timeseries formatting:
    payload = msg.payload.decode().split(" value=b'")[-1].rstrip("'")

    print(payload[0:50], payload[-50:])

    jpg_original = base64.b64decode(payload)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    im = cv2.imdecode(jpg_as_np, flags=1)
    shape = im.shape
    ratio = shape[0]/shape[1]
    im = cv2.resize(im, (600, int(600*ratio)))

    cv2.imshow(window_name, im)
    cv2.waitKey(100)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(args.host, 1883, 60)

print("Start MQTT Event Loop")
client.loop_forever()