from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget
from ..processings.add_baseline import AddBaseline


class AddBaselineOW(FilterWidget):
    name = "Add Baseline"
    description = "add baseline"
    icon = "icons/spectra.svg"

    n_freq = Setting(15)
    amplitude = Setting(2)
    intercept = Setting(10)
    slope = Setting(.01)
    quadratic = Setting(-.000005)

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
