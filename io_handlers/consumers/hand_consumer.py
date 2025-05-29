import json
import threading
from abc import ABC

import paho.mqtt.client as mqtt

from io_handlers.consumers.base_consumer import BaseConsumer
from io_handlers.input_handler import GridMapper
from utils.yaml_loader import load_yaml


class HandConsumer(BaseConsumer, ABC):
    def __init__(self, state):
        super().__init__(state)

        # Load configuration from YAML file
        self.config = load_yaml("config/workstation_config.yaml")
        self.broker_conf = self.config.get("hand_mqtt", {})
        grid_conf = self.config["grid"]

        # Initialize grid mapper with configuration
        self.grid_mapper = GridMapper(
            grid_rows=grid_conf["rows"],
            grid_cols=grid_conf["cols"],
            image_width=grid_conf["image_width"],
            image_height=grid_conf["image_height"]
        )

    def start(self):
        self.client = mqtt.Client()
        self.client.username_pw_set(self.broker_conf["username"], self.broker_conf["password"])
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(self.config["broker_ip"], self.config["broker_port"], 60)
        self.client.subscribe(self.broker_conf["topic"])

        self.thread = threading.Thread(target=self.client.loop_forever, daemon=True)
        self.thread.start()

    def on_connect(self, client, userdata, flags, rc):
        print("[MQTT] Connected with result code", rc)

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))

            for hand_label in ["handL", "handR"]:
                x_key = f"{hand_label}_Wrist_x"
                y_key = f"{hand_label}_Wrist_y"

                if x_key in payload and y_key in payload:
                    x = float(payload[x_key]) * self.grid_mapper.image_width
                    y = float(payload[y_key]) * self.grid_mapper.image_height
                    cell = self.grid_mapper.get_grid_cell(x, y)

                    self.state.update(f"{hand_label}_GridCell", cell)
                    self.state.register_hand_presence(hand_label, True)
                    print(f"[MQTT] {hand_label} at ({x:.1f}, {y:.1f}) → Grid Cell {cell}")

                else:
                    print(f"[MQTT] Missing coordinates for {hand_label}")
                    self.state.update(f"{hand_label}_GridCell", None)
                    self.state.register_hand_presence(hand_label, False)

        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")
