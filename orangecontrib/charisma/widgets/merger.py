from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, OWBaseWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle
from .rc2_base import RC2_Base, RC2Spectra
import matplotlib.pyplot as plt

from AnyQt.QtWidgets import QAbstractItemView

class Merger(RC2_Base):
    name = "Merger"
    description = "merge spectra"
    icon = "icons/spectra.svg"

    def __init__(self):
        self.in_spe_dict = dict()
        super().__init__()

    def input_hook(self):
        while self.select_box.takeItem(0):
            pass
        for spe_i, spe in enumerate(self.in_spe):
            self.select_box.addItem(f'{spe_i}: {spe!r}')

    class Inputs:
        in_spe = Input("RC2Spectra", RC2Spectra, multiple=True)

    @Inputs.in_spe
    def set_in_spe(self, spe, id_):
        self.should_auto_plot= False
        if id_ in self.in_spe_dict:
            if spe is None:
                del self.in_spe_dict[id_]
            else:
                self.in_spe_dict[id_] = spe
        else:
            self.in_spe_dict[id_] = spe

        if self.in_spe_dict:
            self.auto_process()

    def force_process(self):
        self.out_spe = RC2Spectra()
        for id_, spes in self.in_spe_dict.items():
            self.out_spe.extend(spes)
        self.send_outputs()

