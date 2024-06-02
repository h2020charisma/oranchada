import pandas as pd
from Orange.data import Table
from Orange.data.pandas_compat import table_from_frame
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output
from PyQt5.QtCore import QEventLoop, QThread, pyqtSignal
from ramanchada2.misc.types.fit_peaks_result import FitPeaksResult
from ramanchada2.spectrum.peaks.fit_peaks import available_models

from ..base_widget import FilterWidget


class FitterThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, in_spe, peak_profile, should_fit, vary_baseline):
        super().__init__()
        self.in_spe = in_spe
        self.peak_profile = peak_profile
        self.should_fit = should_fit
        self.vary_baseline = vary_baseline
        self.should_break = [False]
        self.setPriority(QThread.LowestPriority)

    def stop(self):
        self.should_break[0] = True

    def run(self):
        self.should_break[0] = False
        out_spe = []
        for spe in self.in_spe:
            out_spe.append(
                spe.fit_peaks_filter(profile=self.peak_profile,
                                     no_fit=not self.should_fit,
                                     vary_baseline=self.vary_baseline,
                                     should_break=self.should_break)
            )
        if self.should_break[0]:
            self.finished.emit([])
        else:
            self.finished.emit(out_spe)


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
        self.stop_processing_btn = gui.button(box, self, "Kill fitting", callback=self.break_fit)

    def break_fit(self):
        self.thread.stop()
        self.is_processed = False

    def on_calculation_finished(self, result):
        self.out_spe = result
        self.process_btn.setDisabled(False)
        self.stop_processing_btn.setDisabled(True)
        dfs = []
        for spe in self.out_spe:
            df = FitPeaksResult.loads(spe.result).to_dataframe_peaks()
            fn = pd.Series([spe.meta['Original file']]*len(df))
            fn.index = df.index
            df['filename'] = fn
            dfs.append(df)
        if self.out_spe:
            self.Outputs.peaks_out.send(table_from_frame(pd.concat(dfs)))
            self.send_outputs()

    def onDeleteWidget(self):
        if self.thread and self.thread.isRunning():
            self.thread.terminate()
            self.thread.wait()

    def perform_threaded_fit(self):
        self.process_btn.setDisabled(True)
        self.stop_processing_btn.setDisabled(False)
        self.thread = FitterThread(in_spe=self.in_spe,
                                   peak_profile=self.peak_profile,
                                   should_fit=self.should_fit,
                                   vary_baseline=self.vary_baseline,
                                   )
        self.thread.finished.connect(self.on_calculation_finished)
        self.event_loop = QEventLoop()
        self.thread.finished.connect(self.event_loop.exit)
        self.thread.start()
        self.event_loop.exec_()

    def process(self):
        self.perform_threaded_fit()

    def custom_plot(self, ax):
        if self.plot_individual_peaks:
            peaks_ax = ax.twinx()
        else:
            peaks_ax = ax
        for spe in self.out_spe:
            FitPeaksResult.loads(spe.result).plot(peaks_ax, individual_peaks=self.plot_individual_peaks)
