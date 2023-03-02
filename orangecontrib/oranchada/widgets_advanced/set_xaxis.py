from Orange.widgets.widget import Input
from .rc2_base import RC2_Filter, RC2Spectra


class SetXaxis(RC2_Filter):
    name = "Set X-axis"
    description = "Set x-axis of the spectra equal to the calibrated spectrum"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.in_spe_calib = None

    class Inputs(RC2_Filter.Inputs):
        in_spe_calib = Input("RC2Spectra calib", RC2Spectra)
    
    @Inputs.in_spe_calib
    def set_in_spe_calib(self, spe):
        self.should_auto_plot = False
        if spe:
            if len(spe) != 1:
                raise ValueError('calibration takes only a single spectrum')
            self.in_spe_calib = spe[0]
            self.auto_process()
        else:
            self.in_spe_calib = RC2Spectra()
        self.input_hook()

    def process(self):
        if not self.in_spe_calib or not self.in_spe:
            return
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.set_new_xaxis(self.in_spe_calib.x)
                )
        self.send_outputs()
