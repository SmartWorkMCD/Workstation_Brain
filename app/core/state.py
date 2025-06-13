from typing import Dict


class WorkstationState:
    def __init__(self, expected_config: Dict[str, int] = None):
        self.data = {
            "CandiesWrapped": False,
            "CombinationValid": False,
            "DetectedCandies": {},
            "CandiesData": {},
            "ExpectedConfig": expected_config or {},  # From product definition
            "Defects": [],  # List of detected defects
            "handL_GridCell": None,  # Grid cell for left hand
            "handR_GridCell": None,  # Grid cell for right hand
            "handL_Present": False,  # Presence of left hand
            "handR_Present": False,  # Presence of right hand
            "handL_data": {},
            "handR_data": {},
            "SubtaskConfigs": {}
        }
        self.base_products = {
            'T1A': {'Red': 1},
            'T1B': {'Green': 1},
            'T1C': {'Blue': 1}
        }

    def update(self, key, value):
        self.data[key] = value
        if key == "DetectedCandies":
            if value != {} and self.data["ExpectedConfig"] != {}:
                self.validate_combination()

    def bulk_update(self, updates: dict):
        for key, value in updates.items():
            self.data[key] = value
        if "DetectedCandies" in updates:
            if value != {} and self.data["ExpectedConfig"] != {}:
                self.validate_combination()

    def add_defect(self, defect_description):
        self.data["Defects"].append(defect_description)

    def reset_defects(self):
        self.data["Defects"] = []

    def validate_combination(self):
        """Check if the detected candies match the expected configuration."""
        print("\033[91m[State] Validating combination...\033[0m")
        expected = self.data["ExpectedConfig"]
        detected = self.data["DetectedCandies"]
        self.data["CombinationValid"] = all(
            detected.get(color, 0) == count for color, count in expected.items()
        ) and all(
            color in expected for color in detected
        )
        print(f"\033[92m[State] Expected Config: {self.data['ExpectedConfig']}\033[0m")
        print(f"\033[93m[State] Detected Candies: {self.data['DetectedCandies']}\033[0m")
        if self.data["CombinationValid"]:
            self.data["CandiesWrapped"] = True
        else:
            self.data["CandiesWrapped"] = False

    def register_hand_presence(self, hand_label, present):
        """Register the presence of a hand."""
        self.data[f"{hand_label}_Present"] = present

    def get_hand_presence(self):
        return self.data['handL_Present'] or self.data['handR_Present']

    def get_hand_grid_cell(self):
        return self.data.get("HandGridCell")

    def to_dict(self):
        """Convert the state to a dictionary for easier access."""
        return self.data
