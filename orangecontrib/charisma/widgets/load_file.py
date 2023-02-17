from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, OWBaseWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging
from itertools import cycle
from .rc2_base import RC2_Creator
from Orange.widgets.utils.filedialogs import RecentPathsWComboMixin, open_filename_dialog



class LoadFile(RC2_Creator):
    name = "Load File"
    description = "Load spectrum from file"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)

        gui.button(box, self, "Load File", callback=self.load_file)
        self.fileformat = 'txt'
        self.backend = 'native'
        gui.comboBox(box, self, 'fileformat', sendSelectedValue=True, items=['txt', 'csv'], label='File format')
        gui.comboBox(box, self, 'backend'   , sendSelectedValue=True, items=['native', 'ramanchada_parser'], label='Backend')


    def load_file(self):
        self.filename, reader, _ = open_filename_dialog('/data/RamanSpe/FNMT-Madrid/Horiba_785nm/PST/PST10_iR785_OP02_8000msx8_01.txt', None, [])
        self.auto_process()

    def multi_process(self):
        return [rc2.spectrum.from_local_file(self.filename, filetype=self.fileformat, backend=self.backend)]
