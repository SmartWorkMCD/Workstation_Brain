from io_handlers.publishers.base_publisher import BasePublisher
from utils.config import CONFIG
import time

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TaskDivisionPublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)
        self.config = CONFIG
        self.topic = self.config.get("task_division_topic", "tasks/subscribe/brain")
        logger.info(f"AAAAAAAA: {self.topic}")

    def send_current_subtask_completed(self, subtask_id: str, start_time: float, end_time: float):
        payload = {
            "subtask_id": subtask_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
        }
        self.publish(self.topic, payload)
