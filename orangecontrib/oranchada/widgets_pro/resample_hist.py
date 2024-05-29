from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg
from scipy import signal
import numpy as np
from ramanchada2.spectrum import Spectrum

from ..base_widget import FilterWidget


class Resample_density(FilterWidget):
    name = "Resample"
    description = "Resample using density"
    icon = "icons/spectra.svg"

    xmin = Setting(100)
    xmax = Setting(3600)
    npoints = Setting(3500)
    window_function = Setting('blackmanharris')

    class Warning(FilterWidget.Warning):
        range = Msg('x-min should be less that x-max')

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'xmin', -1000, 10000, callback=self.auto_process, label='x-min')
        gui.spin(box, self, 'xmax', -1000, 10000, callback=self.auto_process, label='x-max')
        gui.spin(box, self, 'npoints', 1, 10000, callback=self.auto_process, label='npoints')
        

    def process(self):
        self.Warning.clear()
        self.out_spe = list()
        
        for spe in self.in_spe:
            if self.xmin > self.xmax:
                self.Warning.range()
            else:
                dist = spe.spe_distribution(trim_range=(self.xmin, self.xmax))
                x_values = np.linspace(self.xmin, self.xmax, self.npoints)
                #resample using probability density function
                y_values = dist.pdf(x_values)
                scale = np.max(spe.y) / np.max(y_values)
                 # pdf sampling is normalized to area unity, scaling back
                _tmp = y_values *  scale
                self.out_spe.append(
                    Spectrum(x_values,_tmp,metadata=spe.meta)
                    )
        self.send_outputs()


    def custom_plot(self, ax):
        for spe in self.in_spe:
            spe.trim_axes(method="x-axis",boundaries=(self.xmin, self.xmax)).plot(ax=ax,label='original') 
        ax.legend()
