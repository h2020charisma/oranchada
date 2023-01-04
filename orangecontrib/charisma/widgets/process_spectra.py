from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np

class ProcessSpectraWidget(OWWidget):
    # Define the widget's name, category, and outputs
    name = "Process Spectra"
    description = "Process spectra provided as Orange data table"
    icon = "icons/spectra.svg"
    priority = 10
    #want_main_area = False
    #resizing_enabled = False
    #proportion = Setting(50)
    commitOnChange = Setting(0) 
    #label = Setting("")
    
    class Inputs:
        # specify the name of the input and the type
        data = Input("Data", Table)

    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data = Output("Data", Table, default=True)
    
    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.data = None
        self.optionsBox = gui.widgetBox(self.controlArea, "Options")
        gui.checkBox(
            self.optionsBox, self, "commitOnChange", "Commit data on selection change"
        )
        gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        self.optionsBox.setDisabled(False)
            

    @Inputs.data
    def set_data(self, data):
        if data:
            self.data = data
        else:
            self.data = None
            
    def commit(self):
        self.Outputs.data.send(self.process_data())
    
    def send_report(self):
        # self.report_plot() includes visualizations in the report
        #self.report_caption(self.label)
        pass

    def process_data(self):
        x = np.array([float(a.name) for a in self.data.domain.attributes])
        spe = Spectrum(x=x, y=self.data.X[0])
        spe1 = spe.subtract_moving_minimum(16)
        attrs = [ContinuousVariable.make("%f" % f,number_of_decimals=1) for f in spe1.x]
        domain = Domain(attrs, None, #table.domain.class_var,
                                            metas=self.data.metas
                                            )        
        table_processed = Table.from_numpy(domain, X=spe1.y.reshape(1,-1))
        return table_processed



if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  
    from Orange.data import Table
    import os
    try:
        print(os.getcwdb())
        path = r'../datasets/PST_WiICV532_Z005OP02_005_300msx10.txt'
        #with open(path, "r") as f:
        #    data = f.read()
        
        # no reader!
        #table = Table.from_file(path)
        table = Table("../datasets/collagen.csv")
        # Send the data table to the output
        WidgetPreview(ProcessSpectraWidget).run(set_data=table)    
    except Exception as err:
        print(err)
        WidgetPreview(ProcessSpectraWidget).run()    
    