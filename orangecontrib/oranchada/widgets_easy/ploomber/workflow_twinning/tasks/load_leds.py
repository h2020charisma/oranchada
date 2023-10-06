# + tags=["parameters"]
upstream = []
product = None
root_data_folder: None
files_led_reference: None
files_led_twinned: None
files_spectra_reference: None
files_spectra_twinned: None
probe: None

# -
import ramanchada2 as rc2
import numpy as np
import re
import pandas as pd
from fuzzywuzzy import fuzz
import os

def spe_area(spe: rc2.spectrum.Spectrum):
    return np.sum(spe.y * np.diff(spe.x_bin_boundaries))


tags = { '785nm':"wavelength", 
        '532nm':"wavelength", 
        '785':"wavelength", 
        '532':"wavelength", 
          '150ms' : "acquisition_time",
          'Probe': "probe", 
          '1': "replicate",
          '2': "replicate",
          '3': "replicate",
          '4': "replicate",
         '5': "replicate",
         'txt' : "extension"}



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

#fuzzy_match(['LED785nm', 'Probe', '250ms', '10x', '1', 'txt'],tags)


def load_led(root_led=root_data_folder,folder_path_led=[files_led_reference,files_led_twinned],
             filter_filename=r'^(LED|NIR)',filter_probe="Probe"):
    led_spectra={ }
    for subset in folder_path_led:
        print(subset)
        for filename in os.listdir(os.path.join(root_led,subset)):
            if filename.endswith('.xlsx'): 
                continue
            if re.match(filter_filename, filename):
                #print(filename)
                if not filter_probe in filename:
                    continue
                result = re.split(r'[_().]+', filename)
                result = [s for s in result if s]            
                #print(fuzzy_match(result,tags))
                spe_led = rc2.spectrum.from_local_file(os.path.join(root_led,subset,filename))
                spe_led_y = spe_led.y
                spe_led_y[spe_led_y < 0] = 0
                spe_led.y = spe_led_y
                led_spectra[subset]= fuzzy_match(result,tags)[0]
                led_spectra[subset]["spectrum"] = spe_led;
                led_spectra[subset]["spe_dist"] = spe_led.spe_distribution()
                led_spectra[subset]["area"] =   spe_area(spe_led)
    return led_spectra

led_spectra = load_led(root_led=root_data_folder,folder_path_led=[files_led_reference,files_led_twinned],filter_filename=r'^(LED|NIR)',filter_probe=probe)
for key in led_spectra.keys():
    print(led_spectra[key])
assert bool(led_spectra), "No led spectra!"

led_frame = pd.DataFrame(led_spectra).T
led_frame.to_hdf(product["data"], key='led', mode='w')

match_led={
    files_spectra_reference : files_led_reference,
    files_spectra_twinned: files_led_twinned
}
tmp = pd.DataFrame([match_led]).T
tmp.columns=["led_spectra"]
tmp.to_hdf(product["data"], key='match', mode='a')