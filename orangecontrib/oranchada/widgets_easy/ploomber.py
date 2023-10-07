from Orange.data import Table, Domain, StringVariable
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets.widget import OWWidget, Input, Output, Msg
from Orange.data.pandas_compat import table_from_frame
import numpy as np
import logging
from itertools import cycle
import pandas as pd
import ploomber
from ploomber.executors import Serial
from ploomber.spec import DAGSpec
from ploomber import DAG
import os
import yaml

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[logging.FileHandler("charisma.log", mode='w')], level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
log = logging.getLogger("charisma")
log.info("log hijack for debugging")


class PredefinedPloomberWidget(OWWidget):
    # Define the widget's name, category, and outputs
    name = "Ploomber Workflow Runner"
    description = "Execute predefined Ploomber workflows with YAML and environment files."
   # icon = "icons/ploomber.png"
    priority = 10
    # want_main_area = False
    # resizing_enabled = False
    # proportion = Setting(50)
    commitOnChange = Setting(0)
    # label = Setting("")
    yaml_file = os.path.join(os.path.dirname(__file__), "ploomber","workflow_twinning", "pipeline.yaml")
    env_file = os.path.join(os.path.dirname(__file__), "ploomber", "workflow_twinning","env.yaml")


    class Inputs:
        # specify the name of the input and the type
        data = Input("Data", Table)


    class Outputs:
        # if there are two or more outputs, default=True marks the default output
        data_out = Output("Processed Data", Table, default=True)

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    class Error(OWWidget.Error):
        processing_error = Msg("Processing error(s).")

    def env2table(self):
        with open(self.env_file, "r") as file:
            env = yaml.safe_load(file)        
        self.env = env
        self.set_data(table_from_frame(pd.DataFrame.from_dict(env, orient="index", columns=["value"])))

    def __init__(self):
        # Initialize the widget
        super().__init__()

        # Load the environment dictionary from the env.yaml file
        self.env2table()
 
        self.dag=None
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Select ENV File", callback=self.load_file_env)
        gui.button(box, self, "Load pipeline", callback=self.load_workflow)
        gui.button(box, self, "Run pipeline", callback=self.run_workflow)
        #gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        #self.optionsBox.setDisabled(False)

    def load_file_env(self):
        filenames, filt = QFileDialog.getOpenFileNames(
            caption='Select ENV File',
            directory='',
            filter='YAML Files (*.yaml *.yml);;All Files (*)',
            initialFilter='All files (*)',
            )
        if filenames:
            self.env_file = filenames[0]
            self.env2table()   

    def load_workflow(self):
        if not self.yaml_file or not self.env_file:
            self.statusBar().showMessage("Please select both YAML and environment files.")
            return
        try:
            self.dag_spec = DAGSpec(data= self.yaml_file, env = self.env)
            self.dag = self.dag_spec.to_dag()
            self.dag.on_finish(lambda dag,report: print(report))                   
            log.info(self.dag.status())
           
            self.statusBar().showMessage("Workflow loaded successfully.")
        except Exception as e:
            log.info(e)
            self.statusBar().showMessage(f"Error: {str(e)}")

    def run_workflow(self):
        if self.dag is None:
            self.statusBar().showMessage("Please load the pipelinefirst,then click Run.")
            return
        try:
            self.dag.build()
           
            self.statusBar().showMessage("Workflow executed successfully.")
        except Exception as e:
            log.info(e)
            self.statusBar().showMessage(f"Error: {str(e)}")            

    @Inputs.data
    def set_data(self, data):
        self.Error.processing_error.clear()
        if data:
            self.data = data
        else:
            self.data = None


    def send_report(self):
        pass


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from Orange.data import Table
    import os
    try:
        WidgetPreview(PredefinedPloomberWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(PredefinedPloomberWidget).run()
