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

from AnyQt.QtWidgets import QAbstractItemView

class Select(RC2_Filter):
    name = "Select"
    description = "select spectra"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()

        box = gui.widgetBox(self.controlArea, self.name)
        self.select_box = gui.listBox(box, self, 'select_inputs_idx', selectionMode=QAbstractItemView.MultiSelection, callback=self.auto_process)

    def input_hook(self):
        while self.select_box.takeItem(0):
            pass
        for spe_i, spe in enumerate(self.in_spe):
            self.select_box.addItem(f'{spe_i}: {spe!r}')

    def process(self, spe):
        return spe

