from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget

available_models = ['savgol', 'wiener', 'median','gauss','lowess','boxcar']


class Smoothing(FilterWidget):
    name = "Smooth spectrum"
    description = "Smooth spectrum"
    icon = "icons/spectra.svg"

    method = Setting('savgol')
    should_auto_proc = Setting(True)
    should_auto_plot = Setting(True)

    savgol_window_length = Setting(5)
    savgol_polyorder = Setting(3)
    

    def __init__(self):
        # Initialize the widget
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.method_combo = gui.comboBox(
            box, self, "method",
            label="Select method:",
            items=available_models,sendSelectedValue=True,
            callback=self.auto_process
        )                  
        self.savgolbox = gui.widgetBox(self.controlArea, "savgol")      
        gui.spin(self.savgolbox, self, 'savgol_window_length', 2, 31, callback=self.auto_process,label="window length")
        gui.spin(self.savgolbox, self, 'savgol_polyorder', 1, 7,step=2, callback=self.auto_process,label="polyorder")      

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            kwargs = {}
            if self.method == "savgol":
               kwargs["window_length"] = self.savgol_window_length
               kwargs["polyorder"] = self.savgol_polyorder

            self.out_spe.append(
                spe.smoothing_RC1(method=self.method,**kwargs)
            )
            
        self.send_outputs()

   