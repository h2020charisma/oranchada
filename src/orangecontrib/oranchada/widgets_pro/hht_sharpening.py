from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class HHT_Sharpening(FilterWidget):
    name = "HHT Sharpening"
    description = "hht sharpening"
    icon = "icons/spectra.svg"

    window_size = Setting(100)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.hht_sharpening(movmin=self.window_size)
                )
        self.send_outputs()
