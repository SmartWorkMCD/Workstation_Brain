class TaskManager:
    def __init__(self, tasks, task_id):
        # Obtain all tasks from the Task Division
        self.tasks = tasks
        self.task_keys = list(tasks.keys())

        # Obtain the assigned task
        self.current_task_idx = self.task_keys.index(task_id) if task_id in self.task_keys else 0

        # Obtain the subtasks of the assigned task
        self.current_subtask_keys = list(tasks[task_id]['subtasks'].keys())
        self.current_subtask_idx = 0

    def get_current_subtask(self):
        # If invalid task index, return None
        if self.current_task_idx >= len(self.task_keys):
            return None

        # Obtain current task and subtask keys
        task_key = self.task_keys[self.current_task_idx]
        subtask_key = self.current_subtask_keys[self.current_subtask_idx]

        # Obtain current subtask
        return self.tasks[task_key]['subtasks'][subtask_key]

    def get_progress(self):
        return self.current_subtask_idx / len(self.current_subtask_keys)

    def advance(self):
        self.current_subtask_idx += 1

        # Print progress
        print(f"  Progress: {self.get_progress() * 100:.2f}%")

        if self.current_subtask_idx >= len(self.current_subtask_keys):
            # Restart subtask index
            self.current_subtask_idx = 0
