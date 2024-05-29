
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import  Input,Output, Msg, OWWidget
from ..base_widget import BaseWidget , FilterWidget, RC2Spectra
import ramanchada2 as rc2
from Orange.data import Table

from ramanchada2.protocols.calibration import CalibrationModel

class XAxisCalibrationWidget(FilterWidget):
    name = "X axis calibration"
    description = "X-axis  calibration"
    icon = "icons/spectra.svg"

    laser_wl = Setting(785)

    def input_hook(self):
        pass

    class Warning(OWWidget.Warning):
        warning = Msg("Warning")

    class Information(OWWidget.Information):
        success = Msg("Workflow successful")

    class Error(OWWidget.Error):
        processing_error = Msg("Workflow error")

    class Inputs(FilterWidget.Inputs):
        spe_neon = Input("Neon spectrum", RC2Spectra, default=True)
        spe_si = Input("Si spectrum", RC2Spectra, default=False)

    class Outputs(FilterWidget.Outputs):
        out_model = Output("Calibration model", CalibrationModel)

    @Inputs.in_spe
    def set_in_spe(self, spe):
        if spe:
            self.in_spe = spe
        else:
            self.in_spe = RC2Spectra()
        self.update_inputs_info()

    @Inputs.spe_neon
    def set_spe_neon(self, spe):
        if spe:
            self.spe_neon = spe
        else:
            self.spe_neon = RC2Spectra()
        self.update_inputs_info()

    @Inputs.spe_si
    def set_spe_si(self, spe):
        if spe:
            self.spe_si = spe
        else:
            self.spe_si = RC2Spectra()
        self.update_inputs_info()        

    def update_inputs_info(self):
        self.Warning.clear()
        self.should_auto_plot = False        
        len00 = len(self.in_spe) if self.in_spe else None
        len11 = len(self.spe_neon) if self.spe_neon else None
        len12 = len(self.spe_si) if self.spe_si else None
       
        self.info.set_input_summary(f' {len00} RC2Spectra + Neon {len11} RC2Spectra + {len12} Si RC2Spectra')        

    def __init__(self):
        super().__init__()
        self.spe_neon = RC2Spectra()        
        self.spe_si = RC2Spectra()

        self.calibration_model = None
        box = gui.widgetBox(self.controlArea, self.name)
        gui.doubleSpin(box, self, 'laser_wl', 0, 5000, decimals=0, step=1, 
                       #callback=self.auto_process,
                       label='Laser Wavelength [nm]')        

    def derive_model(self,laser_wl,spe_neon,spe_sil):


        calmodel = CalibrationModel(laser_wl)
        calmodel.prominence_coeff = 3
        print("derive_model_zero")
        model_neon = calmodel.derive_model_curve(spe_neon,calmodel.neon_wl[laser_wl],spe_units="cm-1",ref_units="nm",find_kw={},fit_peaks_kw={},should_fit = False,name="Neon calibration")
        spe_sil_ne_calib = model_neon.process(spe_sil,spe_units="cm-1",convert_back=False)
        find_kw = {"prominence" :spe_sil_ne_calib.y_noise * calmodel.prominence_coeff , "wlen" : 200, "width" :  1 }
        print("derive_model_zero")
        model_si = calmodel.derive_model_zero(spe_sil_ne_calib,ref={520.45:1},spe_units="nm",ref_units="cm-1",find_kw=find_kw,fit_peaks_kw={},should_fit=True,name="Si calibration")
        #model_si.peaks.to_csv(os.path.join(config_root,template_file.replace(".xlsx","peaks.csv")),index=False)
        #spe_sil_calib = model_si.process(spe_sil_ne_calib,spe_units="nm",convert_back=False)
        return calmodel        
    
    def apply_calibration_x(self, old_spe: rc2.spectrum.Spectrum, spe_units="cm-1"):
        new_spe = old_spe
        model_units = spe_units
        for model in self.calibration_model.components:
            if model.enabled:
                new_spe = model.process(new_spe, model_units, convert_back=False)
                model_units = model.model_units
        return new_spe    
    
    def process(self):
        #these should be done in previous widgets
        #self.spe_si[0] = self.spe_si[0].trim_axes(method='x-axis',boundaries=(520.45-200,520.45+200))
        #self.spe_neon[0] = self.spe_neon[0].trim_axes(method='x-axis',boundaries=(100,max(self.spe_neon[0].x)))

        ## baseline  SNIP
        #kwargs = {"niter" : 40 }
        #self.spe_neon[0] = self.spe_neon[0].subtract_baseline_rc1_snip(**kwargs)  
        #self.spe_si[0] = self.spe_si[0].subtract_baseline_rc1_snip(**kwargs)          
        self.calibration_model = self.derive_model(self.laser_wl,self.spe_neon[0],self.spe_si[0])

        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                    self.apply_calibration_x(spe)
                )
        self.is_processed = True            
        self.send_outputs()    
    
    def custom_plot(self, ax):
        self.calibration_model.plot(ax=self.axes[0])            
        self.axes[0].legend()
        for spe in self.spe_si:
            spe.plot(ax=self.axes[1]) 
            _tmp = self.apply_calibration_x(spe)
            _tmp.plot(ax=self.axes[1],color='orange', label='calibrated')
        self.axes[1].legend()
        ax.set_xlabel("cm-1")

        self.axes[1].set_xlim(520.45-50,520.45+50)        
        if self.in_spe:
            for spe in self.in_spe:
                spe.plot(ax=self.axes[2],label="original")
    

    def plot_create_axes(self):
        self.axes = self.figure.subplots(nrows=3, sharex=False)
        return self.axes[2]
        
if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    import os
    try:
        WidgetPreview(XAxisCalibrationWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(XAxisCalibrationWidget).run()
