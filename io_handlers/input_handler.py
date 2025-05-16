import random


class GridMapper:
    def __init__(self, grid_rows=3, grid_cols=3, image_width=640, image_height=480):
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
        self.image_width = image_width
        self.image_height = image_height

    def get_grid_cell(self, x_center, y_center):
        row = int(y_center / self.image_height * self.grid_rows)
        col = int(x_center / self.image_width * self.grid_cols)
        return row, col


class InputHandler:
    def __init__(self, state):
        self.state = state
        self.grid_mapper = GridMapper()

    def simulate_hand_tracking(self):
        # Simulate hand coordinates (center_x, center_y)
        hand_x = random.uniform(0, self.grid_mapper.image_width)
        hand_y = random.uniform(0, self.grid_mapper.image_height)

        # Obtain grid cell from coordinates
        cell = self.grid_mapper.get_grid_cell(hand_x, hand_y)

        # Update state with hand position and grid cell
        self.state.update("HandGridCell", cell)
        print(f"[Sim] Hand position: ({hand_x:.1f}, {hand_y:.1f}) -> Grid Cell: {cell}")

    def simulate_candy_detection(self):
        # Simulate YOLO-style bounding box data (center_x, center_y, width, height)
        labels = ["Yellow", "Blue", "Green"]

        use_expected = random.random() < 0.5  # 50% chance to match expected config
        if use_expected:
            detected_candies = self.state.data.get("ExpectedConfig", {}).copy()
            print("[Sim] Using expected config for detection")
        else:
            detected_candies = {}
            for label in labels:
                count = random.randint(0, 3)
                if count > 0:
                    detected_candies[label] = count

        # Update state with detected candies
        self.state.update("DetectedCandies", detected_candies)
        print(f"[Sim] Detected candies: {detected_candies}")

    def update_state_from_sensors(self):
        self.simulate_hand_tracking()
        self.simulate_candy_detection()
