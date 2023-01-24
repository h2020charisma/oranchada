from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra


class AddBaseline(RC2_Filter):
    name = "Add Baseline"
    description = "add baseline"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.n_freq = 15
        self.amplitude = 2
        self.intercept = 10
        self.slope = .01
        self.quadratic = -.000005
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'n_freq', 3, 5000,
                 callback=self.auto_process, label='num freq')
        gui.doubleSpin(box, self, 'amplitude', 0, 5000, decimals=5, step=.01, label='amplitude',
                       callback=self.auto_process)
        gui.doubleSpin(box, self, 'intercept', -20000, 20000, decimals=5, step=1, label='intercept',
                       callback=self.auto_process)
        gui.doubleSpin(box, self, 'slope', -1000, 1000, decimals=5, step=.001, label='slope',
                       callback=self.auto_process)
        gui.doubleSpin(box, self, 'quadratic', -100, 100, decimals=7, step=.000001, label='quadratic',
                       callback=self.auto_process)

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.add_baseline(n_freq=self.n_freq,
                                 amplitude=self.amplitude,
                                 pedestal=0,
                                 func=lambda x: self.intercept + x*self.slope + x**2*self.quadratic
                                 )
                )
        self.send_outputs()
