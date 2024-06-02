from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class BaselineRemove(FilterWidget):
    name = "Baseline remove"
    description = "Detect and remove baseline"
    icon = "icons/spectra.svg"

    niter = Setting(40)
    method = Setting("SNIP")
    als_smooth = Setting(7)
    als_lam = Setting(1e5)
    als_p = Setting(0.001)
    window_size = Setting(10)
    should_auto_proc = Setting(True)
    should_auto_plot = Setting(True)    
    
    def __init__(self):
        # Initialize the widget
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.method_combo = gui.comboBox(
            box, self, "method",
            label="Select method:",
            items=["SNIP","ALS","Moving minimum"],sendSelectedValue=True,
            callback=self.auto_process
        )  
        #snipbox = gui.widgetBox(self.controlArea, "SNIP")
        self.niterspin = gui.spin(box, self, 'niter', 0, 100, callback=self.auto_process,label="niter")        
        self.alsbox = gui.widgetBox(self.controlArea, "ALS")      
        gui.doubleSpin(self.alsbox, self, 'als_lam', 1e2, 1e6, decimals=2, step=100, callback=self.auto_process,
                       label='lam')    
        gui.doubleSpin(self.alsbox, self, 'als_p', 0, 5, decimals=4, step=.0001, callback=self.auto_process,
                       label='p')      
        gui.doubleSpin(self.alsbox, self, 'als_smooth', 0.1, 25, decimals=2, step=0.5, callback=self.auto_process,
                       label='smooth')           
        self.mmbox = gui.widgetBox(self.controlArea, "Moving minimum")           
        gui.spin(self.mmbox, self, 'window_size', 0, 5000, callback=self.auto_process)
        self.update_visibility()

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            if self.method == "ALS":
                kwargs = {"niter" : self.niter, 
                          "smooth" : self.als_smooth,
                          "lam" : self.als_lam,
                          "p" : self.als_p}
                self.out_spe.append(
                    spe.subtract_baseline_rc1_als(**kwargs)
                    )                
                pass
            elif self.method == "SNIP":
                kwargs = {"niter" : self.niter }
                self.out_spe.append(
                    spe.subtract_baseline_rc1_snip(**kwargs)
                    )
            else:
                self.out_spe.append(spe.moving_minimum(self.window_size))    
                            
        self.send_outputs()

    def update_visibility(self):
            # Show or hide boxes based on the selected method
            if self.method == "SNIP":
                self.niterspin.show()
                self.mmbox.hide()
                self.alsbox.hide()
            elif self.method == "ALS":
                self.niterspin.show()
                self.alsbox.show()
                self.mmbox.hide()
            else:
                self.alsbox.hide()
                self.mmbox.show()
                self.niterspin.hide()

    def auto_process(self):
        self.update_visibility()
        super().auto_process()
            