from collections import UserList

from Orange.data import Table
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output, OWBaseWidget

import pandas as pd
from Orange.data.pandas_compat import table_from_frame
import os.path

class LoadFileNames(OWBaseWidget):
    name = "Load File Names"
    description = "Load file names"
    icon = "icons/spectra.svg"
    resizing_enabled = False
    want_main_area = False

    filenames = Setting([])

    class Outputs:
        data = Output("File list", Table, default=False, auto_summary=False)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Load File names", callback=self.load_file)

    def load_file(self):
        self.filenames, filt = QFileDialog.getOpenFileNames(
            caption='Open spectra',
            directory='',
            filter='All files (*)',
            initialFilter='All files (*)',
            )
        _tmp = []
        for fn in self.filenames:
            parent_path, filename = os.path.split(fn)
            _tmp.append([fn,parent_path,filename])
        self.Outputs.data.send(table_from_frame(pd.DataFrame(_tmp,columns=["path","folder","filename"])))

