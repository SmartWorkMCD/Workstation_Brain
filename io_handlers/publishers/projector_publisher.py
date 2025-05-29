from io_handlers.publishers.base_publisher import BasePublisher
from utils.yaml_loader import load_yaml


class ProjectorPublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)
        self.config = load_yaml("config/workstation_config.yaml")
        self.topic = self.config.get("projector_topic", "projector/control")

    def highlight_cell(self, row: int, col: int):
        message = {
            "row": row,
            "col": col,
            "action": "highlight"
        }
        self.publish(self.topic, message)

    def clear_cell(self, row: int, col: int):
        message = {
            "row": row,
            "col": col,
            "action": "clear"
        }
        self.publish(self.topic, message)
