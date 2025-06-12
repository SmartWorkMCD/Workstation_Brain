import time
import logging

from io_handlers.publishers.base_publisher import BasePublisher
from utils.yaml_loader import load_yaml

logger = logging.getLogger(__name__)


class ManagementInterfacePublisher(BasePublisher):
    def __init__(self, state):
        super().__init__(state)
        self.config = load_yaml("config/workstation_config.yaml")
        self.topic = self.config.get("management_topic", "management/interface")

    def send_system_status(self, status: str, message: str = ""):
        """Send system status updates to management interface."""
        data = {
            "timestamp": time.time(),
            "type": "system_status",
            "status": status,  # "idle", "active", "error", "cleaning", etc.
            "message": message
        }
        logger.debug(f"Sending system status: {status}")
        self.publish(self.topic, data)

    def send_state_change(self, from_state: str, to_state: str):
        """Notify management interface of state transitions."""
        data = {
            "timestamp": time.time(),
            "type": "state_transition",
            "from_state": from_state,
            "to_state": to_state
        }
        logger.debug(f"State transition: {from_state} -> {to_state}")
        self.publish(self.topic, data)

    def send_task_update(self, task_id: str, subtask_id: str, status: str, progress: float = 0.0):
        """Send task progress updates to management interface."""
        data = {
            "timestamp": time.time(),
            "type": "task_update",
            "task_id": task_id,
            "subtask_id": subtask_id,
            "status": status,  # "started", "in_progress", "waiting_confirmation", "completed", "failed"
            "progress": round(progress, 2)
        }
        logger.debug(f"Task update: {subtask_id} - {status} ({progress}%)")
        self.publish(self.topic, data)

    # def send_sensor_data_summary(self, candies_count: int, hands_detected: dict):
    #     """Send sensor data summary to management interface."""
    #     data = {
    #         "timestamp": time.time(),
    #         "type": "sensor_summary",
    #         "candies_detected": candies_count,
    #         "hands_detected": hands_detected,  # {"left": bool, "right": bool}
    #     }
    #     self.publish(self.topic, data)

    def send_rule_evaluation(self, rule_id: str, satisfied: bool, details: str = ""):
        """Send rule evaluation results to management interface."""
        data = {
            "timestamp": time.time(),
            "type": "rule_evaluation",
            "rule_id": rule_id,
            "satisfied": satisfied,
            "details": details
        }
        logger.debug(f"Rule evaluation: {rule_id} - {'PASS' if satisfied else 'FAIL'}")
        self.publish(self.topic, data)
