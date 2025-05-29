import json
import threading
from abc import ABC

import paho.mqtt.client as mqtt

from io_handlers.consumers.base_consumer import BaseConsumer
from utils.yaml_loader import load_yaml


class TaskAssignmentConsumer(BaseConsumer, ABC):
    def __init__(self, state, on_assignment_callback):
        super().__init__(state)

        self.config = load_yaml("config/workstation_config.yaml")
        self.broker_conf = self.config.get("task_assignment_mqtt", {})
        self.on_assignment_callback = on_assignment_callback

    def start(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(self.broker_conf.get("username", ""), self.broker_conf.get("password", ""))
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.broker_conf["broker_ip"], self.broker_conf["broker_port"], 60)
        self.client.subscribe(self.broker_conf["topic"])

        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self.thread.start()

    def on_connect(self, client, userdata, flags, rc):
        print(f"[MQTT] Connected to Task Division (code {rc})")

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

    def update(self):
        # No periodic updates needed for MQTT task messages
        pass
