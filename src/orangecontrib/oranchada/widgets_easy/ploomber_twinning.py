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
import tempfile
#from matplotlib.offsetbox import OffsetImage, AnnotationBbox

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
logging.basicConfig(handlers=[logging.FileHandler("charisma_twinning.log", mode='w')], level=logging.NOTSET)
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
        reference_led = Input("Reference device LED spectra (RC2Spectra)", RC2Spectra, default=False)
        twinned_led = Input("Twinned device LED spectra (RC2Spectra)", RC2Spectra, default=False)      
        data_env = Input("Settings", Table, default=False)   

    class Outputs:
#        reference_spe = Output("Reference (RC2Spectra)", RC2Spectra, default=True)
#        twinned_spe = Output("Twinned (RC2Spectra)", RC2Spectra, default=True)
        out_spe = Output("RC2Spectra", RC2Spectra, default=True)
        data = Output("Data", Table, default=False)
        meta_spectra = Output("Metadata spectra", Table, default=False)
        meta_leds = Output("Metadata LEDs", Table, default=False)
               

    @Inputs.reference_spe
    def set_reference_spe(self, spe):
        if spe:
            self.reference_spe = spe
        else:
            self.reference_spe = None
        self.update_inputs_info()


    @Inputs.twinned_spe
    def set_twinned_spe(self, spe):
        if spe:
            self.twinned_spe = spe
        else:
            self.twinned_spe = None
        self.update_inputs_info()
    

    @Inputs.reference_led
    def set_reference_led(self, spe):
        if spe:
            self.reference_led = spe
        else:
            self.reference_led = None
        self.update_inputs_info()

    @Inputs.twinned_led
    def set_twinned_led(self, spe):
        if spe:
            self.twinned_led = spe
        else:
            self.twinned_led = None
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
        len11 = len(self.reference_spe) if self.reference_spe else None
        len12 = len(self.reference_led) if self.reference_led else None
        len21 = len(self.twinned_spe) if self.twinned_spe else None
        len22 = len(self.twinned_led) if self.twinned_led else None        
        self.info.set_input_summary(f' (Reference {len11} RC2Spectra + {len12} LED RC2Spectra)\n (Twinned {len21} RC2Spectra + {len22} LED RC2Spectra)')
        
    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("Warning")

    class Information(OWWidget.Information):
        success = Msg("Workflow successful")

    class Error(OWWidget.Error):
        processing_error = Msg("Workflow error")

    def env2table(self):
        with open(self.env_file, "r") as file:
            env = yaml.safe_load(file)        
        self.env = env
        self.env["output_folder"] = os.path.join(tempfile.gettempdir(),"ploomber_twinning")
        self.set_data_env(table_from_frame(pd.DataFrame.from_dict(env, orient="index", columns=["value"])))

    def __init__(self):
        # Initialize the widget
        super().__init__()

        # Load the environment dictionary from the env.yaml file
        self.env2table()
        self.out_spe = RC2Spectra()
        self.dag=None
        box = gui.widgetBox(self.controlArea, self.name)
        #gui.button(box, self, "Select ENV File", callback=self.load_file_env)
        gui.button(box, self, "Load pipeline", callback=self.load_workflow)
        gui.button(box, self, "Prepare input", callback=self.prepare_input)
        #gui.button(box, self, "Run", callback=self.run_workflow)
        #gui.button(self.optionsBox, self, "Commit", callback=self.commit)
        #self.optionsBox.setDisabled(False)
        cbox = gui.widgetBox(box, "Baseline removal")
        gui.spin(box, self, 'wlen', 1, 5000, step=20, callback=self.auto_process, label='Window length')     
        cbox = gui.widgetBox(box, "Peak fitting")   

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
        #print(dag)
        log.info(report)

    def on_render(self,dag):
        log.info("render ",dag)

    def on_failure(self,dag,report):
        print(report)

    def load_workflow(self):
        if not self.yaml_file or not self.env_file:
            log.info("Please select both YAML and environment files.")
            return
        try:
            log.info(self.yaml_file,self.env_file,self.env)
            self.dag_spec = DAGSpec(data= self.yaml_file, env = self.env)
            self.dag = self.dag_spec.to_dag()
            self.dag.on_finish = self.on_finish
            self.dag.on_render = self.on_render

            log.info(self.dag.status())
            self.plot_spe()
            log.info("Workflow loaded successfully.")
        except Exception as e:
            log.info(e)
            self.Error.processing_error(f"Error: {str(e)}")

    def workflow_input_file(self):
        return os.path.join( self.env["output_folder"],self.env["input_rcspectra"])

    def prepare_input(self):
        df_spectra = None
        df_leds = None
        log.info("prepare_input")
        input_rcspectra = self.workflow_input_file()
        #log.info("prepare_input  {}".format(input_rcspectra))               
        try:
            A = RC2Spectra()
            for spe in self.reference_spe:
                A.append(spe)
            self.send_outputs()
            log.info(len(A.data))
            B = RC2Spectra()
            for spe in self.twinned_spe:
                B.append(spe)
            dfA= pd.DataFrame(A.data,columns=["spectrum"])
            
            dfA["reference"]= True
            dfB= pd.DataFrame(B.data,columns=["spectrum"])
            dfB["reference"]= False
            df_spectra = pd.concat([dfA,dfB], ignore_index=True)  
            df_spectra.to_hdf(input_rcspectra, key=self.env['key_spectra'], mode='w')                  
        except Exception as err:
            log.error(err)

        try:
            A = RC2Spectra()
            for spe in self.reference_led:
                A.append(spe)
            B = RC2Spectra()
            for spe in self.twinned_led:
                B.append(spe)
            log.info(len(A.data))
            dfA= pd.DataFrame(A.data,columns=["spectrum"])
            dfA["reference"]= True
            dfB= pd.DataFrame(B.data,columns=["spectrum"])
            dfB["reference"]= False
            df_leds = pd.concat([dfA,dfB], ignore_index=True)    
            df_leds.to_hdf(input_rcspectra, key=self.env['key_leds'], mode='a')
        except Exception as err:
            log.error(err)
        self.set_meta_spectra(table_from_frame(df_spectra))
        self.set_meta_leds(table_from_frame(df_leds))
      # reference_spe = Input("Raw data (RC2Spectra) of spectrometer A (REFERENCE device)", RC2Spectra, default=True)
      #  twinned_spe = Input("Raw data (RC2Spectra) of spectrometer B (device to TWIN)", RC2Spectra, default=False)
      #  reference_led = Input("Reference device LED spectra (RC2Spectra)", RC2Spectra, default=True)
      #  twinned_led = Input("Twinned device LED spectra (RC2Spectra)", RC2Spectra, default=False)      
      #  data_env = Input("Settings", Table, default=False)               

    def run_workflow(self):
        if self.dag is None:
            self.load_workflow()
        
        try:
            log.info("prepare input")
            self.prepare_input()

        except Exception as err:
            log.error(err)

        try:
            self.dag.build(force=False)
            devices_h5file = os.path.join( self.env["output_folder"],"twinning_spectra_table_harmonized.h5")
            results = pd.read_hdf(devices_h5file, key='devices')
            #devices_h5file= upstream["twinning_peaks"]["data"]
            #devices = pd.read_hdf(devices_h5file, "devices")
            #devices.head()
            #processing = pd.read_hdf(devices_h5file, "processing")

            for index,row in results.iterrows():
                if row["reference"]:
                    key="spectrum_corrected"
                else:
                    key="spectrum_harmonized"
                try:    
                    spe = row[key]
                    sc1 = spe.trim_axes(method='x-axis', boundaries=(100,max(spe.x)-1000))
                    meta={}
                    for tag in ["laser_power","reference","device","laser_power_percent"]:
                        meta[tag] = row[tag]
                    self.out_spe.append(sc1)
                    #rc2.spectrum.Spectrum(sc1.x,sc1.y,meta))
                except Exception as err:
                    print(err)
                #,label="{}".format(row["device"]))
            self.send_outputs()
            self.Information.success()
            #self.statusBar().showMessage("Workflow executed successfully.")
        except Exception as e:
            log.error(e)
            self.Error.processing_error(f"Error: {str(e)}")
            #self.statusBar().showMessage(f"Error: {str(e)}")            

    def set_meta_spectra(self, data):
        self.Error.processing_error.clear()
        if data:
            self.meta_spectra = data
        else:
            self.meta_spectra = None

    def set_meta_leds(self, data):
        self.Error.processing_error.clear()
        if data:
            self.meta_leds = data
        else:
            self.meta_leds = None
    
    def send_report(self):
        pass


    def process(self):
        self.run_workflow()

    def custom_plot(self, ax):      
        if self.dag is None:
            pass
        else:
            pass
            #ipython_image  = self.dag.plot("embed")
            #imagebox = OffsetImage(ipython_image, zoom=0.5)  # You can adjust the zoom factor as needed
            #ab = AnnotationBbox(imagebox, (0.5, 0.5), frameon=False, xycoords='axes fraction')
            #ax.add_artist(ab)

            # Optional: Customize the plot or axis as needed
            #ax.set_xlim(0, 1)
            #ax.set_ylim(0, 1)
            #ax.set_aspect('equal')            

if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    from Orange.data import Table
    import os
    try:
        WidgetPreview(PloomberTwinningWidget).run()
    except Exception as err:
        log.error(err)
        WidgetPreview(PloomberTwinningWidget).run()
