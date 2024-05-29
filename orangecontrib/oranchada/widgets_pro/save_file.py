import ramanchada2 as rc2
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets import gui
from Orange.widgets.settings import Setting

import os

from ..base_widget import FilterWidget


class SaveFile(FilterWidget):
    name = "Save Spectra"
    description = "Save spectra to file"
    icon = "icons/spectra.svg"

    filenames = Setting([])

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Save File", callback=self.save_file)
        
        self.fileformat = 'Auto'
        gui.comboBox(box, self, 'fileformat', sendSelectedValue=True,
                     items=['.cha', 'txt'],
                     label='File format')

    def save_file(self):
        filters = ['CHADA file (*.cha)',
                   'TXT file (*.txt)',
                   'All files (*)']
        filename, filt = QFileDialog.getSaveFileName(
            self, 
            caption='Save spectra',
            directory='',
            filter=';;'.join(filters),
            initialFilter=filters[0]
        )
        if filename:
            _, extension = os.path.splitext(filename)
            if extension.lower() == ".cha":
                for spe in self.in_spe:
                    spe.write_cha(filename,dataset = "/oranchada")
            elif extension.lower() == ".txt":
                for spe in self.in_spe:
                    #spe.write_cha(filename,dataset = "/raw")    
                    pass                

    def process(self):
        self.out_spe = []
        self.send_outputs()
