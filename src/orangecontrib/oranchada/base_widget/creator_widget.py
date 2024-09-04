from .base_widget import BaseWidget
from .types import RC2Spectra


class CreatorWidget(BaseWidget, openclass=True):
    def __init__(self):
        super().__init__()
        self.in_spe = RC2Spectra()
