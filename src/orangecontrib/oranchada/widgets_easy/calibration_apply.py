import pickle
from Orange.widgets import widget, gui
from Orange.widgets.widget import Input, Output
from ramanchada2.protocols.calibration import CalibrationModel
import ramanchada2 as rc2
from ..base_widget import BaseWidget , FilterWidget, RC2Spectra


class ApplyCalibrationModel(FilterWidget):
    name = "x-calibration - Apply"
    description = "Apply x-calibration"
    icon = "icons/spectra.svg"
    priority = 10

    class Inputs(FilterWidget.Inputs):
        calibration_model = Input("Calibration Model", CalibrationModel)

    def __init__(self):
        super().__init__()
        self.calibration_model = None

    @Inputs.calibration_model
    def set_calibration_model(self, calibration_model):
        self.calibration_model = calibration_model


    def apply_calibration_x(self, old_spe: rc2.spectrum.Spectrum, spe_units="cm-1"):
        new_spe = old_spe
        model_units = spe_units
        for model in self.calibration_model.components:
            if model.enabled:
                new_spe = model.process(new_spe, model_units, convert_back=False)
                model_units = model.model_units
        return new_spe

    def process(self):
        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                    self.apply_calibration_x(spe)
                )
        self.is_processed = True            
        self.send_outputs()    

    def custom_plot(self, ax):
        if  self.calibration_model:
            self.calibration_model.plot(ax=self.axes[0])            
        self.axes[0].legend()
        if self.in_spe:
            for spe in self.in_spe:
                spe.plot(ax=self.axes[1],label="original")
    

    def plot_create_axes(self):
        self.axes = self.figure.subplots(nrows=2, sharex=False)
        return self.axes[1]        