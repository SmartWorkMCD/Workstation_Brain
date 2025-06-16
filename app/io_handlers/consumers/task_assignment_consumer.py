import json
from abc import ABC

from io_handlers.consumers.base_consumer import BaseConsumer

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TaskAssignmentConsumer(BaseConsumer, ABC):
    def __init__(self, state, on_assignment_callback):
        super().__init__(state)

        self.topic = self.config.get("task_assignment_topic", "tasks/publish")
        logger.info(self.topic)
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
            logger.info(f"[MQTT] Task Assignment received: {payload}")

            if not payload['tasks'] or not isinstance(payload, dict):
                logger.info(f"[MQTT] Warning: Expected 'payload' as a dict, got {payload}")
                return
            
            for product in payload['tasks'].keys():
                for subtask in payload['tasks'][product]:
                    if subtask in self.base_products.keys():
                        logger.info(f"[MQTT-Tasks] Subtask {subtask} for product {self.base_products[subtask]}")
                        self.on_assignment_callback({"task_id": subtask, "config": self.base_products[subtask]})
                    else:
                        logger.info(f"[MQTT-Tasks] Subtask {subtask} for product {product}")
                        self.on_assignment_callback({"task_id": subtask, "product": product})
            

        except Exception as e:
            logger.info(f"[MQTT] Error decoding task assignment: {e}")
