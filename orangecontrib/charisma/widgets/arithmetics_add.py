from Orange.widgets.widget import Input
from .rc2_base import RC2_Arithmetics
import ramanchada2 as rc2


class Add(RC2_Arithmetics):
    name = "Add"
    description = "add spectra"
    icon = "icons/spectra.svg"

    class Inputs:
        addend1 = Input("Addend (rc2.Spectrum)", rc2.spectrum.Spectrum, default=True)
        addend2 = Input("Addend (rc2.Spectrum)", rc2.spectrum.Spectrum)

    @Inputs.addend1
    def set_addend1(self, spe):
        if spe:
            self.addend1 = spe
        else:
            self.addend1 = None
        if self.commitOnChange and self.addend1 and self.addend2:
            self.commit()

    @Inputs.addend2
    def set_addend2(self, spe):
        if spe:
            self.addend2 = spe
        else:
            self.addend2 = None
        if self.commitOnChange and self.addend1 and self.addend2:
            self.commit()

    def __init__(self):
        super().__init__()
        self.addend1 = None
        self.addend2 = None

    def process(self, spe):
        self.out_spe = self.addend1 + self.addend2
