from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, OWBaseWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle
from .rc2_base import RC2_Filter
import matplotlib.pyplot as plt
from scipy import signal


class Resample_NUDFT(RC2_Filter):
    name = "Resample NUDFT"
    description = "Resample Non-Uniform Discrete Fourier Transform"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.xmin = 0
        self.xmax = 4000
        self.nbins = 100
        self.window_function = 'blackmanharris'
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



    def process(self, spe):
        return spe.resample_NUDFT_filter(x_range=(self.xmin, self.xmax), xnew_bins=self.nbins, window=getattr(signal.windows, self.window_function))

