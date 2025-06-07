import random
import time
import logging
import os
from paho.mqtt import client as mqtt_client
from davan.util import application_logger as app_logger
import davan.config.config_creator as configuration

class MyMqttClient():
    def __init__(self, callback):
        self.logger = logging.getLogger(os.path.basename(__file__))
        self.broker = 'localhost'
        self.port = 1883
        self.callbackListener = callback
        #self.topic = "/roomba/feedback/#"
        self.topic = ["/roomba/feedback/#"]
        #self.topic = ['/roomba/feedback/batPct','/roomba/feedback/bin_full','/roomba/feedback/state','/roomba/feedback/lastCommand_regions']
        
        #self.topic = [('/roomba/feedback/Bogda/batPct',0),('/roomba/feedback/Bogda/bin_full',0),('/roomba/feedback/Bogda/state',0),('/roomba/feedback/Bogda/lastCommand_regions',0)]
        self.client_id = f'python-mqtt-{random.randint(0, 1000)}'
        self.client = None

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected to Broker")
            self.subscribe()
        else:
            self.logger.info("Failed to connect, return code %d\n", rc)

    def connect_mqtt(self):
        self.logger.info("Connecting to Broker")
        self.client = mqtt_client.Client(self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port)
        return self.client

    def on_message(self, client, userdata, msg):
        self.callbackListener.message_received(msg)

    def subscribe(self):
        self.logger.info("Send subscribe")

        for top in self.topic:
            self.client.subscribe(top, 0)

    def publish(self, topic, message):
        result = self.client.publish(topic, message)
        status = result[0]
        if status == 0:
            print(f"Send `{message}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


    def start(self):
        self.logger.info("start")
        self.client = self.connect_mqtt()
        self.client.loop_start()

if __name__ == '__main__':
    config = configuration.create()
    app_logger.start_logging(config['LOGFILE_PATH'],loglevel=4)

    client = MyMqttClient()
    client.start()

    time.sleep(40)
    
