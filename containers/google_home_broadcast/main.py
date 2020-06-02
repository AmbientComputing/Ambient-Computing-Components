
# docker-compose -f docker-compose.core.yml -f docker-compose.google_home.yml build google_home_broadcast;docker-compose -f docker-compose.core.yml -f docker-compose.google_home.yml up

import paho.mqtt.client as mqtt
import tornado.ioloop
import tornado.web
from gtts import gTTS
import pychromecast
import os

import socket

HOST_PORT = 22000

# import subprocess
# subprocess = subprocess.Popen("echo $(ifconfig | grep -Eo 'inet (addr:)?([0-9]*\.){3}[0-9]*' | grep -Eo '([0-9]*\.){3}[0-9]*' | grep -v '127.0.0.1'|grep 192.)", shell=True, stdout=subprocess.PIPE)
# host_ip = subprocess.stdout.read()
# print(host_ip.strip())
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Pull IP Address for Local HTTP File Serving (Note: This requires an internet connection)
s.connect(("8.8.8.8", 80))
host_ip = s.getsockname()[0]
print (host_ip)

chromecasts = None
files_dir = 'mp3_cache'
if not os.path.exists(files_dir):
    os.mkdir(files_dir)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        print(self.request.uri)
        print('Get Gotten')

        with open(self.request.uri.lstrip('/'), 'rb') as f:
            data = f.read()
            self.write(data)
        self.finish()

        # self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r".*", MainHandler),
    ])    

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("+/google_home_broadcast/+")  # $SYS/

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    message = str(msg.payload.decode())
    print(msg.topic+" "+message)

    mp3_file = files_dir + "/" + message.replace(" ","_") + ".mp3"
    print(mp3_file)
    tts = gTTS(text=message, lang='en-uk') # See Google TTS API for more Languages (Note: This may do translation Also - Needs Testing)
    tts.save(mp3_file)
    print("about to cast")
    cast(host_ip, mp3_file)

def cast(ip_add, mp3):
    # Example from here: https://github.com/GhostBassist/GooglePyNotify/blob/master/GooglePyNotify.py
    castdevice = next(cc for cc in CHROMECASTS if cc.device.model_name == "Google Home Mini")
    castdevice.wait()
    mediacontroller = castdevice.media_controller # ChromeCast Specific
    url = "http://{}:{}/{}".format(ip_add, HOST_PORT, mp3)
    # url = "http://" + ip_add + ":" + HOST_PORT + "/" + mp3
    print (url)
    print("ABOUT TO PLAY")
    print(mediacontroller.play_media(url, 'audio/mp3'))
    # mediacontroller.block_until_active()
    # mediacontroller.play()
    return


print("Getting chromecasts...")
CHROMECASTS = pychromecast.get_chromecasts()
print(CHROMECASTS)


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(host_ip, 1883, 60)

print("Start MQTT Event Loop")
client.loop_start()

# if __name__ == "__main__":
print("Start webserver")
app = make_app()
app.listen(HOST_PORT)
tornado.ioloop.IOLoop.current().start()
