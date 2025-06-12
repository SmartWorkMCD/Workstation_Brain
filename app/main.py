from utils.yaml_loader import load_yaml
from core.state import WorkstationState
from core.evaluator import RuleEvaluator
from core.task_manager import TaskManager
from core.state_machine import StateMachine, WorkstationStates
from core.workstation_states import (
    IdleState, WaitingForTaskState, CleaningState,
    ExecutingTaskState, WaitingConfirmationState, TaskCompletedState
)
from io_handlers.consumers.candy_consumer import CandyConsumer
from io_handlers.consumers.hand_consumer import HandConsumer
from io_handlers.consumers.task_assignment_consumer import TaskAssignmentConsumer
from io_handlers.publishers.projector_publisher import ProjectorPublisher
from io_handlers.publishers.task_division_publisher import TaskDivisionPublisher
from io_handlers.publishers.management_publisher import ManagementInterfacePublisher
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WorkstationBrainContext:
    """Context object that holds all the data and components for the state machine"""

    def __init__(self, brain):
        self.brain = brain
        self.rules = brain.rules
        self.tasks_metadata = brain.tasks_metadata
        self.config = brain.config
        self.products = brain.products
        self.state = brain.state
        self.task_manager = brain.task_manager
        self.evaluator = brain.evaluator
        self.projector_publisher = brain.projector_publisher
        self.task_division_publisher = brain.task_division_publisher
        self.management_publisher = brain.management_publisher
        self.first_time = True


class WorkstationBrain:
    def __init__(self):
        try:
            # Load config and metadata
            self.rules = load_yaml("config/rules.yaml")["rules"]
            self.tasks_metadata = load_yaml("config/rules.yaml")["tasks"]
            self.config = load_yaml("config/workstation_config.yaml")
            self.products = load_yaml("config/products.yaml")['produtos']
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise

        # Initialize state (config set later)
        self.state = WorkstationState(expected_config=None)

        # Initialize components
        self.task_manager = TaskManager(self.tasks_metadata)
        self.evaluator = RuleEvaluator()

        # Initialize and start consumers
        try:
            self.hand_consumer = HandConsumer(self.state)
            self.candy_consumer = CandyConsumer(self.state)
            self.task_consumer = TaskAssignmentConsumer(self.state, self.on_assignment_received)
            self.hand_consumer.start()
            self.candy_consumer.start()
            self.task_consumer.start()
            logger.info("MQTT consumers started successfully")
        except Exception as e:
            logger.error(f"Failed to start MQTT consumers: {e}")
            raise

        # Initialize publishers
        try:
            self.projector_publisher = ProjectorPublisher(self.state)
            self.task_division_publisher = TaskDivisionPublisher(self.state)
            self.management_publisher = ManagementInterfacePublisher(self.state)
            logger.info("MQTT publishers initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MQTT publishers: {e}")
            raise

        # Initialize state machine
        self._setup_state_machine()

        # Create context for state machine
        self.context = WorkstationBrainContext(self)

    def _setup_state_machine(self):
        """Setup the state machine with all states and transitions"""
        self.state_machine = StateMachine(WorkstationStates.IDLE)

        # Add all states
        self.state_machine.add_state(IdleState())
        self.state_machine.add_state(WaitingForTaskState())
        self.state_machine.add_state(CleaningState())
        self.state_machine.add_state(ExecutingTaskState())
        self.state_machine.add_state(WaitingConfirmationState())
        self.state_machine.add_state(TaskCompletedState())

        logger.info("State machine initialized")

    def on_assignment_received(self, payload):
        """Called by the TaskAssignmentConsumer when new subtasks are assigned."""
        try:
            subtask_id = payload.get("task_id")
            product_config = payload.get("config", {})

            if product_config == {}:
                product_name = payload.get("product")
                if product_name in self.products:
                    product_config = self.products[product_name]["config"]
                else:
                    logger.warning(f"Product {product_name} not found in configuration")
                    return

            logger.info(f"New task assignment received: {subtask_id} with config {product_config}")

            # Enqueue the subtask
            found = False
            for task_id, task_data in self.tasks_metadata.items():
                if subtask_id in task_data.get("subtasks", {}):
                    self.task_manager.enqueue_subtask(task_id, subtask_id)
                    self.state.data['SubtaskConfigs'][subtask_id] = product_config
                    logger.info(f"Subtask {subtask_id} from {task_id} enqueued")
                    found = True
                    break

            if not found:
                logger.warning(f"Subtask {subtask_id} not found in task metadata")
        except Exception as e:
            logger.error(f"Error processing task assignment: {e}")

    def run(self):
        """Main execution loop using state machine"""
        logger.info("Starting WorkstationBrain main loop...")

        try:
            while True:
                # Execute current state
                self.state_machine.execute(self.context)

                # Sleep to avoid busy-waiting
                time.sleep(0.1)

        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            self.shutdown()
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            self.shutdown()
            raise

    def shutdown(self):
        """Gracefully shutdown all components"""
        logger.info("Shutting down WorkstationBrain...")
        try:
            # Stop consumers
            if hasattr(self, 'hand_consumer'):
                # Note: Add stop() method to consumers if not present
                pass
            if hasattr(self, 'candy_consumer'):
                pass
            if hasattr(self, 'task_consumer'):
                pass
            logger.info("All components shut down successfully")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def sum(a, b):
    """Simple sum function for demonstration"""
    return a + b


if __name__ == "__main__":
    try:
        brain = WorkstationBrain()
        brain.run()
    except Exception as e:
        logger.error(f"Failed to start WorkstationBrain: {e}")
        exit(1)
