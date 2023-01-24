from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra


class HHT_Sharpening(RC2_Filter):
    name = "HHT Sharpening"
    description = "hht sharpening"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.window_size = 100
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.hht_sharpening(movmin=self.window_size)
                )
        self.send_outputs()
