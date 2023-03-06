from Orange.widgets import gui
from ..base_widget import CreatorWidget


class GenSpe(CreatorWidget):
    name = "Gen Spectra"
    description = "gen spectra"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.n_spectra = 1
        box = gui.widgetBox(self.controlArea, self.name)
        box_params = gui.widgetBox(box, 'Spe Params')
        self.gen_spe = GenSpe(self,
                              spe_xmin=('spe_xmin', box_params),
                              spe_xmax=('spe_xmax', box_params),
                              spe_nbins=('spe_nbins', box_params),
                              deltas=('deltas', box_params),
                              )

        gui.spin(box, self, 'n_spectra', 1, 50, label='Number of spectra', callback=self.auto_process)
        self.auto_process()

    def process(self):
        self.out_spe = [self.gen_spe()] * self.n_spectra
        self.send_outputs()
