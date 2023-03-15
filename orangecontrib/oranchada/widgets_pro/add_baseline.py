from Orange.widgets import gui
from ..base_widget import FilterWidget
from ..processings.add_baseline import AddBaseline


class AddBaselineOW(FilterWidget):
    name = "Add Baseline"
    description = "add baseline"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.add_baseline = AddBaseline(self,
                                        n_freq=('n_freq', box),
                                        amplitude=('amplitude', box),
                                        intercept=('intercept', box),
                                        slope=('slope', box),
                                        quadratic=('quadratic', box),
                                        )

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(self.add_baseline(spe))
        self.send_outputs()
