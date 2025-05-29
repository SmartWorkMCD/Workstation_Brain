from abc import ABC, abstractmethod

from utils.yaml_loader import load_yaml


class BaseConsumer(ABC):
    def __init__(self, state):
        self.state = state

        # Load configuration from YAML file
        self.config = load_yaml("config/workstation_config.yaml")
        self.broker_conf = self.config.get("mqtt", {})

    @abstractmethod
    def start(self):
        """Start listening or producing input."""
        self.client = mqtt.Client()
        self.client.username_pw_set(self.broker_conf["username"], self.broker_conf["password"])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.config["broker_ip"], self.config["broker_port"], 60)
        self.client.subscribe(self.broker_conf["topic"])

    @abstractmethod
    def update(self):
        """Manually trigger update if needed (for simulations)."""
        pass
