from core.evaluator import RuleEvaluator
from core.state import WorkstationState
from core.task_manager import TaskManager
from io_handlers.consumers.candy_consumer import CandyConsumer
from io_handlers.consumers.hand_consumer import HandConsumer
from io_handlers.publishers.projector_publisher import ProjectorPublisher
from io_handlers.publishers.task_division_publisher import TaskDivisionPublisher
from utils.yaml_loader import load_yaml
import time


class WorkstationBrain:
    def __init__(self):
        # Load config and metadata
        self.rules = load_yaml("config/rules.yaml")["rules"]
        self.tasks_metadata = load_yaml("config/rules.yaml")["tasks"]
        self.config = load_yaml("config/workstation_config.yaml")

        # Initialize state (config set later)
        self.state = WorkstationState(expected_config=None)

        # Initialize components
        self.task_manager = TaskManager(self.tasks_metadata)
        self.evaluator = RuleEvaluator()

        # Initialize and start consumers
        self.hand_consumer = HandConsumer(self.state)
        self.candy_consumer = CandyConsumer(self.state)
        self.hand_consumer.start()
        self.candy_consumer.start()

        # Initialize publishers
        self.projector_publisher = ProjectorPublisher(self.state)
        self.task_division_publisher = TaskDivisionPublisher(self.state)

    def on_assignment_received(self, payload):
        """Called by the TaskAssignmentConsumer when new subtasks are assigned."""
        subtask_id = payload.get("task_id")
        product_config = payload.get("config", {})

        if self.state.expected_config is None:
            self.state.expected_config = product_config

        found = False
        for task_id, task_data in self.tasks_metadata.items():
            if subtask_id in task_data.get("subtasks", {}):
                self.task_manager.enqueue_subtask(task_id, subtask_id)
                print(f"[Brain] Subtask {subtask_id} from {task_id} enqueued.")
                found = True
                break

        if not found:
            print(f"[Brain] Subtask {subtask_id} not found in task metadata.")

    def run(self):
        print("[Brain] Starting main loop...")

        # Check if table needs cleaning
        clean = False

        while True:

            # Check for new task assignments
            current_subtask, started = self.task_manager.get_current_subtask()

            if clean:
                print("[Brain] Cleaning the table before starting a new subtask...")

                # TODO: Implement table cleaning logic
                # No objects should be on the table
                # No hand should be present

            # If no current subtask, wait for new assignments
            if not current_subtask:
                print("[Brain] Waiting for new task assignments...")
                continue

            task_id = self.task_manager.get_current_task_id()
            subtask_id = self.task_manager.get_current_subtask_id()
            progress = self.task_manager.get_progress()

            # If the subtask has just started
            if started:
                # Send initial task metadata to the projector
                self.projector_publisher.send_task(task_id, subtask_id, progress)

            # TODO: Read input from consumers
            # TODO: Process input and update state

            rules = current_subtask.get("rules", [])
            completed = True

            for rule_id in rules:
                rule = self.rules.get(rule_id)
                if rule and not self.evaluator.evaluate_rule(rule["if"], self.state):
                    print(f"[Brain] Rule {rule_id} not satisfied. Waiting for conditions...")

                    # Notify the projector about the unsatisfied rule: Highlight the last cell in red
                    self.projector_publisher.highlight_cell_red(
                        self.config["grid"]["rows"] - 1,
                        self.config["grid"]["cols"] - 1
                    )

                    # If the rule is not satisfied, we can break out of the loop
                    completed = False
                    break

            if completed:
                print(f"[Brain] All rules satisfied for subtask {subtask_id}.")

                # Mark the subtask as completed
                self.task_manager.advance()

                # Notify the projector about task completion: Highlight the last cell in green
                self.projector_publisher.highlight_cell_green(
                    self.config["grid"]["rows"] - 1,
                    self.config["grid"]["cols"] - 1
                )

                # Notify the task division publisher
                start_time = self.task_manager.current_subtask_start_time
                end_time = self.task_manager.current_subtask_end_time
                self.task_division_publisher.send_current_subtask_completed(subtask_id, start_time, end_time)

                # Table needs cleaning before the next subtask
                clean = True

                # Clear the subtask tracking
                self.task_manager.clear()

            else:
                print(f"[Brain] Waiting for conditions to be satisfied for subtask {subtask_id}...")

            # Sleep to avoid busy-waiting
            time.sleep(0.1)
