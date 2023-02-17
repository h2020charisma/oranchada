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


class AddNoise(RC2_Filter):
    name = "Add Noise"
    description = "add noise"
    icon = "icons/spectra.svg"

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.noise_scale = .01
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'noise_scale', 0, 100, decimals=5, step=.001, callback=self.auto_process)

    def process(self, spe):
        return spe.add_poisson_noise(self.noise_scale)
