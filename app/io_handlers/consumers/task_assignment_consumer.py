import json
from abc import ABC

from io_handlers.consumers.base_consumer import BaseConsumer


class TaskAssignmentConsumer(BaseConsumer, ABC):
    def __init__(self, state, on_assignment_callback):
        super().__init__(state)

        self.topic = self.config.get("task_assignment_topic", "tasks/publish")
        self.on_assignment_callback = on_assignment_callback
        self.base_products = {
            'T1A': {'Red': 1},
            'T1B': {'Green': 1},
            'T1C': {'Blue': 1}
        }

    def get_topic(self):
        return self.topic

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(f"[MQTT] Task Assignment received: {payload}")

            if not payload['tasks'] or not isinstance(payload, dict):
                print(f"[MQTT] Warning: Expected 'payload' as a dict, got {payload}")
                return
            
            for product in payload['tasks'].keys():
                for subtask in payload['tasks'][product]:
                    if subtask in self.base_products.keys():
                        print(f"[MQTT-Tasks] Subtask {subtask} for product {self.base_products[subtask]}")
                        self.on_assignment_callback({"task_id": subtask, "config": self.base_products[subtask]})
                    else:
                        print(f"[MQTT-Tasks] Subtask {subtask} for product {product}")
                        self.on_assignment_callback({"task_id": subtask, "product": product})
            

        except Exception as e:
            print(f"[MQTT] Error decoding task assignment: {e}")
