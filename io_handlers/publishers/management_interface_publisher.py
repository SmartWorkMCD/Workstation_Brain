import json
from io_handlers.publishers.base_publisher import BasePublisher
from utils.yaml_loader import load_yaml


class ManagementInterfacePublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)

        # Load configuration from YAML
        self.config = load_yaml("config/workstation_config.yaml")
        self.topic = self.config.get("management_interface_topic", "management/interface")

    def send(self, message_dict: dict):
        """ Publish a JSON-formatted message to the management interface topic."""
        try:
            payload = json.dumps(message_dict)
            self.client.publish(self.topic, payload)
            print(f"[MQTT] Sent message to Management Interface: {payload}")
        except Exception as e:
            print(f"[MQTT] Failed to send message to Management Interface: {e}")
