from Orange.data import Table
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg

class LoadSpectraWidget(OWWidget):
    # Define the widget's name, category, and outputs
    name = "Load Spectra"
    description = "Load spectra data into an Orange data table"
    icon = "icons/spectra.svg"
    priority = 10
    want_main_area = False
    resizing_enabled = False
    
    label = Setting("")
    
    class Inputs:
        # specify the name of the input and the type
        data = Input("Data", Table)

    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data = Output("Spectra Data", Table, default=True)
    
    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.data = None
        
        self.label_box = gui.lineEdit(
            self.controlArea, self, "label", box="Text", callback=self.commit)
        # Add any necessary GUI elements (e.g. buttons, sliders, etc.)
        #self.file_selection = gui.fileOpen(self, "file_selection", "Select spectra file",
        #                           filter="All files (*.*)")        
        #self.load_button = gui.button(self, self, "Load Data", callback=self.load_data)

    @Inputs.data
    def set_data(self, data):
        if data:
            self.data = data
        else:
            self.data = None
            
    def commit(self):
        self.Outputs.data.send(self.data)
    
    def send_report(self):
        # self.report_plot() includes visualizations in the report
        self.report_caption(self.label)

    def load_data(self):
        # Read the file selected by the user
        with open(self.file_selection, "r") as f:
            data = f.read()
        
        # Parse the data and create an Orange data table
        table = Table.from_file(self.file_selection)
        
        # Send the data table to the output
        self.send("Spectra Data", table)



if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(LoadSpectraWidget).run()