from collections import UserList

from Orange.data import Table
from AnyQt.QtWidgets import QFileDialog
from Orange.widgets import gui
from Orange.widgets.settings import Setting
from Orange.widgets.widget import Output, OWBaseWidget

import pandas as pd
from Orange.data.pandas_compat import table_from_frame
import os.path
from fuzzywuzzy import fuzz
import re
import ramanchada2 as rc2


tags = { '785nm':"wavelength", 
        '532nm':"wavelength", 
        '785':"wavelength", 
        '532':"wavelength", 
        '150mW':"laser_power",
        '327mW':"laser_power",
        '(200mW)':"laser_power",      
        '20%':"laser_power_percent",   
          '150ms' : "acquisition_time",
          '150msx5ac' : "acquisition_time",
          'Probe': "probe", 
          '20x': "probe", 
          '1': "replicate",
          '2': "replicate",
          '3': "replicate",
          '4': "replicate",
         '5': "replicate",
         'position 1': "replicate",
         'txt' : "extension",
         'Neon' : 'sample',
         'Ti' : 'sample',
         'nCal' : 'sample',
         'sCal' : 'sample',
         'Si' : 'sample',
         'S1' : 'sample',
         'S0B' : 'sample',
         'PST' : 'sample',
         'LED' : 'sample',
         'NIR' : 'sample',
         'OP01' : "optical_path"
         }

_lookup = {
    "Original file" : "Original file",
    "laser_wavelength" : "wavelength",
    "model" : "instrument",
    "title" : "title",
    "device" : "instrument",
    "laser_wavelength" : "wavelength",
    "laser_powerlevel" : "laser_power_percent",
    "intigration times(ms)":"acquisition_time",
    "integration times(ms)":"acquisition_time",
    "integ_time" :  "acquisition_time"      
}
def fuzzy_match(vals,tags):
    parsed = {}
    parsed_similarity= {}
    for val in vals:
        similarity_score = None
        match = None
        for tag in tags:
            _tmp = fuzz.ratio(val,tag)
            if (similarity_score is None) or (similarity_score < _tmp):
                similarity_score =_tmp
                match = tags[tag]
        if not match in parsed:
            parsed[match]  = val
            parsed_similarity[match] = similarity_score
        else:
            if parsed_similarity[match] < similarity_score:
                parsed[match]  = val
                parsed_similarity[match] = similarity_score        
    if "wavelength" in parsed:
         parsed["wavelength"] = re.findall(r'\d+', parsed["wavelength"])[0]
    if "extension" in parsed:
        del parsed["extension"]            
    return (parsed,parsed_similarity)

class LoadFileNames(OWBaseWidget):
    name = "Load File Names"
    description = "Load file names"
    icon = "icons/spectra.svg"
    resizing_enabled = False
    want_main_area = False

    filenames = Setting([])

    class Outputs:
        data = Output("File list", Table, default=False, auto_summary=False)

    def __init__(self):
        super().__init__()
        box = gui.widgetBox(self.controlArea, self.name)
        gui.button(box, self, "Load File names", callback=self.load_file)

    def load_file(self):
        self.filenames, filt = QFileDialog.getOpenFileNames(
            caption='Open spectra',
            directory='',
            filter='All files (*)',
            initialFilter='All files (*)',
            )
        _tmp = {}
        for fn in self.filenames:
            #parent_path, filename = os.path.split(fn)
            file_name = os.path.basename(fn)
            file_name, file_extension = os.path.splitext(file_name)
            basename = re.split(r'[-_()]+', file_name)

            parsed,parsed_similarity = fuzzy_match([s for s in basename if s],tags)
            try:
                spe=rc2.spectrum.from_local_file(fn)
                for m in ["Original file","laser_wavelength","model","title","laser_powerlevel","integration times(ms)","intigration times(ms)","integ_time","device","spectrometer"]:
                    try:
                        parsed[_lookup[m]] = spe.meta[m]
                    except:
                        pass
            except Exception as err:
                print(err)
                pass
            
            _tmp[fn] = parsed

        self.Outputs.data.send(table_from_frame(pd.DataFrame.from_dict(_tmp, orient="index")))
        #self.Outputs.data.send(table_from_frame(pd.DataFrame(_tmp,columns=["path","folder","filename"])))
