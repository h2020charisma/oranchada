from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.data import Table
from Orange.widgets.widget import Msg, Input
import numpy as np

from ..base_widget import BaseWidget

from ramanchada2.spectrum import Spectrum

class Table2RCSpectra(BaseWidget):
    name = "Table to RCSpectra"
    description = "Converts table to set of RC2Spectra"
    icon = "icons/spectra.svg"

    should_auto_proc = Setting(True)
    should_auto_plot = Setting(False)

    class Inputs:
        data = Input("Data", Table, default=True)

    def __init__(self):
        # Initialize the widget
        super().__init__()
        self.data = None
        box = gui.widgetBox(self.controlArea, self.name)
                   
    @Inputs.data
    def set_data(self, data):
        self.data = data
        if self.should_auto_proc:
            self.process()

    def process(self):
        self.clear_messages()
        if self.data is None:
            self.error("No data input.")
            return
          
        self.out_spe = list()

        # Filter attributes with names that parse to numbers
        numeric_attrs = []
        numeric_indices = []

        meta_keys = []        

        for i, attr in enumerate(self.data.domain.attributes):
            try:
                x_value = float(attr.name.replace("- Mean","").strip())
                numeric_attrs.append(x_value)
                numeric_indices.append(i)
            except ValueError:
                meta_keys.append(attr.name)

        # Extract metadata values from both metadata and non-numeric attributes
        metadata_values = []
        for row in self.data:
            metadata = {key: row[key] for key in meta_keys}
            for meta_attr in self.data.domain.metas:
                metadata[meta_attr.name] = row[meta_attr]
            metadata_values.append(metadata)

        x = np.array(numeric_attrs)

        self.out_spe = []
        for row, metadata in zip(self.data, metadata_values):
            y = [row[i] for i in numeric_indices]

            # Remove pairs where y is None
            x_filtered = np.array([x[i] for i in range(len(y)) if y[i] is not None])
            y_filtered = np.array([val for val in y if val is not None])
            self.out_spe.append(Spectrum(x_filtered, y_filtered, metadata=metadata))
        self.send_outputs()

