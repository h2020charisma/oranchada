from Orange.widgets import gui
from ..base_widget import CreatorWidget

from ..processings.gen_spe import GenSpe
from ..processings.add_baseline import AddBaseline
from ..processings.add_noise import AddNoise


class GenNoisySpe(CreatorWidget):
    name = "Gen Noisy Spectra"
    description = "Generate spectra with baseline and noise"
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
        box_baseline = gui.widgetBox(box, 'Baseline')
        self.add_baseline = AddBaseline(self,
                                        n_freq=('n_freq', box_baseline),
                                        amplitude=('amplitude', box_baseline),
                                        intercept=('intercept', box_baseline),
                                        slope=('slope', box_baseline),
                                        quadratic=('quadratic', box_baseline),
                                        )
        box_noise = gui.widgetBox(box, 'Noise')
        self.add_noise = AddNoise(self,
                                  noise_scale=('noise_scale', box_noise))

        gui.spin(box, self, 'n_spectra', 1, 50, label='Number of spectra', callback=self.auto_process)
        self.auto_process()

    def process(self):
        clear_spe = self.gen_spe()
        self.out_spe = [
            self.add_noise(
                self.add_baseline(
                    clear_spe
                    )
            )
            for _ in range(self.n_spectra)
            ]

        self.send_outputs()
