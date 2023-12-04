from collections import UserList

from AnyQt.QtWidgets import QFileDialog
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output, OWBaseWidget


class FileList(UserList):
    pass


class LoadFileNames(OWBaseWidget):
    name = "Load File Names"
    description = "Load file names"
    icon = "icons/spectra.svg"
    resizing_enabled = False
    want_main_area = False

    filenames = Setting([])

    class Outputs:
        data = Output("FileList", FileList, auto_summary = False)

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
        self.Outputs.data.send(self.filenames)
