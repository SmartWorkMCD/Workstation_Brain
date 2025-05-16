from typing import Dict


class WorkstationState:
    def __init__(self, expected_config: Dict[str, int] = None):
        self.data = {
            "CandiesWrapped": False,
            "CombinationValid": False,
            "DetectedCandies": {},
            "ExpectedConfig": expected_config or {},  # From product definition
            "Defects": [],  # List of detected defects
            "HandGridCell": None,  # Grid cell where the hand is detected
            "HandInFrame": False,  # Boolean if worker hand is present
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

    def validate_combination(self):
        """Check if the detected candies match the expected configuration."""
        expected = self.data["ExpectedConfig"]
        detected = self.data["DetectedCandies"]
        self.data["CombinationValid"] = all(
            detected.get(color, 0) == count for color, count in expected.items()
        ) and all(
            color in expected for color in detected
        )

    def get_hand_grid_cell(self):
        return self.data.get("HandGridCell")

    def to_dict(self):
        """Convert the state to a dictionary for easier access."""
        return self.data
