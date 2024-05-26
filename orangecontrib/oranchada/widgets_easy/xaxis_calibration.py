
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import  Input,Output, Msg
from ..base_widget import BaseWidget , RC2Spectra
import ramanchada2 as rc2
from Orange.data import Table

from ramanchada2.protocols.calibration import CalibrationModel

class XAxisCalibrationWidget(BaseWidget):
    name = "X axis calibration"
    description = "X-axis  calibration"
    icon = "icons/spectra.svg"

    #selected_wavelength = Setting("785")

    def input_hook(self):
        pass


    class Inputs(BaseWidget):
        in_spe = Input("Spectra to calibrate", RC2Spectra, default=False)
        spe_neon = Input("Neon spectrum", RC2Spectra, default=True)
        spe_si = Input("Si spectrum", RC2Spectra, default=False)

    #class Outputs(BaseWidget.Outputs):
    #    out_table = Output("Calibration model", CalibrationModel)

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
        len11 = len(self.spe_neon) if self.neon_spe else None
        len12 = len(self.spe_si) if self.si_spe else None
       
        self.info.set_input_summary(f' (Neon {len11} RC2Spectra + {len12} Si RC2Spectra)')        

    def __init__(self):
        super().__init__()
        self.spe_neon = RC2Spectra()        
        self.spe_si = RC2Spectra()

        self.calibration_model = None
        box = gui.widgetBox(self.controlArea, self.name)

    def calibration_model(self,laser_wl,spe_neon,spe_sil):
        calmodel = CalibrationModel(laser_wl)
        calmodel.prominence_coeff = 3
        model_neon = calmodel.derive_model_curve(spe_neon,calmodel.neon_wl[laser_wl],spe_units="cm-1",ref_units="nm",find_kw={},fit_peaks_kw={},should_fit = False,name="Neon calibration")
        spe_sil_ne_calib = model_neon.process(spe_sil,spe_units="cm-1",convert_back=False)
        find_kw = {"prominence" :spe_sil_ne_calib.y_noise * calmodel.prominence_coeff , "wlen" : 200, "width" :  1 }
        model_si = calmodel.derive_model_zero(spe_sil_ne_calib,ref={520.45:1},spe_units="nm",ref_units="cm-1",find_kw=find_kw,fit_peaks_kw={},should_fit=True,name="Si calibration")
        #model_si.peaks.to_csv(os.path.join(config_root,template_file.replace(".xlsx","peaks.csv")),index=False)
        #spe_sil_calib = model_si.process(spe_sil_ne_calib,spe_units="nm",convert_back=False)
        return calmodel        
    
    def apply_calibration_x(self,calmodel: CalibrationModel, old_spe: rc2.spectrum.Spectrum, spe_units="cm-1"):
        new_spe = old_spe
        model_units = spe_units
        for model in calmodel.components:
            if model.enabled:
                new_spe = model.process(new_spe, model_units, convert_back=False)
                model_units = model.model_units
        return new_spe    
    
if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    import os
    try:
        WidgetPreview(XAxisCalibrationWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(XAxisCalibrationWidget).run()
