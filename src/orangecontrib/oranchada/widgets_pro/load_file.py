import ramanchada2 as rc2
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets import gui
from Orange.widgets.settings import Setting

import os

from ..base_widget import CreatorWidget


class LoadFile(CreatorWidget):
    name = "Load File"
    description = "Load spectrum from file"
    icon = "icons/spectra.svg"

    filenames = Setting([])
    dataset = Setting("/raw")

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Load File", callback=self.load_file)
        self.fileformat = 'Auto'
        
        gui.comboBox(box, self, 'fileformat', sendSelectedValue=True,
                     items=['Auto', 'spc', 'sp', 'spa', '0', '1', '2',
                            'wdf', 'ngs', 'jdx', 'dx',
                            'txt', 'txtr', 'csv', 'prn', 'rruf',
                            'cha'],
                     label='File format',callback=self.update_visibility)
        self.datasetbox = gui.widgetBox(self.controlArea, "CHADA datasets")    
        self.datasetedit = gui.lineEdit(self.datasetbox, self, "dataset", label="Dataset name  (.cha file):", callback=self.load_file)
        self.datasetbox.hide()

    def update_visibility(self):
            # Show or hide boxes based on the selected method
            if self.fileformat == "cha":
                self.datasetbox.show()
            else:
                self.datasetbox.hide()

    def load_file(self):
        filters = ['TXT (*.txt)',
                   'CSV (*.csv)',
                   'CHADA (*.cha)',
                   'All spectra formats (*.txt *.csv *.spc *.wdf)',
                   'All files (*)',
                   ]
        filenames, filt = QFileDialog.getOpenFileNames(
            caption='Open spectra',
            directory='',
            filter=';;'.join(filters),
            initialFilter=filters[-2],
            )
        if filenames:
            self.filenames = filenames
            self.auto_process()

    def process(self):
        self.out_spe = []
        for fname in self.filenames:
            name, extension = os.path.splitext(fname)
            if extension == ".cha":
                spe = rc2.spectrum.from_chada(fname, dataset=self.dataset)
            else:
                spe = rc2.spectrum.from_local_file(fname,
                                                   filetype=(self.fileformat if self.fileformat != 'Auto' else None),
                                                   )
            meta_dct = spe.meta.model_dump()
            meta_dct['xlabel'] = 'Raman shift [cm¯¹]'
            spe.meta = meta_dct
            self.out_spe.append(spe)
        self.send_outputs()
