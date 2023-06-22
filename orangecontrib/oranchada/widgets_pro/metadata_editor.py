from AnyQt import QtCore
from AnyQt.QtWidgets import (QLineEdit, QTableWidget, QTableWidgetItem,
                             QTabWidget, QVBoxLayout, QWidget)
from Orange.widgets.settings import Setting

from ..base_widget import FilterWidget


class MetadataEditorOW(FilterWidget):
    name = "Metadata editor"
    description = "Visualize and edit metadata of the spectra"
    icon = "icons/spectra.svg"

    noise_scale = Setting(.01)

    def __init__(self):
        super().__init__()
        self.skip_changes = True
        self.tabw = QTabWidget()
        self.mainArea.layout().addWidget(self.tabw)
        self.tmp_spe = []

    def clear_all_tabs(self):
        for tab_i in reversed(range(self.tabw.count())):
            widget = self.tabw.widget(tab_i)
            widget.deleteLater()
            self.tabw.removeTab(tab_i)

    @QtCore.pyqtSlot(QTableWidgetItem)
    def onChanged(self, it):
        if self.skip_changes:
            return
        cur_tab_idx = self.tabw.currentIndex()
        if cur_tab_idx < 0:
            return
        table = self.tables[cur_tab_idx]
        meta = {}
        for row_i in reversed(range(table.rowCount())):
            if table.item(row_i, 0) is None or table.item(row_i, 1) is None:
                if table.item(row_i, 0) is None and table.item(row_i, 1) is None:
                    continue
                else:
                    return
            key = table.item(row_i, 0).text()
            val = table.item(row_i, 1).text()
            if key == '':
                table.removeRow(row_i)
                continue
            if table.item(row_i, 0) is not None and table.item(row_i, 1) is None:
                return

            if key in meta:
                key = key + '_orig'
            meta[key] = val
        print(meta)
        spe = self.tmp_spe[cur_tab_idx] = self.tmp_spe[cur_tab_idx].__copy__()
        spe.meta = meta
        self.spe_to_table(spe, table)
        self.auto_process()

    def spe_to_table(self, spe, table):
        self.skip_changes = True
        for _ in range(table.columnCount()):
            table.removeColumn(0)
        table.setRowCount(0)
        table.setColumnCount(2)
        table.setHorizontalHeaderItem(0, QTableWidgetItem('Metadata keys'))
        table.setHorizontalHeaderItem(1, QTableWidgetItem('Metadata values'))
        for k, v in spe.meta.serialize().items():
            table.insertRow(table.rowCount())
            table.setItem(table.rowCount()-1, 0, QTableWidgetItem(k))
            table.setItem(table.rowCount()-1, 1, QTableWidgetItem(str(v)))
        table.insertRow(table.rowCount())
        table.resizeColumnToContents(0)
        table.resizeColumnToContents(1)
        self.skip_changes = False

    def input_hook(self):
        self.clear_all_tabs()
        self.tmp_spe = []
        self.tables = []
        for spe_i, spe in enumerate(self.in_spe):
            widg = QWidget()
            layout = QVBoxLayout(widg)
            table = QTableWidget()
            table.itemChanged.connect(self.onChanged)
            self.spe_to_table(spe, table)
            le = QLineEdit(None)
            le.setText(repr(spe))
            le.setReadOnly(True)
            layout.addWidget(le)
            layout.addWidget(table)
            self.tabw.addTab(widg, str(spe_i))
            self.tmp_spe.append(spe)
            self.tables.append(table)
        self.auto_process()

    def process(self):
        self.out_spe = self.tmp_spe
        self.send_outputs()
