from typing import Dict


class WorkstationState:
    def __init__(self, expected_config: Dict[str, int] = None):
        self.data = {
            "CandiesWrapped": False,
            "CombinationValid": False,
            "DetectedCandies": {},
            "ExpectedConfig": expected_config or {},  # From product definition
            "Defects": [],  # List of detected defects
            "handL_GridCell": None,  # Grid cell for left hand
            "handR_GridCell": None,  # Grid cell for right hand
            "handL_Present": False,  # Presence of left hand
            "handR_Present": False,  # Presence of right hand
            "handL_data": {},
            "handR_data": {}
        }
        self.base_products = {
            'T1A': {'Yellow': 1},
            'T1B': {'Blue': 1},
            'T1C': {'Green': 1},
            'T1D': {'Red': 1}
        }

    def update(self, key, value):
        self.data[key] = value
        if key == "DetectedCandies":
            self.validate_combination()

    def bulk_update(self, updates: dict):
        for key, value in updates.items():
            self.data[key] = value
        if "DetectedCandies" in updates:
            self.validate_combination()

    def add_defect(self, defect_description):
        self.data["Defects"].append(defect_description)

    def reset_defects(self):
        self.data["Defects"] = []

    def validate_combination(self, subtask_id):
        """Check if the detected candies match the expected configuration."""
        if subtask_id.startswith('T1'):
            self.data["ExpectedConfig"] = self.base_products[subtask_id]
        expected = self.data["ExpectedConfig"]
        detected = self.data["DetectedCandies"]['combo']
        self.data["CombinationValid"] = all(
            detected.get(color, 0) == count for color, count in expected.items()
        ) and all(
            color in expected for color in detected
        )
        if self.data["CombinationValid"]:
            self.data["CandiesWrapped"] = True
        else:
            self.data["CandiesWrapped"] = False

    def register_hand_presence(self, hand_label, present):
        """Register the presence of a hand."""
        self.data[f"{hand_label}_Present"] = present

    def get_hand_grid_cell(self):
        return self.data.get("HandGridCell")

    def to_dict(self):
        """Convert the state to a dictionary for easier access."""
        return self.data
