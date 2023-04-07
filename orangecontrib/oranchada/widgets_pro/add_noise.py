from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget
from ..processings.add_noise import AddNoise


class AddNoiseOW(FilterWidget):
    name = "Add Noise"
    description = "add noise"
    icon = "icons/spectra.svg"

    noise_scale = Setting(.01)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.add_noise = AddNoise(self,
                                  noise_scale=('noise_scale', box))

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                self.add_noise(spe)
                )
        self.send_outputs()
