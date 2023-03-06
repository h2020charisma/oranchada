from Orange.widgets.widget import Input
from ..base_widget import ArithmeticWidget
import ramanchada2 as rc2


class Add(ArithmeticWidget):
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
        if self.addend1 and self.addend2:
            self.auto_process()

    @Inputs.addend2
    def set_addend2(self, spe):
        if spe:
            self.addend2 = spe
        else:
            self.addend2 = None
        if self.addend1 and self.addend2:
            self.auto_process()

    def __init__(self):
        super().__init__()
        self.addend1 = None
        self.addend2 = None

    def process(self):
        self.out_spe = list()
        self.out_spe.append(self.addend1 + self.addend2)
        self.send_outputs()
