from core.evaluator import RuleEvaluator
from core.state import WorkstationState
from core.task_manager import TaskManager
from io_handlers.consumers.candy_consumer import CandyConsumer
from io_handlers.consumers.hand_consumer import HandConsumer
from io_handlers.consumers.task_assignment_consumer import TaskAssignmentConsumer
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
        self.products = load_yaml("config/products.yaml")['produtos']

        # Initialize state (config set later)
        self.state = WorkstationState(expected_config=None)

        # Initialize components
        self.task_manager = TaskManager(self.tasks_metadata)
        self.evaluator = RuleEvaluator()

        # Initialize and start consumers
        self.hand_consumer = HandConsumer(self.state)
        self.candy_consumer = CandyConsumer(self.state)
        self.task_consumer = TaskAssignmentConsumer(self.state, self.on_assignment_received)
        self.hand_consumer.start()
        self.candy_consumer.start()
        self.task_consumer.start()

        # Initialize publishers
        self.projector_publisher = ProjectorPublisher(self.state)
        self.task_division_publisher = TaskDivisionPublisher(self.state)

    def on_assignment_received(self, payload):
        """Called by the TaskAssignmentConsumer when new subtasks are assigned."""
        subtask_id = payload.get("task_id")
        product_config = payload.get("config", {})

        if product_config == {}:
            self.state.expected_config = self.products[payload.get("product")]["config"]
        else:
            self.state.expected_config = product_config

        # Enqueue the subtask
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
        first_time = True
        while True:

            # Check for new task assignments
            current_subtask, started = self.task_manager.get_current_subtask()

            # TODO: Read input from consumers
            candies = self.state.data["DetectedCandies"]
            handL = None
            handR = None
            if self.state.data['handL_Present']:
                handL = self.state.data['handL_data']
            if self.state.data['handR_Present']:
                handR = self.state.data['handR_data']
            # TODO: Process input and update state
            
            if clean:
                print("[Brain] Cleaning the table before starting a new subtask...")
                noHands = False
                noCandies = False                
                # Looks good if state is updated on message call, and no function is required to be called...
                if not handL and not handR:
                    print("[Brain] Cleaning the table, Both hands are not present")
                    noHands = True
                else:
                    print("[Brain] Cleaning the table, Make sure to remove candies from submission area")
                if len(list(candies['combo'].keys())) > 0:
                    print("[Brain] Cleaning the table, Make sure to remove candies from submission area")    
                else:
                    print("[Brain] Cleaning the table, No candies are present")
                    noCandies = True
                all_good = noHands and noCandies
                if all_good: 
                    clean = False
                continue
            
            # If no current subtask, wait for new assignments
            if not current_subtask:
                if first_time:
                    print("[Brain] Waiting for new task assignments...")
                    first_time = False
                continue

            task_id = self.task_manager.get_current_task_id()
            subtask_id = self.task_manager.get_current_subtask_id()
            progress = self.task_manager.get_progress()

            # If the subtask has just started
            if started:
                # Send initial task metadata to the projector
                self.projector_publisher.send_task(task_id, subtask_id, progress)
                
                

            rules = current_subtask.get("rules", [])
            completed = True

            for rule_id in rules:
                rule = self.rules.get(rule_id)
                if rule and not self.evaluator.evaluate_rule(rule["if"], self.state):
                    print(f"[Brain] Rule {rule_id} not satisfied. Waiting for conditions...")

                    # Notify the projector about the unsatisfied rule: Highlight the last cell in red
                    self.projector_publisher.highlight_cell_red(
                        self.config["grid"]["rows"],
                        self.config["grid"]["cols"]
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
                    self.config["grid"]["rows"],
                    self.config["grid"]["cols"]
                )

                # Notify the task division publisher
                start_time = self.task_manager.current_subtask_start_time
                end_time = self.task_manager.current_subtask_end_time
                self.task_division_publisher.send_current_subtask_completed(subtask_id, start_time, end_time)

                # Table needs cleaning before the next subtask
                clean = True
                self.state.data["CombinationValid"] = False
                self.state.data["CandiesWrapped"] = False
                # Clear the subtask tracking
                self.task_manager.clear()

            else:
                print(f"[Brain] Waiting for conditions to be satisfied for subtask {subtask_id}...")

            # Sleep to avoid busy-waiting
            time.sleep(0.1)
