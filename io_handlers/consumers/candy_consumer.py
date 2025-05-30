import json
import random

from io_handlers.consumers.base_consumer import BaseConsumer


class CandyConsumer(BaseConsumer):
    def __init__(self, state):
        super().__init__(state)

        # Load MQTT topic from global config
        self.topic = self.config.get("candy_topic", "candy/detection")

    def get_topic(self):
        return self.topic

    # def update(self):
    #     # Simulate YOLO-style bounding box data (center_x, center_y, width, height)
    #     labels = ["Yellow", "Blue", "Green"]
    #
    #     use_expected = random.random() < 0.5  # 50% chance to match expected config
    #     if use_expected:
    #         detected_candies = self.state.data.get("ExpectedConfig", {}).copy()
    #         print("[Sim] Using expected config for detection")
    #     else:
    #         detected_candies = {}
    #         for label in labels:
    #             count = random.randint(0, 3)
    #             if count > 0:
    #                 detected_candies[label] = count
    #
    #     self.state.update("DetectedCandies", detected_candies)
    #     print(f"[Sim] Detected candies: {detected_candies}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            # TODO: Implement the logic for real detection messages if available

            print(f"[MQTT] Received candy detection message: {payload}")
        except json.JSONDecodeError as e:
            print(f"[MQTT] Error decoding JSON: {e}")
