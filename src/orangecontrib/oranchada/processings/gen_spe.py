from typing import Union

import numpy as np
import ramanchada2 as rc2
from AnyQt.QtWidgets import QGroupBox
from Orange.widgets import gui
from pydantic import validate_call


class GenSpe:
    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __init__(self, parent, *,
                 spe_xmin: tuple[str, Union[None, QGroupBox]],
                 spe_xmax: tuple[str, Union[None, QGroupBox]],
                 spe_nbins: tuple[str, Union[None, QGroupBox]],
                 deltas: tuple[str, Union[None, QGroupBox]],
                 ):
        self._parent = parent

        self._spe_xmin = spe_xmin[0]
        if spe_xmin[1]:
            gui.spin(spe_xmin[1], self._parent, self._spe_xmin, -1000, 10000, label='xmin', callback=self.auto_process)

        self._spe_xmax = spe_xmax[0]
        if spe_xmax[1]:
            gui.spin(spe_xmax[1], self._parent, self._spe_xmax, -1000, 10000, label='xmax', callback=self.auto_process)

        self._spe_nbins = spe_nbins[0]
        if spe_nbins[1]:
            gui.spin(spe_nbins[1], self._parent, self._spe_nbins, 1, 200000, label='n_bins', callback=self.auto_process)

        self._deltas = deltas[0]
        self._deltas_combo = deltas[0] + '_combo'
        if deltas[1]:
            self.deltas_edit = gui.lineEdit(deltas[1], self._parent, self._deltas, label='Deltas',
                                            callback=self.auto_process)
            gui.comboBox(deltas[1], self._parent, self._deltas_combo, sendSelectedValue=True,
                         items=['PST', 'User defined'], callback=self.set_deltas)
            self.set_deltas()

    def set_deltas(self):
        if self.deltas_combo == 'User defined':
            self.deltas_edit.setReadOnly(False)
        else:
            self.deltas = '620.9: 16, 795.8: 10, 1001.4: 100, 1031.8: 27, 1155.3: 13, 1450.5: 8, 1583.1: 12, 1602.3: 28, 2852.4: 9, 2904.5: 13, 3054.3: 32'  # noqa: E501
            self.deltas_edit.setReadOnly(True)

    @validate_call(config=dict(arbitrary_types_allowed=True))
    def __call__(self) -> rc2.spectrum.Spectrum:
        deltas_dict = dict([[float(j) for j in i.split(':')] for i in self.deltas.replace(' ', '').split(',')])
        spe1 = rc2.spectrum.Spectrum(x=np.array(list(deltas_dict.keys())), y=np.array(list(deltas_dict.values())))
        return spe1.resample_NUDFT_filter(x_range=(self.spe_xmin, self.spe_xmax), xnew_bins=self.spe_nbins)

    def auto_process(self):
        self._parent.auto_process()

    @property
    def spe_xmin(self):
        return getattr(self._parent, self._spe_xmin)

    @spe_xmin.setter
    def spe_xmin(self, val):
        setattr(self._parent, self._spe_xmin, val)

    @property
    def spe_xmax(self):
        return getattr(self._parent, self._spe_xmax)

    @spe_xmax.setter
    def spe_xmax(self, val):
        setattr(self._parent, self._spe_xmax, val)

    @property
    def spe_nbins(self):
        return getattr(self._parent, self._spe_nbins)

    @spe_nbins.setter
    def spe_nbins(self, val):
        setattr(self._parent, self._spe_nbins, val)

    @property
    def deltas(self):
        return getattr(self._parent, self._deltas)

    @deltas.setter
    def deltas(self, val):
        setattr(self._parent, self._deltas, val)

    @property
    def deltas_combo(self):
        return getattr(self._parent, self._deltas_combo)

    @deltas_combo.setter
    def deltas_combo(self, val):
        setattr(self._parent, self._deltas_combo, val)
