from typing import Union

import ramanchada2 as rc2
from AnyQt.QtWidgets import QGroupBox
from Orange.widgets import gui
from pydantic import validate_call


class AddBaseline:
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, parent, *,
                 n_freq: tuple[str, Union[None, QGroupBox]],
                 amplitude: tuple[str, Union[None, QGroupBox]],
                 intercept: tuple[str, Union[None, QGroupBox]],
                 slope: tuple[str, Union[None, QGroupBox]],
                 quadratic: tuple[str, Union[None, QGroupBox]],
                 ):
        self._parent = parent

        self._n_freq = n_freq[0]
        if n_freq[1]:
            self.n_freq = 15
            gui.spin(n_freq[1], self._parent, 'n_freq', 3, 5000,
                     callback=self.auto_process, label='num freq')

        self._amplitude = amplitude[0]
        if amplitude[1]:
            gui.doubleSpin(amplitude[1], self._parent, self._amplitude, 0, 5000, decimals=5, step=.01,
                           label='amplitude', callback=self.auto_process)

        self._intercept = intercept[0]
        if intercept[1]:
            gui.doubleSpin(intercept[1], self._parent, self._intercept, -20000, 20000, decimals=5, step=1,
                           label='intercept', callback=self.auto_process)

        self._slope = slope[0]
        if slope[1]:
            gui.doubleSpin(slope[1], self._parent, self._slope, -1000, 1000, decimals=5, step=.001,
                           label='slope', callback=self.auto_process)

        self._quadratic = quadratic[0]
        if quadratic[1]:
            gui.doubleSpin(quadratic[1], self._parent, self._quadratic, -100, 100, decimals=7, step=.000001,
                           label='quadratic', callback=self.auto_process)

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __call__(self, spe: rc2.spectrum.Spectrum) -> rc2.spectrum.Spectrum:
        return spe.add_baseline(n_freq=self.n_freq,
                                amplitude=self.amplitude,
                                pedestal=0,
                                func=lambda x: self.intercept + x*self.slope + x**2*self.quadratic
                                )

    def auto_process(self):
        self._parent.auto_process()

    @property
    def n_freq(self):
        return getattr(self._parent, self._n_freq)

    @n_freq.setter
    def n_freq(self, val):
        setattr(self._parent, self._n_freq, val)

    @property
    def amplitude(self):
        return getattr(self._parent, self._amplitude)

    @amplitude.setter
    def amplitude(self, val):
        setattr(self._parent, self._amplitude, val)

    @property
    def intercept(self):
        return getattr(self._parent, self._intercept)

    @intercept.setter
    def intercept(self, val):
        setattr(self._parent, self._intercept, val)

    @property
    def slope(self):
        return getattr(self._parent, self._slope)

    @slope.setter
    def slope(self, val):
        setattr(self._parent, self._slope, val)

    @property
    def quadratic(self):
        return getattr(self._parent, self._quadratic)

    @quadratic.setter
    def quadratic(self, val):
        setattr(self._parent, self._quadratic, val)
