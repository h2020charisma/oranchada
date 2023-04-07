from Orange.widgets.widget import Input

from .base_widget import BaseWidget
from .types import RC2Spectra


class FilterWidget(BaseWidget, openclass=True):

    def input_hook(self):
        pass

    class Inputs:
        in_spe = Input("RC2Spectra", RC2Spectra, default=True)

    @Inputs.in_spe
    def set_in_spe(self, spe):
        self.should_auto_plot = False
        if spe:
            self.in_spe = spe
            self.auto_process()
        else:
            self.in_spe = RC2Spectra()
        self.input_hook()
