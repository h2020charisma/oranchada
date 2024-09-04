from typing import Union

import ramanchada2 as rc2
from AnyQt.QtWidgets import QGroupBox
from Orange.widgets import gui
from pydantic import validate_call


class AddNoise:
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, parent, *,
                 noise_scale: tuple[str, Union[None, QGroupBox]],
                 ):
        self._parent = parent

        self._noise_scale = noise_scale[0]
        if noise_scale[1]:
            gui.doubleSpin(noise_scale[1], self._parent, self._noise_scale, 0, 100, decimals=5, step=.001,
                           callback=self.auto_process)

    def auto_process(self):
        self._parent.auto_process()

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __call__(self, spe: rc2.spectrum.Spectrum) -> rc2.spectrum.Spectrum:
        return spe.add_poisson_noise(self.noise_scale)

    @property
    def noise_scale(self):
        return getattr(self._parent, self._noise_scale)

    @noise_scale.setter
    def noise_scale(self, val):
        setattr(self._parent, self._noise_scale, val)
