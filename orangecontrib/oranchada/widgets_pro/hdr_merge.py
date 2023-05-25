import ramanchada2 as rc2

from ..base_widget import FilterWidget


class HDRMerger(FilterWidget):
    name = "HDR Merger"
    description = rc2.spectrum.hdr_from_multi_exposure.__doc__
    icon = "icons/spectra.svg"

    def process(self):
        if self.in_spe:
            self.out_spe = [rc2.spectrum.hdr_from_multi_exposure(self.in_spe)]
        self.send_outputs()
