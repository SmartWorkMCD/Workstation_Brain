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
    # TODO: check if on_message runs concurrently with brain, meaning receiving a message would automatically update the state
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
            keys = payload.keys()
            candies_info = [key for key in keys if "yolo" in key]
            candies = {}
            candies_combination = {}
            for i in range(len(candies_info)//6):
                candy = {
                    'class': payload[f'yolo_{i}_class'],
                    'x1': payload[f'yolo_{i}_x1'],
                    'y1': payload[f'yolo_{i}_y1'],
                    'x2': payload[f'yolo_{i}_x2'],
                    'y2': payload[f'yolo_{i}_y2'],
                    'score': payload[f'yolo_{i}_score']
                }
                if payload[f'yolo_{i}_score'] < 0.6:
                    continue
                # check if candy is inside validation area
                # neccessary to normalize x and y values, ask Mateus
                # assumes x is [0, 960] and y [0,720], same as resolution
                x1_norm = float(candy['x1'] / 960)
                x2_norm = float(candy['x2'] / 960)
                y1_norm = float(candy['y1'] / 720)
                y2_norm = float(candy['y2'] / 720)
                if not all(0.3 < val < 0.6 for val in [x1_norm, x2_norm, y1_norm, y2_norm]):
                    print("Removed detection candy outside submission area")
                    continue

                if payload[f'yolo_{i}_class'] in candies_combination.keys():
                    candies_combination[payload[f'yolo_{i}_class']] += 1
                else:
                    candies_combination[payload[f'yolo_{i}_class']] = 1
                candies[f'candy_{i}'] = candy
            candies['combo'] = candies_combination
            self.state.update("DetectedCandies", candies)
            print(f"[MQTT] Detected candies: {candies}")

            print(f"[MQTT] Received candy detection message: {payload}")
        except json.JSONDecodeError as e:
            print(f"[MQTT] Error decoding JSON: {e}")
