from Orange.widgets import gui
from .rc2_base import RC2_Filter


class HHT_Sharpening(RC2_Filter):
    name = "HHT Sharpening"
    description = "hht sharpening"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.window_size = 100
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self, spe):
        return spe.hht_sharpening(movmin=self.window_size)
