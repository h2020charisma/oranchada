from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg

from ..base_widget import FilterWidget


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

    class Warning(FilterWidget.Warning):
        x_label_not_ramanshift = Msg('Expected spectra with Raman shift on xaxis')

    def process(self):
        self.out_spe = list()
        for inspe in self.in_spe:
            spe = inspe.shift_cm_1_to_abs_nm_filter(laser_wave_length_nm=self.laser_wl)
            if 'xlabel' in spe.meta.root:
                if spe.meta['xlabel'] != 'Raman shift [cm¯¹]':
                    self.Warning.x_label_not_ramanshift()
                meta_dct = spe.meta.model_dump()
                meta_dct['xlabel'] = 'Wavelength [nm]'
                spe.meta = meta_dct
            self.out_spe.append(spe)
        self.send_outputs()
