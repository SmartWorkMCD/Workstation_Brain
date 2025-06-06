import paho.mqtt.client as mqtt
import threading
from abc import ABC, abstractmethod

from utils.yaml_loader import load_yaml


class BaseConsumer(ABC):
    def __init__(self, state):
        self.state = state
        self.config = load_yaml("config/workstation_config.yaml")
        self.broker_conf = self.config.get("mqtt", {})
        self.client = None
        self.thread = None

    def start(self, topic=None):
        """
        Initialize the MQTT client and start listening in a background thread.
        """
        self.client = mqtt.Client()
        self.client.username_pw_set(
            self.broker_conf.get("username", ""), self.broker_conf.get("password", "")
        )
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(
            self.broker_conf.get("broker_ip", "127.0.0.1"),
            self.broker_conf.get("broker_port", 1883),
            60
        )

        # Allow subclasses to override the topic, otherwise use what's passed in
        subscribe_topic = topic or self.get_topic()
        if subscribe_topic:
            self.client.subscribe(subscribe_topic)

        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        print(f"[MQTT] Starting MQTT consumer thread..., {subscribe_topic}")
        self.thread.start()

    def get_topic(self):
        """ Override this method in subclasses to fetch the correct topic."""
        return None

    def on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected with result code {rc}")

    @abstractmethod
    def on_message(self, client, userdata, msg):
        """Subclasses must implement message handling."""
        pass
