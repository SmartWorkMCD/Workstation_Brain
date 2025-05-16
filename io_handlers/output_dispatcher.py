import json
import socket


class OutputDispatcher:
    def __init__(self):
        print("[OutputDispatcher initialized]")

    def execute_action(self, action: str):
        # This would normally send instructions to a projector or GUI.
        # For now, simulate with console output.
        print(f"[Output] Action executed: {action}")

    def send_to_management_interface(self, task_name, subtask_name, progress_percentage, state_dict):
        message = json.dumps({
            "task": task_name,
            "subtask": subtask_name,
            "progress": progress_percentage,
            "state": state_dict
        })
        print("[Management Interface]", message)
        print("[Management Interface]")
        print(f"  Task: {task_name}")
        print(f"  Subtask: {subtask_name}")
        print(f"  Progress: {progress_percentage}%")
        print("  State:")
        for key, value in state_dict.items():
            print(f"    {key}: {value}")

        # TODO: Send to management interface
        # self._send_to_socket(message, port=9000)

    def send_to_projector_visuals(self, state_dict):
        message = json.dumps({
            "highlight": "red" if not state_dict.get("CombinationValid", True) else "green",
            "hand_tracking": state_dict.get("HandGridCell")
        })

        print("[Projector Display]", message)
        print("[Projector Display]")
        if not state_dict.get("CombinationValid", True):
            print("✖ Defect detected! Highlighting in red.")
        else:
            print("✔ Assembly correct. Highlighting in green.")

        # TODO: Send to projector
        # self._send_to_socket(message, port=9001)

        hand_cell = state_dict.get("HandGridCell")
        if hand_cell:
            print(f"Hand detected in grid cell: {hand_cell}")

    def _send_to_socket(self, message: str, host: str = "localhost", port: int = 9000):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.sendto(message.encode(), (host, port))
        except Exception as e:
            print(f"[Error] Failed to send to port {port}: {e}")
