from Orange.data import Table
from Orange.widgets import gui
from Orange.widgets.widget import OWBaseWidget, Output
from Orange.data.pandas_compat import table_from_frame

from AnyQt.QtWidgets import QSizePolicy
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

from .types import RC2Spectra


class BaseWidget(OWBaseWidget, openclass=True):
    resizing_enabled = True
    priority = 10

    def __init__(self):
        super().__init__()
        self.in_spe = RC2Spectra()
        self.should_auto_plot = False
        self.should_auto_proc = True
        self.should_pass_datatable = False
        self.figure = None
        self.is_processed = False
        self.controlArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.optionsBox = gui.widgetBox(self.controlArea, "Main Options")
        self.optionsBox.setDisabled(False)
        self.should_auto_plot_checkbox = gui.checkBox(self.optionsBox, self, "should_auto_plot", "Auto update plot",
                                                      stateWhenDisabled=False, callback=self.force_plot)
        pass_datatable = gui.checkBox(self.optionsBox, self, "should_pass_datatable", "Pass datatable",
                                      stateWhenDisabled=False, callback=self.process)
        gui.checkBox(self.optionsBox, self, "should_auto_proc", "Auto process",
                     disables=[self.should_auto_plot_checkbox, pass_datatable])
        gui.button(self.optionsBox, self, "Process", callback=self.process)
        gui.button(self.optionsBox, self, "Plot", callback=self.force_plot)

    class Outputs:
        out_spe = Output("RC2Spectra", RC2Spectra, default=True)
        data = Output("Data", Table, default=False)

    def force_plot(self):
        if not self.is_processed:
            self.process()
            self.is_processed = True
        self.plot_spe()

    def plot_create_axes(self):
        return self.figure.add_subplot(111)

    def plot_spe(self):
        if self.figure is None:
            self.figure = plt.figure(tight_layout=True)
            self.canvas = FigureCanvas(self.figure)
            self.toolbar = NavigationToolbar(self.canvas, self)
            self.mainArea.layout().addWidget(self.toolbar)
            self.mainArea.layout().addWidget(self.canvas)
        for ax in self.figure.axes:
            self.figure.delaxes(ax)
        ax = self.plot_create_axes()
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

    def process(self):
        self.is_processed = True

    def auto_process(self):
        self.is_processed = False
        if self.should_auto_proc:
            self.process()
            self.is_processed = True
            if self.should_auto_plot:
                self.plot_spe()
