from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

class ProcessSpectraWidget:  # (OWWidget):
    # Define the widget's name, category, and outputs
    name = "Process Spectra"
    description = "Process spectra provided as Orange data table"
    icon = "icons/spectra.svg"
    priority = 10
    # want_main_area = False
    # resizing_enabled = False
    # proportion = Setting(50)
    commitOnChange = Setting(0)
    # label = Setting("")

    class Inputs:
        # specify the name of the input and the type
        data = Input("Data", Table)

    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data = Output("Processed Data", Table, default=True)
        peaks = Output("Peaks", Table, default=False)
        model = Output("Model", Table, default=False)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    class Error(OWWidget.Error):
        processing_error = Msg("Processing error(s).")

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.data = None
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.checkBox(
            self.optionsBox, self, "commitOnChange", "Commit data on selection change"
        )
        gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        self.optionsBox.setDisabled(False)

        # logging.warning('warning')
        # logging.error('error')
        # logging.exception('exp')

    @Inputs.data
    def set_data(self, data):
        self.Error.processing_error.clear()
        if data:
            self.data = data
        else:
            self.data = None

    def commit(self):
        processed_data, peaks, peaks_data = self.process_data()
        self.Outputs.data.send(processed_data)
        self.Outputs.peaks.send(peaks)
        self.Outputs.model.send(peaks_data)

    def send_report(self):
        # self.report_plot() includes visualizations in the report
        # self.report_caption(self.label)
        pass

    def find_peaks(self, spe, index, moving_minimum_window=None):
        bgm = spe.bayesian_gaussian_mixture(
            n_samples=20000,
            n_components=20,
            max_iter=1000,
            moving_minimum_window=moving_minimum_window,
            random_state=42,
            # trim_range=trim_range
            )
        bgm_peaks = [[mean[0], np.sqrt(cov[0][0]), weight, i]
                     for mean, cov, weight, i in
                     zip(bgm.means_, bgm.covariances_, bgm.weights_, cycle([index]))]
        bgm_peaks = sorted(bgm_peaks, key=lambda x: x[2], reverse=True)
        n_peaks = (np.round(bgm.weights_, 2) > 0).sum()
        bgm_peaks = bgm_peaks[:n_peaks]
        return bgm, bgm_peaks

    def peaks2table(self, peaks):
        attrs = [ContinuousVariable("mean"), ContinuousVariable("sigma"),
                 ContinuousVariable("weight"), ContinuousVariable("index")]
        log.info(peaks)
        return Table.from_numpy(Domain(attrs), peaks)

    def bgm2spe(self, x, bgm_peaks, threshold=300):
        import scipy.stats as stats
        spey = None
        for peak in bgm_peaks:
            if peak[1] < threshold:
                continue
            gm = stats.norm(peak[0], peak[1])
            tmp = peak[2]*gm.pdf(x)
            if spey is None:
                spey = tmp
            else:
                spey = spey + tmp
        return spey

    def process_data(self):
        x = np.array([float(a.name) for a in self.data.domain.attributes])
        domain = None
        table_processed = self.data
        table_peaks = None
        peaks = []
        try:
            n_rows = self.data.X.shape[0]
            for i in np.arange(0, n_rows):
                spe = Spectrum(x=x, y=self.data[i].x)
                spe1 = spe.trim_axes(method='x-axis', boundaries=(140, np.max(x)))
                log.info(len(spe1.x))
                if domain is None:
                    attrs = [ContinuousVariable.make("%f" % f, number_of_decimals=1) for f in spe1.x]
                    domain = Domain(attrs, class_vars=self.data.domain.class_vars,
                                    metas=self.data.domain.metas)
                    table_processed = Table.from_table(domain, self.data)
                    attrs1 = [ContinuousVariable.make("%f" % f, number_of_decimals=1) for f in spe1.x]
                    domain1 = Domain(attrs1)
                    table_peaks = Table.from_domain(domain1, n_rows=n_rows)
                bgm, bgm_peaks = self.find_peaks(spe1, i, moving_minimum_window=50)
                peaks.extend(bgm_peaks)
                y_bgm = self.bgm2spe(spe1.x, bgm_peaks, threshold=0)

                # log.debug(max(spe1.y))
                # spe1 = spe1.subtract_moving_minimum(50)
                spe1 = spe1.hht_sharpening(movmin=50)
                spe1 = spe1.normalize('unity_area')
                # print(cand)
                inst = table_processed[i]
                log.info("{} {} {} {}".format(len(spe1.x), len(spe1.y), len(y_bgm), len(inst.x)))
                inst.x[:] = spe1.y
                inst1 = table_peaks[i]
                inst1.x[:] = y_bgm
                # inst.x[:]=spe1.y[:]

            return table_processed, self.peaks2table(peaks), table_peaks
        except Exception as err:
            log.exception(err)
            # self.Error(str(err))
            # raise Exception
        return None, None, None


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from Orange.data import Table
    import os
    try:
        log.info(os.getcwdb())
        path = r'../datasets/PST_WiICV532_Z005OP02_005_300msx10.txt'
        # with open(path, "r") as f:
        #     data = f.read()
        log.warning('start')
        # no reader!
        # table = Table.from_file(path)
        data = Table("../datasets/collagen.csv")

        # Send the data table to the output
        WidgetPreview(ProcessSpectraWidget).run(set_data=Table.from_table_rows(data, [0, 1]))
    except Exception as err:
        print(err)
        WidgetPreview(ProcessSpectraWidget).run()
