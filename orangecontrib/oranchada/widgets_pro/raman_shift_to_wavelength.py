from Orange.widgets import gui
from ..base_widget import FilterWidget
from Orange.widgets.settings import Setting


class RS2WL(FilterWidget):
    name = "RS to WL"
    description = "Raman shift to Wavelength"
    icon = "icons/spectra.svg"

    laser_wl = Setting(785)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'laser_wl', 0, 5000, decimals=5, step=1, callback=self.auto_process,
                       label='Laser Wavelength [nm]')

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.shift_cm_1_to_abs_nm_filter(laser_wave_length_nm=self.laser_wl)
            )
        self.send_outputs()
