# + tags=["parameters"]
upstream = []
product = None
key_spectra = None
key_leds= None
input_h5 = None

# -

import os
import ramanchada2 as rc2
import re
import pandas as pd
import numpy as np

input_spe = pd.read_hdf(input_h5, key=key_spectra)
input_spe["reference"].unique()

input_leds = pd.read_hdf(input_h5, key=key_leds)
input_leds["reference"].unique()

from fuzzywuzzy import fuzz

tags = { '785nm':"wavelength", 
        '532nm':"wavelength", 
        '785':"wavelength", 
        '532':"wavelength", 
        '150mW':"laser_power",
        '327mW':"laser_power",
        '(200mW)':"laser_power",        
          '150ms' : "acquisition_time",
          '150msx5ac' : "acquisition_time",
          'Probe': "probe", 
          '1': "replicate",
          '2': "replicate",
          '3': "replicate",
          '4': "replicate",
         '5': "replicate",
         'txt' : "extension"}

_lookup = {
    "Original file" : "Original file",
    "laser_wavelength" : "wavelength",
    "model" : "instrument",
    "title" : "title",
    "laser_wavelength" : "wavelength",
    "laser_powerlevel" : "laser_power_percent",
    "intigration times(ms)":"acquisition_time"    
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


def spe_area(spe: rc2.spectrum.Spectrum):
    return np.sum(spe.y * np.diff(spe.x_bin_boundaries))



def load_spectra(input_spe , leds = False):
    spectra={}
    for index,row in input_spe.iterrows():
        spe=row["spectrum"]
        subset = "reference" if row["reference"] else "twinning"
        result = re.split(r'[_().]+', spe.meta["Original file"])
        parsed,parsed_similarity = fuzzy_match([s for s in result if s],tags)
        #print(result)
        for m in ["Original file","laser_wavelength","model","title","laser_powerlevel","intigration times(ms)"]:
            parsed[_lookup[m]] = spe.meta[m]
        #print("parsed",parsed)
        #print("similarity",parsed_similarity)

        laser_power = parsed["laser_power"] if "laser_power" in parsed else None
        laser_power_percent = parsed["laser_power_percent"] if "laser_power_percent" in parsed else None
        acquisition_time = parsed["acquisition_time"] if "acquisition_time" in parsed else None

        if leds:
            tag=subset
        else:
            tag = "{}:{}:{}:{}:{}".format(subset,
                                    parsed["instrument"],parsed["probe"],laser_power,acquisition_time)
        if not tag in spectra:
            spectra[tag] = {"laser_power" : laser_power, "laser_power_percent" :   laser_power_percent,  
                                    "acquisition_time" :  acquisition_time, "reference" : row["reference"],
                                    "spectrum" : spe , "count" : 1 , "probe" : parsed["probe"],"device":subset,
                                    "instrument" :  parsed["instrument"],"title" :  parsed["title"]
                                    ,"wavelength" :  parsed["wavelength"],
                                    "original_file"  : [parsed["Original file"]]
                                    }
        else:
            spectra[tag]["spectrum"] = spectra[tag]["spectrum"] + spe
            spectra[tag]["count"] = spectra[tag]["count"] + 1
            print(spectra[tag])
            spectra[tag]["original_file"].append(parsed["Original file"])
            
        if leds:
            spe_led_y = spe.y
            spe_led_y[spe_led_y < 0] = 0
            spe.y = spe_led_y
            spectra[tag]["spe_dist"] = spe.spe_distribution()
            spectra[tag]["area"] =   spe_area(spe)                   
        #average replicates

    for tag in spectra:
        spe = spectra[tag]["spectrum"]
        spe /= spectra[tag]["count"]
        
    devices = pd.DataFrame(spectra).T
    devices['laser_power'] = devices['laser_power'].str.extract('(\d+)')
    devices['laser_power'] = pd.to_numeric(devices['laser_power'])
    return devices

devices = None
devices =  load_spectra(input_spe)   
devices.to_hdf(product["data"], key='devices', mode='w')

leds = None
leds =  load_spectra(input_leds,leds=True)   
leds.to_hdf(product["data"], key='led', mode='a')

try:
    devices.to_csv(product["meta_spectra"])
    leds.to_csv(product["meta_leds"])
except:
    pass