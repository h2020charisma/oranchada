from Orange.widgets import gui
import ramanchada2 as rc2
import numpy as np
from .rc2_base import RC2_Creator


class GenSpe(RC2_Creator):
    name = "Gen Spectra"
    description = "gen spectra"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.data = None
        self.deltas = '620.9: 16, 795.8: 10, 1001.4: 100, 1031.8: 27, 1155.3: 13, 1450.5: 8, 1583.1: 12, 1602.3: 28, 2852.4: 9, 2904.5: 13, 3054.3: 32'  # noqa: E501
        self.spe_xmin = 0
        self.spe_xmax = 2000
        self.spe_nbins = 1500
        self.n_spectra = 1
        box = gui.widgetBox(self.controlArea, self.name)
        self.predefined_spe = 'PST'
        gui.comboBox(box, self, 'predefined_spe', sendSelectedValue=True, items=['PST', 'User defined'],
                     callback=self.set_deltas)
        self.deltas_edit = gui.lineEdit(box, self, 'deltas', label='Deltas', callback=self.auto_process)
        gui.spin(box, self, 'spe_xmin', -1000, 10000, label='xmin', callback=self.auto_process)
        gui.spin(box, self, 'spe_xmax', -1000, 10000, label='xmax', callback=self.auto_process)
        gui.spin(box, self, 'spe_nbins', 1, 200000, label='n_bins', callback=self.auto_process)
        gui.spin(box, self, 'n_spectra', 1, 50, label='Number of spectra', callback=self.auto_process)
        self.auto_process()

    def set_deltas(self):
        if self.predefined_spe == 'User defined':
            self.deltas_edit.setReadOnly(False)
        else:
            self.deltas = '620.9: 16, 795.8: 10, 1001.4: 100, 1031.8: 27, 1155.3: 13, 1450.5: 8, 1583.1: 12, 1602.3: 28, 2852.4: 9, 2904.5: 13, 3054.3: 32'  # noqa: E501
            self.deltas_edit.setReadOnly(True)
        self.auto_process()

    def process(self):
        deltas_dict = dict([[float(j) for j in i.split(':')] for i in self.deltas.replace(' ', '').split(',')])
        spe1 = rc2.spectrum.Spectrum(x=np.array(list(deltas_dict.keys())), y=np.array(list(deltas_dict.values())))
        self.out_spe = [
            spe1.resample_NUDFT_filter(x_range=(self.spe_xmin, self.spe_xmax), xnew_bins=self.spe_nbins)
            ] * self.n_spectra
        self.send_outputs()
