from core.evaluator import RuleEvaluator
from core.state import WorkstationState
from core.task_manager import TaskManager
from io_handlers.input_handler import InputHandler
from io_handlers.output_dispatcher import OutputDispatcher
from utils.yaml_loader import load_yaml


class WorkstationBrain:
    def __init__(self, product_id, task_id):

        # TODO: Change this (Task Division should set the rules, tasks, and products)
        self.rules = load_yaml("config/rules.yaml")["rules"]
        self.tasks = load_yaml("config/rules.yaml")["tasks"]
        self.products = load_yaml("config/products.yaml")["produtos"]

        self.state = WorkstationState(expected_config=self.products[product_id]["config"])
        self.input_handler = InputHandler(self.state)
        self.output_dispatcher = OutputDispatcher()

        self.task_manager = TaskManager(self.tasks, task_id)
        self.evaluator = RuleEvaluator()

    def run(self):
        # TODO: Implement infinite loop
        for _ in range(5):
            self.input_handler.update_state_from_sensors()
            current_subtask = self.task_manager.get_current_subtask()

            if not current_subtask:
                print("All tasks completed.")
                return

            task_key = self.task_manager.task_keys[self.task_manager.current_task_idx]
            subtask_key = self.task_manager.current_subtask_keys[self.task_manager.current_subtask_idx]
            progress = self.task_manager.get_progress()

            # Display current state before any rule application
            self.output_dispatcher.send_to_management_interface(task_key, subtask_key, progress, self.state.to_dict())
            self.output_dispatcher.send_to_projector_visuals(self.state.to_dict())

            rules = current_subtask.get("rules", [])
            for rule_id in rules:
                rule = self.rules.get(rule_id)
                if rule and self.evaluator.evaluate_rule(rule["if"], self.state):
                    self.output_dispatcher.execute_action(rule["do"])
                    self.task_manager.advance()
                    break

            print(f"-------------------------------")
