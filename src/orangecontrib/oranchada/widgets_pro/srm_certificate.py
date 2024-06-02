import numpy as np
from Orange.widgets import gui
from Orange.widgets.settings import Setting

from Orange.widgets.widget import  Output
from Orange.data import Table

from ..base_widget import CreatorWidget
from ramanchada2.protocols.calibration import  YCalibrationCertificate
from ramanchada2.spectrum import Spectrum

from Orange.data.pandas_compat import table_from_frame
import pandas as pd

class EditYCalibrationCertificateWidget(CreatorWidget):
    name = "Edit Y Calibration Certificate"
    description = "Edit Y Calibration Certificate and return results as a table"
    icon = "icons/spectra.svg"

    id = Setting("NIR785_EL0-9002")
    wavelength = Setting(785)
    params = Setting("A0 = 5.90134423e-1,A = 5.52032185e-1,B = 5.72123096e-7,x0 = 2.65628776e+3")
    equation = Setting("A0 + A * np.exp(-B * (x - x0)**2)")
    raman_shift_min = Setting(200)
    raman_shift_max = Setting(3500)
    temperature_c_min = Setting(20)
    temperature_c_max = Setting(25)    
    
    class Outputs(CreatorWidget.Outputs):
        out_table = Output("Edited Certificate Table", Table)



    def __init__(self):
        super().__init__()

        mbox = gui.widgetBox(self.controlArea, "Mandatory")
        gui.doubleSpin(mbox, self, 'wavelength', 0, 5000, decimals=0, step=1, 
                       callback=self.auto_process,
                       label='Laser Wavelength [nm]')   
        gui.lineEdit(mbox, self, "id", label="ID:")
        #gui.lineEdit(box, self, "description", label="Description:")
        #gui.lineEdit(mbox, self, "url", label="URL:")
        gui.lineEdit(mbox, self, "params", label="Params:",callback=self.auto_process)
        gui.lineEdit(mbox, self, "equation", label="Equation:",callback=self.auto_process)
     
        obox = gui.widgetBox(self.controlArea, "Optional")
        gui.spin(obox, self, "raman_shift_min", 0, 200, label="Raman Shift Min:",callback=self.auto_process)
        gui.spin(obox, self, "raman_shift_max", 50, 4500, label="Raman Shift Max:",callback=self.auto_process)     
        gui.spin(obox, self, "temperature_c_min", -100, 100, label="Temperature Min (C):",callback=self.auto_process)
        gui.spin(obox, self, "temperature_c_max", -100, 100, label="Temperature Max (C):",callback=self.auto_process)
        self.auto_process()
    
    def process(self):
        _cert = YCalibrationCertificate(
            id=self.id,
            description="",
            url="",
            wavelength=self.wavelength,
            params=self.params,
            equation=self.equation,
            temperature_c=(self.temperature_c_min, self.temperature_c_max),
            raman_shift=(self.raman_shift_min, self.raman_shift_max)
        )        
        if _cert.raman_shift is None:
            x = np.linspace(100, 4000)
        else:
            x = np.linspace(_cert.raman_shift[0], _cert.raman_shift[1])
        y = _cert.Y(x)
        self.out_spe = [Spectrum(x=x,y=y)]

        self.send_outputs()

# Create an Orange data table from the certificate
        columns = [
            "ID",
            "Wavelength",
            "Params",
            "Equation",
            "Temperature Min",
            "Temperature Max",
            "Raman Shift Min",
            "Raman Shift Max"
        ]

        data = [[
            _cert.id,
            int(_cert.wavelength),
            _cert.params,
            _cert.equation,
            _cert.temperature_c[0],
            _cert.temperature_c[1],
            _cert.raman_shift[0],
            _cert.raman_shift[1]
        ]]
        df = pd.DataFrame(data, columns=columns)
        self.Outputs.out_table.send(table_from_frame(df))        