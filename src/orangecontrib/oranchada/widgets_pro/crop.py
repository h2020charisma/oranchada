from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class Crop(FilterWidget):
    name = "Crop spectrum"
    description = "Crop spectrum"
    icon = "icons/spectra.svg"

    left = Setting(100)
    right = Setting(3500)
    should_auto_proc = Setting(True)
    should_auto_plot = Setting(True)

    def __init__(self):
        # Initialize the widget
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.left_spin = gui.doubleSpin(box, self, 'left', 0, 4500 , decimals=2, step=10, callback=self.auto_process,
                       label='Left')      
        self.right_spin = gui.doubleSpin(box, self, 'right', 0, 4500 , decimals=2, step=100, callback=self.auto_process,
                       label='Right')                   

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                spe.trim_axes(method='x-axis',boundaries=(self.left,self.right))
            )
            
        self.send_outputs()

    def check_values(self):
        # Ensure that right is always greater than left
        if self.right <= self.left:
            self.right = self.left + 1

        # Update the spin boxes to reflect the changes
        self.right_spin.setValue(self.right)
        self.left_spin.setValue(self.left)

        self.auto_process(self)        