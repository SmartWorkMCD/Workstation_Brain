from abc import ABC, abstractmethod

class SensorConsumer(ABC):
    def __init__(self, state):
        self.state = state

    @abstractmethod
    def start(self):
        """Start listening or producing input."""
        pass

    @abstractmethod
    def update(self):
        """Manually trigger update if needed (for simulations)."""
        pass
