from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra


class RecoverSpikes(RC2_Filter):
    name = "Recover Spikes"
    description = "Recover single-bin spikes using linear interpolation"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.sigma = 10
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'sigma', 1, 100, callback=self.auto_process)

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.recover_spikes(self.sigma)
                )
        self.send_outputs()
