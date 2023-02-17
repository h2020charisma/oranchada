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


class MovingMinimum(RC2_Filter):
    name = "Moving minimum"
    description = "moving minimum"
    icon = "icons/spectra.svg"

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.window_size = 10
        box = gui.widgetBox(self.controlArea, self.name)
        gui.spin(box, self, 'window_size', 0, 5000, callback=self.auto_process)

    def process(self, spe):
        return spe.moving_minimum(self.window_size)

