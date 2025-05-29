from collections import deque
from core.evaluator import RuleEvaluator
from core.state import WorkstationState
from core.task_manager import TaskManager
from io_handlers.input_handler import InputHandler
from io_handlers.output_dispatcher import OutputDispatcher
from utils.yaml_loader import load_yaml


class WorkstationBrain:
    def __init__(self):
        # Load config and metadata
        self.rules = load_yaml("config/rules.yaml")["rules"]
        self.tasks_metadata = load_yaml("config/rules.yaml")["tasks"]

        # Initialize state (config set later)
        self.state = WorkstationState(expected_config=None)

        # Initialize components
        self.task_manager = TaskManager(self.tasks_metadata)
        self.evaluator = RuleEvaluator()
        self.input_handler = InputHandler(self.state)
        self.output_dispatcher = OutputDispatcher()

    def on_assignment_received(self, payload):
        """Called by the TaskAssignmentConsumer when new subtasks are assigned."""
        subtask_id = payload.get("task_id")
        product_config = payload.get("config", {})

        if self.state.expected_config is None:
            self.state.expected_config = product_config

        found = False
        for task_id, task_data in self.tasks_metadata.items():
            subtasks = task_data.get("subtasks", {})
            if subtask_id in subtasks:
                self.task_manager.enqueue_subtask(task_id, subtask_id)
                print(f"[Brain] Subtask {subtask_id} from {task_id} enqueued.")
                found = True
                break

        if not found:
            print(f"[Brain] Subtask {subtask_id} not found in task metadata.")

    def run(self):
        print("[Brain] Starting main loop...")
        while True:
            self.input_handler.update_state_from_sensors()
            current_subtask = self.task_manager.get_current_subtask()

            if not current_subtask:
                print("[Brain] Waiting for new task assignments...")
                continue

            task_id = self.task_manager.get_current_task_id()
            subtask_id = self.task_manager.get_current_subtask_id()
            progress = self.task_manager.get_progress()

            # TODO: Change this
            self.output_dispatcher.send_to_management_interface(task_id, subtask_id, progress, self.state.to_dict())
            self.output_dispatcher.send_to_projector_visuals(self.state.to_dict())

            rules = current_subtask.get("rules", [])
            for rule_id in rules:
                rule = self.rules.get(rule_id)
                if rule and self.evaluator.evaluate_rule(rule["if"], self.state):
                    self.output_dispatcher.execute_action(rule["do"])
                    self.task_manager.advance()
                    break

            print("-------------------------------")
