from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import CreatorWidget
from ..processings.add_baseline import AddBaseline
from ..processings.add_noise import AddNoise
from ..processings.gen_spe import GenSpe


class GenNoisySpe(CreatorWidget):
    name = "Gen Noisy Spectra"
    description = "Generate spectra with baseline and noise"
    icon = "icons/spectra.svg"

    # Generate Spectrum
    spe_xmin = Setting(0)
    spe_xmax = Setting(2000)
    spe_nbins = Setting(1500)
    deltas_combo = Setting('PST')
    deltas = Setting('1: 1')

    # Add baseline
    n_freq = Setting(15)
    amplitude = Setting(2)
    intercept = Setting(10)
    slope = Setting(.01)
    quadratic = Setting(-.000005)

    # Add noise
    noise_scale = Setting(.01)

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
