import ramanchada2 as rc2
from AnyQt.QtWidgets import QAbstractItemView
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from ramanchada2.auxiliary.spectra import datasets2 as data

from ..base_widget import CreatorWidget


class TestSpectra(CreatorWidget):
    name = "Load Test Spectra"
    description = "load test spectra from ramanchada2"
    icon = "icons/spectra.svg"

    filters = Setting({})
    selected_filenames = Setting([])

    def __init__(self):
        super().__init__()
        self.list_boxes = {}
        box = gui.widgetBox(self.controlArea, self.name)
        for k, v in data.get_filters().items():
            var = 'listbox_' + k + '_select_idx'
            setattr(self, var, list())
            gui.label(box, self, k)
            self.list_boxes[k] = gui.listBox(
                box, self, var, selectionMode=QAbstractItemView.MultiSelection,
                callback=self.update_filters)
            for item in sorted(v):
                self.list_boxes[k].addItem(item)

        gui.label(box, self, 'filenames')

        self.listbox_filename_select_idx = []
        self.list_box_filename = gui.listBox(
            box, self, 'listbox_filename_select_idx', selectionMode=QAbstractItemView.MultiSelection,
            callback=self.select_filename)

        filenames = sorted(data.get_filenames(**self.filters))
        for item in filenames:
            self.list_box_filename.addItem(item)
        self.auto_process()

    def update_filters(self):
        self.filters = {}
        for k, lb in self.list_boxes.items():
            self.filters[k] = [item.text() for item in self.list_boxes[k].selectedItems()]
        filenames = sorted(data.get_filenames(**self.filters))
        self.list_box_filename.clear()
        for item in filenames:
            self.list_box_filename.addItem(item)

    def select_filename(self):
        self.selected_filenames = [fn_item.text() for fn_item in self.list_box_filename.selectedItems()]
        self.auto_process()

    def process(self):
        self.out_spe = list()
        for fn in data.prepend_prefix(self.selected_filenames):
            spe = rc2.spectrum.from_local_file(fn)
            meta_dct = spe.meta.model_dump()
            meta_dct['xlabel'] = 'Raman shift [cm¯¹]'
            spe.meta = meta_dct
            self.out_spe.append(spe)
        self.send_outputs()
