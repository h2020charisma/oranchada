from Orange.widgets import gui
import ramanchada2 as rc2
import numpy as np
from .rc2_base import RC2_Creator
from ramanchada2.aux.spectra import datasets2 as data
from AnyQt.QtWidgets import QAbstractItemView


class TestSpectra(RC2_Creator):
    name = "Load Test Spectra"
    description = "load test spectra from ramanchada2"
    icon = "icons/spectra.svg"

    def __init__(self):
        super().__init__()
        self.list_boxes = dict()

        box = gui.widgetBox(self.controlArea, self.name)
        for k, v in data.get_filters().items():
            var = k + '_select_list_box_idx'
            setattr(self, var, list())
            gui.label(box, self, k)
            self.list_boxes[k] = gui.listBox(
                box, self, var, selectionMode=QAbstractItemView.MultiSelection,
                callback=self.update_filters)
            for item in sorted(v):
                self.list_boxes[k].addItem(item)

        gui.label(box, self, 'filenames')

        self.filename_select_list_box_idx = list()
        self.list_box_filename = gui.listBox(
            box, self, 'filename_select_list_box_idx', selectionMode=QAbstractItemView.MultiSelection,
            callback=self.auto_process)
        self.update_filters()

    def update_filters(self):
        filters = dict()
        for k, lb in self.list_boxes.items():
            filters[k] = [item.text() for item in self.list_boxes[k].selectedItems()]
        filenames = data.get_filenames(**filters)
        self.list_box_filename.clear()
        for item in sorted(filenames):
            self.list_box_filename.addItem(item)

    def process(self):
        self.out_spe = list()
        for fn_item in self.list_box_filename.selectedItems():
            fn = fn_item.text()
            spe = rc2.spectrum.from_local_file(fn)
            self.out_spe.append(spe)
        self.send_outputs()
