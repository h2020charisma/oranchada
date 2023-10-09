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
from ..base_widget import FilterWidget
from ..base_widget import BaseWidget, RC2Spectra

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[logging.FileHandler("charisma.log", mode='w')], level=logging.NOTSET)
logging.root.setLevel(logging.NOTSET)
log = logging.getLogger("charisma")
log.info("log hijack for debugging")


class PloomberTwinningWidget(BaseWidget):
    # Define the widget's name, category, and outputs
    name = "CHARISMA Twinning protocol"
    description = """Protocol for twinning devices and spectra harmonization.\n\n
            - Input: 5 spectra per spectrometer using different laser power (mW).\n\n
            - Spectra treatment: Normalize Raman spectra (same power and integration time). Remove baseline.\n
            - LED correction: LED intensity correction.\n
            - Power regression line and Factor Correction (FC) calculation: Find 144 cm-1 peaks. Linear regression (laser power vs maximum intensity). FC = Slope A/ Slope B.\n
            - Harmonization: FC * spectra to harmonize\n
            - Quality calculation
            \n"""
    icon = "icons/twinning.png"
    priority = 10
    # want_main_area = False
    # resizing_enabled = False
    # proportion = Setting(50)
    commitOnChange = Setting(0)


    baseline_algorithm =  Setting("movmin") #als ,snip, none
    wlen =   Setting(10)    
    baseline_after_ledcorrection =  Setting(False)
    fit_peak = Setting(False)

    # label = Setting("")
    yaml_file = os.path.join(os.path.dirname(__file__), "ploomber","workflow_twinning", "pipeline_ploomber.yaml")
    env_file = os.path.join(os.path.dirname(__file__), "ploomber", "workflow_twinning","env_ploomber.yaml")


    should_auto_proc = Setting(False)

    class Inputs:
        reference_spe = Input("Raw data (RC2Spectra) of spectrometer A (REFERENCE device)", RC2Spectra, default=True)
        twinned_spe = Input("Raw data (RC2Spectra) of spectrometer B (device to TWIN)", RC2Spectra, default=False)
        reference_led = Input("Reference device LED spectra (RC2Spectra)", RC2Spectra, default=True)
        twinned_led = Input("Twinned device LED spectra (RC2Spectra)", RC2Spectra, default=False)      
        data_env = Input("Settings", Table, default=False)   

    class Outputs:
        reference_spe = Output("Reference (RC2Spectra)", RC2Spectra, default=True)
        twinned_spe = Output("Twinned (RC2Spectra)", RC2Spectra, default=True)
               

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("My warning!")

    class Error(OWWidget.Error):
        processing_error = Msg("Processing error(s).")

    def env2table(self):
        with open(self.env_file, "r") as file:
            env = yaml.safe_load(file)        
        self.env = env
        self.set_data_env(table_from_frame(pd.DataFrame.from_dict(env, orient="index", columns=["value"])))

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
        box = gui.widgetBox(self.controlArea, "Baseline removal")
        gui.spin(box, self, 'wlen', 1, 5000, step=20, callback=self.auto_process, label='Window length')     
        box = gui.widgetBox(self.controlArea, "Peak fitting")   

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

    def on_finish(self,dag,report):
        print(dag)
        print(report)

    def on_render(self,dag):
        print("render ",dag)

    def on_failure(self,dag,report):
        print(report)

    def load_workflow(self):
        if not self.yaml_file or not self.env_file:
            self.statusBar().showMessage("Please select both YAML and environment files.")
            return
        try:
            self.dag_spec = DAGSpec(data= self.yaml_file, env = self.env)
            self.dag = self.dag_spec.to_dag()
            self.dag.on_finish = self.on_finish
            self.dag.on_render = self.on_render

            log.info(self.dag.status())
           
            self.statusBar().showMessage("Workflow loaded successfully.")
        except Exception as e:
            log.info(e)
            self.statusBar().showMessage(f"Error: {str(e)}")


    def prepare_input(self):
        A = RC2Spectra()
        for spe in self.reference_spe:
            A.append(spe)
        B = RC2Spectra()
        for spe in self.twinned_spe:
            B.append(spe)
        dfA= pd.DataFrame(A.data,columns=["spectrum"])
        dfA["reference"]= True
        dfB= pd.DataFrame(B.data,columns=["spectrum"])
        dfB["reference"]= False
        df_spectra = pd.concat([dfA,dfB], ignore_index=True)        

        A = RC2Spectra()
        for spe in self.reference_led:
            A.append(spe)
        B = RC2Spectra()
        for spe in self.twinned_led:
            B.append(spe)
        dfA= pd.DataFrame(A.data,columns=["spectrum"])
        dfA["reference"]= True
        dfB= pd.DataFrame(B.data,columns=["spectrum"])
        dfB["reference"]= False
        df_leds = pd.concat([dfA,dfB], ignore_index=True)    

        df_spectra.to_hdf(os.path.join( self.env["output_folder"],"input_data.h5"), key='input_spectra', mode='w')
        df_leds.to_hdf(self.env["output_folder"],"input_data.h5", key='input_leds', mode='w')
      # reference_spe = Input("Raw data (RC2Spectra) of spectrometer A (REFERENCE device)", RC2Spectra, default=True)
      #  twinned_spe = Input("Raw data (RC2Spectra) of spectrometer B (device to TWIN)", RC2Spectra, default=False)
      #  reference_led = Input("Reference device LED spectra (RC2Spectra)", RC2Spectra, default=True)
      #  twinned_led = Input("Twinned device LED spectra (RC2Spectra)", RC2Spectra, default=False)      
      #  data_env = Input("Settings", Table, default=False)               

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

    @Inputs.reference_spe
    def set_reference_spe(self, spe):
        if spe:
            self.reference_spe = spe
        else:
            self.reference_spe = None
        self.update_inputs_info()
        self.auto_process()

    @Inputs.twinned_spe
    def set_twinned_spe(self, spe):
        if spe:
            self.twinned_spe = spe
        else:
            self.twinned_spe = None
        self.update_inputs_info()
        self.auto_process()     

    @Inputs.reference_led
    def set_reference_led(self, spe):
        if spe:
            self.reference_led = spe
        else:
            self.reference_led = None
        self.update_inputs_info()
        self.auto_process()

    @Inputs.twinned_led
    def set_twinned_spe(self, spe):
        if spe:
            self.twinned_led = spe
        else:
            self.twinned_led = None
        self.update_inputs_info()
        self.auto_process()            

    @Inputs.data_env
    def set_data_env(self, data_env):
        self.Error.processing_error.clear()
        if data_env:
            self.data_env = data_env
        else:
            self.data_env = None


    def send_report(self):
        pass


if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from Orange.data import Table
    import os
    try:
        WidgetPreview(PloomberTwinningWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(PloomberTwinningWidget).run()
