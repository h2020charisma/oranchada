from Orange.widgets import gui
from ..base_widget import FilterWidget


class HHT_Sharpening(FilterWidget):
    name = "HHT Sharpening"
    description = "hht sharpening"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.window_size = 100
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.hht_sharpening(movmin=self.window_size)
                )
        self.send_outputs()
