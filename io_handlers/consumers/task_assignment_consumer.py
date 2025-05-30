import json
from abc import ABC

from io_handlers.consumers.base_consumer import BaseConsumer


class TaskAssignmentConsumer(BaseConsumer, ABC):
    def __init__(self, state, on_assignment_callback):
        super().__init__(state)

        self.topic = self.config.get("task_assignment_topic", "v1/devices/me/attributes")
        self.on_assignment_callback = on_assignment_callback

    def get_topic(self):
        return self.topic

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            print(f"[MQTT] Task Assignment received: {payload}")

            tasks = payload.get("tasks")
            if not tasks or not isinstance(tasks, list):
                print(f"[MQTT] Warning: Expected 'tasks' as a list, got {tasks}")
                return

            for task_id in tasks:
                if self.on_assignment_callback:
                    self.on_assignment_callback(task_id)

        except Exception as e:
            print(f"[MQTT] Error decoding task assignment: {e}")
