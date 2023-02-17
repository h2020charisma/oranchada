from Orange.widgets import gui
from .rc2_base import RC2_Filter


class MovingMinimum(RC2_Filter):
    name = "Moving minimum"
    description = "moving minimum"
    icon = "icons/spectra.svg"

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.window_size = 10
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self, spe):
        return spe.moving_minimum(self.window_size)
