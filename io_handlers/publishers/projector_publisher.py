from io_handlers.publishers.base_publisher import BasePublisher
from utils.yaml_loader import load_yaml


class ProjectorPublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)
        self.config = load_yaml("config/workstation_config.yaml")
        self.topic = self.config.get("projector_topic", "projector/control")

    def highlight_cell_green(self, row: int, col: int):
        """Highlight a cell in green."""
        message = {
            "row": row,
            "col": col,
            "action": "highlight-green"
        }
        self.publish(self.topic, message)

    def highlight_cell_red(self, row: int, col: int):
        """Highlight a cell in red (e.g., to indicate an error)."""
        message = {
            "row": row,
            "col": col,
            "action": "highlight-red"
        }
        self.publish(self.topic, message)

    def clear_cell(self, row: int, col: int):
        """Clear highlight from a cell."""
        message = {
            "row": row,
            "col": col,
            "action": "clear"
        }
        self.publish(self.topic, message)

    def send_task(self, task_id: str, subtask_id: str, progress: float):
        """Send task metadata and progress to the projector module."""
        message = {
            "task_id": task_id,
            "subtask_id": subtask_id,
            "progress": round(progress, 2) # Between 0 and 100
        }
        self.publish(self.topic, message)
