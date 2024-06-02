from Orange.widgets import gui
from Orange.widgets.settings import Setting
from ramanchada2.misc.types.peak_candidates import ListPeakCandidateMultiModel

from ..base_widget import FilterWidget


class FindPeaks(FilterWidget):
    name = "Find Peaks"
    description = "Find Peaks"
    icon = "icons/spectra.svg"

    prominence_val = Setting(5)
    hht_chain_str = Setting('80 20')
    is_sharpening_enabled = Setting(True)
    wlen = Setting(200)
    min_peak_width = Setting(2)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.hht_chain_edit = gui.lineEdit(box, self, 'hht_chain_str', label='HHT Chain', callback=self.auto_process)
        gui.checkBox(box, self, "is_sharpening_enabled", "Enable sharpening", callback=self.auto_process,
                     stateWhenDisabled=False, disables=self.hht_chain_edit)
        self.is_sharpening_enabled = False

        self.prominence_val_spin = gui.doubleSpin(box, self, 'prominence_val', 0, 1000, decimals=2,
                                                  label='Prominence [×σ]', step=.5, callback=self.auto_process)
        gui.spin(box, self, 'wlen', 1, 5000, step=20, callback=self.auto_process, label='Window length')
        gui.spin(box, self, 'min_peak_width', 1, 5000, callback=self.auto_process, label='Min peak width')

    def process(self):
        hht_chain = [int(i) for i in self.hht_chain_str.split()]
        self.hht_chain_str = ' '.join([str(i) for i in hht_chain])
        self.out_spe = list()
        for spe in self.in_spe:
            prominence = spe.y_noise * self.prominence_val
            self.out_spe.append(
                spe.find_peak_multipeak_filter(
                    wlen=self.wlen,
                    width=self.min_peak_width,
                    hht_chain=hht_chain,
                    sharpening=('hht' if self.is_sharpening_enabled else None),
                    prominence=prominence)
                )
        self.send_outputs()

    def custom_plot(self, ax):
        for spe in self.out_spe:
            ListPeakCandidateMultiModel.validate(spe.result).plot(ax)
