from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra
from ramanchada2.misc.types.peak_candidates import ListPeakCandidateMultiModel


class FindPeaks(RC2_Filter):
    name = "Find Peaks"
    description = "Find Peaks"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.prominence_val = .02
        self.hht_chain_str = '80 20'
        self.manual_prominence = True
        self.is_sharpening_enabled = True
        self.prominence_val_spin = gui.doubleSpin(box, self, 'prominence_val', 0, 100, decimals=5,
                                                  label='Prominence', step=.001, callback=self.auto_process)

        gui.checkBox(box, self, "manual_prominence", "Manual Prominence", callback=self.auto_process,
                     stateWhenDisabled=False, disables=self.prominence_val_spin)

        self.hht_chain_edit = gui.lineEdit(box, self, 'hht_chain_str', label='HHT Chain', callback=self.auto_process)
        gui.checkBox(box, self, "is_sharpening_enabled", "Enable shaprening", callback=self.auto_process,
                     stateWhenDisabled=False, disables=self.hht_chain_edit)
        self.is_sharpening_enabled = False
        self.manual_prominence = False

        self.wlen = 50
        self.min_peak_width = 1
        gui.spin(box, self, 'wlen', 1, 5000, callback=self.auto_process, label='Window length')
        gui.spin(box, self, 'min_peak_width', 1, 5000, callback=self.auto_process, label='Min peak width')

    def process(self):
        hht_chain = [int(i) for i in self.hht_chain_str.split()]
        self.hht_chain_str = ' '.join([str(i) for i in hht_chain])
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.find_peak_multipeak_filter(
                    wlen=self.wlen,
                    width=self.min_peak_width,
                    hht_chain=hht_chain,
                    sharpening=('hht' if self.is_sharpening_enabled else None),
                    prominence=(self.prominence_val if self.manual_prominence else None))
                )
        self.send_outputs()

    def custom_plot(self, ax):
        for spe in self.out_spe:
            ListPeakCandidateMultiModel.validate(spe.result).plot(ax)
