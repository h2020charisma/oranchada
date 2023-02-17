from Orange.widgets.widget import Input
import ramanchada2 as rc2
from .rc2_base import RC2_Arithmetics, RC2Spectra


class Subtract(RC2_Arithmetics):
    name = "Subtract"
    description = "subtract spectra"
    icon = "icons/spectra.svg"

    class Inputs:
        minuend = Input("Minuend (rc2.Spectrum)", rc2.spectrum.Spectrum)
        subtrahend = Input("Subtrahend (rc2.Spectrum)", rc2.spectrum.Spectrum)

    @Inputs.minuend
    def set_minuend(self, spe):
        if spe:
            self.minuend = spe
        else:
            self.minuend = None
        if self.commitOnChange and self.minuend and self.subtrahend:
            self.commit()

    @Inputs.subtrahend
    def set_subtrahend(self, spe):
        if spe:
            self.subtrahend = spe
        else:
            self.subtrahend = None
        if self.commitOnChange and self.minuend and self.subtrahend:
            self.commit()

    def __init__(self):
        super().__init__()
        self.minuend = None
        self.subtrahend = None

    def process(self):
        self.out_spe = RC2Spectra()
        self.out_spe.append(self.minuend - self.subtrahend)
        self.send_outputs()
