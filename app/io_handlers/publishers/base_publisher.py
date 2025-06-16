import json
import paho.mqtt.client as mqtt
from utils.config import CONFIG
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
class BasePublisher:
    def __init__(self, state):
        self.state = state

        # Load configuration from YAML
        self.config = CONFIG
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
                logger.info(f"[MQTT] Failed to publish to {topic}: {result.rc}")
            else:
                logger.info(f"[MQTT] Published to {topic}: {payload}")
        except Exception as e:
            logger.info(f"[MQTT] Error publishing to {topic}: {e}")

    def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
