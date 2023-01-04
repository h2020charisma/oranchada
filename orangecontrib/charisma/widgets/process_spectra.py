from Orange.data import Table, Domain, ContinuousVariable
from Orange.widgets import gui, utils
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Output, Msg
import ramanchada2 as rc2
from ramanchada2.spectrum import Spectrum
import numpy as np
import logging

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[logging.FileHandler("charisma.log", mode='w')], level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
log = logging.getLogger("charisma")
log.info("log hijack for debugging")

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
        data = Output("Processed Data", Table, default=True)
        peaks = Output("Peaks", Table, default=False)
    
    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    class Error(OWWidget.Error):
        processing_error = Msg("Processing error(s).")        

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

        #logging.warning('warning')
        #logging.error('error')
        #logging.exception('exp')
            

    @Inputs.data
    def set_data(self, data):
        self.Error.processing_error.clear()
        if data:
            self.data = data
        else:
            self.data = None
            
    def commit(self):
        processed_data,peaks = self.process_data()
        self.Outputs.data.send(processed_data)
        self.Outputs.peaks.send(peaks)
    
    def send_report(self):
        # self.report_plot() includes visualizations in the report
        #self.report_caption(self.label)
        pass

    def process_data(self):
        x = np.array([float(a.name) for a in self.data.domain.attributes])
        domain = None
        table_processed =self.data
        peaks = None
        try:
            n_rows = self.data.X.shape[0]
            for i in np.arange(0,n_rows):
                spe = Spectrum(x=x, y=self.data[i].x)
                spe1 = spe.trim_axes(method='x-axis',boundaries=(140,np.max(x)))
                if domain is None:
                    attrs = [ContinuousVariable.make("%f" % f,number_of_decimals=1) for f in spe1.x]
                    domain = Domain(attrs, class_vars = self.data.domain.class_vars,metas = self.data.domain.metas)
                    #,metas=self.data.metas)
                    table_processed = Table.from_table(domain, self.data) 
                #spe1 = spe.subtract_moving_minimum(16)
                spe1 = spe1.hht_sharpening(movmin=16) 
                #spe1 = spe.normalize('unity_area')
                #log.debug(max(spe1.y))
                inst = table_processed[i]
                inst.x[:]=spe1.y[:]
            return table_processed, peaks
        except Exception as err:
            log.exception(err)
            #self.Error(str(err))
            #raise Exception
        return None



if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview  
    from Orange.data import Table
    import os
    try:
        log.info(os.getcwdb())
        path = r'../datasets/PST_WiICV532_Z005OP02_005_300msx10.txt'
        #with open(path, "r") as f:
        #    data = f.read()
        
        log.warning('start')

        # no reader!
        #table = Table.from_file(path)
        data = Table("../datasets/collagen.csv")
        
        # Send the data table to the output
        WidgetPreview(ProcessSpectraWidget).run(set_data=data)    
    except Exception as err:
        print(err)
        WidgetPreview(ProcessSpectraWidget).run()    
    