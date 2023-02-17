from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, OWBaseWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle
from .rc2_base import RC2_Arithmetics
import matplotlib.pyplot as plt


class Subtract(RC2_Arithmetics):
    name = "Subtract"
    description = "subtract spectra"
    icon = "icons/spectra.svg"


    class Inputs:
        minuend = Input("Minuend (rc2.Spectrum)", rc2.spectrum.Spectrum)
        subtrahend = Input("Subtrahend (rc2.Spectrum)", rc2.spectrum.Spectrum)

    @Inputs.minuend
    def set_minuend(self, spe):
        if spe:
            self.minuend = spe
        else:
            self.minuend = None
        if self.commitOnChange and self.minuend and self.subtrahend:
            self.commit()

    @Inputs.subtrahend
    def set_subtrahend(self, spe):
        if spe:
            self.subtrahend = spe
        else:
            self.subtrahend = None
        if self.commitOnChange and self.minuend and self.subtrahend:
            self.commit()

    def __init__(self):
        super().__init__()
        self.minuend = None
        self.subtrahend = None

    def process(self, spe):
        self.out_spe = self.minuend - self.subtrahend
