import numpy as np
import ramanchada2.misc.constants as rc2const
import ramanchada2.misc.utils as rc2utils
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import OWWidget, Input, Msg
from ..base_widget import BaseWidget , RC2Spectra
import logging
import ramanchada2 as rc2

from ramanchada2.protocols.calibration import YCalibrationComponent, YCalibrationCertificate, CertificatesDict



class YAxisCalibrationWidget(BaseWidget):
    name = "Y axis calibration"
    description = "Y-axis (intensity) calibration"
    icon = "icons/spectra.svg"

    selected_wavelength = Setting("785")
    selected_certificate = Setting('NIST785_SRM2241')
    should_auto_proc = Setting(True)
    should_auto_plot = Setting(True)

    def input_hook(self):
        pass


    class Inputs:
        in_spe = Input("Spectra to calibrate", RC2Spectra, default=True)
        srm_spe = Input("SRM spectrum", RC2Spectra, default=False)


    @Inputs.in_spe
    def set_in_spe(self, spe):
        if spe:
            self.in_spe = spe
        else:
            self.in_spe = RC2Spectra()
        self.update_inputs_info()

    @Inputs.srm_spe
    def set_srm_spe(self, spe):
        if spe:
            self.srm_spe = spe
        else:
            self.srm_spe = RC2Spectra()
        self.update_inputs_info()

    # same class can be initiated for Error and Information messages
    class Warning(OWWidget.Warning):
        warning = Msg("Warning")

    class Information(OWWidget.Information):
        success = Msg("Workflow successful")

    class Error(OWWidget.Error):
        processing_error = Msg("Workflow error")

    def update_inputs_info(self):
        self.Warning.clear()
        len11 = len(self.in_spe) if self.in_spe else None
        len12 = len(self.srm_spe) if self.srm_spe else None
       
        self.info.set_input_summary(f' (Input {len11} RC2Spectra + {len12} SRM RC2Spectra)')

    def __init__(self):
        super().__init__()
        self.srm_spe = RC2Spectra()
        self.certificates = CertificatesDict()

        box = gui.widgetBox(self.controlArea, self.name)
        self.wavelength_options = self.certificates.get_laser_wl()
        self.wavelength_options = sorted(map(int, self.wavelength_options))
        self.selected_wavelength = 0
        self.wavelength_combo = gui.comboBox(
            box, self, "selected_wavelength",
            label="Select Wavelength:",
            items=self.wavelength_options,
            callback=self.update_certificate_options
        )

        # Second dropdown for selecting SRM certificate based on wavelength
        # Second dropdown for selecting SRM certificate based on wavelength
        self.certificate_combo = gui.comboBox(
            box, self, "selected_certificate",
            label="Select SRM Certificate:",
            items=[],sendSelectedValue=True,
            callback=self.auto_process
        )
        self.update_certificate_options()                
        
    def update_certificate_options(self):
        # Get the selected wavelength
        self.should_auto_proc = False
        selected_wavelength = self.wavelength_options[self.selected_wavelength]
        certs = self.certificates.get_certificates(wavelength=selected_wavelength)
        self.certificate_combo.clear()
        self.certificate_combo.addItems(certs.keys())
        self.certificate_combo.setCurrentIndex(0)
        #print(self.certificate_combo.currentIndex(),self.certificate_combo.currentText())
        self.should_auto_proc = True

    def get_certificate(self):
        selected_wavelength = self.wavelength_options[self.selected_wavelength]
        return self.certificates.get(selected_wavelength,self.certificate_combo.currentText())

    def ycalibrate(self,spe,ycal):
        return ycal.process(spe)

    def process(self):
        selected_wavelength = self.wavelength_options[self.selected_wavelength]
        cert = self.get_certificate()
        ycal = YCalibrationComponent(selected_wavelength, reference_spe_xcalibrated=self.srm_spe[0],certificate=cert)
        print("Processing Y-axis calibration with SRM: {}".format(cert.id))

        self.out_spe = list()
        for spe in self.in_spe:
            self.out_spe.append(
                    self.ycalibrate(spe,ycal)
                )
        self.is_processed = True            
        self.send_outputs()

    def custom_plot(self, ax):

        if not self.in_spe:
            return
        for spe in self.in_spe:
            spe.plot(ax=self.axes[0])
        for spe in self.srm_spe:
            try:
                spe.plot(ax=self.axes[0],color="magenta",label=spe.meta["Original file"])
            except:
                pass
        cert = self.get_certificate()
        if cert != None:
            cert.plot(ax=self.axes[0].twinx(),color="pink")

    

    def plot_create_axes(self):
        self.axes = self.figure.subplots(nrows=2, sharex=True)
        return self.axes[1]

if __name__ == "__main__":
    from Orange.widgets.utils.widgetpreview import WidgetPreview
    import os
    try:
        WidgetPreview(YAxisCalibrationWidget).run()
    except Exception as err:
        print(err)
        WidgetPreview(YAxisCalibrationWidget).run()
