from AnyQt.QtWidgets import QAbstractItemView
from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class Select(FilterWidget):
    name = "Select"
    description = "select spectra"
    icon = "icons/spectra.svg"

    select_inputs_idx = Setting([])

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.select_box = gui.listBox(box, self, 'select_inputs_idx',
                                      selectionMode=QAbstractItemView.MultiSelection, callback=self.auto_process)

    def input_hook(self):
        while self.select_box.takeItem(0):
            pass
        for spe_i, spe in enumerate(self.in_spe):
            self.select_box.addItem(f'{spe_i}: {spe!r}')

    def process(self):
        self.out_spe = list()
        for i in self.select_inputs_idx:
            self.out_spe.append(self.in_spe[i])
        self.send_outputs()
