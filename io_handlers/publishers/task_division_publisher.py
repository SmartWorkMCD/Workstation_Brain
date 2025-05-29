import time
import threading
from io_handlers.publishers.base_publisher import BasePublisher
from utils.yaml_loader import load_yaml


class TaskDivisionPublisher(BasePublisher):
    def __init__(self, state, interval_seconds=10):
        super().__init__(state)
        self.config = load_yaml("config/workstation_config.yaml")
        self.topic = self.config.get("task_division_topic", "v1/devices/me/telemetry")
        self.running = False
        self.thread = None
        self.interval = interval_seconds

    def collect_statistics(self):
        return {
            "subtasks_completed": self.state.subtasks_completed,
            "subtask_timings": self.state.subtask_timings,
        }

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        while self.running:
            stats = self.collect_statistics()
            self.publish(self.topic, stats)
            time.sleep(self.interval)

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
