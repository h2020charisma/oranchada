from Orange.widgets.widget import Input

from .base_widget import BaseWidget
from .types import RC2Spectra


class FilterWidget(BaseWidget, openclass=True):

    def input_hook(self):
        pass

    class Inputs:
        in_spe = Input("RC2Spectra", RC2Spectra, default=True, auto_summary = False)

    @Inputs.in_spe
    def set_in_spe(self, spe):
        self.Warning.clear()
        self.should_auto_plot = False
        if spe:
            self.in_spe = spe
            self.auto_process()
            self.info.set_input_summary(f'{len(self.in_spe)} RC2Spectra',
                                        '\n'.join([f'· {repr(i)}' for i in self.in_spe]))
        else:
            self.in_spe = RC2Spectra()
            self.info.set_input_summary(self.info.NoInput)
        self.input_hook()
