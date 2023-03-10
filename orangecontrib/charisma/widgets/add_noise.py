from Orange.widgets import gui
from .rc2_base import RC2_Filter, RC2Spectra
from AnyQt.QtWidgets import QGroupBox
import ramanchada2 as rc2

import pydantic
from typing import Union


class AddNoise:
    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __init__(self, parent, *,
                 noise_scale: tuple[str, Union[None, QGroupBox]],
                 ):
        self._parent = parent

        self._noise_scale = noise_scale[0]
        if noise_scale[1]:
            self.noise_scale = .01
            gui.doubleSpin(noise_scale[1], self._parent, self._noise_scale, 0, 100, decimals=5, step=.001,
                           callback=self.auto_process)

    def auto_process(self):
        self._parent.auto_process()

    @pydantic.validate_arguments(config=dict(arbitrary_types_allowed=True))
    def __call__(self, spe: rc2.spectrum.Spectrum) -> rc2.spectrum.Spectrum:
        return spe.add_poisson_noise(self.noise_scale)

    @property
    def noise_scale(self):
        return getattr(self._parent, self._noise_scale)

    @noise_scale.setter
    def noise_scale(self, val):
        setattr(self._parent, self._noise_scale, val)


class AddNoiseOW(RC2_Filter):
    name = "Add Noise"
    description = "add noise"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        self.add_noise = AddNoise(self,
                                  noise_scale=('noise_scale', box))

    def process(self):
        self.out_spe = RC2Spectra()
        for spe in self.in_spe:
            self.out_spe.append(
                self.add_noise(spe)
                )
        self.send_outputs()
