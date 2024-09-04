from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg

from ..base_widget import FilterWidget


class WL2RS(FilterWidget):
    name = "WL to RS"
    description = "Wavelength to Raman shift"
    icon = "icons/spectra.svg"

    laser_wl = Setting(785)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'laser_wl', 0, 5000, decimals=5, step=1, callback=self.auto_process,
                       label='Laser Wavelength [nm]')

    class Warning(FilterWidget.Warning):
        x_label_not_wavelength = Msg('Expected spectra with wavelengths on xaxis')

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            if 'xlabel' in spe.meta.root:
                if spe.meta['xlabel'] != 'Wavelength [nm]':
                    self.Warning.x_label_not_wavelength()
                meta_dct = spe.meta.model_dump()
                meta_dct['xlabel'] = 'Raman shift [cm¯¹]'
                spe.meta = meta_dct
            self.out_spe.append(
                spe.abs_nm_to_shift_cm_1_filter(laser_wave_length_nm=self.laser_wl)
            )
        self.send_outputs()
