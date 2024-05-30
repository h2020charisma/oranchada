from Orange.data import Table, Domain, StringVariable
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data.pandas_compat import table_from_frame, table_to_frame
import numpy as np
import logging
from itertools import cycle
import pandas as pd
import ploomber
from ploomber.executors import Serial
from ploomber.spec import DAGSpec
from ploomber import DAG
from ..base_widget import BaseWidget
from .ploomber_base import load_env, env2table
import os.path

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[logging.FileHandler("charisma_ploomber.log", mode='w')], level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
log = logging.getLogger("charisma")
log.info("log hijack for debugging")

class PloomberImportWidget(BaseWidget):
    # Define the widget's name, category, and outputs
    name = "CHARISMA database import"
    description = "CHARISMA database import"
    icon = "icons/upload.png"
    priority = 10
    # want_main_area = False
    # resizing_enabled = False
    # proportion = Setting(50)
    commitOnChange = Setting(0)
    should_auto_proc = Setting(False)
    investigation =  Setting("TEST") 

    # label = Setting("")
    yaml_file = os.path.join(os.path.dirname(__file__), "ploomber","workflow_import", "pipeline_import.yaml")
    env_file = os.path.join(os.path.dirname(__file__), "ploomber", "workflow_import","env_ploomber.yaml")


    class Inputs:
        # specify the name of the input and the type
        metadata = Input("Metadata", Table)
        data_env = Input("Settings", Table, default=False)           

    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data = Output("Processed Data", Table, default=True)

    @Inputs.metadata
    def set_metadata(self, metadata):
        if metadata:
            self.metadata = metadata
        else:
            self.metadata = None
        self.update_inputs_info()
        

    @Inputs.data_env
    def set_data_env(self, data_env):
        self.Error.processing_error.clear()
        if data_env:
            self.data_env = data_env
        else:
            self.data_env = None


    def update_inputs_info(self):
        self.Warning.clear()
        len11 = len(self.metadata) if self.metadata else None
    
        self.info.set_input_summary(f' (Reference {len11} metadata)')

 
    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    class Error(OWWidget.Error):
        processing_error = Msg("Processing error(s).")
    
    class Information(OWWidget.Warning):
        success = Msg("Workflow successful")

    def __init__(self):
        # Initialize the widget
        super().__init__()

        # Load the environment dictionary from the env.yaml file
        self.env = load_env(self.env_file,"ploomber_import")
        self.env["input_folder"] = ""
        self.investigation = self.env["hsds_investigation"]
        self.provider = self.env["hsds_provider"]
        self.instrument = self.env["hsds_instrument"]
        self.username = self.env["hs_username"]
        self.password = self.env["hs_password"]

        self.set_data_env(env2table(self.env))
        self.dag=None
        box = gui.widgetBox(self.controlArea, self.name)
        #gui.button(box, self, "Load pipeline", callback=self.load_workflow)
        self.investigation_edit = gui.lineEdit(box, self, 'investigation', label='Investigation')
        self.provider_edit = gui.lineEdit(box, self, 'provider', label='Provider')
        self.instrument_edit = gui.lineEdit(box, self, 'instrument', label='Instrument')

        self.instrument_edit.textChanged.connect(lambda text: self.update_field("hsds_instrument", text))
        self.provider_edit.textChanged.connect(lambda text: self.update_field("hsds_provider", text))
        self.investigation_edit.textChanged.connect(lambda text: self.update_field("hsds_investigation", text))

        box1 = gui.widgetBox(box, "CHARISMA DB login")
        self.user_edit = gui.lineEdit(box1, self, 'username', label='Username')
        self.password_edit = gui.lineEdit(box1, self, 'password', label='Password')
        
        self.user_edit.textChanged.connect(lambda text: self.update_field("hs_username", text))
        self.password_edit.textChanged.connect(lambda text: self.update_field("hs_password", text))

    def update_field(self, field_name, text):
        setattr(self, field_name, text)
        self.env[field_name] = text
        self.set_data_env(env2table(self.env))
   

    def workflow_input_file(self):
        return os.path.join( self.env["output_folder"],'metadata.xlsx')
    
    def prepare_input(self):
        metadata_file = self.workflow_input_file()
        df = table_to_frame(self.metadata,include_metas=True)
        df.set_index("index", inplace=True)
        df["enabled"] = True
        df["delete"] = False
        df["hsds_investigation"] = self.env["hsds_investigation"]
        df["hsds_provider"] = self.env["hsds_provider"]
        df["hsds_instrument"] = self.env["hsds_instrument"]        

        with pd.ExcelWriter(metadata_file, engine='openpyxl') as writer:
            df.to_excel(writer,sheet_name="files", index=True)
            pd.DataFrame({"value": [self.env["input_folder"]]}, index=["path"]).to_excel(writer, sheet_name='paths')        
    

    def load_workflow(self):
        if not self.yaml_file or not self.env_file:
            log.info("Please select both YAML and environment files.")
            return
        try:
            log.info(self.yaml_file,self.env_file,self.env)
            self.dag_spec = DAGSpec(data= self.yaml_file, env = self.env)
            self.dag = self.dag_spec.to_dag()

            log.info(self.dag.status())
            #self.plot_spe()
            log.info("Workflow loaded successfully.")
        except Exception as e:
            log.info(e)
            self.Error.processing_error(f"Error: {str(e)}")

    def run_workflow(self):
        if self.dag is None:
            self.load_workflow()
        
        try:
            log.info("prepare input")
            self.prepare_input()

        except Exception as err:
            log.error(err)
            self.Error.processing_error(f"Error while preparing input: {str(err)}")

        try:
            self.dag.build(force=True)
            #tbd read results
            #self.send_outputs()
            self.Information.success()
            #self.statusBar().showMessage("Workflow executed successfully.")
        except Exception as e:
            log.error(e)
            self.Error.processing_error(f"Error: {str(e)}")
            #self.statusBar().showMessage(f"Error: {str(e)}")   

    def process(self):
        self.run_workflow()

    def send_report(self):
        pass

    def plot_spe(self):    
        pass


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from Orange.data import Table
    import os
    try:
        WidgetPreview(PloomberImportWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(PloomberImportWidget).run()
