from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg
from scipy import signal

from ..base_widget import FilterWidget


class Resample_NUDFT(FilterWidget):
    name = "Resample NUDFT"
    description = "Resample Non-Uniform Discrete Fourier Transform"
    icon = "icons/spectra.svg"

    xmin = Setting(0)
    xmax = Setting(4000)
    nbins = Setting(100)
    window_function = Setting('blackmanharris')

    class Warning(FilterWidget.Warning):
        small_boundaries = Msg('Provided spectra exceed x-min/x-max limits')

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'xmin', -1000, 10000, callback=self.auto_process, label='x-min')
        gui.spin(box, self, 'xmax', -1000, 10000, callback=self.auto_process, label='x-max')
        gui.spin(box, self, 'nbins', 1, 10000, callback=self.auto_process, label='n-bins')
        gui.comboBox(box, self, 'window_function', label='window', sendSelectedValue=True,
                     items=['barthann',
                            'bartlett',
                            'blackman',
                            'blackmanharris',
                            'bohman',
                            'boxcar',
                            'hamming',
                            'hann',
                            'nuttall',
                            'parzen',
                            'triang',
                            ], callback=self.auto_process)

    def process(self):
        self.Warning.clear()
        self.out_spe = list()
        for spe in self.in_spe:
            if self.xmin > spe.x.min() or self.xmax < spe.x.max():
                self.Warning.small_boundaries()
            self.out_spe.append(
                spe.resample_NUDFT_filter(x_range=(self.xmin, self.xmax), xnew_bins=self.nbins,
                                          window=getattr(signal.windows, self.window_function))
                )
        self.send_outputs()

    def custom_plot(self, ax):
        for spe in self.in_spe:
            spe.trim_axes(method="x-axis",boundaries=(self.xmin, self.xmax)).plot(ax=ax,label='original') 
        ax.legend()