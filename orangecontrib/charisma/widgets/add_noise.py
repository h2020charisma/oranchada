from Orange.widgets import gui
from .rc2_base import RC2_Filter


class AddNoise(RC2_Filter):
    name = "Add Noise"
    description = "add noise"
    icon = "icons/spectra.svg"

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.noise_scale = .01
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'noise_scale', 0, 100, decimals=5, step=.001, callback=self.auto_process)

    def process(self, spe):
        return spe.add_poisson_noise(self.noise_scale)
