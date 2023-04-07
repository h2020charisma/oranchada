import pandas as pd
from Orange.data import Table
from Orange.data.pandas_compat import table_from_frame
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output
from ramanchada2.misc.types.fit_peaks_result import FitPeaksResult
from ramanchada2.spectrum.peaks.fit_peaks import available_models

from ..base_widget import FilterWidget


class Fit(FilterWidget):
    name = "Fit Peaks"
    description = "Fit Peaks"
    icon = "icons/spectra.svg"

    should_fit = Setting(True)
    vary_baseline = Setting(False)
    peak_profile = Setting(available_models[0])
    plot_individual_peaks = Setting(False)
    should_auto_proc = Setting(False)

    class Outputs(FilterWidget.Outputs):
        peaks_out = Output("Peaks", Table, default=False)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)

        gui.checkBox(box, self, "should_fit", "Perform fit", callback=self.auto_process)
        gui.checkBox(box, self, "plot_individual_peaks", "Plot individual peaks", callback=self.auto_process)
        gui.checkBox(box, self, "vary_baseline", "Vary baseline", callback=self.auto_process)
        gui.comboBox(box, self, 'peak_profile', sendSelectedValue=True, items=available_models,
                     callback=self.auto_process)

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.fit_peaks_filter(profile=self.peak_profile, no_fit=not self.should_fit,
                                     vary_baseline=self.vary_baseline)
            )
        self.send_outputs()
        dfs = [FitPeaksResult.loads(spe.result).to_dataframe_peaks() for spe in self.out_spe]
        self.Outputs.peaks_out.send(table_from_frame(pd.concat(dfs)))

    def custom_plot(self, ax):
        if self.plot_individual_peaks:
            peaks_ax = ax.twinx()
        else:
            peaks_ax = ax
        for spe in self.out_spe:
            FitPeaksResult.loads(spe.result).plot(peaks_ax, individual_peaks=self.plot_individual_peaks)
