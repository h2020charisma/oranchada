from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra


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

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.moving_minimum(self.window_size)
                )
        self.send_outputs()
