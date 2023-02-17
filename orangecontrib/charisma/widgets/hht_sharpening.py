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


class HHT_Sharpening(RC2_Filter):
    name = "HHT Sharpening"
    description = "hht sharpening"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.window_size = 100
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self, spe):
        return spe.hht_sharpening(movmin=self.window_size)

