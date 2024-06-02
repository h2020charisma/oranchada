# + tags=["parameters"]
upstream = None
product = None
input_folder = None
hsds_investigation = None
hsds_instrument = None
hsds_provider = None
# -

import os
import glob
import re
from fuzzywuzzy import fuzz
import pandas as pd
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

def list_files_in_directory(directory, file_pattern='*.*'):
    metadata = {}
    files = glob.glob(os.path.join(directory, '**', file_pattern), recursive=True)
    for file in files:
        try:
            spe=rc2.spectrum.from_local_file(file)
            #print(spe.meta)
            file_name = os.path.basename(file)
            file_name, file_extension = os.path.splitext(file_name)
            basename = re.split(r'[-_()]+', file_name)
            if file_extension in ["json","xlsx"]:
                continue
            parsed,parsed_similarity = fuzzy_match([s for s in basename if s],tags)
            for m in ["Original file","laser_wavelength","wl","model","title","laser_powerlevel","integration times(ms)","intigration times(ms)","integ_time","device","spectrometer"]:
                try:
                    parsed[_lookup[m]] = spe.meta[m]
                except:
                    pass
            relative_path = os.path.relpath(file, directory)
            metadata[relative_path] = parsed
        except:
            pass
    return metadata



metadata = list_files_in_directory(input_folder)

df = pd.DataFrame.from_dict(metadata, orient="index")
df["hsds_investigation"] = hsds_investigation
df["hsds_provider"] = hsds_provider
df["hsds_instrument"] = hsds_instrument
df["enabled"] = True
df["delete"] = False

with pd.ExcelWriter(product["data"], engine='openpyxl') as writer:
    df.to_excel(writer,sheet_name="files")
    pd.DataFrame({"value": [input_folder]}, index=["path"]).to_excel(writer, sheet_name='paths')