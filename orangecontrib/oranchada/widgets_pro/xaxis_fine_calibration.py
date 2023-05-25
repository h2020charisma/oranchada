import numpy as np
import ramanchada2.misc.constants as rc2const
import ramanchada2.misc.utils as rc2utils
from Orange.widgets import gui
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class XAxisFineCalibration(FilterWidget):
    name = "Xaxis fine calibration"
    description = "X-axis fine calibration"
    icon = "icons/spectra.svg"

    predefined_deltas = Setting('Ne WL D3.3')
    deltas = Setting('')
    poly_order = Setting('poly3')
    should_fit = Setting(False)
    prominence = Setting(3.)
    wlen = Setting(200)
    min_peak_width = Setting(2)
    should_auto_proc = Setting(False)
    n_iters = Setting(1)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)

        gui.doubleSpin(box, self, 'prominence', 0, 50000, decimals=2, step=1, callback=self.auto_process,
                       label='Prominence [×σ]')
        gui.spin(box, self, 'wlen', 0, 50000, step=1, callback=self.auto_process, label='wlen')
        gui.spin(box, self, 'min_peak_width', 1, 5000, callback=self.auto_process, label='Min peak width')

        gui.checkBox(box, self, "should_fit", "Should fit", callback=self.auto_process)

        gui.comboBox(box, self, 'poly_order', sendSelectedValue=True,
                     items=['poly0', 'poly1', 'poly2', 'poly3', 'poly4', 'RBF thin-plate-spline'],
                     callback=self.auto_process
                     )

        self.combo = gui.comboBox(box, self, 'predefined_deltas', sendSelectedValue=True,
                                  items=[
                                      'Ne RS 532nm', 'Ne RS 633nm', 'Ne RS 785nm',
                                      'Ne WL 532nm', 'Ne WL 633nm', 'Ne WL 785nm',
                                      'Ne WL D3.3', 'PST', 'User defined'], label='Deltas',
                                  callback=self.deltas_combo_callback)
        self.deltas_edit = gui.lineEdit(box, self, 'deltas', callback=self.auto_process)

        gui.spin(box, self, 'n_iters', 0, 20, label='N iters', callback=self.auto_process)

        self.deltas_combo_callback()

    def deltas_combo_callback(self):
        self.deltas_edit.setReadOnly(True)
        if self.predefined_deltas == 'Ne RS 532nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_rs_532_nist_dict.items()])
        elif self.predefined_deltas == 'Ne RS 633nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_rs_532_nist_dict.items()])
        elif self.predefined_deltas == 'Ne RS 785nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_rs_785_nist_dict.items()])
        elif self.predefined_deltas == 'Ne WL 532nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_wl_532_nist_dict.items()])
        elif self.predefined_deltas == 'Ne WL 633nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_wl_532_nist_dict.items()])
        elif self.predefined_deltas == 'Ne WL 785nm':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_wl_785_nist_dict.items()])
        elif self.predefined_deltas == 'Ne WL D3.3':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.neon_wl_D3_3_dict.items()])
        elif self.predefined_deltas == 'PST':
            self.deltas = ', '.join([f'{k}: {v}' for k, v in rc2const.PST_RS_dict.items()])
        elif self.predefined_deltas == 'User defined':
            self.deltas_edit.setReadOnly(False)
        self.auto_process()

    def process(self):
        self.deltas_dict = dict([[float(j) for j in i.split(':')] for i in self.deltas.replace(' ', '').split(',')])
        if self.poly_order == 'poly0':
            poly_order_num = 0
        elif self.poly_order == 'poly1':
            poly_order_num = 1
        elif self.poly_order == 'poly2':
            poly_order_num = 2
        elif self.poly_order == 'poly3':
            poly_order_num = 3
        elif self.poly_order == 'poly4':
            poly_order_num = 4

        self.out_spe = list()
        if len(self.in_spe) > 1:
            raise ValueError(f'Expects a single spectrum input. {len(self.in_spe)} found')
        for spe in self.in_spe:
            for iter in range(self.n_iters):
                if self.poly_order == 'RBF thin-plate-spline':
                    spe = spe.xcal_fine_RBF(ref=self.deltas_dict, should_fit=self.should_fit,
                                            find_peaks_kw=dict(prominence=spe.y_noise*self.prominence,
                                                               wlen=self.wlen,
                                                               width=self.min_peak_width,
                                                               )
                                            )
                else:
                    spe = spe.xcal_fine(ref=self.deltas_dict, poly_order=poly_order_num, should_fit=self.should_fit,
                                        find_peaks_kw=dict(prominence=spe.y_noise*self.prominence,
                                                           wlen=self.wlen,
                                                           width=self.min_peak_width,
                                                           )
                                        )
            self.out_spe.append(spe)
        self.send_outputs()

    def custom_plot(self, ax):
        if not self.in_spe:
            return
        self.in_spe[0].plot(ax=self.axes[0])
        self.axes[0].twinx().stem(list(self.deltas_dict.keys()), list(self.deltas_dict.values()),
                                  basefmt='', linefmt='r:', label='reference')
        ax1_twin = self.axes[1].twinx()
        ax1_twin.stem(list(self.deltas_dict.keys()), list(self.deltas_dict.values()),
                      basefmt='', linefmt='r:', label='reference')
        x, x_exp, y, yerr = self.diff(self.out_spe[0], self.deltas_dict)
        ax1_twin.plot([x, x_exp], [0, 0], 'r', lw=4)
        self.axes[2].errorbar(x, y, yerr, fmt='.:', label='difference')
        for a in self.axes:
            a.grid()
            a.legend()
        y_ub = y + yerr
        y_lb = y - yerr
        y_ub = np.mean(y_ub) + np.std(y_ub)*3
        y_lb = np.mean(y_lb) - np.std(y_lb)*3
        self.axes[2].set_ylim(y_lb, y_ub)
        self.axes[0].set_title('Before calibration')
        self.axes[1].set_title('After calibration')
        self.axes[2].set_title('Difference')
        self.axes[2].set_xlabel(ax.get_xlabel())
        ax.set_xlabel('')

    def plot_create_axes(self):
        self.axes = self.figure.subplots(nrows=3, sharex=True)
        return self.axes[1]

    def diff(self, spe, ref_pos):
        if isinstance(ref_pos, dict):
            ref_pos = list(ref_pos.keys())
        if isinstance(ref_pos, list):
            ref_pos = np.array(ref_pos)
        ss = spe.subtract_moving_minimum(100)
        kw = dict(sharpening=None, hht_chain=[100])
        cand = ss.find_peak_multipeak(**kw)

        if self.should_fit:
            kw = dict(profile='Gaussian')
            fit_res = spe.fit_peak_multimodel(candidates=cand, **kw)
            spe_pos, spe_pos_err = fit_res.centers_err.T
        else:
            spe_pos = np.array(list(cand.get_pos_ampl_dict().keys()))
            spe_pos_err = np.zeros_like(spe_pos)

        spe_pos_match_idx, ref_pos_match_idx = rc2utils.find_closest_pairs_idx(spe_pos, ref_pos)
        spe_pos_match = spe_pos[spe_pos_match_idx]
        ref_pos_match = ref_pos[ref_pos_match_idx]
        return ref_pos_match, spe_pos_match, (spe_pos_match-ref_pos_match), spe_pos_err[spe_pos_match_idx]
