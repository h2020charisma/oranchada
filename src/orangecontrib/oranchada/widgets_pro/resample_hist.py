from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg
import numpy as np
from ramanchada2.spectrum import Spectrum
from Orange.data import Domain, ContinuousVariable, Table, StringVariable


from ..base_widget import FilterWidget


class Resample_density(FilterWidget):
    name = "Resample"
    description = "Resample using density"
    icon = "icons/spectra.svg"

    xmin = Setting(100)
    xmax = Setting(3600)
    npoints = Setting(3500)
    show_original = Setting(False)

    class Warning(FilterWidget.Warning):
        range = Msg('x-min should be less that x-max')

    def __init__(self):
        super().__init__()
        box1 = gui.widgetBox(self.controlArea, "Resampled x axis")
        gui.spin(box1, self, 'xmin', -1000, 10000, callback=self.auto_process, label='x-min')
        gui.spin(box1, self, 'xmax', -1000, 10000, callback=self.auto_process, label='x-max')
        gui.spin(box1, self, 'npoints', 1, 10000, callback=self.auto_process, label='npoints')
        box2 = gui.widgetBox(self.controlArea, "Visualisaiton")
        gui.checkBox(box2, self, "show_original", "Show original", callback=self.auto_process)

    def process(self):
        self.Warning.clear()
        self.out_spe = list()
        x_values = np.linspace(self.xmin, self.xmax, self.npoints)
        for spe in self.in_spe:
            if self.xmin > self.xmax:
                self.Warning.range()
            else:
                dist = spe.spe_distribution(trim_range=(self.xmin, self.xmax))

                # resample using probability density function
                y_values = dist.pdf(x_values)
                scale = np.max(spe.y) / np.max(y_values)
                # pdf sampling is normalized to area unity, scaling back
                _tmp = y_values * scale
                self.out_spe.append(
                    Spectrum(x_values, _tmp, metadata=spe.meta)
                    )
        self.send_outputs()

    def custom_plot(self, ax):
        if self.show_original:
            for spe in self.in_spe:
                spe.trim_axes(method="x-axis", boundaries=(self.xmin, self.xmax)).plot(ax=ax, label='original')
        ax.legend()
