from .state_machine import State, WorkstationStates
import logging
import time

logger = logging.getLogger(__name__)


class IdleState(State):
    def __init__(self):
        super().__init__(WorkstationStates.IDLE)

    def enter(self, context):
        logger.info("Entering IDLE state")
        context.first_time = True
        context.management_publisher.send_system_status("idle", "System initialized")
        context.management_publisher.send_state_change("unknown", "idle")

    def execute(self, context):
        if context.first_time:
            logger.info("WorkstationBrain initialized and ready")
            context.first_time = False
        return WorkstationStates.WAITING_FOR_TASK

    def exit(self, context):
        logger.debug("Exiting IDLE state")


class WaitingForTaskState(State):
    def __init__(self):
        super().__init__(WorkstationStates.WAITING_FOR_TASK)

    def enter(self, context):
        if context.first_time:
            logger.info("Waiting for new task assignments...")
            context.first_time = False
        context.management_publisher.send_system_status("waiting", "Waiting for task assignments")
        context.management_publisher.send_state_change("idle", "waiting_for_task")
        progress = context.task_manager.get_progress()
        context.projector_publisher.send_task("WAITING","Waiting for task assignments", progress* 100)
    def execute(self, context):
        current_subtask = context.task_manager.get_current_subtask()
        if current_subtask:
            return WorkstationStates.EXECUTING_TASK

        return None  # Stay in current state

    def exit(self, context):
        logger.debug("Exiting WAITING_FOR_TASK state")


class CleaningState(State):
    def __init__(self):
        super().__init__(WorkstationStates.CLEANING)

    def enter(self, context):
        logger.info("Starting table cleaning process...")
        context.management_publisher.send_system_status("cleaning", "Table cleaning in progress")
        context.management_publisher.send_state_change("task_completed", "cleaning")
        context.projector_publisher.task_clear(True)
        progress = context.task_manager.get_progress()
        context.projector_publisher.send_task("CLEANING","Cleaning in progress", progress * 100)

    def execute(self, context):
        # Get current sensor data
        candies = context.state.data["DetectedCandies"]
        left_hand = context.state.data['handL_data'] if context.state.data['handL_Present'] else None
        right_hand = context.state.data['handR_data'] if context.state.data['handR_Present'] else None

        no_hands = not left_hand and not right_hand
        no_candies = len(list(candies.keys())) == 0

        if no_hands:
            logger.info("Both hands are not present")
        else:
            logger.info("Make sure to remove hands from workspace")

        if no_candies:
            logger.info("No candies are present")
        else:
            logger.info("Make sure to remove candies from submission area")

        if no_hands and no_candies:
            logger.info("Table cleaning completed")
            context.management_publisher.send_system_status("ready", "Table cleaning completed")
            return WorkstationStates.WAITING_FOR_TASK

        return None  # Stay in cleaning state

    def exit(self, context):
        logger.debug("Exiting CLEANING state")


class ExecutingTaskState(State):
    def __init__(self):
        super().__init__(WorkstationStates.EXECUTING_TASK)

    def enter(self, context):
        current_subtask = context.task_manager.get_current_subtask()
        task_id = context.task_manager.get_current_task_id()
        subtask_id = context.task_manager.get_current_subtask_id()
        progress = context.task_manager.get_progress()
        print(f"\033[91mExecuting subtask: {subtask_id} of task {task_id}\033[0m")
        # Update expected configuration
        if current_subtask:
            expected_config = context.state.data['SubtaskConfigs'][subtask_id]
            context.state.update("ExpectedConfig", expected_config)
            logger.info(f"Executing subtask: {subtask_id} with config {expected_config}")
            
            # Notify management interface
            task_name = context.task_manager.get_current_task_name()
            product_description = context.state.data['ExpectedConfig']
            desc = ''
            for key, value in product_description.items():
                desc += f"{key}: {value}, "
            # transform product_description dict to string
            context.management_publisher.send_system_status("executing", f"Executing subtask {subtask_id}")
            context.management_publisher.send_state_change("waiting_for_task", "executing_task")
            context.management_publisher.send_task_update(task_id, subtask_id, "started", progress)

        # Send initial task metadata to projector if just started
        context.projector_publisher.send_task(task_id, subtask_id + ' - ' + task_name + '-> ' +  desc ,  progress* 100)

    def execute(self, context):
        current_subtask = context.task_manager.get_current_subtask()

        if not current_subtask:
            return WorkstationStates.WAITING_FOR_TASK

        # Evaluate all rules for the current subtask
        rules = current_subtask.get("rules", [])
        all_rules_satisfied = True

        for rule_id in rules:
            rule = context.rules.get(rule_id)
            if rule and not context.evaluator.evaluate_rule(rule["if"], context.state):
                all_rules_satisfied = False
                break

        if all_rules_satisfied:
            subtask_id = context.task_manager.get_current_subtask_id()
            context.management_publisher.send_task_update(
                context.task_manager.get_current_task_id(), 
                subtask_id, 
                "waiting_confirmation", 
                context.task_manager.get_progress()
            )
            return WorkstationStates.WAITING_CONFIRMATION

        last_row = context.config["grid"]["rows"] - 3
        last_col = context.config["grid"]["cols"] - 1
        context.projector_publisher.highlight_cell_red(last_row, last_col)
        return None  # Stay in current state

    def exit(self, context):
        logger.debug("Exiting EXECUTING_TASK state")


class WaitingConfirmationState(State):
    def __init__(self):
        super().__init__(WorkstationStates.WAITING_CONFIRMATION)
        
    def enter(self, context):
        subtask_id = context.task_manager.get_current_subtask_id()
        logger.info(f"Task rules satisfied for subtask {subtask_id}. Waiting for user confirmation...")
        logger.info("Please place your hand in the last cell (bottom-right corner) to confirm completion")
        
        # Notify management interface
        context.management_publisher.send_system_status("waiting_confirmation", "Waiting for user confirmation")
        context.management_publisher.send_state_change("executing_task", "waiting_confirmation")
        context.management_publisher.send_user_action("confirmation_required", {
            "subtask_id": subtask_id,
            "message": "Place hand in last cell to confirm completion"
        })
        
        # Highlight the confirmation cell (last row, last col)
        last_row = context.config["grid"]["rows"] - 3
        last_col = context.config["grid"]["cols"] - 1
        context.projector_publisher.highlight_cell_green(last_row, last_col)
        
    def execute(self, context):
        # Check if hand is in the last cell (confirmation cell)
        last_row = context.config["grid"]["rows"] - 3
        last_col = context.config["grid"]["cols"] - 1
        logger.info(f"Waiting for user confirmation in last cell ({last_row}, {last_col})")
        # Get hand data
        left_hand = context.state.data['handL_GridCell'] if context.state.data['handL_Present'] else None
        right_hand = context.state.data['handR_GridCell'] if context.state.data['handR_Present'] else None
        
        confirmation_detected = False
        
        # Check if either hand is in the last cell
        if left_hand:
            hand_row = left_hand[0]
            hand_col = left_hand[1]
            if hand_row == last_row and hand_col == last_col:
                confirmation_detected = True
                logger.info("Left hand confirmation detected in last cell")
                
        if right_hand and not confirmation_detected:
            hand_row = right_hand[0] 
            hand_col = right_hand[1]
            if hand_row == last_row and hand_col == last_col:
                confirmation_detected = True
                logger.info("Right hand confirmation detected in last cell")
        
        if confirmation_detected:
            logger.info("User confirmation received - proceeding to task completion")
            context.management_publisher.send_user_action("confirmation_received", {
                "subtask_id": context.task_manager.get_current_subtask_id()
            })
            # Clear the confirmation cell highlight
            last_row = context.config["grid"]["rows"] - 3
            last_col = context.config["grid"]["cols"] - 1
            context.projector_publisher.clear_cell(last_row, last_col)

            return WorkstationStates.TASK_COMPLETED
            
        return None  # Stay in waiting confirmation state
        
    def exit(self, context):
        logger.debug("Exiting WAITING_CONFIRMATION state")


class TaskCompletedState(State):
    def __init__(self):
        super().__init__(WorkstationStates.TASK_COMPLETED)

    def enter(self, context):
        subtask_id = context.task_manager.get_current_subtask_id()
        logger.info(f"All rules satisfied for subtask {subtask_id}")
        
        # Notify management interface
        context.management_publisher.send_system_status("completing", f"Completing subtask {subtask_id}")
        context.management_publisher.send_state_change("waiting_confirmation", "task_completed")

    def execute(self, context):
        # Mark subtask as completed
        context.task_manager.advance()

        # Notify projector about completion
        
        context.projector_publisher.task_complete(
            True
        )

        # Notify task division publisher
        subtask_id = context.task_manager.get_current_subtask_id()
        start_time = context.task_manager.current_subtask_start_time
        end_time = context.task_manager.current_subtask_end_time
        context.task_division_publisher.send_current_subtask_completed(
            subtask_id, start_time, end_time
        )
        
        # Notify management interface of completion
        task_id = context.task_manager.get_current_task_id()
        completion_time = end_time - start_time if start_time and end_time else 0
        context.management_publisher.send_task_update(
            task_id, subtask_id, "completed", 100.0
        )
        context.management_publisher.send_performance_metrics({
            "task_completion_time": completion_time,
            "subtask_id": subtask_id
        })

        # Reset state for next task
        context.state.data["CombinationValid"] = False
        context.state.data["CandiesWrapped"] = False
        context.state.data["ExpectedConfig"] = {}
        context.task_manager.clear()

        context.management_publisher.send_system_status("task_completed", f"Subtask {subtask_id} completed successfully")
        return WorkstationStates.CLEANING

    def exit(self, context):
        logger.debug("Exiting TASK_COMPLETED state")
