from Orange.data import Table
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

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
        return self.data



if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  
    from Orange.data import Table
    try:
        path = r'datasets/PST_WiICV532_Z005OP02_005_300msx10.txt'
        #with open(path, "r") as f:
        #    data = f.read()
        
        # Parse the data and create an Orange data table
        #table = Table.from_file(path)
        
        # Send the data table to the output
        WidgetPreview(ProcessSpectraWidget).run()    
    except Exception as err:
        print(err)
        WidgetPreview(ProcessSpectraWidget).run()    
    