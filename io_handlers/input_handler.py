from io_handlers.consumers.candy_consumer import CandyConsumer
from io_handlers.consumers.hand_consumer import HandConsumer


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

        self.hand_consumer = HandConsumer(state)
        self.candy_consumer = CandyConsumer(state)

        self.hand_consumer.start()
        self.candy_consumer.start()

    def update_state_from_sensors(self):
        self.hand_consumer.update()
        self.candy_consumer.update()
