import pickle
from Orange.widgets import widget, gui
from Orange.widgets.widget import Input, Output
from ramanchada2.protocols.calibration import CalibrationModel
from AnyQt.QtWidgets import QFileDialog

class LoadCalibrationModel(widget.OWWidget):
    name = "x-calibration Load"
    description = "Load x-Calibration Model"
    icon = "icons/spectra.svg"
    priority = 10

    class Outputs:
        calmodel = Output("Calibration Model", CalibrationModel)

    def __init__(self):
        super().__init__()
        self.calmodel = None

        # Create load button
        self.load_button = gui.button(self.controlArea, self, "Load", callback=self.load_file)


    def load_file(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(self, "Load x-calibration model", "",
                                                  "Calibration model (*.calmodel)", options=options)

        if filename:
            with open(filename, 'rb') as file:
                self.calmodel = pickle.load(file)
                self.Outputs.calmodel.send(self.calmodel)               

    def custom_plot(self, ax):
        self.calibration_model.plot(ax=self.ax)            
