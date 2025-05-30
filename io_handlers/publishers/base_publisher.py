import json
import paho.mqtt.client as mqtt
from utils.yaml_loader import load_yaml


class BasePublisher:
    def __init__(self, state):
        self.state = state

        # Load configuration from YAML
        self.config = load_yaml("config/workstation_config.yaml")
        self.mqtt_conf = self.config.get("mqtt", {})

        # MQTT client setup
        self.client = mqtt.Client()
        self.client.username_pw_set(
            self.mqtt_conf.get("username", ""), self.mqtt_conf.get("password", "")
        )
        self.client.connect(
            self.mqtt_conf.get("broker_ip", "localhost"),
            self.mqtt_conf.get("broker_port", 1883),
            60
        )
        self.client.loop_start()  # <-- important for async publishing

    def publish(self, topic, data):
        try:
            payload = json.dumps(data)
            result = self.client.publish(topic, payload)
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                print(f"[MQTT] Failed to publish to {topic}: {result.rc}")
            else:
                print(f"[MQTT] Published to {topic}: {payload}")
        except Exception as e:
            print(f"[MQTT] Error publishing to {topic}: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
