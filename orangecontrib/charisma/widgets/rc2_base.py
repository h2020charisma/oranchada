from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.widget import OWBaseWidget, Input, Output
from Orange.data.pandas_compat import table_from_frame
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from AnyQt.QtWidgets import QSizePolicy

from collections import UserList


class RC2Spectra(UserList):
    pass


class RC2_Base(OWBaseWidget, openclass=True):
    resizing_enabled = True
    priority = 10

    def __init__(self):
        super().__init__()
        self.in_spe = RC2Spectra()
        self.select_inputs_idx = None
        self.should_auto_plot = False
        self.should_auto_proc = True
        self.should_pass_datatable = False
        self.figure = None
        self.controlArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.optionsBox = gui.widgetBox(self.controlArea, "Main Options")
        self.optionsBox.setDisabled(False)
        self.should_auto_plot_checkbox = gui.checkBox(self.optionsBox, self, "should_auto_plot", "Auto update plot",
                                                      stateWhenDisabled=False, callback=self.force_plot)
        pass_datatable = gui.checkBox(self.optionsBox, self, "should_pass_datatable", "Pass datatable",
                                      stateWhenDisabled=False, callback=self.force_process)
        gui.checkBox(self.optionsBox, self, "should_auto_proc", "Auto process",
                     disables=[self.should_auto_plot_checkbox, pass_datatable])
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
            spe.plot(ax=ax, label=f'id(spe)={id(spe)}')
        self.custom_plot(ax)
        self.canvas.draw()

    def custom_plot(self, ax):
        pass

    def send_outputs(self):
        self.Outputs.out_spe.send(self.out_spe)
        if self.should_pass_datatable:
            df = pd.DataFrame([pd.Series(index=spe.x, data=spe.y) for spe in self.out_spe])
            df = df.sort_index(axis='columns')
            df.columns = [f'{i}' for i in df.columns]
            self.Outputs.data.send(table_from_frame(df))

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


class RC2_Creator(RC2_Base, openclass=True):
    def __init__(self):
        super().__init__()
        self.in_spe = RC2Spectra()

    def force_process(self):
        self.out_spe = self.multi_process()
        self.send_outputs()


class RC2_Filter(RC2_Base, openclass=True):
    def input_hook(self):
        pass

    class Inputs:
        in_spe = Input("RC2Spectra", RC2Spectra)

    @Inputs.in_spe
    def set_in_spe(self, spe):
        self.should_auto_plot = False
        if spe:
            self.in_spe = spe
            self.auto_process()
        else:
            self.in_spe = RC2Spectra()
        self.input_hook()


class RC2_Arithmetics(RC2_Base, openclass=True):
    pass
