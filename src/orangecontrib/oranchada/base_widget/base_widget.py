import matplotlib.pyplot as plt
import pandas as pd
from AnyQt.QtWidgets import QSizePolicy
from matplotlib.backends.backend_qt5agg import \
    FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import \
    NavigationToolbar2QT as NavigationToolbar
from Orange.data import Table, Domain, ContinuousVariable, Table,StringVariable,DiscreteVariable

from Orange.data.pandas_compat import table_from_frame
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Msg, Output, OWBaseWidget, OWWidget

from .types import RC2Spectra


class BaseWidget(OWBaseWidget, openclass=True):
    resizing_enabled = True
    priority = 10

    should_auto_plot = Setting(False)
    should_auto_proc = Setting(True)
    should_pass_datatable = Setting(False)
    should_plot_legend = Setting(True)

    class Warning(OWWidget.Warning):
        different_x_labels = Msg('When multiple spectra are provided they are expected to have same xlabel')

    def __init__(self):
        super().__init__()
        self.info.set_input_summary(self.info.NoInput)
        self.info.set_output_summary(self.info.NoOutput)
        self.in_spe = RC2Spectra()
        self.figure = None
        self.is_processed = False
        self.controlArea.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        self.optionsBox = gui.widgetBox(self.controlArea, "Main Options")
        self.optionsBox.setDisabled(False)
        self.should_auto_plot_checkbox = gui.checkBox(self.optionsBox, self, "should_auto_plot", "Auto update plot",
                                                      stateWhenDisabled=False, callback=self.force_plot)
        gui.checkBox(self.optionsBox, self, "should_pass_datatable", "Pass datatable",
                     stateWhenDisabled=False, callback=self.process)
        gui.checkBox(self.optionsBox, self, "should_auto_proc", "Auto process",
                     disables=[self.should_auto_plot_checkbox])
        self.process_btn = gui.button(self.optionsBox, self, "Process", callback=self.process)
        gui.button(self.optionsBox, self, "Plot", callback=self.force_plot)
        gui.checkBox(self.optionsBox, self, "should_plot_legend", "Plot legend", callback=self.auto_process)

    class Outputs:
        out_spe = Output("RC2Spectra", RC2Spectra, default=True, auto_summary=False)
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
            self.mainArea.layout().insertWidget(0, self.canvas)
            self.toolbar = None
        for a in self.figure.axes:
            self.figure.delaxes(a)
        ax = self.plot_create_axes()
        for spe in self.out_spe:
            spe.plot(ax=ax, label=f'id(spe)={id(spe)}')
        self.set_x_title(ax)
        self.custom_plot(ax)
        if self.should_plot_legend:
            ax.legend(fontsize='x-small', ncols=2)
        else:
            ax.legend([])
        if self.toolbar:
            self.toolbar.setParent(None)
            self.toolbar.destroy()
        self.toolbar = NavigationToolbar(self.canvas, self, coordinates=True)
        self.mainArea.layout().insertWidget(0, self.toolbar)
        self.figure.set_tight_layout(True)
        self.canvas.draw()

    def custom_plot(self, ax):
        pass

    def set_x_title(self, ax):
        xlab = ''
        for spe in reversed(self.out_spe):
            if 'xlabel' in spe.meta.root:
                xlab = spe.meta['xlabel']
        if not xlab:
            return
        should_warn = False
        for spe in self.out_spe:
            if 'xlabel' in spe.meta.root:
                if xlab != spe.meta['xlabel']:
                    should_warn = True
            else:
                should_warn = True
        if should_warn:
            self.Warning.different_x_labels()
        ax.set_xlabel(xlab)

    def output_table_old(self):
        # has no metadata
        df = pd.DataFrame([pd.Series(index=spe.x, data=spe.y) for spe in self.out_spe])
        df = df.sort_index(axis='columns')
        df.columns = [f'{i}' for i in df.columns]
        return table_from_frame(df)

    def send_output_table(self):
        if self.should_pass_datatable:
            if self.out_spe:
                try:
                    self.Outputs.data.send(self.output_table_domain())
                except:  # just in case the new implementation breaks
                    self.Outputs.data.send(self.output_table_old())

    def output_table_domain(self):

        # Extract unique x values from all spectra
        unique_x_values = sorted(set(x for spe in self.out_spe for x in spe.x))
        # Extract metadata keys
        all_meta_keys = set()
        for spe in self.out_spe:
            all_meta_keys.update(spe.meta.get_all_keys())

            # Create Orange Table Domain
            domain_variables = [ContinuousVariable(str(x)) for x in unique_x_values]
            meta_variables = [StringVariable(key) for key in all_meta_keys]
            domain = Domain(domain_variables, metas=meta_variables)
            data = []
            for spe in self.out_spe:
                row_data = [None] * len(unique_x_values)  # Initialize row data with None
                for x, y in zip(spe.x, spe.y):
                    column_index = unique_x_values.index(x)
                    row_data[column_index] = y
                meta_values = []
                for key in all_meta_keys:
                    if key in spe.meta.root:
                        meta_values.append(spe.meta[key])
                    else:
                        meta_values.append(None)
                data.append(row_data + meta_values)

            return Table.from_list(domain, data)

    def send_outputs(self):
        if self.out_spe:
            self.Outputs.out_spe.send(self.out_spe)
            self.send_output_table()
            self.info.set_output_summary(f'{len(self.out_spe)} RC2Spectra',
                                         '\n'.join([f'· {repr(i)}' for i in self.out_spe]))
        else:
            self.info.set_output_summary(self.info.NoOutput)

    def process(self):
        self.is_processed = True

    def auto_process(self):
        self.is_processed = False
        if self.should_auto_proc:
            self.process()
            self.is_processed = True
            if self.should_auto_plot:
                self.plot_spe()
