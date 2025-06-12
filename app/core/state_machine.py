from abc import ABC, abstractmethod
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class WorkstationStates(Enum):
    IDLE = "idle"
    WAITING_FOR_TASK = "waiting_for_task"
    CLEANING = "cleaning"
    EXECUTING_TASK = "executing_task"
    WAITING_CONFIRMATION = "waiting_confirmation"
    TASK_COMPLETED = "task_completed"

class StateTransition:
    def __init__(self, from_state: WorkstationStates, to_state: WorkstationStates, condition_func=None):
        self.from_state = from_state
        self.to_state = to_state
        self.condition_func = condition_func

class State(ABC):
    def __init__(self, name: WorkstationStates):
        self.name = name
        
    @abstractmethod
    def enter(self, context):
        """Called when entering this state"""
        pass
        
    @abstractmethod
    def execute(self, context):
        """Called during state execution, returns next state or None to stay"""
        pass
        
    @abstractmethod
    def exit(self, context):
        """Called when exiting this state"""
        pass

class StateMachine:
    def __init__(self, initial_state: WorkstationStates):
        self.current_state = initial_state
        self.states = {}
        self.transitions = []
        
    def add_state(self, state: State):
        self.states[state.name] = state
        
    def add_transition(self, transition: StateTransition):
        self.transitions.append(transition)
        
    def transition_to(self, new_state: WorkstationStates, context):
        if new_state not in self.states:
            logger.error(f"State {new_state} not found")
            return False
            
        logger.info(f"Transitioning from {self.current_state} to {new_state}")
        
        # Exit current state
        if self.current_state in self.states:
            self.states[self.current_state].exit(context)
            
        # Enter new state
        old_state = self.current_state
        self.current_state = new_state
        self.states[new_state].enter(context)
        
        return True
        
    def execute(self, context):
        """Execute current state and check for transitions"""
        if self.current_state not in self.states:
            logger.error(f"Current state {self.current_state} not found")
            return
            
        # Execute current state
        next_state = self.states[self.current_state].execute(context)
        
        # If state returns a specific next state, transition to it
        if next_state and next_state != self.current_state:
            self.transition_to(next_state, context)
            return
            
        # Check automatic transitions
        for transition in self.transitions:
            if (transition.from_state == self.current_state and 
                (transition.condition_func is None or transition.condition_func(context))):
                self.transition_to(transition.to_state, context)
                break