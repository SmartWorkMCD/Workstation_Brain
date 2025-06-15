from io_handlers.publishers.base_publisher import BasePublisher
from utils.config import CONFIG
import time


class TaskDivisionPublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)
        self.config = CONFIG
        self.topic = self.config.get("task_division_topic", "v1/devices/me/telemetry")

    def send_current_subtask_completed(self, subtask_id: str, start_time: float, end_time: float):
        payload = {
            "subtask_id": subtask_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
        }
        self.publish(self.topic, payload)
