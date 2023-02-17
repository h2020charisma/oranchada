from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, OWBaseWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle
import matplotlib.pyplot as plt
from abc import ABC, ABCMeta, abstractmethod


import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QVBoxLayout, QSizePolicy, QMessageBox, QWidget, QPushButton, QGridLayout

from Orange.widgets import widget
from AnyQt.QtWidgets import QVBoxLayout
from typing import List

from collections import UserList

class RC2Spectra(UserList):
    pass


class RC2_Base(OWBaseWidget):
    resizing_enabled = True
    priority = 10

    def __init__(self):
        super().__init__()
        self.in_spe = None
        self.select_inputs_idx = None
        self.should_auto_plot = False
        self.should_auto_proc = True
        self.figure = None
        self.controlArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.optionsBox = gui.widgetBox(self.controlArea, "Main Options")
        self.optionsBox.setDisabled(False)
        self.should_auto_plot_checkbox = gui.checkBox(self.optionsBox, self, "should_auto_plot", "Auto update plot", stateWhenDisabled=False)
        gui.checkBox(self.optionsBox, self, "should_auto_proc", "Auto process", disables=self.should_auto_plot_checkbox)
        gui.button(self.optionsBox, self, "Process", callback=self.force_process)
        gui.button(self.optionsBox, self, "Plot", callback=self.force_plot)

    class Outputs:
        out_spe = Output("RC2Spectra", RC2Spectra, default=True)
        data = Output("Data", Table, default=False)

    def force_plot(self):
        self.force_process()
        self.plot_spe()

    def plot_spe(self):
        if self.figure is None:
            self.figure = plt.figure(tight_layout=True)
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.mainArea.layout().addWidget(self.toolbar)
            self.mainArea.layout().addWidget(self.canvas)
        for ax in self.figure.axes:
            self.figure.delaxes(ax)
        ax = self.figure.add_subplot(111)
        for spe in self.out_spe:
            spe.plot(ax=ax)
        self.canvas.draw()

    def send_outputs(self):
        self.Outputs.out_spe.send(self.out_spe)
        #out_data = Table.from_numpy(Domain([ContinuousVariable.make(f'{i}') for i in self.out_spe.x]), [self.out_spe.y])
        #self.Outputs.data.send(out_data)

    def process(self, spe):
        pass

    def force_process(self):
        self.out_spe = RC2Spectra()
        if self.select_inputs_idx is not None:
            for i in self.select_inputs_idx:
                self.out_spe.append(self.process(self.in_spe[i]))
        else:
            for spe in self.in_spe:
                self.out_spe.append(self.process(spe))
        self.send_outputs()

    def auto_process(self):
        if self.should_auto_proc:
            self.force_process()
            if self.should_auto_plot:
                self.plot_spe()


class RC2_Creator(RC2_Base):
    def __init__(self):
        super().__init__()

    def force_process(self):
        self.out_spe = self.multi_process()
        #self.out_spe = None
        #self.out_spe = self.process([None])
        self.send_outputs()


class RC2_Filter(RC2_Base):
    def input_hook(self):
        pass

    class Inputs:
        in_spe = Input("RC2Spectra", RC2Spectra)

    @Inputs.in_spe
    def set_in_spe(self, spe):
        self.should_auto_plot= False
        if spe:
            self.in_spe = spe
            self.auto_process()
        else:
            #self.in_spe = None
            self.in_spe = RC2Spectra()
        self.input_hook()

class RC2_Arithmetics(RC2_Base):
    pass
