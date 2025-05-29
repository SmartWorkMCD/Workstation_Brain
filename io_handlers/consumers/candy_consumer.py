import json
import random

from io_handlers.consumers.base_consumer import BaseConsumer
from utils.yaml_loader import load_yaml


class CandyConsumer(BaseConsumer):

    def __init__(self, state):
        super().__init__(state)
        self.config = load_yaml("config/workstation_config.yaml")["candy_mqtt"]
        self.broker_conf = self.config.get("candy_mqtt", {})

    def start(self):
        pass

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] Connected with result code", rc)

    def update(self):
        # Simulate YOLO-style bounding box data (center_x, center_y, width, height)
        labels = ["Yellow", "Blue", "Green"]

        use_expected = random.random() < 0.5  # 50% chance to match expected config
        if use_expected:
            detected_candies = self.state.data.get("ExpectedConfig", {}).copy()
            print("[Sim] Using expected config for detection")
        else:
            detected_candies = {}
            for label in labels:
                count = random.randint(0, 3)
                if count > 0:
                    detected_candies[label] = count

        # Update state with detected candies
        self.state.update("DetectedCandies", detected_candies)
        print(f"[Sim] Detected candies: {detected_candies}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            # TODO: Implement the logic for processing candy detection messages

        except json.JSONDecodeError as e:
            print(f"[MQTT] Error decoding JSON: {e}")
            return
