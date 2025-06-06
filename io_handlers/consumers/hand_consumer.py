import json
from abc import ABC

from io_handlers.consumers.base_consumer import BaseConsumer
from io_handlers.consumers.grid_mapper import GridMapper


class HandConsumer(BaseConsumer, ABC):
    def __init__(self, state):
        super().__init__(state)

        # Load MQTT topic from global config
        self.topic = self.config.get("hand_topic", "hands/position")

        # Initialize GridMapper with workspace grid setup
        grid_conf = self.config["grid"]
        self.grid_mapper = GridMapper(
            grid_rows=grid_conf["rows"],
            grid_cols=grid_conf["cols"],
            image_width=grid_conf["image_width"],
            image_height=grid_conf["image_height"]
        )

    def get_topic(self):
        return self.topic

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
