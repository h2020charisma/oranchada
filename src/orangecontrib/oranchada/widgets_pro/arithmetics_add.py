from Orange.widgets.widget import Input, Msg

from ..base_widget import ArithmeticWidget
from ..base_widget.types import RC2Spectra


class Add(ArithmeticWidget):
    name = "Add"
    description = "add spectra"
    icon = "icons/spectra.svg"

    class Inputs:
        addend1 = Input("Addend1 (RC2Spectra)", RC2Spectra, default=True, auto_summary = False)
        addend2 = Input("Addend2 (RC2Spectra)", RC2Spectra, default=False, auto_summary = False)

    class Warning(ArithmeticWidget.Warning):
        operands_dont_broadcast = Msg('Operands do not broadcast')

    def update_inputs_info(self):
        self.Warning.clear()
        len1 = len(self.addend1) if self.addend1 else None
        len2 = len(self.addend2) if self.addend2 else None
        self.info.set_input_summary(f'{len1} RC2Spectra + {len2} RC2Spectra')

    @Inputs.addend1
    def set_addend1(self, spe):
        if spe:
            self.addend1 = spe
        else:
            self.addend1 = None
        self.update_inputs_info()
        self.auto_process()

    @Inputs.addend2
    def set_addend2(self, spe):
        if spe:
            self.addend2 = spe
        else:
            self.addend2 = None
        self.update_inputs_info()
        self.auto_process()

    def __init__(self):
        super().__init__()
        self.addend1 = None
        self.addend2 = None
        self.info.set_input_summary(self.info.NoInput)

    def process(self):
        self.out_spe = list()
        if self.addend1 and self.addend2:
            len1 = len(self.addend1)
            len2 = len(self.addend2)
            if len1 == len2:
                for i in range(len1):
                    self.out_spe.append(self.addend1[i] + self.addend2[i])
            elif len1 == 1:
                for i in range(len2):
                    self.out_spe.append(self.addend1[0] + self.addend2[i])
            elif len2 == 1:
                for i in range(len1):
                    self.out_spe.append(self.addend1[i] + self.addend2[0])
            else:
                self.Warning.operands_dont_broadcast()
        self.send_outputs()
