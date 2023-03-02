from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra
from ramanchada2.misc.types.peak_candidates import ListPeakCandidateMultiModel
from ramanchada2.spectrum.peaks.fit_peaks import available_models


class WL2RS(RC2_Filter):
    name = "WL to RS"
    description = "Wavelength to Raman shift"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.laser_wl = 785
        gui.doubleSpin(box, self, 'laser_wl', 0, 5000, decimals=5, step=1, callback=self.auto_process,
                       label='Laser Wavelength [nm]')


    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.abs_nm_to_shift_cm_1_filter(laser_wave_length_nm=self.laser_wl)
            )
        self.send_outputs()
