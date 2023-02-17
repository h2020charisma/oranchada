from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra

from AnyQt.QtWidgets import QAbstractItemView


class Select(RC2_Filter):
    name = "Select"
    description = "select spectra"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.select_inputs_idx = []
        box = gui.widgetBox(self.controlArea, self.name)
        self.select_box = gui.listBox(box, self, 'select_inputs_idx',
                                      selectionMode=QAbstractItemView.MultiSelection, callback=self.auto_process)

    def input_hook(self):
        while self.select_box.takeItem(0):
            pass
        for spe_i, spe in enumerate(self.in_spe):
            self.select_box.addItem(f'{spe_i}: {spe!r}')

    def process(self):
        self.out_spe = RC2Spectra()
        for i in self.select_inputs_idx:
            self.out_spe.append(self.in_spe[i])
        self.send_outputs()
