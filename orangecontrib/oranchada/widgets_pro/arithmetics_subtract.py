from Orange.widgets.widget import Input, Msg

from ..base_widget import ArithmeticWidget
from ..base_widget.types import RC2Spectra


class Subtract(ArithmeticWidget):
    name = "Subtract"
    description = "subtract spectra\nDifference spectra = Minuends - Subtrahends"
    icon = "icons/spectra.svg"

    class Inputs:
        minuend = Input("Minuend (RC2Spectra)", RC2Spectra, auto_summary = False)
        subtrahend = Input("Subtrahend (RC2Spectra)", RC2Spectra, auto_summary = False)

    class Warning(ArithmeticWidget.Warning):
        operands_dont_broadcast = Msg('Operands do not broadcast')

    def update_inputs_info(self):
        self.Warning.clear()
        len_minuend = len(self.minuend) if self.minuend else None
        len_subtrahend = len(self.subtrahend) if self.subtrahend else None
        self.info.set_input_summary(f'{len_minuend} RC2Spectra - {len_subtrahend} RC2Spectra')

    @Inputs.minuend
    def set_minuend(self, spe):
        if spe:
            self.minuend = spe
        else:
            self.minuend = None
        self.update_inputs_info()
        self.auto_process()

    @Inputs.subtrahend
    def set_subtrahend(self, spe):
        if spe:
            self.subtrahend = spe
        else:
            self.subtrahend = None
        self.update_inputs_info()
        self.auto_process()

    def __init__(self):
        super().__init__()
        self.minuend = None
        self.subtrahend = None
        self.info.set_input_summary(self.info.NoInput)

    def process(self):
        self.out_spe = list()
        if self.minuend and self.subtrahend:
            len1 = len(self.minuend)
            len2 = len(self.subtrahend)
            if len1 == len2:
                for i in range(len1):
                    self.out_spe.append(self.minuend[i] - self.subtrahend[i])
            elif len1 == 1:
                for i in range(len2):
                    self.out_spe.append(self.minuend[0] - self.subtrahend[i])
            elif len2 == 1:
                for i in range(len1):
                    self.out_spe.append(self.minuend[i] - self.subtrahend[0])
            else:
                self.Warning.operands_dont_broadcast()
        self.send_outputs()
