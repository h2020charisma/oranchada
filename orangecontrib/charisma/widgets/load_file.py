from Orange.widgets import gui
import ramanchada2 as rc2
from .rc2_base import RC2_Creator
from AnyQt.QtWidgets import QFileDialog


class LoadFile(RC2_Creator):
    name = "Load File"
    description = "Load spectrum from file"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.filenames = list()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Load File", callback=self.load_file)
        self.fileformat = 'txt'
        self.backend = 'native'
        gui.comboBox(box, self, 'fileformat', sendSelectedValue=True,
                     items=['txt', 'csv'], label='File format')
        gui.comboBox(box, self, 'backend', sendSelectedValue=True,
                     items=['native', 'ramanchada_parser'], label='Backend')

    def load_file(self):
        filters = ['TXT (*.txt)',
                   'CSV (*.csv)',
                   'All spectra formats (*.txt *.csv)',
                   'All files (*)',
                   ]
        filenames, filt = QFileDialog.getOpenFileNames(
            caption='Open spectra',
            directory='/data/RamanSpe/FNMT-Madrid/Horiba_785nm/PST/PST10_iR785_OP02_8000msx8_01.txt',
            filter=';;'.join(filters),
            initialFilter=filters[-2],
            )
        if filenames:
            self.filenames = filenames
            self.auto_process()

    def process(self):
        self.out_spe = [
            rc2.spectrum.from_local_file(fname, filetype=self.fileformat, backend=self.backend)
            for fname in self.filenames
            ]
        self.send_outputs()
