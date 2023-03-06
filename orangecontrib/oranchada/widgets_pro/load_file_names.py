from collections import UserList
from Orange.widgets import gui
from Orange.widgets.widget import OWBaseWidget, Output
from AnyQt.QtWidgets import QFileDialog


class FileList(UserList):
    pass


class LoadFileNames(OWBaseWidget):
    name = "Load File Names"
    description = "Load file names"
    icon = "icons/spectra.svg"
    resizing_enabled = False
    want_main_area = False

    class Outputs:
        data = Output("FileList", FileList)

    def __init__(self):
        super().__init__()
        self.filenames = list()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Load File names", callback=self.load_file)

    def load_file(self):
        self.filenames, filt = QFileDialog.getOpenFileNames(
            caption='Open spectra',
            directory='/data/RamanSpe/FNMT-Madrid/Horiba_785nm/PST/PST10_iR785_OP02_8000msx8_01.txt',
            filter='All files (*)',
            initialFilter='All files (*)',
            )
        self.Outputs.data.send(self.filenames)
