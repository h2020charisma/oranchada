from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra


class AddNoise(RC2_Filter):
    name = "Add Noise"
    description = "add noise"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.noise_scale = .01
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'noise_scale', 0, 100, decimals=5, step=.001, callback=self.auto_process)

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.add_poisson_noise(self.noise_scale)
                )
        self.send_outputs()
