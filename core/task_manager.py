import time
from collections import deque


class TaskManager:
    def __init__(self, tasks):
        """
        Initialize TaskManager with all possible task definitions.
        Tasks will be added one at a time from Task Division.
        """
        self.tasks = tasks  # All possible subtask definitions
        self.subtask_queue = deque()  # Queue of received subtask IDs

        # For progress tracking
        self.completed_count = 0
        self.total_enqueued = 0

        # For timing subtasks
        self.current_subtask_start_time = None
        self.current_subtask_end_time = None
        self.current_subtask_id = None

    def enqueue_subtask(self, task_id, subtask_id):
        """Add a subtask to the queue for execution."""
        if task_id in self.tasks and subtask_id in self.tasks[task_id]["subtasks"]:

            # Add the subtask to the queue
            self.subtask_queue.append((task_id, subtask_id))
            print(f"[TaskManager] Enqueued subtask {subtask_id} from {task_id}.")

            # Track the total number of tasks received
            self.total_enqueued += 1

        else:
            print(f"[TaskManager] Invalid subtask {subtask_id} for task {task_id}.")

    def get_current_subtask(self):
        """Return the current subtask at the front of the queue."""
        if self.subtask_queue:

            # Check if it is a new subtask
            started = False

            # Get the task and subtask IDs
            task_id, subtask_id = self.subtask_queue[0]

            # Check if we need to start timing this subtask
            if subtask_id != self.current_subtask_id:
                started = True
                self.current_subtask_start_time = time.time()
                self.current_subtask_id = subtask_id
                print(f"[TaskManager] Started timing for {subtask_id}.")

            return self.tasks[task_id]["subtasks"].get(subtask_id, None), started

        return None, False

    def get_current_subtask_id(self):
        """Return the ID of the current subtask, or None if none available."""
        return self.subtask_queue[0] if self.subtask_queue else None

    def get_current_task_id(self):
        """Return the ID of the current task based on the front of the queue."""
        return self.subtask_queue[0] if self.subtask_queue else None

    def advance(self):
        """Advance to the next subtask and increment completed count."""
        if self.subtask_queue:
            # Pop the current subtask from the queue
            task_id, subtask_id = self.subtask_queue.popleft()

            # Stop timing the current subtask
            current_subtask_end_time = time.time()
            duration = current_subtask_end_time - self.current_subtask_start_time

            self.completed_count += 1

            print(f"[TaskManager] Completed {subtask_id} in {duration:.2f} seconds.")
        else:
            print("[TaskManager] No subtasks to advance.")

    def clear(self):
        """Clear the current subtask tracking."""
        self.current_subtask_start_time = None
        self.current_subtask_end_time = None
        self.current_subtask_id = None

    def get_progress(self):
        """Calculate the progress as a fraction of completed subtasks."""
        if self.total_enqueued == 0:
            return 0.0
        return self.completed_count / self.total_enqueued

    def get_stats(self):
        """Return a dictionary with current task statistics."""
        return {
            "completed": self.completed_count,
            "remaining": len(self.subtask_queue),
            "total": self.total_enqueued,
            "progress": round(self.get_progress(), 2)
        }
