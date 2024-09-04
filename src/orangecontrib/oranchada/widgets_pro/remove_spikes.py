from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class RecoverSpikes(FilterWidget):
    name = "Recover Spikes"
    description = "Recover single-bin spikes using linear interpolation"
    icon = "icons/spectra.svg"

    sigma = Setting(10)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'sigma', 1, 100, callback=self.auto_process)

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.recover_spikes(self.sigma)
                )
        self.send_outputs()
