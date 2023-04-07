from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class Normalize(FilterWidget):
    name = "Normalize"
    description = "Normalize"
    icon = "icons/spectra.svg"

    method = Setting('minmax')

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.comboBox(box, self, 'method', sendSelectedValue=True,
                     items=['unity', 'min_unity', 'unity_density', 'minmax'],
                     label='Normalization method', callback=self.auto_process)

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.normalize(self.method)
                )
        self.send_outputs()
